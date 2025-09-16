import logging
import asyncio
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN, PORT
from message_parser import SaleMessageParser
from simple_storage import SimpleStorageManager

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class SalesBot:
    """Основной класс телеграм бота для учета продаж"""
    
    def __init__(self):
        self.parser = SaleMessageParser()
        self.storage = SimpleStorageManager()
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Настройка обработчиков сообщений"""
        # Команды
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("export", self.export_command))
        self.application.add_handler(CommandHandler("sheets", self.sheets_command))
        
        # Обработчик всех текстовых сообщений
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        welcome_message = """
🤖 Добро пожаловать в бота для учета рекламы!

⚡️ Быстрый (без запятых, просто накидал):
• "@n2342rik 12.10 1845 6000р русский биз"
• "@ivan 16.12 1430 200usdt канал"
• "@maria 20.01.2025 1800 5000р группа"

Я автоматически извлеку:
👤 Ник покупателя
📅 Дату и время публикации
💰 Сумму покупки (поддерживает 5000р, 200usdt)
📺 Источник размещения

📊 Доступные команды:
/help — показать справку
/stats — показать статистику
/export — экспорт данных
/sheets — статус Google Sheets
        """
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_message = """
📋 Как использовать бота:

1️⃣ Отправьте сообщение о размещении рекламы в любом формате
2️⃣ Бот автоматически извлечет:
   👤 Ник покупателя (@username)
   📅 Дату и время публикации
   💰 Сумму покупки (usdt, ₽, btc, eth)
   📺 Источник размещения

3️⃣ Данные автоматически сохранятся в таблицу

🔤 Примеры сообщений:

📝 Форматированный (с запятыми и кавычками):
• "@nikita 15.12.2025 на 19:30 200usdt \"соль да перец\""
• "@ivan вчера на 14:00 150₽ \"криптоканал\""

⚡ Быстрый (без запятых, просто накидал):
• "@n2342rik 12.10 1845 6000р русский биз"
• "@ivan 16.12 1430 200usdt канал"
• "@maria 20.01.2025 1800 5000р группа"
• "@alex 25.12 1200 0.01btc блог"

📊 Команды:
/start — начать работу
/help — эта справка
/stats — статистика размещений
/export — экспорт данных в CSV
/sheets — статус Google Sheets
        """
        await update.message.reply_text(help_message)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /stats"""
        try:
            stats = self.storage.get_stats()
            
            stats_message = f"""
📊 Статистика рекламы:

📈 Всего размещений: {stats['total']}
💰 USDT: {stats['usdt_count']} ({stats['usdt_total']:.0f} USDT)
💴 Рубли: {stats['rub_count']} ({stats['rub_total']:.0f}₽)

💾 Данные сохраняются в файл: sales_data.csv
            """
            
            await update.message.reply_text(stats_message)
            
        except Exception as e:
            logger.error(f"Ошибка при получении статистики: {e}")
            await update.message.reply_text("❌ Ошибка при получении статистики.")
    
    
    async def export_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /export"""
        try:
            # Отправляем CSV файл пользователю
            with open('sales_data.csv', 'rb') as file:
                await update.message.reply_document(
                    document=file,
                    filename='sales_data.csv',
                    caption='📊 Экспорт данных о продажах'
                )
        except Exception as e:
            logger.error(f"Ошибка при экспорте: {e}")
            await update.message.reply_text("❌ Ошибка при экспорте данных.")
    
    async def sheets_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /sheets для проверки статуса Google Sheets"""
        try:
            if self.storage.google_sheets.is_connected():
                message = """
✅ Google Sheets подключен!

📊 Данные автоматически синхронизируются с Google Sheets
🔗 Таблица доступна по ссылке из config.py

💡 Для настройки Google Sheets используйте инструкцию в файле GOOGLE_SHEETS_SETUP.md
                """
            else:
                message = """
❌ Google Sheets не подключен

📝 Данные сохраняются только в локальный CSV файл
🔧 Для подключения Google Sheets:
1. Следуйте инструкции в GOOGLE_SHEETS_SETUP.md
2. Добавьте файл credentials.json в папку с ботом
3. Перезапустите бота

💾 Локальные данные доступны в файле sales_data.csv
                """
            
            await update.message.reply_text(message)
            
        except Exception as e:
            logger.error(f"Ошибка при проверке Google Sheets: {e}")
            await update.message.reply_text("❌ Ошибка при проверке статуса Google Sheets.")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Основной обработчик сообщений о продажах"""
        message_text = update.message.text
        user_id = update.effective_user.id
        username = update.effective_user.username or "неизвестно"
        
        logger.info(f"Получено сообщение от {username} ({user_id}): {message_text}")
        
        try:
            # Парсим сообщение
            parsed_data = self.parser.parse_message(message_text)
            
            # Проверяем валидность данных
            is_valid, error_message = self.parser.validate_parsed_data(parsed_data)
            
            if not is_valid:
                await update.message.reply_text(
                    f"❌ {error_message}\n\n"
                    "Попробуйте переформулировать сообщение или используйте /help для примеров.\n\n"
                    "Примеры правильных сообщений:\n"
                    "• @nikita 15.12.2025 на 19:30 200usdt \"соль да перец\"\n"
                    "• @ivan вчера на 14:00 150₽ \"криптоканал\"\n"
                    "• @maria сегодня на 20:15 0.01btc \"телеграм группа\""
                )
                return
            
            # Сохраняем данные
            success = self.storage.add_sale_record(
                buyer=parsed_data['buyer'],
                datetime=parsed_data['datetime'],
                amount=parsed_data['amount'],
                source=parsed_data['source']
            )
            
            if success:
                # Отправляем подтверждение
                confirmation = f"""
