from datetime import datetime, timedelta, timezone

from openai import OpenAI

from config import OPENAI_API_KEY
from db import get_expenses_since

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None


def start_of_today() -> datetime:
    now = datetime.now(timezone.utc)
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


def start_of_week() -> datetime:
    start = start_of_today()
    return start - timedelta(days=start.weekday())


def start_of_month() -> datetime:
    start = start_of_today()
    return start.replace(day=1)


def summarize(expenses):
    total = sum(e["amount"] for e in expenses)
    by_category = {}
    for e in expenses:
        by_category[e["category"]] = by_category.get(e["category"], 0) + e["amount"]
    return total, by_category


def format_breakdown(by_category: dict) -> str:
    if not by_category:
        return "No expenses recorded."
    lines = [f"• {cat}: ${amt:.2f}" for cat, amt in sorted(by_category.items(), key=lambda x: -x[1])]
    return "\n".join(lines)


def narrate(period: str, total: float, by_category: dict) -> str:
    if total == 0:
        return f"No expenses logged this {period}. Add one anytime with ➕ Add Expense."
    if not client:
        return "Keep tracking your expenses to spot trends over time."
    breakdown = ", ".join(f"{c}: ${a:.2f}" for c, a in by_category.items())
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"A user spent a total of ${total:.2f} this {period}. "
                        f"Breakdown by category: {breakdown}. Write a short, warm, encouraging "
                        f"3-4 sentence summary of their spending with one practical, specific tip "
                        f"for next {period}. Do not use markdown."
                    ),
                }
            ],
            max_tokens=250,
            temperature=0.7,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return "Keep tracking your expenses to spot trends over time."


def build_report(chat_id: int, period: str) -> str:
    since = start_of_week() if period == "week" else start_of_month()
    expenses = get_expenses_since(chat_id, since.isoformat())
    total, by_category = summarize(expenses)
    label = "This Week" if period == "week" else "This Month"
    narration = narrate(period, total, by_category)
    return (
        f"<b>{label}'s Report</b>\n\n"
        f"Total spent: <b>${total:.2f}</b>\n\n"
        f"{format_breakdown(by_category)}\n\n"
        f"{narration}"
    )


def build_today(chat_id: int) -> str:
    since = start_of_today()
    expenses = get_expenses_since(chat_id, since.isoformat())
    total, by_category = summarize(expenses)
    return f"<b>Today's Spending</b>\n\nTotal: <b>${total:.2f}</b>\n\n{format_breakdown(by_category)}"
