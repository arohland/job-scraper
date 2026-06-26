import json
from pathlib import Path
from .logger import get_logger
from .models import Job

logger = get_logger(__name__)

SEEN_FILE = Path("seen_jobs.json")


def load_seen_jobs() -> dict[str, Job]:
    if not SEEN_FILE.exists():
        logger.info("No seen_jobs.json found, starting fresh")
        return {}

    data = json.loads(SEEN_FILE.read_text(encoding="utf-8"))

    # migrate old format: list of titles -> dict
    if isinstance(data, list):
        logger.info(f"Migrating seen_jobs.json from list to dict format ({len(data)} entries)")
        data = {title: {} for title in data}

    seen = {title: Job.from_dict({"title": title, "site": "", "link": "", **job_data})
            for title, job_data in data.items()}
    logger.info(f"Loaded {len(seen)} previously seen jobs")
    return seen


def save_seen_jobs(seen: dict[str, Job]):
    serialized = {title: job.to_dict() for title, job in seen.items()}
    SEEN_FILE.write_text(json.dumps(serialized, indent=2, ensure_ascii=False), encoding="utf-8")
    logger.info(f"Saved {len(seen)} seen jobs to {SEEN_FILE}")
