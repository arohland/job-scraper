import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def parser_bgd(soup: BeautifulSoup, site_key:str, base_url: str) -> list[dict]:
    jobs = []
    for article in soup.select("article.news-full-width"):
        job = {}
        pdf_link = article.find("a", href=lambda x: x and x.startswith("doc/"))
        if pdf_link:
            job["link"] = urljoin(base_url, pdf_link["href"])

        title = article.find("h2")
        if title:
            job["site"] = site_key
            job["title"] = title.get_text(strip=True)

        for h3 in article.find_all("h3"):
            if "Bewerbungsschluss" in h3.get_text():
                p = h3.find_next_sibling("p")
                if p:
                    job["deadline"] = p.get_text(strip=True)
                    break

        if job:
            jobs.append(job)
    return jobs


def parser_bwd(soup: BeautifulSoup, site_key:str, base_url: str) -> list[dict]:
    jobs = []
    for section in soup.select("article > section"):
        job = {}

        h3 = section.find("h3")
        if h3 and h3.a:
            job["site"] = site_key
            job["title"] = h3.get_text(strip=True)
            job["link"] = urljoin(base_url, h3.a["href"])

        p = section.find("p")
        if p and "Bewerbungsfrist" in p.get_text():
            job["deadline"] = (
                p.get_text(strip=True).replace("Bewerbungsfrist:", "").strip()
            )

        if job:
            jobs.append(job)
    return jobs

def parser_ht(soup: BeautifulSoup, site_key:str, base_url: str) -> list[dict]:

    jobs = []

    cards = soup.select("div.uk-card.uk-card-default")

    for card in cards:
        job = {}

        # Title + link
        title_link = card.select_one("h3.titel a.detail-link")
        if not title_link:
            continue

        job["site"] = site_key
        job["title"] = title_link.get_text(strip=True)
        job["link"] = urljoin(base_url, title_link.get("href"))

        # Intro / summary text
        intro = card.select_one("div.introtext")
        if intro:
            paragraphs = [
                p.get_text(strip=True)
                for p in intro.find_all("p")
                if p.get_text(strip=True)
            ]
            job["description"] = "\n".join(paragraphs)

        # Optional date
        date_el = card.select_one("div.article_date")
        if date_el:
            job["date"] = date_el.get_text(strip=True)

        jobs.append(job)

    return jobs