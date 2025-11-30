# sheets.py
import json
import gspread
from google.oauth2.service_account import Credentials

from config import SPREADSHEET_ID, SERVICE_ACCOUNT_JSON, SERVICE_ACCOUNT_FILE

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def _get_client():
    if SERVICE_ACCOUNT_JSON:
        info = json.loads(SERVICE_ACCOUNT_JSON)
        creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    else:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    return gspread.authorize(creds)


def get_ws(name: str):
    gc = _get_client()
    sh = gc.open_by_key(SPREADSHEET_ID)
    try:
        ws = sh.worksheet(name)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=name, rows=1000, cols=20)
    return ws


def log_job_row(job: dict, job_id: int):
    ws = get_ws("vacancies")
    row = [
        job_id,
        job.get("source", ""),
        job.get("company", ""),
        job.get("title", ""),
        job.get("location", ""),
        job.get("salary_raw", ""),
        job.get("url", ""),
        job.get("description", "")
    ]
    ws.append_row(row, value_input_option="RAW")


def log_action(job_id: int, user_id: int, action: str):
    ws = get_ws("actions")
    row = [
        job_id,
        user_id,
        action
    ]
    ws.append_row(row, value_input_option="RAW")
