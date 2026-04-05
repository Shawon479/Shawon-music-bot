# 🚆 Deployment Guide for Shawon v3.5

This version of Shawon is optimized for **One-Click Railway Deployment** with a built-in **Premium Web Control Panel** and **Local SQLite Database**.

---

## 🛠️ Step 1: Requirements
Before starting, gather these values from Telegram (using [@BotFather](https://t.me/BotFather) and [@MyTelegramOrgBot](https://t.me/MyTelegramOrgBot)):
- `API_ID` & `API_HASH` (from [my.telegram.org](https://my.telegram.org))
- `BOT_TOKEN`
- `OWNER_ID` (Your unique Telegram ID)
- `LOGGER_ID` (ID of a private group where the bot can log its activities)
- `SESSION` (A Pyrogram session string)

---

## 🚀 Step 2: One-Click Deployment on Railway

1. **Fork this repository** to your own GitHub account.
2. Log in to [Railway.app](https://railway.app/).
3. Click **"New Project"** -> **"Deploy from GitHub repo"**.
4. Select your forked repository.
5. In the **Variables** tab, add the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `API_ID` | Your Telegram API ID | Required |
| `API_HASH` | Your Telegram API Hash | Required |
| `BOT_TOKEN` | Your Telegram Bot Token | Required |
| `OWNER_ID` | Your Telegram User ID | Required |
| `LOGGER_ID` | Group ID for bot logs | Required |
| `SESSION` | Your Pyrogram String Session | Required |
| `WEB_PASSWORD` | Password for the web dashboard | `admin` |
| `PORT` | Port for the dashboard | `8080` (Railway will override) |
| `DATABASE_URL` | Name of database file | `database.db` |

6. Click **Deploy**. Railway will handle the build and startup automatically using the `railway.json` and `Procfile` provided.

---

## 🌐 Step 3: Accessing the Dashboard

Once the bot is "Active" on Railway:
1. Go to the **Settings** tab in your Railway service.
2. Find the **Public Networking** section and generate a domain.
3. Open the domain (e.g., `https://your-bot-production.up.railway.app`).
4. Log in using your `WEB_PASSWORD` (default: `admin`).

---

## 📊 Dashboard Features
- **Overview**: Real-time stats, CPU/RAM usage, and Global Broadcast.
- **Remote Control**: Perform Admin actions (Ban, Kick, Mute, Promote) on users in *any* group the bot is in, directly from the web!
- **System Logs**: View live server status logs to debug issues instantly.
- **DB Backup**: Download your entire user/chat database with one click.

---

---

## 💻 Local Execution (Windows/Linux)

If you wish to run the bot on your own computer:

1. **Install Python 3.10+** and make sure it is in your PATH.
2. **Install FFmpeg** (Required for audio/video playback).
3. **Download/Clone** this repository and open a terminal in the folder.
4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Configure Environment**: Create a `.env` file or use the provided `credentials.txt` values.
6. **Start the Bot**:
   ```bash
   python -m anony
   ```
7. **Access Dashboard**: Open `http://localhost:8080` in your browser.

---

## 🆘 Support & Source
- **Owner username**: [Shawon](https://t.me/ShawonXnone)
- **Support Channel**: [Shawon](https://t.me/Shawon_28)

**Note**: This bot uses **SQLite** for performance and simplicity. If you want the database to survive between restarts, ensure Railway's "Volume" feature is correctly configured for `database.db`.

