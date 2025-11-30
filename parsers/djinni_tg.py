# parsers/djinni_tg.py

import re

def parse_djinni_message(text: str):
    """
    Парсер повідомлень Djinni з фіксованою локацією Remote.
    """

    lines = [l.strip() for l in text.split("\n") if l.strip()]
    full = " ".join(lines)

    # Title
    title = lines[0]

    # URL
    url = ""
    for l in lines:
        if l.startswith("http"):
            url = l
            break

    # Salary
    salary_match = re.search(r"\$[\d,]+", full)
    salary_raw = salary_match.group(0) if salary_match else ""

    # Description
    description_lines = []
    for l in lines[1:]:
        if l.startswith("http") or l.lower().startswith("subscription"):
            break
        description_lines.append(l)
    description = " ".join(description_lines)

    # FIXED location
    location = "Remote"

    return {
        "source": "djinni",
        "external_id": url,
        "title": title,
        "company": "",
        "location": location,
        "salary_raw": salary_raw,
        "url": url,
        "description": description,
    }
