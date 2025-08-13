import sqlite3
import time

def get_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS articles (
            id TEXT PRIMARY KEY,
            source TEXT,
            title TEXT,
            url TEXT UNIQUE,
            author TEXT,
            published_at TEXT,
            summary TEXT,
            content TEXT,
            tags TEXT DEFAULT '',
            created_at INTEGER,
            updated_at INTEGER
        );
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(published_at DESC);")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_articles_tags ON articles(tags);")
    conn.commit()