import logging

from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from config import BOT_TOKEN
from db import init_db
from handlers import (
    add_cmd,
    button_handler,
    cancel_cmd,
    help_cmd,
    month_cmd,
    start,
    text_handler,
    today_cmd,
    week_cmd,
)
from scheduler import start_scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def main():
    init_db()
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("add", add_cmd))
    application.add_handler(CommandHandler("today", today_cmd))
    application.add_handler(CommandHandler("week", week_cmd))
    application.add_handler(CommandHandler("month", month_cmd))
    application.add_handler(CommandHandler("cancel", cancel_cmd))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    start_scheduler(application)

    logger.info("ExpenseTrackB bot starting (long polling)...")
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
