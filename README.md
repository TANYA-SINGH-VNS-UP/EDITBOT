# 🚨 Edit Guardian Bot
A powerful Telegram bot built with **Python** to protect your groups from edited messages.  
It automatically deletes edited messages to maintain transparency and keeps you notified when any message is removed.

---

## ✨ Features
- 🔹 **Auto-delete edited messages** in groups  
- 🔹 **Instant notifications** for deleted messages  
- 🔹 **Easy setup** — just add to your group and start  
- 🔹 **Customizable** via environment variables  
- 🔹 Works 24/7 on **Heroku**  

---

## 🚀 Deployment

### Heroku (One-Click Deploy)
Click the button below to deploy directly to Heroku:

<p align="center">
  <a href="https://dashboard.heroku.com/new?template=https://github.com/Aashik-team/EDITGUARDIAN">
    <img src="https://img.shields.io/badge/Deploy%20On%20Heroku-7056bf?style=for-the-badge&logo=heroku&logoColor=white" width="220" height="38"/>
  </a>
</p>

---

## ⚙️ Environment Variables

Set these in your Heroku app’s **Config Vars**:

| Variable       | Description                                   | Example |
|----------------|-----------------------------------------------|---------|
| `API_ID`       | Your Telegram API ID from [my.telegram.org](https://my.telegram.org) | `1234567` |
| `API_HASH`     | Your Telegram API Hash from my.telegram.org   | `abcd1234efgh5678` |
| `TELEGRAM_TOKEN` | Bot token from [@BotFather](https://t.me/BotFather) | `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11` |
| `OWNER_ID`     | Your Telegram numeric user ID (for admin)     | `123456789` |
| `SUDO_ID`      | List of sudo user IDs                         | `[111111111, 222222222]` |
| `MONGO_URI`    | Your MongoDB connection URI                   | `mongodb+srv://user:pass@cluster.mongodb.net` |
| `DB_NAME`      | Database name                                 | `x` |

---

## 🛠️ Local Development

```bash
# Clone the repository
git clone https://github.com/Aashik-team/EDITGUARDIAN.git
cd EDITGUARDIAN

# Install dependencies
pip install -r requirements.txt

# Run the bot
python Aashik-Edit/main.py
