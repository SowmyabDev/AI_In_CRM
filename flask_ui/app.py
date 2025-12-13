from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__, template_folder="templates")
FASTAPI_URL = os.environ.get("FASTAPI_URL", "http://127.0.0.1:8000")

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/chat")
def chat_page():
    return render_template("chat.html")

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    try:
        resp = requests.post(f"{FASTAPI_URL}/login", json=data, timeout=10)
        return jsonify(resp.json()), resp.status_code
    except requests.RequestException:
        return jsonify({"success": False, "message": "Backend not available"}), 503

@app.route("/chat_api", methods=["POST"])
def chat_api():
    data = request.get_json()
    try:
        resp = requests.post(f"{FASTAPI_URL}/chat", json=data, timeout=120)
        return jsonify(resp.json()), resp.status_code
    except requests.RequestException:
        return jsonify({"reply": "⚠️ Backend not reachable. Please try later."}), 503

@app.route("/backend_health")
def backend_health():
    try:
        resp = requests.get(f"{FASTAPI_URL}/health", timeout=5)
        return jsonify(resp.json())
    except requests.RequestException:
        return jsonify({"ok": False}), 503

if __name__ == "__main__":
    app.run(debug=True, port=5000)
