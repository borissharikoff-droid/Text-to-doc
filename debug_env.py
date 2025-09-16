#!/usr/bin/env python3
"""
Отладка переменных окружения на Railway
"""

import os
import json

def debug_environment():
    print("🔍 Отладка переменных окружения...")
    print("=" * 50)
    
    # Проверяем все переменные окружения
    print("📋 Все переменные окружения:")
    for key, value in os.environ.items():
        if 'GOOGLE' in key.upper() or 'SHEET' in key.upper():
            print(f"  {key}: {value[:100]}...")
    
    print("\n" + "=" * 50)
    
    # Проверяем конкретно GOOGLE_CREDENTIALS
    google_creds = os.getenv('GOOGLE_CREDENTIALS')
    if google_creds:
        print("✅ GOOGLE_CREDENTIALS найдена!")
        print(f"Длина: {len(google_creds)} символов")
        try:
            parsed = json.loads(google_creds)
            print(f"✅ JSON валидный")
            print(f"Email: {parsed.get('client_email', 'НЕ НАЙДЕН')}")
            print(f"Project ID: {parsed.get('project_id', 'НЕ НАЙДЕН')}")
        except json.JSONDecodeError as e:
            print(f"❌ Ошибка парсинга JSON: {e}")
    else:
        print("❌ GOOGLE_CREDENTIALS НЕ НАЙДЕНА!")
    
    print("\n" + "=" * 50)
    
    # Проверяем другие переменные
    print("📊 Другие переменные:")
    print(f"TELEGRAM_BOT_TOKEN: {'✅' if os.getenv('TELEGRAM_BOT_TOKEN') else '❌'}")
    print(f"GOOGLE_SHEETS_ID: {'✅' if os.getenv('GOOGLE_SHEETS_ID') else '❌'}")
    print(f"PORT: {os.getenv('PORT', 'НЕ УСТАНОВЛЕН')}")

if __name__ == "__main__":
    debug_environment()
