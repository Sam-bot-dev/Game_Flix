from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import tempfile, os, subprocess, shutil, json

    # -----------------------------
    # Gemini Setup
    # -----------------------------
API_KEY = "AIzaSyAzABFVkaH12O5xGAyKVoFFA5byGMKA7BQ"
genai.configure(api_key=API_KEY)

app = Flask(__name__)
model = genai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat(history=[])

    # -----------------------------
    # Routes for pages
    # -----------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chatbot.html')
def chatbot():
    return render_template('chatbot.html')

    # -----------------------------
    # Vulnerability Scanner Route
    # -----------------------------
@app.route('/scan', methods=['POST'])
def scan():
    data = request.get_json()
    code_snippet = data.get('code', '').strip()
    lang = data.get('lang', 'python').lower()

    if not code_snippet:
        return jsonify({'error': "No code provided."}), 400

    tmpdir = None
    try:
            # 1️⃣ Save snippet temporarily
        ext = {"python": ".py", "javascript": ".js"}.get(lang, ".txt")
        tmpdir = tempfile.mkdtemp(prefix="scan_")
        file_path = os.path.join(tmpdir, "snippet" + ext)
        with open(file_path, "w", encoding="utf-8") as f:
                f.write(code_snippet)

            # 2️⃣ Run security tools
        results = []

        if lang == "python":
                # Run Bandit (Python security scanner)
            proc = subprocess.run(
                ["bandit", "-f", "json", "-r", file_path],
                capture_output=True, text=True
            )
            if proc.returncode in (0, 1):
                output = json.loads(proc.stdout or "{}")
                for issue in output.get("results", []):
                    results.append({
                            "tool": "Bandit",
                            "issue": issue.get("issue_text"),
                            "severity": issue.get("issue_severity"),
                            "confidence": issue.get("issue_confidence"),
                            "line": issue.get("line_number")
                    })
            else:
                results.append({"tool": "Bandit", "error": proc.stderr})

        else:
                # Run Semgrep for other languages
            proc = subprocess.run(
                 ["semgrep", "--config", "auto", "--json", file_path],
                 capture_output=True, text=True
            )
            if proc.returncode in (0, 1):
                output = json.loads(proc.stdout or "{}")
                for issue in output.get("results", []):
                    results.append({
                            "tool": "Semgrep",
                            "check_id": issue.get("check_id"),
                            "message": issue.get("extra", {}).get("message"),
                            "severity": issue.get("extra", {}).get("severity"),
                            "line": issue.get("start", {}).get("line")
                        })
                else:
                    results.append({"tool": "Semgrep", "error": proc.stderr})

            # 3️⃣ Return result
            return jsonify({
                "status": "success",
                "language": lang,
                "issues": results if results else [{"message": "No vulnerabilities found ✅"}]
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
            # 4️⃣ Clean up temporary folder
        if tmpdir and os.path.exists(tmpdir):
            shutil.rmtree(tmpdir)

    # -----------------------------
    # Chatbot Route (Gemini)
    # -----------------------------
@app.route('/ask', methods=['POST'])
def ask():
    
    data = request.get_json()
    question = data.get('question', '').strip()

    if not question:
         return jsonify({'answer': "Please enter a question."})

    try:
        response = chat.send_message(
                f"Answer briefly (2–3 short paragraphs max). "
                f"Plain text only, no emojis or markdown. "
                f"If the question is not related to cyber security say can't answer. "
                f"Question: {question}"
        )
        return jsonify({'answer': response.text})
    except Exception as e:
        return jsonify({'answer': f"Error: {str(e)}"})

    # -----------------------------
    # Run Flask
    # -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
