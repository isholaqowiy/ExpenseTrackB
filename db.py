import sqlite3
from contextlib import contextmanager
from datetime import datetime

from config import DATABASE_PATH


@contextmanager
def get_conn():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                chat_id INTEGER PRIMARY KEY,
                first_name TEXT,
                created_at TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS pending (
                chat_id INTEGER PRIMARY KEY,
                category TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def ensure_user(chat_id: int, first_name: str = ""):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (chat_id, first_name, created_at) VALUES (?, ?, ?)",
            (chat_id, first_name, datetime.utcnow().isoformat()),
        )
        conn.commit()


def all_user_chat_ids():
    with get_conn() as conn:
        rows = conn.execute("SELECT chat_id FROM users").fetchall()
        return [r["chat_id"] for r in rows]


def set_pending(chat_id: int, category: str):
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO pending (chat_id, category, created_at) VALUES (?, ?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET category=excluded.category, created_at=excluded.created_at
            """,
            (chat_id, category, datetime.utcnow().isoformat()),
        )
        conn.commit()


def get_pending(chat_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT category FROM pending WHERE chat_id = ?", (chat_id,)).fetchone()
        return row["category"] if row else None


def clear_pending(chat_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM pending WHERE chat_id = ?", (chat_id,))
        conn.commit()


def add_expense(chat_id: int, category: str, amount: float):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO expenses (chat_id, category, amount, created_at) VALUES (?, ?, ?, ?)",
            (chat_id, category, amount, datetime.utcnow().isoformat()),
        )
        conn.commit()


def get_expenses_since(chat_id: int, since_iso: str):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT category, amount, created_at FROM expenses WHERE chat_id = ? AND created_at >= ? ORDER BY created_at",
            (chat_id, since_iso),
        ).fetchall()
        return [dict(r) for r in rows]
