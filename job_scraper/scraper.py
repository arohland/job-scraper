import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


def fetch_html(url: str) -> BeautifulSoup:
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "lxml")


def parse_site_a(soup: BeautifulSoup, base_url: str) -> list[dict]:
    jobs = []
    for article in soup.select("article.news-full-width"):
        job = {}
        pdf_link = article.find("a", href=lambda x: x and x.startswith("doc/"))
        if pdf_link:
            job["link"] = urljoin(base_url, pdf_link["href"])

        title = article.find("h2")
        if title:
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


def parse_site_b(soup: BeautifulSoup, base_url: str) -> list[dict]:
    jobs = []
    for section in soup.select("article > section"):
        job = {}

        h3 = section.find("h3")
        if h3 and h3.a:
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


PARSERS = {
    "site_a": parse_site_a,
    "site_b": parse_site_b,
}


def check_new_jobs(sites: dict) -> dict[str, list[dict]]:
    """
    sites = {
      "berchtesgaden": {"url": "...", "parser": "site_a"},
      "falkenstein": {"url": "...", "parser": "site_b"}
    }
    """
    results = {}
    for name, site in sites.items():
        soup = fetch_html(site["url"])
        parser_fn = PARSERS.get(site["parser"])
        if not parser_fn:
            raise ValueError(f"Unknown parser type: {site['parser']}")
        results[name] = parser_fn(soup, site["url"])
    return results

# import requests
# from urllib.parse import urljoin
# from bs4 import BeautifulSoup
#
# def check_new_jobs(sites: list[str]) -> list[dict]:
#     jobs = []
#     for site in sites:
#         response = requests.get(site, timeout=10)
#         soup = BeautifulSoup(response.text, "lxml")
#         # Each posting is in <article class="news-full-width">
#         for article in soup.select("article.news-full-width"):
#             job = {}
#
#             # PDF link (first "doc/" href we find)
#             pdf_link = article.find("a", href=lambda x: x and x.startswith("doc/"))
#             if pdf_link:
#                 job["pdf"] = urljoin(site, pdf_link["href"])
#
#             # Job title
#             title = article.find("h2")
#             if title:
#                 job["title"] = title.get_text(strip=True)
#
#             # Deadline
#             deadline = None
#             for h3 in article.find_all("h3"):
#                 if "Bewerbungsschluss" in h3.get_text():
#                     # next <p> usually contains the date
#                     next_p = h3.find_next_sibling("p")
#                     if next_p:
#                         deadline = next_p.get_text(strip=True)
#                         break
#             if deadline:
#                 job["deadline"] = deadline
#
#             # Contacts
#             contacts = []
#             for strong in article.find_all("strong"):
#                 name = strong.get_text(strip=True)
#                 email = strong.find_next("a", href=lambda x: x and x.startswith("mailto:"))
#                 phone = strong.find_next("a", href=lambda x: x and x.startswith("tel:"))
#                 contacts.append({
#                     "name": name,
#                     "email": email.get_text(strip=True) if email else None,
#                     "phone": phone.get_text(strip=True) if phone else None
#                 })
#             if contacts:
#                 job["contacts"] = contacts
#
#             if job:
#                 jobs.append(job)
#     return jobs
