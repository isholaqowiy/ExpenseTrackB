# ExpenseTrackB — Telegram Expense Tracker Bot

Structured, button-driven expense tracking with AI-narrated weekly and monthly reports.

## Features
- `/start` — main menu with inline buttons
- **➕ Add Expense** — pick a category button, then send the amount
- **📊 Today / 📅 Week / 🗓️ Month** — spending summaries
- Weekly report auto-sent every **Monday 08:00** (server timezone)
- Monthly report auto-sent on the **1st of each month, 08:00**
- Report narration written by OpenAI (`gpt-4o-mini`); falls back to a generic note if the API call fails or no key is set

## Local setup
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # then fill in BOT_TOKEN and OPENAI_API_KEY
python main.py
```

## Deploying on Render.com (Background Worker)
1. Push this folder to a GitHub repo.
2. On Render: **New +** → **Background Worker** → connect the repo.
3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `python main.py`
5. Add environment variables in the Render dashboard (**do not** commit `.env`):
   - `BOT_TOKEN`
   - `OPENAI_API_KEY`
   - `TIMEZONE` (optional, e.g. `Africa/Lagos`)
6. Deploy. This bot uses long polling, so no public URL/webhook is needed — a Background Worker is the right fit.

### ⚠️ Persistent storage
Render's default filesystem is **ephemeral** — `expenses.db` will be wiped on every redeploy/restart. For real usage, attach a [Render Disk](https://render.com/docs/disks) and point `DATABASE_PATH` at a path on that disk (e.g. `/data/expenses.db`), or migrate to a managed Postgres database.

### Security
Never commit your `.env` file or paste tokens/keys into chat, code comments, or version control. If a token or key is ever exposed, revoke and regenerate it immediately (BotFather → `/mybots` → your bot → API Token → Revoke; OpenAI → API Keys → Delete).
