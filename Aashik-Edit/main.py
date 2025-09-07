import html
import logging
import re
import asyncio
import time
from random import choice
from Edit import *
from telegram import Update, Bot
from pyrogram import Client, filters
from pyrogram.types import Message
from telegram.utils.helpers import escape_markdown, mention_html
from telegram.utils.helpers import mention_markdown
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.error import Unauthorized, BadRequest   # ✅ FIXED IMPORT
from pymongo import MongoClient
from config import LOGGER, MONGO_URI, DB_NAME, TELEGRAM_TOKEN, OWNER_ID, SUDO_ID, BOT_NAME, SUPPORT_ID, API_ID, API_HASH

# Pyrogram client
app = Client("AutoDelete", bot_token=TELEGRAM_TOKEN, api_id=API_ID, api_hash=API_HASH)
print("INFO: Starting Autodelete")
app.start()
bot = app

# Define the text variables
texts = {
    "sudo_5": "Current Sudo Users:\n",
    "sudo_6": "Other Sudo Users:\n",
    "sudo_7": "No sudo users found."
}

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Start time
StartTime = time.time()

# MongoDB setup
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
users_collection = db['users']

# Define a list to store sudo user IDs
if isinstance(SUDO_ID, list):
    sudo_users = SUDO_ID.copy()
else:
    sudo_users = [SUDO_ID]
sudo_users.append(OWNER_ID)

# Helper: uptime
def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]

    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)

    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "

    time_list.reverse()
    ping_time += ":".join(time_list)
    return ping_time

# ================= Commands ================= #

def start(update: Update, context: CallbackContext):
    args = context.args
    uptime = get_readable_time((time.time() - StartTime))

    if update.effective_chat.type == "private":
        first_name = update.effective_user.first_name
        update.effective_message.reply_text(
            PM_START_TEXT.format(escape_markdown(first_name), (PM_START_IMG), BOT_NAME),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN,
            timeout=60,
        )
    else:
        update.effective_message.reply_photo(
            PM_START_IMG,
            reply_markup=InlineKeyboardMarkup(buttons),
            caption="ɪ ᴀᴍ ᴀʟɪᴠᴇ ʙᴀʙʏ!\n<b>ᴜᴘᴛɪᴍᴇ :</b> <code>{}</code>".format(uptime),
            parse_mode=ParseMode.HTML,
        )

def check_edit(update: Update, context: CallbackContext):
    bot: Bot = context.bot
    if update.edited_message:
        edited_message = update.edited_message
        chat_id = edited_message.chat_id
        message_id = edited_message.message_id
        user_id = edited_message.from_user.id
        user_mention = f"<a href='tg://user?id={user_id}'>{html.escape(edited_message.from_user.first_name)}</a>"

        if user_id not in sudo_users:
            bot.delete_message(chat_id=chat_id, message_id=message_id)
            bot.send_message(chat_id=chat_id, text=f"{user_mention} edited a message. Deleted!", parse_mode='HTML')

def add_sudo(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        update.message.reply_text("You are not allowed to use this command.")
        return

    if len(context.args) != 1:
        update.message.reply_text("Usage: /addsudo <user_id>")
        return

    try:
        sudo_user_id = int(context.args[0])
        if sudo_user_id not in sudo_users:
            sudo_users.append(sudo_user_id)
            update.message.reply_text(f"Added {sudo_user_id} as sudo user.")
        else:
            update.message.reply_text("Already in sudo list.")
    except Exception as e:
        update.message.reply_text(f"Error: {e}")

def sudo_list(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        update.message.reply_text("Not allowed.")
        return

    text = "Sudo Users:\n"
    count = 1
    for uid in sudo_users:
        text += f"{count}. {uid}\n"
        count += 1
    update.message.reply_text(text)

def send_stats(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        update.message.reply_text("Not allowed.")
        return

    try:
        users_count = users_collection.count_documents({})
        stats_msg = f"Total Users: {users_count}\n"
        update.message.reply_text(stats_msg)
    except Exception as e:
        logger.error(f"Stats error: {e}")
        update.message.reply_text("Failed to fetch stats.")

def help(update: Update, context: CallbackContext):
    help_text = f"""
<b>Help Menu:</b>

🔧 Owner Commands:
- /addsudo - Add sudo user
- /sudolist - Show sudo users
- /stats - Show bot stats  

🔍 Other Commands:
- /id - Get user or chat ID
- /start - Start the bot
"""
    update.message.reply_text(help_text, parse_mode=ParseMode.HTML)

# ================= Main Function ================= #

def main():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    if SUPPORT_ID:
        try:
            dispatcher.bot.send_photo(
                chat_id=f"{SUPPORT_ID}",
                photo=PM_START_IMG,
                caption="Hello, bot started successfully!",
                parse_mode=ParseMode.MARKDOWN,
            )
        except Unauthorized:
            LOGGER.warning(f"Bot can't send message to {SUPPORT_ID}.")
        except BadRequest as e:
            LOGGER.warning(e.message)

    # Handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.update.edited_message, check_edit))
    dispatcher.add_handler(CommandHandler("addsudo", add_sudo))
    dispatcher.add_handler(CommandHandler("sudolist", sudo_list))
    dispatcher.add_handler(CommandHandler("stats", send_stats))
    dispatcher.add_handler(CommandHandler("help", help))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
