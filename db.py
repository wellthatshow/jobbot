# db.py
import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "jobs.db")


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_conn()
    c = conn.cursor()

    # Таблиця вакансій
    c.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT NOT NULL,
        external_id TEXT NOT NULL,
        title TEXT,
        company TEXT,
        location TEXT,
        salary_raw TEXT,
        url TEXT NOT NULL,
        description TEXT,
        created_at TEXT,
        UNIQUE(source, external_id)
    )
    """)

    # Дії юзерів по вакансіях
    c.execute("""
    CREATE TABLE IF NOT EXISTS actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        action TEXT NOT NULL,
        created_at TEXT,
        FOREIGN KEY(job_id) REFERENCES jobs(id)
    )
    """)

    # Фільтри юзерів
    c.execute("""
    CREATE TABLE IF NOT EXISTS user_filters (
        user_id INTEGER PRIMARY KEY,
        exp_levels TEXT,
        min_salary INTEGER,
        allow_no_salary INTEGER,
        locations TEXT,
        stack TEXT
    )
    """)

    # Settings — наприклад, стан парсера
    c.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    conn.commit()
    conn.close()


def set_setting(key: str, value: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO settings (key, value)
        VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
    """, (key, value))
    conn.commit()
    conn.close()


def get_setting(key: str, default=None):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else default


def job_exists(source: str, external_id: str) -> bool:
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT 1 FROM jobs WHERE source = ? AND external_id = ?",
        (source, external_id)
    )
    exists = c.fetchone() is not None
    conn.close()
    return exists


def insert_job(source, external_id, title, company,
               location, salary_raw, url, description):
    conn = get_conn()
    c = conn.cursor()

    try:
        c.execute("""
            INSERT INTO jobs (
                source, external_id, title, company,
                location, salary_raw, url, description, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            source, external_id, title, company,
            location, salary_raw, url, description,
            datetime.utcnow().isoformat()
        ))
        job_id = c.lastrowid
    except sqlite3.IntegrityError:
        job_id = None

    conn.commit()
    conn.close()

    return job_id


def add_job_action(job_id: int, user_id: int, action: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO actions (job_id, user_id, action, created_at)
        VALUES (?, ?, ?, ?)
    """, (job_id, user_id, action, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
