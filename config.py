import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "8361266417:AAEfwm_4kJHnLopUyH_sA3nArNcb42CcRpQ"

# Google Sheets Configuration
GOOGLE_SHEETS_ID = "1KGi1sDNqFzSZwDJLa9zcCXAv6fwbyOmEF-34eZdQKXc"

# OpenAI Configuration (опционально для улучшенного парсинга)
OPENAI_API_KEY = ""

# Настройки таблицы
SHEET_NAME = "Лист1"  # Название листа в Google Sheets
SHEET_RANGE = "A:D"   # Диапазон колонок: A=Дата, B=Покупатель, C=Время, D=Формат оплаты

# Railway Configuration
PORT = 8000
