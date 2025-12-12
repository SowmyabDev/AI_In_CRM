from flask import Flask, render_template, request, redirect, url_for, session
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fastapi_backend.users_db import USERS

app = Flask(__name__)
app.secret_key = "mysecretkey123"

@app.route("/")
def home():
    if "user" in session:
        return redirect(url_for("chat"))
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    # Debug prints
    print("Username:", username)
    print("Password typed:", password)
    print("Stored user:", USERS.get(username))

    # Correct login check for nested user structure
    if username in USERS and USERS[username]["password"] == password:
        session["user"] = username
        return redirect(url_for("chat"))
    else:
        return render_template("login.html", error="Invalid username or password")

@app.route("/chat")
def chat():
    if "user" not in session:
        return redirect(url_for("home"))
    return render_template("chat.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
