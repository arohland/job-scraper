import json
from pathlib import Path

SEEN_FILE = Path("seen_jobs.json")

def load_seen() -> dict[str, list[str]]:
    if SEEN_FILE.exists():
        with open(SEEN_FILE, "r") as f:
            return json.load(f)
    return {}


def save_seen(seen: dict[str, list[str]]):
    with open(SEEN_FILE, "w") as f:
        json.dump(seen, f, indent=2)


def filter_new_jobs(all_jobs: dict[str, list[dict]]) -> dict[str, list[dict]]:
    seen = load_seen()
    new_jobs = {}

    for site, jobs in all_jobs.items():
        site_seen = set(seen.get(site, []))

        # choose a unique key (pdf or link or title+deadline)
        fresh = [
            job for job in jobs
            if (job.get("link")) not in site_seen
        ]

        if fresh:
            new_jobs[site] = fresh
            # update seen
            for job in fresh:
                site_seen.add(job.get("pdf") or job.get("link"))
            seen[site] = list(site_seen)

    if new_jobs:
        save_seen(seen)

    return new_jobs
