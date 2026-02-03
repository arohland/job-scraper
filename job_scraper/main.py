from job_scraper.config import load_config
from job_scraper.scraper import fetch_page, parse_jobs
from job_scraper.storage import load_seen_jobs, save_seen_jobs
from job_scraper.notifier import send_email
from job_scraper.parsers import parser_bgd, parser_bwd, parser_ht
from job_scraper.logger import get_logger

logger = get_logger(__name__)

PARSERS = {
    "parser_bgd": parser_bgd,
    "parser_bwd": parser_bwd,
    "parser_ht": parser_ht,
}

def main():
    logger.info("Starting job watcher")
    config = load_config()
    seen_jobs = load_seen_jobs()
    new_jobs = []

    for site_key, site_cfg in config["sites"].items():
        if site_key == "email":
            continue

        url, parser_name = site_cfg["url"], site_cfg["parser"]
        parser_func = PARSERS.get(parser_name)

        if not parser_func:
            logger.warning(f"No parser found for site '{site_key}', skipping")
            continue

        try:
            soup = fetch_page(url)
            jobs = parse_jobs(soup, parser_func, site_key, url)
        except Exception as e:
            logger.error(f"Error fetching/parsing site '{site_key}': {e}", exc_info=True)
            continue

        for job in jobs:
            if job["title"] not in seen_jobs:
                logger.info(f"New job found: {job['title']} ({job['link']})")
                new_jobs.append(job)
                seen_jobs.add(job["title"])
            else:
                logger.debug(f"Already seen job: {job['title']} ({job['link']})")

    if new_jobs:
        subject = f"New job postings ({len(new_jobs)})"
        body = "\n\n".join([f"{job['site']} – {job['title']}\n{job['link']}" for job in new_jobs])
        logger.info(f"Sending email with {len(new_jobs)} new jobs")
        sending_success = send_email(config, subject, body)
        if sending_success:
            save_seen_jobs(seen_jobs)
    else:
        logger.info("No new jobs found")

    logger.info("Job watcher finished")

main()