import requests
from bs4 import BeautifulSoup
from job_scraper.logger import get_logger

logger = get_logger(__name__)

def fetch_page(url: str) -> BeautifulSoup:
    logger.info(f"Fetching page: {url}")
    response = requests.get(url)
    response.raise_for_status()
    logger.info(f"Successfully fetched {url} ({len(response.text)} bytes)")
    return BeautifulSoup(response.text, "html.parser")

def parse_jobs(soup, parser_func, site_key: str, url:str):
    logger.debug(f"Parsing jobs for site '{site_key}' using parser '{parser_func.__name__}'")
    jobs = parser_func(soup, site_key, url)
    logger.info(f"Parsed {len(jobs)} jobs from site '{site_key}'")
    return jobs