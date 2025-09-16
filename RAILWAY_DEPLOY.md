# Деплой Telegram бота на Railway

Этот документ описывает, как развернуть Telegram бота для учета рекламы на платформе Railway.

## Подготовка к деплою

### 1. Создание репозитория

1. Создайте новый репозиторий на GitHub
2. Загрузите все файлы проекта в репозиторий
3. Убедитесь, что файл `credentials.json` НЕ загружен в репозиторий (добавьте в `.gitignore`)

### 2. Настройка Railway

1. Зайдите на [railway.app](https://railway.app)
2. Войдите через GitHub
3. Нажмите "New Project" → "Deploy from GitHub repo"
4. Выберите ваш репозиторий

### 3. Настройка переменных окружения

В настройках проекта Railway добавьте следующие переменные окружения:

```
TELEGRAM_BOT_TOKEN=ваш_токен_бота
GOOGLE_SHEETS_ID=1KGi1sDNqFzSZwDJLa9zcCXAv6fwbyOmEF-34eZdQKXc
SHEET_NAME=Лист1
SHEET_RANGE=A:D
OPENAI_API_KEY=ваш_openai_ключ (опционально)
```

### 4. Настройка Google Sheets

Поскольку файл `credentials.json` не может быть загружен в репозиторий, нужно настроить Google Sheets через переменные окружения:

1. Создайте Service Account в Google Cloud Console
2. Скачайте JSON ключ
3. В Railway добавьте переменную `GOOGLE_CREDENTIALS` со всем содержимым JSON файла

### 5. Обновление кода для Railway

Обновите файл `google_sheets.py` для работы с переменной окружения:

```python
import json
import os

# В методе _authenticate замените:
self.creds = Credentials.from_service_account_file(
    'credentials.json', scopes=self.scope
)

# На:
credentials_json = os.getenv('GOOGLE_CREDENTIALS')
if credentials_json:
    credentials_info = json.loads(credentials_json)
    self.creds = Credentials.from_service_account_info(
        credentials_info, scopes=self.scope
    )
```

## Деплой

1. Railway автоматически начнет деплой после подключения репозитория
2. Проверьте логи в разделе "Deployments"
3. Убедитесь, что бот запустился без ошибок

## Проверка работы

1. Найдите вашего бота в Telegram
2. Отправьте команду `/start`
3. Отправьте тестовое сообщение: `@testuser 16.09.2025 12:30 1000р тестовый канал`
4. Проверьте, что данные сохранились в Google Sheets

## Мониторинг

- Railway предоставляет логи в реальном времени
- Используйте команду `/sheets` для проверки подключения к Google Sheets
- Проверяйте статистику через команду `/stats`

## Обновления

Для обновления бота:
1. Внесите изменения в код
2. Запушьте изменения в GitHub
3. Railway автоматически пересоберет и перезапустит приложение

## Troubleshooting

### Бот не отвечает
- Проверьте логи в Railway
- Убедитесь, что токен бота правильный
- Проверьте, что все переменные окружения установлены

### Google Sheets не работает
- Проверьте переменную `GOOGLE_CREDENTIALS`
- Убедитесь, что Service Account имеет доступ к таблице
- Проверьте ID таблицы в переменной `GOOGLE_SHEETS_ID`

### Ошибки парсинга
- Проверьте логи бота
- Используйте команду `/help` для просмотра примеров
- Убедитесь, что сообщения соответствуют ожидаемому формату
