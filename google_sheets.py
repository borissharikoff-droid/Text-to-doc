#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gspread
import json
import os
from google.oauth2.service_account import Credentials
import logging
from typing import List, Optional
from config import GOOGLE_SHEETS_ID, SHEET_NAME, get_google_credentials

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleSheetsManager:
    """Класс для работы с Google Sheets"""
    
    def __init__(self):
        self.sheet_id = GOOGLE_SHEETS_ID
        self.sheet_name = SHEET_NAME
        self.worksheet = None
        self._setup_connection()
    
    def _setup_connection(self):
        """Настройка подключения к Google Sheets"""
        try:
            # Определяем область доступа
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Получаем учетные данные из config.py
            credentials_info = get_google_credentials()
            creds = Credentials.from_service_account_info(credentials_info, scopes=scope)
            logger.info("Используются учетные данные из config.py")
            
            # Подключаемся к Google Sheets
            gc = gspread.authorize(creds)
            spreadsheet = gc.open_by_key(self.sheet_id)
            self.worksheet = spreadsheet.worksheet(self.sheet_name)
            
            logger.info("Подключение к Google Sheets установлено")
            
        except Exception as e:
            logger.error(f"Ошибка подключения к Google Sheets: {e}")
            logger.info("Google Sheets отключен, данные будут сохраняться только в CSV")
            self.worksheet = None
    
    def add_record(self, buyer: str, datetime: str, amount: str, source: str) -> bool:
        """
        Добавляет запись в Google Sheets
        
        Args:
            buyer: Ник покупателя
            datetime: Дата и время публикации
            amount: Сумма покупки
            source: Источник размещения
            
        Returns:
            bool: True если запись успешно добавлена
        """
        if not self.worksheet:
            logger.warning("Google Sheets не подключен")
            return False
        
        try:
            # Добавляем строку в конец таблицы
            row = [buyer, datetime, amount, source]
            self.worksheet.append_row(row)
            
            logger.info(f"Запись добавлена в Google Sheets: {row}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при добавлении записи в Google Sheets: {e}")
            return False
    
    def get_all_records(self) -> Optional[List[List]]:
        """
        Получает все записи из Google Sheets
        
        Returns:
            List[List]: Список всех записей или None при ошибке
        """
        if not self.worksheet:
            logger.warning("Google Sheets не подключен")
            return None
        
        try:
            # Получаем все записи
            records = self.worksheet.get_all_values()
            logger.info(f"Получено {len(records)} записей из Google Sheets")
            return records
            
        except Exception as e:
            logger.error(f"Ошибка при получении записей из Google Sheets: {e}")
            return None
    
    def setup_headers(self) -> bool:
        """
        Настраивает заголовки в Google Sheets
        
        Returns:
            bool: True если заголовки успешно настроены
        """
        if not self.worksheet:
            logger.warning("Google Sheets не подключен")
            return False
        
        try:
            # Проверяем, есть ли уже заголовки
            existing_data = self.worksheet.get_all_values()
            
            if not existing_data:
                # Добавляем заголовки
                headers = ['Ник покупателя', 'Дата и время публикации', 'Сумма', 'Источник размещения']
                self.worksheet.append_row(headers)
                logger.info("Заголовки добавлены в Google Sheets")
            
            return True
            
        except Exception as e:
            logger.error(f"Ошибка при настройке заголовков: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Проверяет, подключен ли Google Sheets"""
        return self.worksheet is not None
