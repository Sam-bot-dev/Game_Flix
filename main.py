# app.py
import time
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# ---- TWITCH / IGDB CREDENTIALS (you provided these) ----
CLIENT_ID = "aekin04nz4qs94z3qu96q69q7pxzoq"
CLIENT_SECRET = "jpc43hdv4r29dhngg1yfybjiz3q6sv"

# ---- token cache ----
_TOKEN = None
_TOKEN_EXPIRES_AT = 0

def get_twitch_app_token(force=False):
    """
    Get (and cache) Twitch app access token using client credentials flow.
    """
    global _TOKEN, _TOKEN_EXPIRES_AT
    if not force and _TOKEN and time.time() < _TOKEN_EXPIRES_AT - 60:
        return _TOKEN

    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    res = requests.post(url, params=params, timeout=10)
    res.raise_for_status()
    data = res.json()
    token = data.get("access_token")
    expires_in = data.get("expires_in", 0)
    if not token:
        raise RuntimeError("Failed to obtain Twitch token: " + str(data))
    _TOKEN = token
    _TOKEN_EXPIRES_AT = time.time() + int(expires_in)
    return _TOKEN

def igdb_post(path, body, timeout=15):
    """
    Helper to POST to IGDB endpoints.
    path: 'games' or 'genres' etc.
    body: raw apicalypse query string or data.
    """
    token = get_twitch_app_token()
    url = f"https://api.igdb.com/v4/{path}"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {token}"
    }
    res = requests.post(url, headers=headers, data=body, timeout=timeout)
    # If token expired or unauthorized, refresh once
    if res.status_code == 401:
        get_twitch_app_token(force=True)
        token = get_twitch_app_token()
        headers["Authorization"] = f"Bearer {token}"
        res = requests.post(url, headers=headers, data=body, timeout=timeout)
    # propagate errors gracefully
    try:
        res.raise_for_status()
    except Exception as e:
        # include response body for debugging
        raise RuntimeError(f"IGDB request failed ({res.status_code}): {res.text}") from e
    return res.json()

# ---- utilities to normalize IGDB responses ----

def igdb_cover_url(image_id, size_token="t_1080p"):
    if not image_id:
        return None
    return f"https://images.igdb.com/igdb/image/upload/{size_token}/{image_id}.jpg"

def fetch_genre_names_by_ids(ids):
    if not ids:
        return []
    ids_list = ", ".join(map(str, ids))
    body = f"fields id, name; where id = ({ids_list});"
    try:
        genres = igdb_post("genres", body)
        id_to_name = {g["id"]: g.get("name", "") for g in genres}
        # preserve order
        return [id_to_name.get(i, "") for i in ids]
    except Exception as e:
        # fallback: return empty or numeric ids as strings
        return [str(i) for i in ids]

def normalize_game_item(item):
    """
    Map raw IGDB game object to simplified dict used by frontend.
    """
    game = {}
    game["id"] = item.get("id")
    game["title"] = item.get("name")
    # cover may be a nested object with image_id
    cover = item.get("cover") or {}
    image_id = None
    if isinstance(cover, dict):
        # cover may contain image_id
        image_id = cover.get("image_id") or cover.get("cloudinary_id")
    # fallback: some providers include 'cover.image_id' directly
    if not image_id and item.get("cover") and isinstance(item.get("cover"), int):
        # if cover is an id, we would need another request for cover details; skipping
        image_id = None
    game["cover"] = igdb_cover_url(image_id) if image_id else None

    # genres: IGDB returns list of genre ids in "genres" field
    genre_ids = item.get("genres") or []
    game["genres"] = fetch_genre_names_by_ids(genre_ids) if genre_ids else []

    game["summary"] = item.get("summary") or item.get("storyline") or ""
    game["first_release_date"] = item.get("first_release_date") or None
    game["rating"] = item.get("rating") or None
    return game

# -------------------- API ROUTES --------------------

