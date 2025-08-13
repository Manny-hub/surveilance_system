import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# SQLite database path
DATABASE_URL = os.getenv("DATABASE_URL", str(DATA_DIR / "news.db"))

# Polite UA for RSS requests
USER_AGENT = os.getenv("USER_AGENT", "NaijaCrimeWatchBot/0.1 (+https://example.com)")