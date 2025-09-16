import os
import json
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Google Sheets Configuration
GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID", "")

# OpenAI Configuration (optional)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Sheet settings
SHEET_NAME = os.getenv("SHEET_NAME", "Лист1")
SHEET_RANGE = os.getenv("SHEET_RANGE", "A:D")

# Railway / Server
PORT = int(os.getenv("PORT", 8000))

# Helper to obtain Google credentials
def get_google_credentials():
    """Return Google Service Account credentials from env or local credentials.json.
    Returns a dict or None.
    """
    google_credentials = os.getenv("GOOGLE_CREDENTIALS")
    if google_credentials:
        try:
            return json.loads(google_credentials)
        except json.JSONDecodeError:
            pass
    if os.path.exists("credentials.json"):
        try:
            with open("credentials.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return None
