from flask import Flask, request, jsonify
import sqlite3
import subprocess
import hashlib
import os
import logging
from pathlib import Path
import json

app = Flask(__name__)

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

API_KEY = os.getenv("API_KEY")  # must be set in environment
DATABASE = "users.db"
BASE_DIR = Path("/app/data").resolve()  # allowed file access root

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def get_db():
    return sqlite3.connect(DATABASE)

def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def safe_path(filename: str) -> Path:
    path = (BASE_DIR / filename).resolve()
    if not str(path).startswith(str(BASE_DIR)):
        raise ValueError("Invalid file path")
    return path

# -------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------

@app.route("/auth", methods=["POST"])
def auth():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing credentials"}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM users WHERE username=? AND password=?",
        (username, hash_text(password))
    )

    authenticated = cursor.fetchone() is not None
    conn.close()

    return jsonify({"status": "authenticated" if authenticated else "denied"})

# -------------------------------------------------------------------

@app.route("/exec", methods=["POST"])
def exec_cmd():
    """
    Safe command execution using allowlist
    """
    data = request.get_json(silent=True) or {}
    command = data.get("command")

    ALLOWED_COMMANDS = {
        "date": ["date"],
        "uptime": ["uptime"]
    }

    if command not in ALLOWED_COMMANDS:
        return jsonify({"error": "Command not allowed"}), 403

    output = subprocess.check_output(
        ALLOWED_COMMANDS[command],
        shell=False,
        text=True
    )

    return jsonify({"output": output.strip()})

# -------------------------------------------------------------------

@app.route("/deserialize", methods=["POST"])
def deserialize():
    """
    Safe deserialization using JSON
    """
    try:
        data = json.loads(request.data.decode("utf-8"))
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON"}), 400

    return jsonify({"object": data})

# -------------------------------------------------------------------

@app.route("/encrypt", methods=["POST"])
def encrypt():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")

    return jsonify({"hash": hash_text(text)})

# -------------------------------------------------------------------

@app.route("/file", methods=["POST"])
def read_file():
    data = request.get_json(silent=True) or {}
    filename = data.get("filename")

    if not filename:
        return jsonify({"error": "Filename required"}), 400

    try:
        path = safe_path(filename)
        with open(path, "r", encoding="utf-8") as f:
            return jsonify({"content": f.read()})
    except (ValueError, FileNotFoundError):
        return jsonify({"error": "File access denied"}), 403

# -------------------------------------------------------------------

@app.route("/log", methods=["POST"])
def log_data():
    data = request.get_json(silent=True)

    logging.info("User input received", extra={"payload": data})
    return jsonify({"status": "logged"})

# -------------------------------------------------------------------

if __name__ == "__main__":
    # Debug explicitly disabled
    app.run(host="0.0.0.0", port=5000, debug=False)

