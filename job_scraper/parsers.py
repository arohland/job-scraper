from bs4 import BeautifulSoup
from urllib.parse import urljoin

from .models import Job


def parser_bgd(soup: BeautifulSoup, site_key: str, base_url: str) -> list[Job]:
    jobs = []
    for article in soup.select("article.news-full-width"):
        title_el = article.find("h2")
        if not title_el:
            continue

        pdf_link = article.find("a", href=lambda x: x and x.startswith("doc/"))
        link = urljoin(base_url, pdf_link["href"]) if pdf_link else base_url

        deadline = None
        for h3 in article.find_all("h3"):
            if "Bewerbungsschluss" in h3.get_text():
                p = h3.find_next_sibling("p")
                if p:
                    deadline = p.get_text(strip=True)
                break

        jobs.append(Job(
            title=title_el.get_text(strip=True),
            site=site_key,
            link=link,
            deadline=deadline,
        ))
    return jobs


def parser_bwd(soup: BeautifulSoup, site_key: str, base_url: str) -> list[Job]:
    jobs = []
    for section in soup.select("article > section"):
        h3 = section.find("h3")
        if not h3 or not h3.a:
            continue

        deadline = None
        p = section.find("p")
        if p and "Bewerbungsfrist" in p.get_text():
            deadline = p.get_text(strip=True).replace("Bewerbungsfrist:", "").strip()

        jobs.append(Job(
            title=h3.get_text(strip=True),
            site=site_key,
            link=urljoin(base_url, h3.a["href"]),
            deadline=deadline,
        ))
    return jobs


def parser_ht(soup: BeautifulSoup, site_key: str, base_url: str) -> list[Job]:
    jobs = []
    for card in soup.select("div.uk-card.uk-card-default"):
        title_link = card.select_one("h3.titel a.detail-link")
        if not title_link:
            continue

        description = None
        intro = card.select_one("div.introtext")
        if intro:
            paragraphs = [p.get_text(strip=True) for p in intro.find_all("p") if p.get_text(strip=True)]
            description = "\n".join(paragraphs) or None

        date_el = card.select_one("div.article_date")

        jobs.append(Job(
            title=title_link.get_text(strip=True),
            site=site_key,
            link=urljoin(base_url, title_link.get("href")),
            description=description,
            date=date_el.get_text(strip=True) if date_el else None,
        ))
    return jobs
