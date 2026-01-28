#! app/utils/formatters.py
import re
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation







def clean_user_input(text: str) -> str:
    """
    Очищает ввод, но оставляет запятые, точки, дефисы для имён.
    """
    # Удаляем только действительно опасные для SQL/инъекций
    sql_dangerous = [';', '--', '/*', '*/', "'", '"', '`', '=', '%']
    
    for char in sql_dangerous:
        text = text.replace(char, ' ')
    
    # Оставляем нормальные знаки препинания
    text = re.sub(r'\s+', ' ', text)  # Множественные пробелы
    return text.strip()



def remove_emojis(text: str) -> str:
    """Удаляет эмодзи и лишние пробелы в начале/конце"""
    import re
    cleaned = re.sub(r'[^\w\s,.!?;:()\-@#%&*+=/\\|"\'<>$€£¥₹₽]', '', str(text))
    return cleaned.strip()


def extract_emoji(text: str) -> str:
    """Вырезает всё, кроме эмодзи (предполагая, что он там есть)"""
    cleaned = ''.join([c for c in str(text) if not c.isalnum() and not c.isspace()])
    # Удаляем оставшиеся знаки препинания (опционально)
    import string
    for punct in string.punctuation:
        cleaned = cleaned.replace(punct, '')
    return cleaned


COUNTRY_CODE = '7'
PHONE_LENGTH = 11
LEGACY_CODE = '8'

def format_phone(phone):
    if not phone:
        return None
    
    phone = ''.join(c for c in str(phone) if c.isdigit())
    
    if phone.startswith(LEGACY_CODE) and len(phone) == PHONE_LENGTH:
        phone = COUNTRY_CODE + phone[1:]
    
    if len(phone) == PHONE_LENGTH - 1:
        phone = COUNTRY_CODE + phone
    
    if len(phone) == PHONE_LENGTH and phone.startswith(COUNTRY_CODE):
        return f"+{COUNTRY_CODE} ({phone[1:4]}) {phone[4:7]}-{phone[7:9]}-{phone[9:]}"
    
    return None



def format_date_nice(dt_str, lang):
    """Преобразует дату из строки в красивый формат"""
    try:
        # Если dt_str уже datetime
        if hasattr(dt_str, 'strftime'):
            dt = dt_str
        else:
            # Парсим строку
            dt = datetime.strptime(dt_str, "%d.%m.%y %H:%M")
        
        if lang == "ru":
            months = {
                1: "января", 2: "февраля", 3: "марта", 4: "апреля",
                5: "мая", 6: "июня", 7: "июля", 8: "августа",
                9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
            }
            return f"{dt.day} {months[dt.month]} {dt.year}, {dt.strftime('%H:%M')}"
        else:
            months = {
                1: "January", 2: "February", 3: "March", 4: "April",
                5: "May", 6: "June", 7: "July", 8: "August",
                9: "September", 10: "October", 11: "November", 12: "December"
            }
            return f"{dt.strftime('%d')} {months[dt.month]} {dt.year}, {dt.strftime('%H:%M')}"
            
    except:
        return dt_str  # Возвращаем как есть, если ошибка
    

def parse_cost(cost_text: str) -> Decimal:
    """Из '1000 RUB' → Decimal(1000.00)"""
    digits = ''.join(ch for ch in cost_text if ch.isdigit() or ch == '.')
    return Decimal(digits) if digits else Decimal('0')


def add_days_from_text(text: str) -> datetime:
    """Извлекает число дней из текста диагностики, возвращает дату ~ диагностики """
    date = datetime.now()
    days = int(re.search(r'\d+', text).group()) if re.search(r'\d+', text) else 0
    new_date = date + timedelta(days=days) if days > 0 else date
    day_str = new_date.strftime("%Y-%m-%d %H:%M:%S")
    return datetime.strptime(day_str, '%Y-%m-%d %H:%M:%S')


def format_telegram_username(username: str) -> str | None:
    """Форматирует имя пользователя Telegram: добавляет @ если нужно"""
    if not username:
        return None
    
    # Убираем пробелы и уже существующий @
    username = username.strip().lstrip('@')
    
    if username:  # если после очистки что-то осталось
        return f"@{username}"
    return None


# Правильная safe_decimal
def safe_decimal(value) -> Decimal | None:
    """Безопасное преобразование в Decimal."""
    try:
        if isinstance(value, Decimal):
            return value
        elif isinstance(value, (int, float, str)):
            return Decimal(str(value))
        else:
            return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError, AttributeError):
        return None



def safe_int(value, only_positive: bool = True) -> int | None:
    """ Из str в INT """
    try:
        if isinstance(value, (int, float)):
            num = int(value)
        else:
            num = int(str(value).strip())
        
        if only_positive:
            num = abs(num)
        
        return num
    except (ValueError, TypeError, AttributeError):
        return None
    

def safe_float(value) -> float | None:
    """ Из str в Float"""
    try:
        if isinstance(value, (float, int)):
            num = float(value)
        else:
            num = float(str(value).strip())
        
        num = abs(num)
        
        return num
    except (ValueError, TypeError, AttributeError):
        return None
    






# # Настройки телефонов
# PHONE_COUNTRY_CODE = '7'           # Код страны
# PHONE_TOTAL_LENGTH = 11            # Всего цифр (с кодом)
# PHONE_LEGACY_CODE = '8'            # Устаревший код (опционально)
# PHONE_FORMAT_TEMPLATE = "+{0} ({1}) {2}-{3}-{4}"  # Шаблон форматирования
# PHONE_FORMAT_GROUPS = [1, 3, 3, 2, 2]  # Группировка цифр после кода


# def format_phone(phone):
#     if not phone:
#         return None
    
#     phone = ''.join(c for c in str(phone) if c.isdigit())
    
#     # Замена легаси
#     if PHONE_LEGACY_CODE and phone.startswith(PHONE_LEGACY_CODE) and len(phone) == PHONE_TOTAL_LENGTH:
#         phone = PHONE_COUNTRY_CODE + phone[1:]
    
#     # Добавление кода страны
#     if len(phone) == PHONE_TOTAL_LENGTH - len(PHONE_COUNTRY_CODE):
#         phone = PHONE_COUNTRY_CODE + phone
    
#     # Валидация
#     if len(phone) != PHONE_TOTAL_LENGTH or not phone.startswith(PHONE_COUNTRY_CODE):
#         return None
    
#     # Форматирование по группам
#     parts = [PHONE_COUNTRY_CODE]
#     idx = len(PHONE_COUNTRY_CODE)
#     for group_len in PHONE_FORMAT_GROUPS[1:]:  # Пропускаем первую (код страны)
#         parts.append(phone[idx:idx + group_len])
#         idx += group_len
    
#     return PHONE_FORMAT_TEMPLATE.format(*parts)
