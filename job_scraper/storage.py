import json
from pathlib import Path
from .logger import get_logger

logger = get_logger(__name__)

SEEN_FILE = Path("seen_jobs.json")

def load_seen_jobs() -> set:
    if SEEN_FILE.exists():
        seen = set(json.loads(SEEN_FILE.read_text()))
        logger.info(f"Loaded {len(seen)} previously seen jobs")
        return seen
    else:
        logger.info("No seen_jobs.json found, starting fresh")
        return set()

def save_seen_jobs(seen: set):
    SEEN_FILE.write_text(json.dumps(list(seen), indent=2))
    logger.info(f"Saved {len(seen)} seen jobs to {SEEN_FILE}")
