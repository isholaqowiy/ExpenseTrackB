import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DATABASE_PATH = os.getenv("DATABASE_PATH", "expenses.db")
TIMEZONE = os.getenv("TIMEZONE", "UTC")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is required. Set it in your .env file or Render dashboard.")
