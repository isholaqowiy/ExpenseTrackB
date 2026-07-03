import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram.ext import Application

from config import TIMEZONE
from db import all_user_chat_ids
from reports import build_report

logger = logging.getLogger(__name__)


async def _send_all(application: Application, period: str):
    for chat_id in all_user_chat_ids():
        try:
            await application.bot.send_message(chat_id, build_report(chat_id, period), parse_mode="HTML")
        except Exception:
            logger.exception("Failed sending %s report to %s", period, chat_id)


def start_scheduler(application: Application) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=TIMEZONE)

    scheduler.add_job(
        lambda: application.create_task(_send_all(application, "week")),
        CronTrigger(day_of_week="mon", hour=8, minute=0),
        id="weekly-report",
        replace_existing=True,
    )
    scheduler.add_job(
        lambda: application.create_task(_send_all(application, "month")),
        CronTrigger(day=1, hour=8, minute=0),
        id="monthly-report",
        replace_existing=True,
    )

    scheduler.start()
    return scheduler
