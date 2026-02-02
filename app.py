import os

from flask import Flask, redirect, session, url_for
from models import init_db
from auth import auth
from diary import diary
import config

# Optional: load local .env for development (ignored by .gitignore)
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Sensible cookie defaults (still need HTTPS in production)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

init_db()
app.register_blueprint(diary, url_prefix="/diary")
app.register_blueprint(auth)

# ---------- ROOT ROUTE ----------
@app.route("/")
def root():
    if "user_id" in session:
        return redirect(url_for("diary.index"))
    else:
        return redirect(url_for("auth.login"))

# ---------- DIARY REDIRECT ----------
@app.route("/diary")
def diary_redirect():
    return redirect(url_for("diary.index"))

if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG") == "1"
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "5000"))
    app.run(debug=debug, host=host, port=port)
