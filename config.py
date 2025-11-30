# config.py
import os
from dotenv import load_dotenv

# Локально читаємо .env, на Railway він не потрібен
load_dotenv()

# 🔐 Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# 🕒 Інтервал парсингу в ХВИЛИНАХ
PARSER_INTERVAL_MINUTES = float(os.getenv("PARSER_INTERVAL_MINUTES", "30"))

# 📊 Google Sheets
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "")

# Сервіс-акаунт:
# - локально можна юзати файл service_account.json
# - на Railway краще покласти JSON в env SERVICE_ACCOUNT_JSON
SERVICE_ACCOUNT_JSON = os.getenv("SERVICE_ACCOUNT_JSON")  # може бути None
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE", "service_account.json")
