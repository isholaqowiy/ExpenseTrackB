from telegram import InlineKeyboardButton, InlineKeyboardMarkup

CATEGORIES = ["Food", "Transport", "Bills", "Shopping", "Entertainment", "Health", "Other"]


def main_menu_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("➕ Add Expense", callback_data="add")],
            [
                InlineKeyboardButton("📊 Today", callback_data="today"),
                InlineKeyboardButton("📅 Week", callback_data="week"),
                InlineKeyboardButton("🗓️ Month", callback_data="month"),
            ],
        ]
    )


def category_keyboard():
    rows = []
    for i in range(0, len(CATEGORIES), 2):
        rows.append(
            [InlineKeyboardButton(cat, callback_data=f"cat:{cat}") for cat in CATEGORIES[i : i + 2]]
        )
    rows.append([InlineKeyboardButton("✖ Cancel", callback_data="cancel")])
    return InlineKeyboardMarkup(rows)
