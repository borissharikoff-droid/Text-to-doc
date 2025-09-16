# СРОЧНОЕ ИСПРАВЛЕНИЕ GOOGLE SHEETS

## Шаг 1: Создайте новый сервисный аккаунт

1. Идите на https://console.cloud.google.com/
2. Создайте новый проект или выберите существующий
3. Включите Google Sheets API
4. Создайте сервисный аккаунт:
   - IAM & Admin → Service Accounts → Create Service Account
   - Name: `telegram-bot-sheets-new`
   - Create and Continue → Continue → Done

## Шаг 2: Создайте ключ

1. Найдите созданный сервисный аккаунт
2. Keys → Add Key → Create new key → JSON
3. Скачайте файл

## Шаг 3: Настройте доступ к таблице

1. Откройте таблицу: https://docs.google.com/spreadsheets/d/1KGi1sDNqFzSZwDJLa9zcCXAv6fwbyOmEF-34eZdQKXc
2. Share → Добавьте email из JSON (поле client_email)
3. Права: Editor

## Шаг 4: Добавьте в Railway

1. Скопируйте ВЕСЬ JSON из скачанного файла
2. Railway → Variables → Add Variable
3. Name: `GOOGLE_CREDENTIALS`
4. Value: вставьте JSON
5. Redeploy

## Шаг 5: Проверьте

Отправьте боту сообщение и проверьте таблицу!
