import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))
SUDO_ID = int(os.getenv("SUDO_ID"))
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
LOGGER = os.getenv("LOGGER", "True").lower() == "true"
BOT_NAME = os.getenv("BOT_NAME", "EDITBOT")
SUPPORT_ID = os.getenv("SUPPORT_ID")
