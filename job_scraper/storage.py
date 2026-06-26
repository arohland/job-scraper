import json
from pathlib import Path
from .logger import get_logger

logger = get_logger(__name__)

SEEN_FILE = Path("seen_jobs.json")


def load_seen_jobs() -> dict:
    if not SEEN_FILE.exists():
        logger.info("No seen_jobs.json found, starting fresh")
        return {}

    data = json.loads(SEEN_FILE.read_text(encoding="utf-8"))

    # migrate old format: list of titles -> dict
    if isinstance(data, list):
        logger.info(f"Migrating seen_jobs.json from list to dict format ({len(data)} entries)")
        data = {title: {} for title in data}

    logger.info(f"Loaded {len(data)} previously seen jobs")
    return data


def save_seen_jobs(seen: dict):
    SEEN_FILE.write_text(json.dumps(seen, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"Saved {len(seen)} seen jobs to {SEEN_FILE}")
