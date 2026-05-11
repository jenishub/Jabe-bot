# JB Travel Bot 🌍

Telegram bot for JB Travel — tour operator, Almaty.
Sends hotel booking emails and manages queries (Fresh → Confirmed → Finished).

---

## 📁 Project Structure

```
tourbot/
├── bot.py               ← Main bot (Railway runs this)
├── run.py               ← Local dev entry point (loads .env)
├── database.py          ← JSON storage (Railway Volume)
├── email_sender.py      ← Gmail SMTP
├── Procfile             ← Tells Railway how to start the bot
├── runtime.txt          ← Pins Python 3.11
├── requirements.txt
├── .gitignore           ← Keeps .env and data/ off GitHub
├── .env.example         ← Template — copy to .env for local dev
└── handlers/
    ├── main_handler.py
    ├── email_handler.py
    └── query_handler.py
```

---

## 🚀 Deploying to Railway (from GitHub)

### Step 1 — Push code to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/jb-travel-bot.git
git push -u origin main
```

> .gitignore already excludes .env and data/ — your secrets stay local.

---

### Step 2 — Create Railway project

1. Go to railway.app and log in
2. Click **New Project → Deploy from GitHub repo**
3. Select your `jb-travel-bot` repository
4. Railway will detect the `Procfile` automatically

---

### Step 3 — Add a Volume (persistent storage)

Railway's filesystem resets on every deploy. A Volume keeps your queries safe.

1. In your Railway project, click **New → Volume**
2. Mount path: `/data`
3. Done — `database.json` will live there permanently across redeploys

---

### Step 4 — Set environment variables

In Railway → your service → **Variables**, add these five:

| Variable | Value |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Token from @BotFather |
| `GMAIL_USER` | your_email@gmail.com |
| `GMAIL_APP_PASSWORD` | 16-char App Password (see below) |
| `WEBHOOK_URL` | Your Railway public domain (see below) |
| `RAILWAY_VOLUME_MOUNT_PATH` | `/data` |

**Getting WEBHOOK_URL:**
- Railway → your service → **Settings → Networking → Generate Domain**
- Copy the domain, e.g. `jb-travel-bot-production.up.railway.app`
- Set `WEBHOOK_URL` to `https://jb-travel-bot-production.up.railway.app`

**Getting Gmail App Password:**
1. Enable 2-Step Verification on your Google account
2. Google Account → Security → App Passwords → create one for Mail
3. Copy the 16-character code (spaces don't matter)

---

### Step 5 — Deploy

Railway auto-deploys on every `git push`. After adding variables, click **Redeploy** in the dashboard.

Check **Logs** — you should see:
```
Starting webhook on port XXXX → https://your-domain.up.railway.app
```

---

## 💻 Local Development

```bash
# 1. Clone your repo
git clone https://github.com/YOUR_USERNAME/jb-travel-bot.git
cd jb-travel-bot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure credentials
cp .env.example .env
# Edit .env with your tokens

# 4. Run (uses polling mode when WEBHOOK_URL is not set)
python run.py
```

---

## 🤖 Bot Usage

### Send Hotel Email
1. Press **Send Hotel Email**
2. Enter hotel name and email: `Rixos Almaty | reservations@rixos.com`
3. Enter number of guests, check-in, check-out, room type
4. Confirm — email is sent and query **JB001** is saved to Fresh Queries automatically

### Query Workflow

```
Add Query  →  Fresh  →  Confirmed  →  Finished
```

Each query is tagged **JBxxx** (counter never resets, even across redeploys).

---

## 🔄 Pushing Updates

```bash
git add .
git commit -m "describe your change"
git push
```

Railway redeploys automatically. The Volume keeps all data safe.

---

## Notes

- Never commit `.env` — already in `.gitignore`
- All query data lives on the Railway Volume at `/data/database.json`
- Railway Hobby plan ($5/mo) is more than enough for this bot
