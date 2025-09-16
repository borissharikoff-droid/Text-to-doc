# Исправление Google Sheets

## Проблема
Google Sheets не работает из-за ошибки "Invalid JWT Signature". Это означает, что сервисный аккаунт неактивен или неправильно настроен.

## Решение

### 1. Создайте новый сервисный аккаунт:

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Выберите проект или создайте новый
3. Перейдите в "IAM & Admin" → "Service Accounts"
4. Нажмите "Create Service Account"
5. Заполните:
   - Name: `telegram-bot-sheets`
   - Description: `Service account for Telegram bot Google Sheets integration`
6. Нажмите "Create and Continue"
7. Роли не нужны, нажмите "Continue"
8. Нажмите "Done"

### 2. Создайте ключ:

1. Найдите созданный сервисный аккаунт
2. Нажмите на него
3. Перейдите в "Keys" → "Add Key" → "Create new key"
4. Выберите "JSON" и нажмите "Create"
5. Скачайте файл

### 3. Настройте доступ к Google Sheets:

1. Откройте вашу Google таблицу: https://docs.google.com/spreadsheets/d/1KGi1sDNqFzSZwDJLa9zcCXAv6fwbyOmEF-34eZdQKXc
2. Нажмите "Share" (Поделиться)
3. Добавьте email сервисного аккаунта (из JSON файла, поле "client_email")
4. Дайте права "Editor"
5. Нажмите "Send"

### 4. Обновите Railway:

1. Скопируйте содержимое JSON файла
2. В Railway Dashboard → Variables
3. Добавьте переменную `GOOGLE_CREDENTIALS` со значением JSON
4. Перезапустите приложение

### 5. Альтернативное решение (только CSV):

Если Google Sheets не нужен, можно отключить его:

1. В Railway Dashboard → Variables
2. Удалите переменную `GOOGLE_CREDENTIALS`
3. Данные будут сохраняться только в CSV файл
4. Используйте команду `/export` для получения данных

## Проверка

После настройки отправьте боту сообщение и проверьте:
- Логи Railway: должно быть "Подключение к Google Sheets установлено"
- Команда `/sheets` в боте: должна показать "Google Sheets подключен"
- Новая строка в Google таблице
