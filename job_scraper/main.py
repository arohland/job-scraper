from job_scraper.config import load_config
from job_scraper.scraper import fetch_page, parse_jobs
from job_scraper.storage import load_seen_jobs, save_seen_jobs
from job_scraper.notifier import send_email
from job_scraper.parsers import parser_bgd, parser_bwd, parser_ht, parser_gesaeuse, parser_kalkalpen
from job_scraper.relevance_filter import filter_jobs_by_relevance
from job_scraper.logger import get_logger

logger = get_logger(__name__)

PARSERS = {
    "parser_bgd": parser_bgd,
    "parser_bwd": parser_bwd,
    "parser_ht": parser_ht,
    "parser_gesaeuse": parser_gesaeuse,
    "parser_kalkalpen": parser_kalkalpen,
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
                seen_jobs[job["title"]] = job
            else:
                logger.debug(f"Already seen job: {job['title']} ({job['link']})")

    if new_jobs:
        new_jobs = filter_jobs_by_relevance(new_jobs, config)

    if new_jobs:
        subject = f"New relevant job postings ({len(new_jobs)})"
        lines = []
        for job in new_jobs:
            line = f"{job['site']} – {job['title']}\n{job['link']}"
            if job.get("deadline"):
                line += f"\nDeadline: {job['deadline']}"
            if job.get("llm_reason"):
                line += f"\nWhy relevant: {job['llm_reason']}"
            lines.append(line)
        body = "\n\n".join(lines)
        logger.info(f"Sending email with {len(new_jobs)} relevant jobs")
        sending_success = send_email(config, subject, body)
        if sending_success:
            save_seen_jobs(seen_jobs)
    else:
        logger.info("No new relevant jobs found")

    logger.info("Job watcher finished")

main()