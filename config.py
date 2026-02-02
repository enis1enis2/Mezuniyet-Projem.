import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-change-me"
DATABASE = os.path.join(BASE_DIR, "data", "diary.db")

os.makedirs(os.path.join(BASE_DIR, "data"), exist_ok=True)
