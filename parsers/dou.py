# parsers/dou.py
import requests
from bs4 import BeautifulSoup

DOU_URL = "https://jobs.dou.ua/vacancies/?category=Data+Science&search=data%20analyst"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
}

def parse_dou():
    try:
        resp = requests.get(DOU_URL, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print("DOU ERROR:", e)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    cards = soup.select(".vacancy-item")  # 2025 селектор
    jobs = []

    for card in cards:
        title_el = card.select_one(".title a")
        company_el = card.select_one(".company a")
        location_el = card.select_one(".cities")
        salary_el = card.select_one(".salary")

        title = title_el.get_text(strip=True) if title_el else ""
        company = company_el.get_text(strip=True) if company_el else ""
        location = location_el.get_text(strip=True) if location_el else ""
        salary_raw = salary_el.get_text(strip=True) if salary_el else ""
        url = title_el["href"] if title_el else ""

        jobs.append({
            "source": "dou",
            "external_id": url,
            "title": title,
            "company": company,
            "location": location,
            "salary_raw": salary_raw,
            "url": url,
            "description": ""
        })

    return jobs
