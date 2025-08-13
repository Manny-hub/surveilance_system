import re
from pathlib import Path

# Load Nigerian locations from file
LOCATIONS = []
loc_file = Path(__file__).parent / "locations_ng.txt"
if loc_file.exists():
    with open(loc_file, encoding="utf-8") as f:
        LOCATIONS = [line.strip() for line in f if line.strip()]

# Simple keyword sets
CRIME_KEYWORDS = {
    "kidnap", "murder", "armed robbery", "fraud", "rape",
    "smuggling", "trafficking", "theft", "assault", "arson",
    "bandit", "cultist", "homicide", "terrorist", "militant"
}

AI_MISUSE_KEYWORDS = {
    "deepfake", "ai scam", "ai fraud", "chatbot abuse",
    "voice cloning", "fake ai", "ai generated scam", "malicious ai"
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def detect_tags(title: str, summary: str) -> list[str]:
    text = normalize_text(f"{title} {summary}")
    tags = []

    if any(k in text for k in CRIME_KEYWORDS):
        tags.append("crime")

    if any(k in text for k in AI_MISUSE_KEYWORDS):
        tags.append("ai-misuse")

    return tags


def extract_location(title: str, summary: str) -> str | None:
    combined = f"{title} {summary}"
    for loc in LOCATIONS:
        pattern = rf"\b{re.escape(loc)}\b"
        if re.search(pattern, combined, flags=re.IGNORECASE):
            return loc
    return None
