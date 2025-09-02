from job_scraper.scraper import check_new_jobs
from job_scraper.notifier import send_email
from job_scraper.config import load_config
from job_scraper.storage import filter_new_jobs

def main():
    config = load_config()
    all_jobs = check_new_jobs(config["sites"])
    new_jobs = filter_new_jobs(all_jobs)

    if new_jobs:
        send_email(new_jobs=new_jobs, config=config)
    else:
        print("No new jobs today.")

if __name__ == "__main__":
    main()
