# bot.py
import asyncio
import time

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton,
    CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import TELEGRAM_BOT_TOKEN, PARSER_INTERVAL_MINUTES
from db import (
    init_db, job_exists, insert_job, add_job_action,
    set_setting, get_setting
)
from parsers.dou import parse_dou
from parsers.linkedin import parse_linkedin
from sheets import log_job_row, log_action
from filters import (
    get_filters,
    save_filters,
    get_all_user_ids,
    job_matches_filters,
    _toggle,
)
from parsers.djinni_tg import parse_djinni_message


bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

PARSING_ENABLED = False


# ==========================
# UI
# ==========================
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="▶️ Старт парсингу"),
                KeyboardButton(text="⛔ Стоп парсингу")
            ],
            [
                KeyboardButton(text="🎛 Фільтри"),
                KeyboardButton(text="🧪 Тест")
            ],
            [
                KeyboardButton(text="ℹ️ Хелп")
            ]
        ],
        resize_keyboard=True
    )


def job_keyboard(job_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅", callback_data=f"job:{job_id}:good"),
            InlineKeyboardButton(text="➖", callback_data=f"job:{job_id}:maybe"),
            InlineKeyboardButton(text="🚫", callback_data=f"job:{job_id}:ignore"),
        ]
    ])


def _mark(active: bool, text: str) -> str:
    return f"✅ {text}" if active else text


def filters_keyboard(f: dict) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=_mark("0-1" in f["exp_levels"], "0-1y"),
                callback_data="f:exp:0-1"
            ),
            InlineKeyboardButton(
                text=_mark("1-2" in f["exp_levels"], "1-2y"),
                callback_data="f:exp:1-2"
            ),
        ],
        [
            InlineKeyboardButton(
                text=_mark("2-3" in f["exp_levels"], "2-3y"),
                callback_data="f:exp:2-3"
            ),
            InlineKeyboardButton(
                text=_mark("3+" in f["exp_levels"], "3+"),
                callback_data="f:exp:3+"
            ),
        ],
        [
            InlineKeyboardButton(
                text=_mark(f["min_salary"] == 0 or f["min_salary"] is None, "ЗП ≥ 0"),
                callback_data="f:sal:0"
            ),
            InlineKeyboardButton(
                text=_mark(f["min_salary"] == 1200, "ЗП ≥ 1200"),
                callback_data="f:sal:1200"
            ),
            InlineKeyboardButton(
                text=_mark(f["min_salary"] == 1800, "ЗП ≥ 1800"),
                callback_data="f:sal:1800"
            ),
        ],
        [
            InlineKeyboardButton(
                text="Без ЗП: ✅" if f["allow_no_salary"] else "Без ЗП: ❌",
                callback_data="f:allow_no_salary"
            )
        ],
        [
            InlineKeyboardButton(
                text=_mark("remote" in f["locations"], "Remote"),
                callback_data="f:loc:remote"
            ),
            InlineKeyboardButton(
                text=_mark("ua" in f["locations"], "UA"),
                callback_data="f:loc:ua"
            ),
            InlineKeyboardButton(
                text=_mark("eu" in f["locations"], "EU"),
                callback_data="f:loc:eu"
            ),
        ],
        [
            InlineKeyboardButton(
                text=_mark("world" in f["locations"], "World"),
                callback_data="f:loc:world"
            )
        ],
        [
            InlineKeyboardButton(
                text=_mark("sql_dwh" in f["stack"], "SQL/DWH"),
                callback_data="f:stack:sql_dwh"
            ),
            InlineKeyboardButton(
                text=_mark("bi" in f["stack"], "BI (Tab/PowerBI/Looker)"),
                callback_data="f:stack:bi"
            )
        ],
    ])
    return kb


def format_filters_text(f: dict) -> str:
    return (
        "🎛 <b>Фільтри вакансій</b>\n\n"
        f"• Досвід: {', '.join(f['exp_levels']) or '—'}\n"
        f"• Мін. ЗП: {f['min_salary'] if f['min_salary'] else '—'}\n"
        f"• Без ЗП: {'Так' if f['allow_no_salary'] else 'Ні'}\n"
        f"• Локації: {', '.join(f['locations']) or '—'}\n"
        f"• Стек: {', '.join(f['stack']) or '—'}\n\n"
        "Тисни на кнопки нижче 👇"
    )


def format_job_text(job: dict) -> str:
    lines = [
        f"📊 <b>{job['title']}</b>",
        f"🏢 {job['company']}" if job.get("company") else "",
        f"🌍 {job['location']}" if job.get("location") else "",
        f"💰 {job['salary_raw']}" if job.get("salary_raw") else "",
        f"🔗 <a href=\"{job['url']}\">Переглянути</a>",
        f"🌀 Джерело: {job['source'].upper()}",
    ]
    return "\n".join([l for l in lines if l])


