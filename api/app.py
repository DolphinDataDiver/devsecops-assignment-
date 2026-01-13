from flask import Flask, request
from flask_wtf import CSRFProtect
import hashlib
import subprocess
import os

app = Flask(__name__)
app.secret_key = "my_secret_key"

# Environment variable for admin password
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# Enable CSRF protection
csrf = CSRFProtect(app)

# --- Fix 1: Use SHA-256 instead of insecure MD5 ---
def hash_password(password: str) -> str:
    """Return the SHA-256 hash of a password."""
    return hashlib.sha256(password.encode()).hexdigest()

@app.route("/login")
def login():
    username = request.args.get("username")
    password = request.args.get("password")
    if username == "admin" and hash_password(password) == hash_password(ADMIN_PASSWORD):
        return "Logged in"
    return "Invalid credentials"

# --- Fix 2: Use subprocess safely without shell=True ---
@app.route("/ping")
def ping():
    host = request.args.get("host", "localhost")
    # Use a list and shell=False to prevent command injection
    result = subprocess.check_output(["ping", "-c", "1", host])
    return result

@app.route("/hello")
def hello():
    name = request.args.get("name", "user")
    return f"<h1>Hello {name}</h1>"

if __name__ == "__main__":
    app.run()

