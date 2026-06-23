# Mezüniyet — Project Code Guide

This document is a **high-signal map** of the codebase (what matters, what to ignore, and how things connect).  
It intentionally **does not** embed full source code dumps.

## What this project is
- **Flask web app** (server-rendered HTML via Jinja templates)
- **SQLite** persistence (`data/diary.db`)
- **Session-based auth** (no `flask_login` usage in code, despite being in `requirements.txt`)
- **Optional AI analysis** (mood + summary):
  - **Local**: `llama-cpp-python` reading a **GGUF** model from `models/`
  - **Cloud**: OpenAI-compatible API when configured via `.env`

## Quickstart (local dev)
1. Install dependencies:
   - `pip install -r requirements.txt`
2. Run the app:
   - `python app.py`
3. First run creates:
   - `data/diary.db` (SQLite database)

## Curated project structure
```
Mezüniyet/
├── .github/
│   └── copilot-instructions.md
├── .env.example           # environment template (copy to .env locally)
├── app.py                 # Flask entrypoint + blueprint wiring
├── auth.py                # /login /register /logout
├── config.py              # DATABASE path + ensures data/ exists
├── diary.py               # diary CRUD + analyze routes (mounted under /diary)
├── diary_llm.py            # local GGUF LLM analysis via llama_cpp
├── models.py              # SQLite schema + CRUD helpers
├── requirements.txt
├── static/
│   └── style.css
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── create.html
│   ├── edit.html
│   ├── analyze.html
│   ├── login.html
│   └── register.html
├── data/
│   └── diary.db           # runtime artifact (do not edit by hand)
├── models/
│   └── *.gguf             # large model files (do not commit changes)
├── llama.cpp/             # vendored upstream (avoid editing unless asked)
└── Python-Kodland-Repo/   # separate archive / unrelated projects
```

## Main modules and responsibilities
- **`app.py`**
  - Creates the Flask app, sets `app.secret_key = config.SECRET_KEY`, and calls `init_db()`
  - Loads a local `.env` automatically (if present) for development
  - Registers the diary blueprint from `diary.py` under `/diary`
  - Registers the `auth` blueprint from `auth.py`
  - Keeps only the top-level redirects (`/` → login or diary)

- **`diary.py`**
  - Implements diary CRUD routes under the `diary` blueprint
  - Implements `/diary/analyze/<entry_id>` using `analyze_mood_and_summary`
  - Implements `login_required` using `session["user_id"]`

- **`auth.py`**
  - Implements register/login/logout flows
  - Passwords are stored hashed using `werkzeug.security`

- **`models.py`**
  - Owns the SQLite schema (`users`, `entries`)
  - Provides all DB access functions:
    - Users: `get_user`, `create_user`
    - Entries: `get_entries`, `get_entry`, `create_entry`, `update_entry`, `delete_entry`

- **`diary_llm.py`**
  - Implements `analyze_mood_and_summary(text: str) -> dict`
  - Supports two backends:
    - **External (cloud)** if `EXTERNAL_API_KEY` + `EXTERNAL_API_URL` are set (or `LLM_PROVIDER=external`)
    - **Local GGUF** via `llama_cpp.Llama` (default path: `models/koala-7B-HF.Q3_K_L.gguf`)
  - Returns a dict with keys `mood` and `summary`, with safe fallbacks on errors

## Files/folders that are “out of scope” for most work
- `.venv/`, `__pycache__/`: generated locally
- `.env`: local secrets file (ignored by `.gitignore`)
- `llama.cpp/`: huge upstream C/C++ project included in the workspace
- `Python-Kodland-Repo/`: separate repo archive, not part of the Flask app
- `data/diary.db`: user data
- `models/*.gguf`: model binaries

## Notes / current inconsistencies to be aware of
- The app uses **plain Flask sessions** (no `flask_login` import).
- `diary_llm.py` can use an **external API** or **local `llama_cpp`**; if neither is configured, analysis returns a safe fallback.
- `SECRET_KEY` should be set via environment (see `.env.example`).