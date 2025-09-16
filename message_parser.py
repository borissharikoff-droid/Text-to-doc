import re
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple
import pytz

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SaleMessageParser:
    """Класс для парсинга сообщений о продажах"""
    
    def __init__(self):
        # Паттерны для извлечения информации
        self.buyer_patterns = [
            r'@(\w+)',  # Telegram username (приоритет)
            r'(?:продал|продажа|клиент|покупатель|купил)\s*:?\s*([А-Яа-яA-Za-z0-9\s@_-]+?)(?:\s|$|,|\.|!)',
            r'([А-Я][а-я]+(?:\s[А-Я][а-я]+)*)',  # Имя и фамилия
        ]
        
        # Паттерны для суммы
        self.amount_patterns = [
            r'(\d+(?:[.,]\d+)?)\s*(?:usdt|usd|₽|руб|рубл|btc|eth|долл)',
            r'(\d+(?:[.,]\d+)?)\s*(?:тысяч|к|k)',
            r'(\d+(?:[.,]\d+)?)(?:р|₽|руб|рубл)',  # Число с р в конце
            r'(\d+(?:[.,]\d+)?)',  # Просто число
        ]
        
        # Паттерны для источника (в кавычках)
        self.source_patterns = [
            r'"([^"]+)"',  # Текст в двойных кавычках
            r"'([^']+)'",  # Текст в одинарных кавычках
            r'«([^»]+)»',  # Текст в кавычках-елочках
        ]
        
        self.time_patterns = [
            r'(?:на\s+)?(\d{1,2}:\d{2})',  # Время в формате ЧЧ:ММ с "на"
            r'в\s*(\d{1,2})\s*час',  # "в 15 часов"
            r'(\d{1,2})\s*ч',  # "15ч"
        ]
        
        self.date_patterns = [
            r'(\d{1,2})[./](\d{1,2})[./](\d{2,4})',  # ДД.ММ.ГГГГ или ДД/ММ/ГГГГ
            r'сегодня',
            r'вчера',
        ]
        
        # Названия месяцев на русском
        self.month_names = {
            'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
            'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
            'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
        }
    
    def parse_message(self, message_text: str) -> Dict[str, Optional[str]]:
        """
        Парсит сообщение и извлекает данные о продаже
        
        Args:
            message_text: Текст сообщения
            
        Returns:
            Dict с ключами: buyer, datetime, amount, source
        """
        original_text = message_text
        message_text_lower = message_text.lower().strip()
        logger.info(f"Парсинг сообщения: {message_text}")
        
        # Сначала пытаемся парсить как неформатированный текст
        is_unformatted = self._is_unformatted_text(message_text)
        logger.info(f"Текст неформатированный: {is_unformatted}")
        
        if is_unformatted:
            result = self._parse_unformatted_text(message_text)
            logger.info(f"Результат неформатированного парсинга: {result}")
            # Проверяем, что хотя бы покупатель определен
            if result and result.get('buyer'):
                logger.info(f"Результат парсинга (неформатированный): {result}")
                return result
        
        # Если не получилось, используем стандартный парсинг
        date = self._extract_date(message_text_lower)
        time = self._extract_time(message_text_lower)
        
        # Объединяем дату и время
        datetime_str = f"{date} {time}" if date and time else None
        if not datetime_str:
            # Если нет даты или времени, используем текущие
            if not date:
                date = datetime.now(pytz.timezone('Europe/Moscow')).strftime('%d.%m.%Y')
            if not time:
                time = datetime.now(pytz.timezone('Europe/Moscow')).strftime('%H:%M')
            datetime_str = f"{date} {time}"
        
        result = {
            'buyer': self._extract_buyer(original_text),
            'datetime': datetime_str,
            'amount': self._extract_amount(original_text),
            'source': self._extract_source(original_text)
        }
        
        logger.info(f"Результат парсинга: {result}")
        return result
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Извлекает дату из текста"""
        # Проверяем специальные слова
        if 'сегодня' in text:
            return datetime.now(pytz.timezone('Europe/Moscow')).strftime('%d.%m.%Y')
        
        if 'вчера' in text:
            yesterday = datetime.now(pytz.timezone('Europe/Moscow')).replace(hour=0, minute=0, second=0, microsecond=0)
            yesterday = yesterday.replace(day=yesterday.day - 1)
            return yesterday.strftime('%d.%m.%Y')
        
        # Ищем даты с названиями месяцев (например, "12 декабря")
        for month_name, month_num in self.month_names.items():
            pattern = rf'(\d{{1,2}})\s+{month_name}'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                day = match.group(1)
                current_year = datetime.now().year
                try:
                    # Проверяем валидность даты
                    datetime.strptime(f"{day}.{month_num}.{current_year}", '%d.%m.%Y')
                    return f"{day.zfill(2)}.{month_num:02d}.{current_year}"
                except ValueError:
                    continue
        
        # Ищем даты в формате ДД.ММ.ГГГГ
        for pattern in self.date_patterns:
            match = re.search(pattern, text)
            if match and len(match.groups()) >= 3:
                day, month, year = match.groups()[:3]
                if len(year) == 2:
                    year = '20' + year
                try:
                    # Проверяем валидность даты
                    datetime.strptime(f"{day}.{month}.{year}", '%d.%m.%Y')
                    return f"{day.zfill(2)}.{month.zfill(2)}.{year}"
                except ValueError:
                    continue
        
        return None
    
    def _extract_buyer(self, text: str) -> Optional[str]:
        """Извлекает информацию о покупателе"""
        original_text = text
        
        # Ищем Telegram username
        username_match = re.search(r'@(\w+)', text)
        if username_match:
            return '@' + username_match.group(1)
        
        # Ищем имена после ключевых слов
        keywords = ['продал', 'продажа', 'клиент', 'покупатель', 'купил', 'заказчик']
        
        for keyword in keywords:
            pattern = rf'{keyword}\s*:?\s*([А-Яа-яA-Za-z0-9\s_-]+?)(?:\s(?:за|в|на|по|крипт|рубл|₽|час|мин)|$|[.!,])'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                buyer = match.group(1).strip()
                if len(buyer) > 1 and not buyer.isdigit():
                    return buyer.title()
        
        # Ищем имена в начале сообщения
        name_match = re.search(r'^([А-Я][а-я]+(?:\s[А-Я][а-я]+)*)', original_text)
        if name_match:
            return name_match.group(1)
        
        # Ищем любые имена собственные
        names = re.findall(r'[А-Я][а-я]+', original_text)
        if names:
            return ' '.join(names[:2])  # Берем первые два слова (имя и фамилия)
        
        return None
    
    def _extract_time(self, text: str) -> Optional[str]:
        """Извлекает время из текста"""
        # Ищем время в формате ЧЧ:ММ
        time_match = re.search(r'(\d{1,2}):(\d{2})', text)
        if time_match:
            hours, minutes = time_match.groups()
            try:
                # Проверяем валидность времени
                hours, minutes = int(hours), int(minutes)
                if 0 <= hours <= 23 and 0 <= minutes <= 59:
                    return f"{hours:02d}:{minutes:02d}"
            except ValueError:
                pass
        
        # Ищем время в других форматах
        hour_match = re.search(r'(?:в\s*)?(\d{1,2})\s*(?:час|ч)', text)
        if hour_match:
            hour = int(hour_match.group(1))
            if 0 <= hour <= 23:
                return f"{hour:02d}:00"
        
        return None
    
    def _extract_payment_format(self, text: str) -> Optional[str]:
        """Извлекает формат оплаты"""
        # Проверяем на криптовалюту
        crypto_keywords = ['крипт', 'crypto', 'btc', 'eth', 'usdt', 'bitcoin', 'ethereum', 'криптовалют']
        for keyword in crypto_keywords:
            if keyword in text:
                return 'Крипта'
        
        # Проверяем на рубли
        rub_keywords = ['рубл', 'руб', '₽', 'rub', 'cash', 'нал', 'наличные', 'перевод']
        for keyword in rub_keywords:
            if keyword in text:
                return 'Рубль'
        
        return None
    
    def _extract_amount(self, text: str) -> Optional[str]:
        """Извлекает сумму из текста"""
        # Ищем числа с валютами
        for pattern in self.amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = match.group(1)
                # Определяем валюту из контекста
                full_match = match.group(0).lower()
                
                if any(currency in full_match for currency in ['usdt', 'usd', 'долл']):
                    return f"{amount} USDT"
                elif any(currency in full_match for currency in ['₽', 'руб', 'рубл', 'р']):
                    return f"{amount} ₽"
                elif any(currency in full_match for currency in ['btc', 'bitcoin']):
                    return f"{amount} BTC"
                elif any(currency in full_match for currency in ['eth', 'ethereum']):
                    return f"{amount} ETH"
                elif any(currency in full_match for currency in ['тысяч', 'к', 'k']):
                    return f"{amount}k ₽"
                else:
                    # Просто число - пытаемся определить валюту из контекста
                    if any(word in text.lower() for word in ['usdt', 'usd', 'долл']):
                        return f"{amount} USDT"
                    elif any(word in text.lower() for word in ['₽', 'руб', 'рубл', 'р', 'наличн']):
                        return f"{amount} ₽"
                    else:
                        return f"{amount} USDT"  # По умолчанию USDT
        
        return None
    
    def _extract_source(self, text: str) -> Optional[str]:
        """Извлекает источник (канал/группу) из текста"""
        # Ищем текст в кавычках
        for pattern in self.source_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        # Если кавычек нет, пытаемся найти источник как текст ПОСЛЕ суммы
        words = text.split()
        # Находим слово с суммой (число+валюта в одном слове: 1488usdt, 5000р и т.п.)
        amount_word_index = -1
        for i, w in enumerate(words):
            lw = w.lower()
            if re.search(r'\d', lw) and any(cur in lw for cur in ['usdt', 'usd', '₽', 'руб', 'btc', 'eth', 'юсдт', 'долл', 'р']):
                amount_word_index = i
                break
        source_tokens = []
        if amount_word_index != -1:
            for w in words[amount_word_index + 1:]:
                lw = w.lower()
                # Отфильтровываем дату/время/валюту/числа/@username
                if (
                    re.fullmatch(r'\d{1,2}\.\d{1,2}(?:\.\d{2,4})?', w) or
                    re.fullmatch(r'\d{3,4}', w) or
                    re.fullmatch(r'\d{1,2}:\d{2}', w) or
                    w.startswith('@') or
                    re.search(r'\d', lw) or
                    any(cur in lw for cur in ['usdt', 'usd', '₽', 'руб', 'btc', 'eth', 'юсдт', 'долл', 'р'])
                ):
                    continue
                # Разрешаем слова с точками/символами (например, Анал.Жесткий)
                if re.search(r'[A-Za-zА-Яа-я]', w):
                    source_tokens.append(w)
            if source_tokens:
                return ' '.join(source_tokens).strip()

        # Фоллбэк: берем последнее слово, если оно похоже на текст источника
        if words:
            last = words[-1]
            ll = last.lower()
            if re.search(r'[A-Za-zА-Яа-я]', last) and not re.search(r'\d', ll) and not any(cur in ll for cur in ['usdt','usd','₽','руб','btc','eth','юсдт','долл','р']):
                return last.strip()
        
        return None
    
    def validate_parsed_data(self, data: Dict[str, Optional[str]]) -> Tuple[bool, str]:
        """
        Проверяет корректность распарсенных данных
        
        Returns:
            Tuple[bool, str]: (валидность, сообщение об ошибке)
        """
        if not data.get('buyer'):
            return False, "Не удалось определить ник покупателя"
        
        if not data.get('amount'):
            return False, "Не удалось определить сумму"
        
        # Источник не обязателен для неформатированного текста
        if not data.get('source'):
            data['source'] = "Не указан"
        
        return True, "Данные корректны"
    
    def _is_unformatted_text(self, text: str) -> bool:
        """Проверяет, является ли текст неформатированным (без запятых, кавычек и т.д.)"""
        # Если есть кавычки, запятые или структурированные слова - это форматированный текст
        if any(char in text for char in ['"', "'", '«', '»', ',', ';']):
            return False
        
        # Если есть ключевые слова структурированного формата (проверяем как отдельные слова)
        # Исключаем короткие предлоги 'на' и 'в', чтобы не ловить их в датах/временах
        structured_words = ['за', 'через', 'сегодня', 'вчера', 'продал', 'клиент', 'покупатель']
        lowered = text.lower()
        if any(re.search(rf"\b{re.escape(word)}\b", lowered) for word in structured_words):
            return False
        
        # Если есть @username и числа - вероятно неформатированный текст
        if '@' in text and re.search(r'\d', text):
            return True
        
        # Дополнительная проверка: если есть числа и валюты без структурированных слов
        if re.search(r'\d', text) and any(currency in text.lower() for currency in ['usdt', 'usd', '₽', 'руб', 'btc', 'eth', 'юсдт', 'долл', 'р']):
            return True
        
        # Проверка на формат: @username дата время суммар источник
        if '@' in text and re.search(r'\d+р\b', text):
            return True
        
        return False
    
    def _parse_unformatted_text(self, text: str) -> Dict[str, Optional[str]]:
        """Парсит неформатированный текст типа '@swagger 15.09 1230 65юсдт биб'"""
        words = text.split()
        result = {
            'buyer': None,
            'datetime': None,
            'amount': None,
            'source': None
        }
        
        # Ищем покупателя (@username)
        buyer = None
        for word in words:
            if word.startswith('@'):
                buyer = word
                break
        
        if not buyer:
            # Если нет @username, ищем имя в начале
            for word in words:
                if word.isalpha() and len(word) > 2:
                    buyer = word
                    break
        
        result['buyer'] = buyer
        
        # Ищем дату (формат ДД.ММ, ДД.ММ.ГГГГ или "12 декабря")
        date = None
        for i, word in enumerate(words):
            # Проверяем формат ДД.ММ или ДД.ММ.ГГГГ
            if re.match(r'\d{1,2}\.\d{1,2}(?:\.\d{2,4})?$', word):
                date = word
                break
            # Проверяем формат "12 декабря"
            elif re.match(r'\d{1,2}$', word) and i + 1 < len(words):
                next_word = words[i + 1].lower()
                if next_word in self.month_names:
                    day = word
                    month_num = self.month_names[next_word]
                    current_year = datetime.now().year
                    date = f"{day}.{month_num:02d}.{current_year}"
                    break
        
        # Ищем время (формат ЧЧММ или ЧЧ:ММ)
        time = None
        for word in words:
            if re.match(r'\d{3,4}$', word):  # 1230, 1430
                time_str = word
                if len(time_str) == 3:
                    time_str = '0' + time_str
                time = f"{time_str[:2]}:{time_str[2:]}"
                break
            elif re.match(r'\d{1,2}:\d{2}$', word):  # 12:30
                time = word
                break
        
        # Формируем datetime
        if date and time:
            # Добавляем год если его нет
            if len(date.split('.')) == 2:
                current_year = datetime.now().year
                date = f"{date}.{current_year}"
            result['datetime'] = f"{date} {time}"
        elif date:
            result['datetime'] = f"{date} {datetime.now().strftime('%H:%M')}"
        elif time:
            result['datetime'] = f"{datetime.now().strftime('%d.%m.%Y')} {time}"
        else:
            result['datetime'] = datetime.now().strftime('%d.%m.%Y %H:%M')
        
        # Ищем сумму (число + валюта)
        amount = None
        for i, word in enumerate(words):
            # Пропускаем @username и даты/время
            if word.startswith('@') or re.match(r'\d{1,2}\.\d{1,2}(?:\.\d{2,4})?$', word) or re.match(r'\d{3,4}$', word) or re.match(r'\d{1,2}:\d{2}$', word):
                continue
            
            # Сначала проверяем, есть ли в слове валюта (например, 5000р)
            if any(currency in word.lower() for currency in ['usdt', 'usd', '₽', 'руб', 'btc', 'eth', 'юсдт', 'долл', 'р']):
                # Извлекаем число из слова с валютой
                number_match = re.search(r'(\d+(?:[.,]\d+)?)', word)
                if number_match:
                    number = number_match.group(1)
                    if any(currency in word.lower() for currency in ['usdt', 'usd', 'юсдт', 'долл']):
                        amount = f"{number} USDT"
                    elif any(currency in word.lower() for currency in ['₽', 'руб', 'р']):
                        amount = f"{number} ₽"
                    elif 'btc' in word.lower():
                        amount = f"{number} BTC"
                    elif 'eth' in word.lower():
                        amount = f"{number} ETH"
                    else:
                        amount = f"{number} USDT"
                    break
            # Если в слове нет валюты, ищем число
            elif re.match(r'\d+(?:[.,]\d+)?$', word):
                # Проверяем следующее слово на валюту
                if i + 1 < len(words):
                    next_word = words[i + 1].lower()
                    if any(currency in next_word for currency in ['usdt', 'usd', '₽', 'руб', 'btc', 'eth', 'юсдт', 'долл']):
                        # Определяем валюту
                        if any(currency in next_word for currency in ['usdt', 'usd', 'юсдт', 'долл']):
                            amount = f"{word} USDT"
                        elif any(currency in next_word for currency in ['₽', 'руб']):
                            amount = f"{word} ₽"
                        elif 'btc' in next_word:
                            amount = f"{word} BTC"
                        elif 'eth' in next_word:
                            amount = f"{word} ETH"
                        else:
                            amount = f"{word} USDT"  # По умолчанию
                        break
        
        result['amount'] = amount
        
        # Ищем источник (слова после суммы, которые не являются числами, валютами или датами)
        source = None
        source_words = []
        
        # Находим индекс суммы, чтобы искать источник после неё
        amount_index = -1
        if amount:
            amount_number = amount.split()[0]
            for i, word in enumerate(words):
                # Проверяем точное совпадение или если слово содержит число суммы
                if word == amount_number or (amount_number in word and re.search(r'\d', word)):
                    amount_index = i
                    break
        
        # Если сумма найдена, ищем источник после неё
        if amount_index >= 0:
            for i in range(amount_index + 1, len(words)):
                word = words[i]
                # Проверяем, что это не число, валюта, дата, время или @username
                if (not re.match(r'^\d+$', word) and 
                    not any(currency in word.lower() for currency in ['usdt', 'usd', '₽', 'руб', 'btc', 'eth', 'юсдт', 'долл', 'р']) and
                    not re.match(r'\d{1,2}\.\d{1,2}(?:\.\d{2,4})?$', word) and
                    not re.match(r'\d{3,4}$', word) and
                    not re.match(r'\d{1,2}:\d{2}$', word) and
                    not word.startswith('@')):
                    source_words.append(word)
        
        # Если источник не найден после суммы, ищем в конце
        if not source_words:
            for word in reversed(words):
                if (not re.match(r'^\d+$', word) and 
                    not any(currency in word.lower() for currency in ['usdt', 'usd', '₽', 'руб', 'btc', 'eth', 'юсдт', 'долл', 'р']) and
                    not re.match(r'\d{1,2}\.\d{1,2}(?:\.\d{2,4})?$', word) and
                    not re.match(r'\d{3,4}$', word) and
                    not re.match(r'\d{1,2}:\d{2}$', word) and
                    not word.startswith('@') and
                    word != buyer):
                    source_words.append(word)
                    break
        
        if source_words:
            source = ' '.join(source_words)
        
        result['source'] = source
        
        return result
