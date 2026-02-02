import sqlite3
from config import DATABASE

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row  # Access columns by name
    return db

def init_db():
    db = get_db()
    c = db.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    db.commit()
    db.close()

# CRUD helpers
def get_user(username):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    db.close()
    return user

def create_user(username, password_hash):
    db = get_db()
    db.execute("INSERT INTO users(username,password) VALUES(?,?)", (username, password_hash))
    db.commit()
    db.close()

def get_entries(user_id):
    db = get_db()
    entries = db.execute("SELECT * FROM entries WHERE user_id=? ORDER BY created DESC", (user_id,)).fetchall()
    db.close()
    return entries

def get_entry(user_id, entry_id):
    db = get_db()
    entry = db.execute("SELECT * FROM entries WHERE user_id=? AND id=?", (user_id, entry_id)).fetchone()
    db.close()
    return entry

def create_entry(user_id, content):
    db = get_db()
    db.execute("INSERT INTO entries(user_id, content) VALUES(?,?)", (user_id, content))
    db.commit()
    db.close()

def update_entry(user_id, entry_id, content):
    db = get_db()
    db.execute("UPDATE entries SET content=? WHERE user_id=? AND id=?", (content, user_id, entry_id))
    db.commit()
    db.close()

def delete_entry(user_id, entry_id):
    db = get_db()
    db.execute("DELETE FROM entries WHERE user_id=? AND id=?", (user_id, entry_id))
    db.commit()
    db.close()
