@echo off
echo Запуск Telegram бота для учета продаж...
echo.

REM Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Python не установлен или не добавлен в PATH
    echo Установите Python с https://python.org
    pause
    exit /b 1
)

REM Устанавливаем зависимости
echo Установка зависимостей...
pip install -r requirements.txt

REM Проверяем наличие основного файла
if not exist main.py (
    echo ОШИБКА: Файл main.py не найден
    pause
    exit /b 1
)

echo.
echo Бот запущен! Для остановки нажмите Ctrl+C
echo.

REM Запускаем бота
python main.py

echo.
echo Бот остановлен.
pause
