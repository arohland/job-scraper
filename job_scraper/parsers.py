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


def parser_gesaeuse(soup: BeautifulSoup, site_key: str, base_url: str) -> list[dict]:
    # Gesäuse posts jobs as PDF downloads under the main content area.
    # When no positions are open the page just shows a "keine Stellen" paragraph.
    jobs = []
    main = soup.find("main") or soup
    for a in main.find_all("a", href=True):
        href = a["href"]
        if not (href.endswith(".pdf") or "pdf" in href.lower()):
            continue
        # use the closest preceding heading as the title
        title_el = a.find_previous(["h2", "h3"])
        title = title_el.get_text(strip=True) if title_el else a.get_text(strip=True)
        if not title:
            continue
        jobs.append({
            "site": site_key,
            "title": title,
            "link": urljoin(base_url, href),
        })
    return jobs


_KALKALPEN_NOISE = {"Cookie Information", "Cookie-Einstellungen", "Datenschutz"}

def parser_kalkalpen(soup: BeautifulSoup, site_key: str, base_url: str) -> list[dict]:
    # Kalkalpen uses h3 headings for position titles with deadline in a following <p>.
    # Links are sometimes javascript:void(0), so fall back to the page URL.
    # Noise entries (form labels, cookie banners) are excluded by requiring a
    # following descriptive paragraph before the next heading.
    jobs = []
    for h3 in soup.find_all("h3"):
        title = h3.get_text(strip=True)
        if not title or title.endswith(":") or title in _KALKALPEN_NOISE:
            continue

        # require at least one descriptive paragraph after the heading
        has_description = False
        deadline = None
        for sibling in h3.find_next_siblings(["p", "h3", "h2"]):
            if sibling.name in ("h3", "h2"):
                break
            text = sibling.get_text(strip=True)
            if len(text) > 30:
                has_description = True
            if "Bewerbung" in text or "einlangend" in text:
                deadline = text

        if not has_description:
            continue

        link = base_url
        a = h3.find_next("a", href=lambda x: x and not x.startswith("javascript"))
        next_h3 = h3.find_next("h3")
        if a and (next_h3 is None or a.find_previous("h3") == h3):
            link = urljoin(base_url, a["href"])

        jobs.append({
            "site": site_key,
            "title": title,
            "link": link,
            "deadline": deadline,
        })
    return jobs
