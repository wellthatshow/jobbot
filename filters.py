# filters.py
import json
from typing import List, Dict, Any

from db import get_conn


def default_filters() -> dict:
    return {
        "exp_levels": [],          # ["0-1", "1-2", "2-3", "3+"]
        "min_salary": None,        # int або None
        "allow_no_salary": True,   # якщо True — вакансії без зп проходять
        "locations": [],           # ["remote", "ua", "eu", "world"]
        "stack": []                # ["sql_dwh", "bi"]
    }


def get_filters(user_id: int) -> dict:
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        "SELECT exp_levels, min_salary, allow_no_salary, locations, stack "
        "FROM user_filters WHERE user_id = ?",
        (user_id,)
    )
    row = c.fetchone()
    conn.close()

    if not row:
        return default_filters()

    return {
        "exp_levels": json.loads(row[0]),
        "min_salary": row[1],
        "allow_no_salary": bool(row[2]),
        "locations": json.loads(row[3]),
        "stack": json.loads(row[4]),
    }


def save_filters(user_id: int, f: dict):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO user_filters (
            user_id, exp_levels, min_salary,
            allow_no_salary, locations, stack
        )
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            exp_levels = excluded.exp_levels,
            min_salary = excluded.min_salary,
            allow_no_salary = excluded.allow_no_salary,
            locations = excluded.locations,
            stack = excluded.stack
    """, (
        user_id,
        json.dumps(f["exp_levels"]),
        f["min_salary"],
        int(f["allow_no_salary"]),
        json.dumps(f["locations"]),
        json.dumps(f["stack"]),
    ))
    conn.commit()
    conn.close()


def get_all_user_ids() -> List[int]:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT user_id FROM user_filters")
    rows = c.fetchall()
    conn.close()
    return [r[0] for r in rows]


def _toggle(lst: list, value: str):
    if value in lst:
        lst.remove(value)
    else:
        lst.append(value)


def job_matches_filters(job: Dict[str, Any], f: dict) -> bool:
    descr = (job.get("title", "") + " " + job.get("description", "")).lower()
    loc_text = (job.get("location", "") + " " + job.get("description", "")).lower()

    # 1) Salary
    if f["min_salary"]:
        if job.get("salary_raw"):
            numbers = "".join(ch if ch.isdigit() else " " for ch in job["salary_raw"])
            nums = [int(n) for n in numbers.split() if n.isdigit()]
            if nums:
                if max(nums) < f["min_salary"]:
                    return False
            else:
                if not f["allow_no_salary"]:
                    return False
        else:
            if not f["allow_no_salary"]:
                return False

    # 2) Locations
    loc_filters = f["locations"]
    if loc_filters:
        ok = False

        if "world" in loc_filters:
            ok = True
        else:
            if "remote" in loc_filters and any(x in loc_text for x in ["remote", "віддалено"]):
                ok = True
            if "ua" in loc_filters and any(x in loc_text for x in ["ukraine", "україна", "kyiv", "lviv"]):
                ok = True
            if "eu" in loc_filters and any(x in loc_text for x in
                                           ["europe", "eu", "germany", "poland", "netherlands", "spain", "france"]):
                ok = True

        if not ok:
            return False

    # 3) Stack
    stack = f["stack"]
    descr_full = descr

    sql_keywords = [
        "sql", "postgres", "mysql", "mariadb", "clickhouse",
        "bigquery", "snowflake", "redshift", "athena", "etl", "elt", "dwh", "data warehouse"
    ]
    bi_keywords = [
        "tableau", "power bi", "powerbi", "looker", "looker studio",
        "data studio", "google data studio", "metabase", "superset", "qlik"
    ]

    if "sql_dwh" in stack:
        if not any(k in descr_full for k in sql_keywords):
            return False

    if "bi" in stack:
        if not any(k in descr_full for k in bi_keywords):
            return False

    # 4) Досвід поки не ріжемо
    return True
