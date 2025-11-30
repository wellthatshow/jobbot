# parsers/linkedin.py
import requests
from bs4 import BeautifulSoup

SEARCH_URL = (
    "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
    "?keywords=data%20analyst&location=Worldwide"
)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def parse_linkedin():
    try:
        resp = requests.get(SEARCH_URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print("LinkedIn ERROR:", e)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")

    cards = soup.select("a.result-card__full-card-link")
    jobs = []

    for card in cards:
        url = card["href"]

        title_el = card.select_one(".result-card__title")
        company_el = card.select_one(".result-card__subtitle")
        location_el = card.select_one(".job-result-card__location")

        title = title_el.get_text(strip=True) if title_el else ""
        company = company_el.get_text(strip=True) if company_el else ""
        location = location_el.get_text(strip=True) if location_el else ""

        jobs.append({
            "source": "linkedin",
            "external_id": url,
            "title": title,
            "company": company,
            "location": location,
            "salary_raw": "",
            "url": url,
            "description": ""
        })

    return jobs
