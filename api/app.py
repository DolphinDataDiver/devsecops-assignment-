from flask import Flask, request, render_template_string
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
import hashlib
import subprocess
import os

app = Flask(__name__)
app.secret_key = "my_secret_key"

# Environment variable for admin password
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# Enable CSRF protection
csrf = CSRFProtect(app)


def hash_password(password: str) -> str:
    """Return the MD5 hash of a password."""
    return hashlib.md5(password.encode()).hexdigest()


@app.route("/login")
def login():
    username = request.args.get("username")
    password = request.args.get("password")

    if username == "admin" and hash_password(password) == hash_password(ADMIN_PASSWORD):
        return "Logged in"

    return "Invalid credentials"


@app.route("/ping")
def ping():
    host = request.args.get("host", "localhost")

    result = subprocess.check_output(f"ping -c 1 {host}", shell=True)
    return result


@app.route("/hello")
def hello():
    name = request.args.get("name", "user")
    return f"<h1>Hello {name}</h1>"


if __name__ == "__main__":
    app.run(debug=True)

