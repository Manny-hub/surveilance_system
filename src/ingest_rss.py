import hashlib
import logging
import time
from datetime import datetime, timezone
from .enrich import detect_tags, extract_location

import feedparser

from .config import DATABASE_URL, USER_AGENT
from .db import get_db, init_db
from .feeds import FEEDS

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def to_iso8601(entry) -> str | None:
    """Convert RSS date fields to ISO8601 if available."""
    try:
        if getattr(entry, "published_parsed", None):
            dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            return dt.isoformat()
        if getattr(entry, "updated_parsed", None):
            dt = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
            return dt.isoformat()
        if getattr(entry, "published", None):
            return entry.published
    except Exception:
        pass
    return None


def parse_feed(url: str):
    logging.info(f"Fetching feed: {url}")
    feed = feedparser.parse(url, request_headers={"User-Agent": USER_AGENT})
    if getattr(feed, "bozo", False):
        logging.warning(f"Feed had error: {getattr(feed, 'bozo_exception', '')}")
    return feed


def upsert(conn, entry, source_title: str) -> int:
    link = getattr(entry, "link", None)
    if not link:
        return 0

    uid = hashlib.sha256(link.encode("utf-8")).hexdigest()
    title = (getattr(entry, "title", "") or "")[:500]
    summary = getattr(entry, "summary", "") or ""
    author = getattr(entry, "author", "") or ""
    published_at = to_iso8601(entry)
    now = int(time.time())

    tags = detect_tags(title, summary)
    location = extract_location(title, summary)
    tag_str = ",".join(tags) if tags else ""

    if location and location not in tag_str:
        tag_str = f"{tag_str},{location}" if tag_str else location


    try:
        conn.execute(
            """
            INSERT INTO articles (id, source, title, url, author, published_at, summary, content, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
            title=excluded.title,
            summary=excluded.summary,
            author=excluded.author,
            published_at=COALESCE(excluded.published_at, articles.published_at),
            tags=excluded.tags,
            updated_at=excluded.updated_at
        """,
        (uid, source_title, title, link, author, published_at, summary, "", tag_str, now, now),   
        )
        return 1
    except Exception as e:
        logging.error(f"DB upsert error for {link}: {e}")
        return 0


def main():
    conn = get_db(DATABASE_URL)
    init_db(conn)

    total = 0
    for url in FEEDS:
        feed = parse_feed(url)
        source_title = getattr(feed, "feed", {}).get("title", url) if getattr(feed, "feed", None) else url
        for entry in getattr(feed, "entries", []):
            total += upsert(conn, entry, source_title)

    conn.commit()
    logging.info(f"Ingested/updated: {total} items")


if __name__ == "__main__":
    main()

  



