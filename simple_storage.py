import csv
import os
import logging
from typing import List, Optional
from datetime import datetime
from google_sheets import GoogleSheetsManager

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleStorageManager:
    """Простой класс для хранения данных в CSV файле"""
    
    def __init__(self, filename: str = "sales_data.csv"):
        self.filename = filename
        self.headers = ['Ник покупателя', 'Дата и время публикации', 'Сумма', 'Источник размещения']
        self.google_sheets = GoogleSheetsManager()
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Создает файл с заголовками, если он не существует"""
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(self.headers)
            logger.info(f"Создан новый файл: {self.filename}")
    
    def add_sale_record(self, buyer: str, datetime: str, amount: str, source: str) -> bool:
        """
        Добавляет запись о продаже в CSV файл и Google Sheets
        
        Args:
            buyer: Ник покупателя
            datetime: Дата и время публикации
            amount: Сумма покупки
            source: Источник размещения
            
        Returns:
            bool: True если запись успешно добавлена
        """
        success = True
        
        # Сохраняем в CSV файл
        try:
            with open(self.filename, 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([buyer, datetime, amount, source])
            
            logger.info(f"Добавлена запись в CSV: {buyer}, {datetime}, {amount}, {source}")
            
        except Exception as e:
            logger.error(f"Ошибка при добавлении записи в CSV: {e}")
            success = False
        
        # Сохраняем в Google Sheets (если подключен)
        if self.google_sheets.is_connected():
            try:
                google_success = self.google_sheets.add_record(buyer, datetime, amount, source)
                if google_success:
                    logger.info(f"Добавлена запись в Google Sheets: {buyer}, {datetime}, {amount}, {source}")
                else:
                    logger.warning("Не удалось добавить запись в Google Sheets")
            except Exception as e:
                logger.error(f"Ошибка при добавлении записи в Google Sheets: {e}")
        else:
            logger.info("Google Sheets не подключен, данные сохранены только в CSV")
        
        return success
    
    def get_all_records(self) -> Optional[List[List]]:
        """
        Получает все записи из CSV файла
        
        Returns:
            List[List]: Список всех записей или None при ошибке
        """
        try:
            records = []
            with open(self.filename, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    records.append(row)
            return records
            
        except Exception as e:
            logger.error(f"Ошибка при чтении файла: {e}")
            return None
    
    def get_stats(self) -> dict:
        """Получает статистику продаж"""
        records = self.get_all_records()
        
        if not records or len(records) <= 1:
            return {
                'total': 0,
                'usdt_count': 0,
                'usdt_total': 0,
                'rub_count': 0,
                'rub_total': 0
            }
        
        # Исключаем заголовок
        data_records = records[1:]
        total = len(data_records)
        
        # Подсчитываем по валютам и суммам
        usdt_count = 0
        usdt_total = 0
        rub_count = 0
        rub_total = 0
        
        for record in data_records:
            if len(record) > 2:
                amount_str = record[2].lower()
                if 'usdt' in amount_str:
                    usdt_count += 1
                    # Извлекаем число из строки
                    import re
                    number_match = re.search(r'(\d+(?:[.,]\d+)?)', record[2])
                    if number_match:
                        usdt_total += float(number_match.group(1).replace(',', '.'))
                elif '₽' in record[2]:
                    rub_count += 1
                    # Извлекаем число из строки
                    import re
                    number_match = re.search(r'(\d+(?:[.,]\d+)?)', record[2])
                    if number_match:
                        rub_total += float(number_match.group(1).replace(',', '.'))
        
        return {
            'total': total,
            'usdt_count': usdt_count,
            'usdt_total': usdt_total,
            'rub_count': rub_count,
            'rub_total': rub_total
        }
    
    def setup_headers(self) -> bool:
        """Настройка заголовков (уже выполняется в __init__)"""
        return True