@app.route("/api/search_game")
def api_search_game():
    """
    Search games by name (used by your SEARCH.html).
    Query param: q
    """
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"results": []})

    # IGDB apicalypse query - search by name/summary, pull covers & genres
    body = f'''
    fields name, cover.image_id, genres, summary, first_release_date, rating;
    search "{q}";
    limit 30;
    '''
    try:
        raw = igdb_post("games", body)
        results = [normalize_game_item(item) for item in raw]
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/games/trending")
def api_games_trending():
    """
    TRENDING FIXED:
    Sort by total_rating_count (most reliable field for popularity).
    """
    body = """
    fields name, cover.image_id, genres, summary, first_release_date, rating, total_rating_count;
    where total_rating_count != null;
    sort total_rating_count desc;
    limit 12;
    """

    try:
        raw = igdb_post("games", body)
        results = [normalize_game_item(item) for item in raw]
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/games/new")
def api_games_new():
    """
    New releases: games released in the last ~120 days (or upcoming small window).
    We'll compute unix timestamps for date range.
    """
    # compute unix timestamps (seconds)
    now = int(time.time())
    days_back = 120
    since = now - days_back * 24 * 3600
    # optionally include upcoming releases in next 30 days:
    until = now + 30 * 24 * 3600

    body = f'''
    fields name, cover.image_id, genres, summary, first_release_date, rating;
    where first_release_date >= {since} & first_release_date <= {until};
    sort first_release_date desc;
    limit 12;
    '''
    try:
        raw = igdb_post("games", body)
        results = [normalize_game_item(item) for item in raw]
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/recommend", methods=["GET", "POST"])
def api_recommend():
    """
    Guaranteed to return EXACTLY 5 horror recommendations.
    No invalid IGDB queries.
    """
    payload = request.get_json(silent=True) or {}

    prefs = payload.get("context", {}).get("preferences", [])

    # Default horror preferences
    if not prefs:
        prefs = [
            "survival horror",
            "psychological horror",
            "first-person horror",
            "zombies",
            "dark atmosphere",
            "supernatural horror",
            "story rich horror"
        ]

    RESULTS_NEEDED = 5
    QUERY_LIMIT = 5

    all_results = {}

    # -------------------------------------
    # FETCH RESULTS BASED ON HORROR THEMES
    # -------------------------------------
    for pref in prefs:
        q = pref.replace('"', "")

        body = f"""
        fields name, cover.image_id, genres, summary, first_release_date, rating, total_rating_count;
        search "{q}";
        limit {QUERY_LIMIT};
        """

        try:
            raw = igdb_post("games", body)

            for game in raw:
                gid = game.get("id")
                if gid not in all_results:
                    all_results[gid] = normalize_game_item(game)

                if len(all_results) >= RESULTS_NEEDED:
                    break

        except Exception as e:
            print("Error IGDB horror search:", e)
            continue

        if len(all_results) >= RESULTS_NEEDED:
            break

    # -------------------------------------
    # FALLBACK (if <5 results found)
    # -------------------------------------
    if len(all_results) < RESULTS_NEEDED:
        fallback_body = """
        fields name, cover.image_id, genres, summary, first_release_date, rating, total_rating_count;
        where total_rating_count > 200;
        limit 20;
        """

        try:
            raw = igdb_post("games", fallback_body)
            for g in raw:
                gid = g["id"]
                if gid not in all_results:
                    all_results[gid] = normalize_game_item(g)
                if len(all_results) >= RESULTS_NEEDED:
                    break
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # -------------------------------------
    # RETURN EXACTLY 5 GAMES
    # -------------------------------------
    final_list = list(all_results.values())[:RESULTS_NEEDED]

    return jsonify({"results": final_list})



# Optional: simple route to refresh token manually
@app.route("/api/token/refresh")
def refresh_token():
    try:
        token = get_twitch_app_token(force=True)
        return jsonify({"access_token": token, "expires_at": _TOKEN_EXPIRES_AT})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_twitch_token():
    global TOKEN, TOKEN_EXPIRE
    if TOKEN and time.time() < TOKEN_EXPIRE - 60:
        return TOKEN
    url = f"https://id.twitch.tv/oauth2/token?client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}&grant_type=client_credentials"
    res = requests.post(url).json()
    TOKEN = res.get("access_token")
    TOKEN_EXPIRE = time.time() + res.get("expires_in", 3600)
    return TOKEN

@app.route("/api/game-by-name")
def game_by_name():
    name = request.args.get("name")
    if not name:
        return jsonify({"error": "Name query parameter is required"}), 400

    try:
        token = get_twitch_app_token()
        headers = {
            "Client-ID": CLIENT_ID,
            "Authorization": f"Bearer {token}"
        }

        query = f'''
        search "{name}";
        fields id,name,summary,total_rating,first_release_date,genres,platforms,cover.image_id,screenshots.image_id,videos.video_id,similar_games;
        limit 1;
        '''
        res = requests.post("https://api.igdb.com/v4/games", headers=headers, data=query, timeout=10)
        if res.status_code != 200:
            return jsonify({"error": f"IGDB error {res.status_code}: {res.text}"}), res.status_code

        games = res.json()
        if not games:
            return jsonify({"error": "Game not found"}), 404

        game = games[0]

        # Fetch genres names
        game["genres"] = fetch_genre_names_by_ids(game.get("genres", []))

        # Fetch similar games
        if "similar_games" in game and game["similar_games"]:
            ids = ",".join(map(str, game["similar_games"]))
            sim_query = f'fields id,name,cover.image_id; where id = ({ids}); limit 10;'
            sim_res = requests.post("https://api.igdb.com/v4/games", headers=headers, data=sim_query, timeout=10)
            if sim_res.status_code == 200:
                game["similar_games"] = sim_res.json()
            else:
                game["similar_games"] = []

        return jsonify(game)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Serve index / pages if using Flask templates
@app.route("/")
def index():
    return render_template("HOME.html")

@app.route("/SEARCH.html")
def search_page():
    return render_template("SEARCH.html")

@app.route("/G_DETAILS.html")
def details_page():
    return render_template("G_DETAILS.html")

@app.route("/FAV.html")
def fav_page():
    return render_template("FAV.html")

if __name__ == "__main__":
    # Pre-warm token
    try:
        get_twitch_app_token()
    except Exception as e:
        print("Warning: failed to obtain Twitch token at startup:", e)
    app.run(host="0.0.0.0", port=5000, debug=True)
