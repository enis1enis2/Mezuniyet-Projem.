from flask import Blueprint, render_template, request, redirect, session, url_for
from models import get_entries, get_entry, create_entry, update_entry, delete_entry
from diary_llm import analyze_mood_and_summary

diary = Blueprint("diary", __name__)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated

@diary.route("/")
@login_required
def index():
    entries = get_entries(session["user_id"])
    return render_template("index.html", entries=entries)

@diary.route("/create", methods=["GET","POST"])
@login_required
def create():
    if request.method == "POST":
        content = request.form["text"]
        create_entry(session["user_id"], content)
        return redirect(url_for("diary.index"))
    return render_template("create.html")

@diary.route("/edit/<int:entry_id>", methods=["GET","POST"])
@login_required
def edit(entry_id):
    entry = get_entry(session["user_id"], entry_id)
    if not entry:
        return redirect(url_for("diary.index"))
    if request.method == "POST":
        update_entry(session["user_id"], entry_id, request.form["text"])
        return redirect(url_for("diary.index"))
    return render_template("edit.html", entry=entry)

@diary.route("/delete/<int:entry_id>")
@login_required
def delete(entry_id):
    delete_entry(session["user_id"], entry_id)
    return redirect(url_for("diary.index"))

@diary.route("/analyze/<int:entry_id>")
@login_required
def analyze(entry_id):
    entry = get_entry(session["user_id"], entry_id)
    if not entry:
        return redirect(url_for("diary.index"))
    result = analyze_mood_and_summary(entry["content"])
    return render_template("analyze.html", entry=entry, result=result)
