# 🎶 Shawon Music Bot v3.5

<p align="center">
  <img src="https://graph.org/file/4140af2f231047e48e991-affc220fd2004b04b0.jpg" alt="Shawon Music Logo" width="300">
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" alt="Python Version"></a>
  <a href="https://github.com/Kurigram/Kurigram"><img src="https://img.shields.io/badge/Library-Kurigram-orange?style=for-the-badge&logo=telegram" alt="Library"></a>
  <a href="https://github.com/pytgcalls/pytgcalls"><img src="https://img.shields.io/badge/Voice%20Calls-PyTgCalls-red?style=for-the-badge" alt="PyTgCalls"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License"></a>
</p>

---

## 🌟 Overview
**Shawon Music** is a high-performance, feature-rich Telegram Music Bot designed to provide seamless audio and video playback in Telegram Voice Chats. Built with speed and reliability in mind, it features a modern web dashboard for remote management and is optimized for cloud deployment.

## 🚀 Key Features
- 🎵 **High-Quality Audio**: Stream crystal clear music with minimal latency.
- 🎬 **Video Playback**: Supports video streaming directly in voice chats.
- 📊 **Web Dashboard**: 
  - Manage bot stats, CPU, and RAM usage.
  - Perform remote admin actions (Ban, Kick, Mute).
  - Download SQLite database backups.
  - View live system logs.
- ⚡ **Optimized Performance**:
  - **yt-dlp Engine**: High-speed media downloads.
  - **Smart Cleanup**: 30-minute automatic file cleanup to save disk space.
  - **Idle Auto-Stop**: Automatically leaves voice chats after 2 minutes of inactivity.
  - **Advanced Audit Logging**: Tracks bot activities for better management.
- 💾 **Local Storage**: Uses **SQLite** for lightweight and reliable data management.
- 🌍 **Multi-language Support**: Easily configurable for different languages.

---

## 🎮 Commands List

### 🎵 Music Commands
- `/play [song name / link]` - Starts audio/video playback in the voice chat.
- `/vplay [song name / link]` - Explicitly play video files in the voice chat.
- `/pause` - Pause the current playback.
- `/resume` - Resume the paused playback.
- `/skip` - Skip to the next track in the queue.
- `/stop` - Stop the playback and clear the queue.
- `/queue` - Shows the list of upcoming songs.
- `/seek [time]` - Seek the current track to a specific time (e.g., `/seek 1m`).

### 🛡️ Admin & Control
- `/auth [user/reply]` - Add a user to the bot's auth list in the group.
- `/unauth [user/reply]` - Remove a user from the auth list.
- `/active` - Check active voice chats on the bot.
- `/ping` - Check the bot's response time.
- `/stats` - View global bot statistics.

### 👤 Owner/Sudo Commands
- `/broadcast [message]` - Broadcast a message to all users and groups.
- `/sudoers` - View the list of sudo users.
- `/restart` - Restart the bot remotely.

---

## 🛠️ Deployment Guide

### 🚆 One-Click Railway Deployment
Perfect for hosting your bot 24/7 with zero maintenance.

1. **Fork** this repository.
2. Log in to [Railway.app](https://railway.app/).
3. Create a **New Project** and select your forked GitHub repo.
4. Add the required **Environment Variables** (see below).
5. Click **Deploy**.

> [!TIP]
> For a detailed walkthrough, check out the [DEPLOYMENT.md](DEPLOYMENT.md) file.

### 💻 Local Deployment
1. **Install Python 3.10+** and **FFmpeg**.
2. **Clone the Repo**:
   ```bash
   git clone https://github.com/Shawon479/Shawon-music-bot.git
   cd Shawon-music-bot
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure `.env`**: Create a `.env` file with your credentials.
5. **Start the Bot**:
   ```bash
   python -m S
   ```

---

## ⚙️ Configuration (Environment Variables)

| Variable | Description |
|----------|-------------|
| `API_ID` | Your Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | Your Telegram API Hash |
| `BOT_TOKEN` | Your Telegram Bot Token from [@BotFather](https://t.me/BotFather) |
| `OWNER_ID` | Your unique Telegram User ID |
| `SESSION` | A Pyrogram String Session (v2) |
| `LOGGER_ID` | ID of a private group for bot logs |
| `WEB_PASSWORD`| Password for the Web Dashboard (default: `admin`) |

---

## 👤 Owner & Support
- **Owner**: [@ShawonXnone](https://t.me/ShawonXnone)
- **Support Channel**: [@Shawon_28](https://t.me/Shawon_28)
- **Dev Support**: [@ShawonXnone](https://t.me/ShawonXnone)

## 📜 License
This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  <b>Built with ❤️ by Shawon</b>
</p>
