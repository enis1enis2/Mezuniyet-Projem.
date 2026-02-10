# Copilot Instructions for Mezüniyet

## What this repo is
Mezüniyet is a **Flask + SQLite** diary web app with:
- **Authentication** (register/login/logout) using **Flask sessions** and **Werkzeug password hashing**
- **Diary CRUD** (create/edit/delete/list) stored in SQLite (`data/diary.db`)
- **Optional AI analysis** (mood + summary):
  - Local GGUF via `llama-cpp-python`
  - External OpenAI-compatible API when configured (see `.env.example`)

The primary entrypoint is `app.py`.

## Golden rules (important)
- **Do not edit vendored/huge folders unless explicitly asked**:
  - `.venv/` (local environment)
  - `__pycache__/` (generated)
  - `llama.cpp/` (vendored upstream C/C++ project)
  - `Python-Kodland-Repo/` (separate archive / unrelated projects)
- **Do not commit or “fix” runtime artifacts**:
  - `data/diary.db` (user data)
  - `models/*.gguf` (large model binaries)
- **Do not commit secrets**:
  - `.env` (use `.env.example` as a template)
- **Keep changes minimal and consistent** with existing style (simple Flask routes + helper functions in `models.py`).

## Code map (edit the right file)
- **App wiring / entrypoint**: `app.py`
  - Creates `app = Flask(__name__)`
  - Sets `app.secret_key = config.SECRET_KEY`
  - Calls `init_db()`
  - Registers two blueprints:
    - `diary` blueprint (imported from `diary.py`) mounted at `/diary`
    - `auth` blueprint handles `/login`, `/register`, `/logout`
- **Diary routes**: `diary.py`
  - All diary CRUD + analysis routes (mounted under `/diary/...`)
  - Defines `login_required` decorator (session-based)
- **Auth routes**: `auth.py`
  - Uses `werkzeug.security` (`generate_password_hash`, `check_password_hash`)
  - Stores `session["user_id"]` and `session["username"]`
- **Database layer (SQLite)**: `models.py`
  - `init_db()` creates `users` and `entries` tables
  - CRUD helpers: `get_entries`, `get_entry`, `create_entry`, `update_entry`, `delete_entry`
  - Auth helpers: `get_user`, `create_user`
- **LLM analysis**: `diary_llm.py`
  - Uses `llama_cpp.Llama` and expects a GGUF model at `models/koala-7B-HF.Q3_K_L.gguf` by default
  - Function to call: `analyze_mood_and_summary(text: str) -> dict`
- **Config**: `config.py`
  - Defines `DATABASE` path and ensures `data/` exists
  - Loads `SECRET_KEY` from environment (falls back to a dev default)
- **UI**: `templates/*.html` and `static/style.css`

## Known “gotchas” to keep in mind while editing
- **The app uses sessions directly** (no `flask_login` usage).
- **Secrets**: `SECRET_KEY` should come from the environment (see `.env.example`). Avoid committing real secrets.
- **LLM is optional**: if neither the external API nor the local model is available, analysis returns a safe fallback message.
- **Prefer `url_for()`** in Python and Jinja templates (avoid hard-coded paths).

## Safe workflows / suggestions for changes
- If changing DB schema or queries, update only `models.py` and keep helpers small and testable.
- If changing routes, keep URL patterns consistent:
  - Diary pages under `/diary/...`
  - Auth pages under `/login`, `/register`, `/logout`
- If changing analysis behavior, keep the return shape stable:
  - `{"mood": "<string>", "summary": "<string>"}`
  - On failure, return a safe fallback (current behavior already does this).

## How to run (local dev)
- Install deps: `pip install -r requirements.txt`
- Start server: `python app.py`
- The database file `data/diary.db` is auto-created on first run (via `init_db()`).
- Use `.env` (copied from `.env.example`) to set `SECRET_KEY`, `FLASK_DEBUG`, `HOST`, and `PORT`.
