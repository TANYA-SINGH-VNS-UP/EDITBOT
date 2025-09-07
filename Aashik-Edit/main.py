import html
import logging
import time
from telegram import Update, Bot, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.error import Unauthorized, BadRequest
from pyrogram import Client, filters
from pymongo import MongoClient
from config import LOGGER, MONGO_URI, DB_NAME, TELEGRAM_TOKEN, OWNER_ID, SUDO_ID, BOT_NAME, SUPPORT_ID, API_ID, API_HASH

# Pyrogram client (optional, can be used for async tasks)
app = Client("AutoDelete", bot_token=TELEGRAM_TOKEN, api_id=API_ID, api_hash=API_HASH)
print("INFO: Starting Autodelete")
app.start()
bot = app

# Logging setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Start time
StartTime = time.time()

# MongoDB setup
mongo_client = MongoClient(MONGO_URI)
db = mongo_client[DB_NAME]
users_collection = db['users']

# Ensure SUDO_ID is a list
if isinstance(SUDO_ID, list):
    sudo_users = SUDO_ID.copy()
else:
    sudo_users = [SUDO_ID]
sudo_users.append(OWNER_ID)

# ---------------- Helper Functions ---------------- #
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

# ---------------- Command Handlers ---------------- #
def start(update: Update, context: CallbackContext):
    uptime = get_readable_time(int(time.time() - StartTime))
    update.effective_message.reply_text(f"Hello! Bot is alive.\nUptime: {uptime}")

def check_edit(update: Update, context: CallbackContext):
    if update.edited_message:
        edited_msg = update.edited_message
        chat_id = edited_msg.chat_id
        message_id = edited_msg.message_id
        user_id = edited_msg.from_user.id
        user_mention = f"<a href='tg://user?id={user_id}'>{html.escape(edited_msg.from_user.first_name)}</a>"

        if user_id not in sudo_users:
            try:
                context.bot.delete_message(chat_id=chat_id, message_id=message_id)
                context.bot.send_message(chat_id=chat_id, text=f"{user_mention} edited a message. Deleted!", parse_mode='HTML')
            except Exception as e:
                logger.error(f"Failed to delete message: {e}")

def add_sudo(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        update.message.reply_text("You are not allowed to use this command.")
        return
    if len(context.args) != 1:
        update.message.reply_text("Usage: /addsudo <user_id>")
        return
    try:
        uid = int(context.args[0])
        if uid not in sudo_users:
            sudo_users.append(uid)
            update.message.reply_text(f"Added {uid} as sudo user.")
        else:
            update.message.reply_text("Already in sudo list.")
    except Exception as e:
        update.message.reply_text(f"Error: {e}")

def sudo_list(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        update.message.reply_text("Not allowed.")
        return
    text = "Sudo Users:\n"
    for idx, uid in enumerate(sudo_users, 1):
        text += f"{idx}. {uid}\n"
    update.message.reply_text(text)

def send_stats(update: Update, context: CallbackContext):
    if update.effective_user.id != OWNER_ID:
        update.message.reply_text("Not allowed.")
        return
    try:
        users_count = users_collection.count_documents({})
        update.message.reply_text(f"Total Users: {users_count}")
    except Exception as e:
        logger.error(f"Stats error: {e}")
        update.message.reply_text("Failed to fetch stats.")

def help_command(update: Update, context: CallbackContext):
    help_text = """
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

# ---------------- Main Function ---------------- #
def main():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Notify support group
    if SUPPORT_ID:
        try:
            dispatcher.bot.send_photo(
                chat_id=SUPPORT_ID,
              #  photo=PM_START_IMG,
                caption="Hello, bot started successfully!",
                parse_mode=ParseMode.MARKDOWN
            )
        except Unauthorized:
            LOGGER.warning(f"Bot can't send message to {SUPPORT_ID}.")
        except BadRequest as e:
            LOGGER.warning(e.message)

    # Register handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.update.edited_message, check_edit))
    dispatcher.add_handler(CommandHandler("addsudo", add_sudo))
    dispatcher.add_handler(CommandHandler("sudolist", sudo_list))
    dispatcher.add_handler(CommandHandler("stats", send_stats))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # Start polling
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
