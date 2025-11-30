JobBot — це система автоматизованого збору та фільтрування вакансій для
Data Analyst / Product Analyst / BI Analyst спеціалістів.

Бот:

отримує вакансії з Djinni через Telegram forward

додатково парсить DOU

фільтрує вакансії за досвідом, зарплатою, стеком, локацією

надсилає лише релевантні вакансії в Telegram

веде лог дій у Google Sheets

працює автоматично через APScheduler

має інтуїтивне меню з кнопками

легко деплоїться через Docker + Railway

Це реальний ETL-проєкт для аналітика з автоматизацією процесів найму.

✔ Автоматизація бізнес-процесів
✔ Парсинг даних (HTML, Telegram Forward)
✔ Робота з API Google Sheets
✔ Зберігання структурованих даних (SQLite)
✔ Логіка фільтрації SQL-подібного формату
✔ Scheduler / cron-подібний запуск задач
✔ Контейнеризація (Docker)
✔ Деплой на Railway
✔ Робота зі структурованими джерелами вакансій

🛠 Технології
Компонент	Технологія
Telegram Bot	Aiogram 3
Парсинг	BeautifulSoup
Джерела	Djinni (Telegram), DOU
База	SQLite
Автоматизація	APScheduler
Логи	Google Sheets API
Кофінг	python-dotenv
Деплой	Docker + Railway


🚀 Як це працює
1️⃣ Користувач запускає бота

Отримує меню:

▶️ Старт парсингу

⛔ Стоп

🎛 Фільтри

🧪 Тест

2️⃣ Фільтри

Доступні:

Досвід: 0–1 / 1–2 / 2–3 / 3+

Мінімальна ЗП

Враховувати / ігнорувати вакансії без ЗП

Локація: Remote / UA / EU / World

Стек: SQL/DWH, BI (Tableau/PowerBI/Looker)

3️⃣ Джерела вакансій

Djinni → Телеграм forward (стабільно працює, без банів)

DOU парсер

4️⃣ Збереження в Google Sheets

Jobs

id

title

salary

description

source

url

Actions

job_id

user_id

action


5️⃣ Scheduler

Кожні N хвилин виконується:

збір нових вакансій

фільтрація

надсилання релевантних вакансій у чат

🧩 Архітектура проєкту
/jobbot
│ bot.py
│ config.py
│ db.py
│ filters.py
│ sheets.py
│ Dockerfile
│ requirements.txt
│ .env.example
│
└── parsers/
       dou.py
       djinni_tg.py

🐳 Docker
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "bot.py"]



🧪 Локальний запуск
pip install -r requirements.txt
python bot.py

📄 Ліцензія

MIT — можна використовувати будь-де.


English Version

JobBot — Intelligent Job Monitoring Telegram Bot
Automated Vacancy Tracking for Data/Product/BI Analysts
Project Overview

JobBot is an automated system that aggregates and filters job listings for
Data Analysts, Product Analysts, and BI Analysts.

The bot:

receives job posts from Djinni via Telegram forwarding

scrapes DOU job listings

filters jobs by experience, salary, stack, location

sends only relevant jobs to the user

logs user actions in Google Sheets

runs automatically using APScheduler

provides a clean, interactive UI in Telegram

is fully containerized and deployable on Railway

This is a real-world ETL-style automation project for analysts.

Skills Demonstrated

✔ Automation of repetitive workflows
✔ Web scraping & HTML parsing
✔ Integrating Google Sheets API
✔ Structured data storage (SQLite)
✔ SQL-like filtering logic in Python
✔ Scheduled/cron-style background jobs
✔ Docker containerization
✔ Railway cloud deployment
✔ Working with job data sources

🛠 Tech Stack
Component	Technology
Telegram Bot	Aiogram 3
Parsing	BeautifulSoup
Sources	Djinni (Telegram), DOU
Database	SQLite
Automation	APScheduler
Logs	Google Sheets API
Config	python-dotenv
Deployment	Docker + Railway
🚀 How It Works

1️⃣ User opens the bot and sees the menu
2️⃣ User configures filters
3️⃣ Bot processes job posts from Djinni & DOU
4️⃣ Only matching jobs are forwarded
5️⃣ User reactions stored for analytics
6️⃣ Scheduler sends new jobs every N minutes

🧩 Project Structure
/jobbot
│ bot.py
│ config.py
│ db.py
│ filters.py
│ sheets.py
│ Dockerfile
│ requirements.txt
│ .env.example
│
└── parsers/
       dou.py
       djinni_tg.py

🐳 Docker
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "bot.py"]


🧪 Local Run
pip install -r requirements.txt
python bot.py

📄 License

MIT License
