#!/usr/bin/env python3
"""
Тест подключения к Google Sheets
"""

import os
import json
from google_sheets import GoogleSheetsManager

def test_connection():
    print("🔍 Тестирование Google Sheets...")
    
    # Проверяем переменные окружения
    google_credentials = os.getenv('GOOGLE_CREDENTIALS')
    if google_credentials:
        print("✅ GOOGLE_CREDENTIALS найдена")
        try:
            creds = json.loads(google_credentials)
            print(f"✅ Email сервисного аккаунта: {creds.get('client_email', 'НЕ НАЙДЕН')}")
        except:
            print("❌ Ошибка парсинга GOOGLE_CREDENTIALS")
    else:
        print("❌ GOOGLE_CREDENTIALS не найдена")
    
    # Проверяем файл
    if os.path.exists('credentials.json'):
        print("✅ credentials.json найден")
    else:
        print("❌ credentials.json не найден")
    
    # Тестируем подключение
    try:
        sheets = GoogleSheetsManager()
        if sheets.is_connected():
            print("✅ Подключение к Google Sheets успешно!")
            
            # Пробуем добавить тестовую запись
            success = sheets.add_record(
                "test_user", 
                "2024-01-01 12:00", 
                "100 USDT", 
                "test"
            )
            if success:
                print("✅ Тестовая запись добавлена!")
            else:
                print("❌ Не удалось добавить тестовую запись")
        else:
            print("❌ Подключение к Google Sheets не удалось")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_connection()