# ==========================
# HANDLERS
# ==========================
@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    user_id = message.from_user.id
    f = get_filters(user_id)
    save_filters(user_id, f)

    await message.answer(
        "🚀 Привіт! Це бот автоматичного збору вакансій.\n"
        "Використовуй меню нижче.",
        reply_markup=main_menu(),
        parse_mode=ParseMode.HTML
    )


@dp.message(F.text == "🎛 Фільтри")
@dp.message(F.text == "/filters")
async def cmd_filters(message: Message):
    user_id = message.from_user.id
    f = get_filters(user_id)
    save_filters(user_id, f)

    await message.answer(
        format_filters_text(f),
        reply_markup=filters_keyboard(f),
        parse_mode=ParseMode.HTML
    )


@dp.callback_query(F.data.startswith("f:"))
async def filters_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    f = get_filters(user_id)

    _, kind, *rest = callback.data.split(":")

    if kind == "exp":
        _toggle(f["exp_levels"], rest[0])
    elif kind == "sal":
        v = int(rest[0])
        f["min_salary"] = None if v == 0 else v
    elif kind == "loc":
        _toggle(f["locations"], rest[0])
    elif kind == "stack":
        _toggle(f["stack"], rest[0])
    elif kind == "allow_no_salary":
        f["allow_no_salary"] = not f["allow_no_salary"]

    save_filters(user_id, f)

    await callback.message.edit_text(
        format_filters_text(f),
        reply_markup=filters_keyboard(f),
        parse_mode=ParseMode.HTML
    )
    await callback.answer("Готово")


@dp.callback_query(F.data.startswith("job:"))
async def job_action(callback: CallbackQuery):
    _, job_id_str, action = callback.data.split(":")
    job_id = int(job_id_str)
    user_id = callback.from_user.id

    add_job_action(job_id, user_id, action)
    log_action(job_id, user_id, action)

    await callback.answer(
        "Зберіг ✅" if action == "good"
        else "Відмічено ➖" if action == "maybe"
        else "Ігнор 🚫"
    )


@dp.message(F.text == "/test")
@dp.message(F.text == "🧪 Тест")
async def cmd_test(message: Message):
    fake_job = {
        "source": "test",
        "external_id": str(time.time()),
        "title": "Senior Tester",
        "company": "JobBot Inc.",
        "location": "Remote",
        "salary_raw": "$5000",
        "url": "https://example.com",
        "description": "..."
    }

    job_id = insert_job(**fake_job)
    log_job_row(fake_job, job_id)

    await message.answer(
        format_job_text(fake_job),
        reply_markup=job_keyboard(job_id),
        parse_mode=ParseMode.HTML
    )


@dp.message(F.text == "▶️ Старт парсингу")
async def start_parsing(message: Message):
    global PARSING_ENABLED
    PARSING_ENABLED = True
    set_setting("parsing_enabled", "true")
    await message.answer("Парсинг увімкнено ✅")


@dp.message(F.text == "⛔ Стоп парсингу")
async def stop_parsing(message: Message):
    global PARSING_ENABLED
    PARSING_ENABLED = False
    set_setting("parsing_enabled", "false")
    await message.answer("Парсинг вимкнено ⛔")


# =============================
# DJINNI TELEGRAM FORWARD
# =============================
@dp.message(F.forward_origin)
async def forwarded_djinni_handler(message: Message):
    text = message.text or message.caption or ""
    if not text or "djinni.co/jobs" not in text:
        return

    job = parse_djinni_message(text)

    if job_exists(job["source"], job["external_id"]):
        return

    job_id = insert_job(**job)
    log_job_row(job, job_id)

    f = get_filters(message.from_user.id)
    if job_matches_filters(job, f):
        await message.answer(
            format_job_text(job),
            reply_markup=job_keyboard(job_id),
            parse_mode=ParseMode.HTML
        )


# =============================
# SCHEDULER
# =============================
async def fetch_and_send_jobs():
    global PARSING_ENABLED
    if not PARSING_ENABLED:
        return

    parsers = (parse_dou, parse_linkedin)
    all_jobs = []

    for p in parsers:
        try:
            all_jobs.extend(p())
        except Exception as e:
            print("Parser error:", p.__name__, e)

    user_ids = get_all_user_ids()

    for job in all_jobs:
        if job_exists(job["source"], job["external_id"]):
            continue

        job_id = insert_job(**job)
        log_job_row(job, job_id)

        for uid in user_ids:
            if job_matches_filters(job, get_filters(uid)):
                await bot.send_message(
                    uid,
                    format_job_text(job),
                    reply_markup=job_keyboard(job_id)
                )


# =============================
# RUN
# =============================
async def main():
    global PARSING_ENABLED
    init_db()

    saved = get_setting("parsing_enabled", "false")
    PARSING_ENABLED = (saved == "true")

    scheduler.add_job(fetch_and_send_jobs,
                      "interval",
                      minutes=PARSER_INTERVAL_MINUTES)
    scheduler.start()

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
