from flask import Flask, render_template, request
import sqlite3
from pathlib import Path
import logging

# Import scheduler & ingestion
from .scheduler import start_scheduler
from .ingest_rss import main as run_ingestion

app = Flask(__name__)
DB_PATH = Path(__file__).parent.parent / "data" / "news.db"

logging.basicConfig(level=logging.INFO)

def get_articles(tag=None, location=None, search=None):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    query = "SELECT * FROM articles WHERE 1=1"
    params = []

    if tag:
        query += " AND tags LIKE ?"
        params.append(f"%{tag}%")
    if location:
        query += " AND tags LIKE ?"
        params.append(f"%{location}%")
    if search:
        query += " AND (title LIKE ? OR summary LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " ORDER BY published_at DESC LIMIT 50"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows

@app.route("/")
def index():
    tag = request.args.get("tag")
    location = request.args.get("location")
    search = request.args.get("search")
    articles = get_articles(tag, location, search)
    return render_template("index.html", articles=articles, tag=tag, location=location, search=search)

if __name__ == "__main__":
    # Start background auto-refresh
    start_scheduler(run_ingestion, interval_minutes=15)
    app.run(debug=True)
    logging.info("Starting Flask app...")