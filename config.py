"""
Bot settings.

Secrets (bot token, admin ID) are read from the .env file, so they never
end up in the code or on GitHub.
"""
import os

from dotenv import load_dotenv

# Read variables from .env into the environment
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
DB_PATH = os.getenv("DB_PATH", "shop.db")

CURRENCY = "$"

# Order lifecycle. "new" is set automatically, the rest are set by the admin.
ORDER_STATUSES = ("new", "accepted", "shipped", "delivered", "cancelled")
ADMIN_STATUSES = ORDER_STATUSES[1:]

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set. Copy .env.example to .env and fill it in.")
