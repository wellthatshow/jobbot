📊 JobBot — Automated Job Scraper & Filter for Data / Product / BI Analysts

JobBot is an automated system for collecting, filtering, and delivering relevant job postings for Data Analyst, Product Analyst, and BI Analyst roles.

It combines structured scraping + Telegram workflow + live filtering — packaged as a lightweight ETL-like automation tool.

🚀 Features
🔎 Data Collection

    Receives Djinni job posts via Telegram forwarding

    Scrapes DOU job listings

    Normalizes data into a unified job format

🎯 Smart Filtering

    Experience level

    Salary range

    Location (Remote / UA / EU / Worldwide)

    Tech stack (SQL/DWH, BI tools)

    Salary presence (optional)

📬 Delivery

    Sends only matching vacancies to the user

    Interactive inline buttons: Good / Maybe / Ignore

    Logs actions & jobs to Google Sheets

⚙️ Automation

    Scheduled parsing via APScheduler

    Persistent filter settings via SQLite

    Fully containerized with Docker

🧠 How It Works

    User sets filters (experience, salary, location, stack)

    Bot receives jobs from Djinni (forward) or scrapes DOU

    Job is normalized & stored in SQLite

    Match is evaluated via filter engine

    If relevant → sent to user with action buttons

    Job + user actions are logged to Google Sheets

🛠️ Setup

        1️⃣ Install dependencies
        pip install -r requirements.txt

        2️⃣ Fill .env
        TELEGRAM_BOT_TOKEN=xxx
        SPREADSHEET_ID=xxx
        SERVICE_ACCOUNT_JSON={...}

        3️⃣ Run bot
        python bot.py

☁️ Deployment (Docker)
        docker build -t jobbot .
        docker run -d jobbot

🧩 Tech Stack

    Python (Aiogram, APScheduler, BeautifulSoup)

    SQLite (lightweight persistent storage)

    Google Sheets API

    Docker


⭐ Why This Project Matters

    This bot demonstrates practical automation for analysts:

    End-to-end ETL pipeline

    Real job-sourcing automation

    Data filtering engine

    Integration with external APIs

    Deployable real-world microservice

    Perfect for showcasing automation, data engineering basics, and Python backend skills.
