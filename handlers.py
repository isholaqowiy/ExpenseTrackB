from telegram import Update
from telegram.ext import ContextTypes

from db import add_expense, clear_pending, ensure_user, get_expenses_since, get_pending, set_pending
from keyboards import category_keyboard, main_menu_keyboard
from reports import build_report, build_today, start_of_today, summarize

WELCOME = (
    "👋 Welcome to Expense Tracker!\n\n"
    "I'll help you log daily spending and send weekly/monthly reports "
    "with a plain-English breakdown.\n\nUse the menu below to get started."
)

HELP = (
    "Commands:\n"
    "/start - main menu\n"
    "/add - log an expense\n"
    "/today - today's spending\n"
    "/week - this week's report\n"
    "/month - this month's report\n"
    "/cancel - cancel current entry"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    ensure_user(chat_id, update.effective_user.first_name or "")
    clear_pending(chat_id)
    await update.message.reply_html(WELCOME, reply_markup=main_menu_keyboard())


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP)


async def add_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ensure_user(update.effective_chat.id, update.effective_user.first_name or "")
    await update.message.reply_text("Choose a category:", reply_markup=category_keyboard())


async def today_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    ensure_user(chat_id, update.effective_user.first_name or "")
    await update.message.reply_html(build_today(chat_id), reply_markup=main_menu_keyboard())


async def week_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    ensure_user(chat_id, update.effective_user.first_name or "")
    await update.message.reply_html(build_report(chat_id, "week"), reply_markup=main_menu_keyboard())


async def month_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    ensure_user(chat_id, update.effective_user.first_name or "")
    await update.message.reply_html(build_report(chat_id, "month"), reply_markup=main_menu_keyboard())


async def cancel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    clear_pending(chat_id)
    await update.message.reply_text("Cancelled.", reply_markup=main_menu_keyboard())


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    ensure_user(chat_id, query.from_user.first_name or "")
    data = query.data

    if data == "add":
        await query.message.reply_text("Choose a category:", reply_markup=category_keyboard())
    elif data.startswith("cat:"):
        category = data.split(":", 1)[1]
        set_pending(chat_id, category)
        await query.message.reply_html(f"Category: <b>{category}</b>\nNow send the amount (e.g. 25.50):")
    elif data == "cancel":
        clear_pending(chat_id)
        await query.message.reply_text("Cancelled.", reply_markup=main_menu_keyboard())
    elif data == "today":
        await query.message.reply_html(build_today(chat_id), reply_markup=main_menu_keyboard())
    elif data == "week":
        await query.message.reply_html(build_report(chat_id, "week"), reply_markup=main_menu_keyboard())
    elif data == "month":
        await query.message.reply_html(build_report(chat_id, "month"), reply_markup=main_menu_keyboard())


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    ensure_user(chat_id, update.effective_user.first_name or "")
    text = (update.message.text or "").strip()
    category = get_pending(chat_id)

    if not category:
        await update.message.reply_text("I didn't understand that. Use /help to see available commands.")
        return

    cleaned = "".join(c for c in text if c.isdigit() or c == ".")
    try:
        amount = float(cleaned)
        if amount <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("That doesn't look like a valid amount. Send a number like 25.50, or /cancel.")
        return

    add_expense(chat_id, category, amount)
    clear_pending(chat_id)
    today_expenses = get_expenses_since(chat_id, start_of_today().isoformat())
    total, _ = summarize(today_expenses)
    await update.message.reply_html(
        f"✅ Logged <b>${amount:.2f}</b> for <b>{category}</b>.\nToday's total: <b>${total:.2f}</b>",
        reply_markup=main_menu_keyboard(),
    )