✅ Реклама успешно записана!

👤 Ник покупателя: {parsed_data['buyer']}
📅 Дата и время публикации: {parsed_data['datetime']}
💰 Сумма: {parsed_data['amount']}
📺 Источник размещения: {parsed_data['source']}

💾 Данные сохранены в sales_data.csv
📊 Используйте /stats для просмотра статистики
                """
                await update.message.reply_text(confirmation)
            else:
                await update.message.reply_text(
                    "❌ Ошибка при сохранении данных. Попробуйте еще раз."
                )
        
        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения: {e}")
            await update.message.reply_text(
                "❌ Произошла ошибка при обработке сообщения. Попробуйте еще раз."
            )
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ошибок"""
        logger.error(f"Exception while handling an update: {context.error}")
    
    def run(self):
        """Запуск бота"""
        # Добавляем обработчик ошибок
        self.application.add_error_handler(self.error_handler)
        
        logger.info("Запуск бота...")
        print("🤖 Бот запущен! Нажмите Ctrl+C для остановки.")
        
        # Запускаем бота
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

def test_parser_locally():
    """Локальный тест парсера"""
    from message_parser import SaleMessageParser
    from simple_storage import SimpleStorageManager
    
    print("🔍 ЛОКАЛЬНЫЙ ТЕСТ ПАРСЕРА")
    print("=" * 50)
    
    parser = SaleMessageParser()
    storage = SimpleStorageManager()
    
    test_message = "@swagger 15.09 1230 65юсдт биб"
    print(f"📝 Тестовое сообщение: '{test_message}'")
    
    # Парсим
    parsed = parser.parse_message(test_message)
    print(f"👤 Покупатель: {parsed['buyer']}")
    print(f"📅 Дата/время: {parsed['datetime']}")
    print(f"💰 Сумма: {parsed['amount']}")
    print(f"📺 Источник: {parsed['source']}")
    
    # Проверяем валидность
    is_valid, error = parser.validate_parsed_data(parsed)
    print(f"✅ Валидно: {is_valid}")
    if not is_valid:
        print(f"❌ Ошибка: {error}")
        return
    
    # Сохраняем
    success = storage.add_sale_record(
        buyer=parsed['buyer'],
        datetime=parsed['datetime'],
        amount=parsed['amount'],
        source=parsed['source']
    )
    print(f"💾 Сохранено: {success}")
    
    # Статистика
    stats = storage.get_stats()
    print(f"📊 Всего записей: {stats['total']}")

def create_web_server():
    """Создает простой веб-сервер для Railway"""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import threading
    
    class HealthCheckHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'text/plain')
                self.end_headers()
                self.wfile.write(b'OK')
            else:
                self.send_response(404)
                self.end_headers()
    
    def run_server():
        server = HTTPServer(('0.0.0.0', PORT), HealthCheckHandler)
        logger.info(f"Web server running on port {PORT}")
        server.serve_forever()
    
    # Запускаем веб-сервер в отдельном потоке
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_parser_locally()
    elif len(sys.argv) > 1 and sys.argv[1] == "debug":
        from debug_env import debug_environment
        debug_environment()
    else:
        # Запускаем веб-сервер для Railway
        create_web_server()
        
        # Запускаем бота
        bot = SalesBot()
        bot.run()
