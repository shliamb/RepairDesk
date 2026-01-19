#! app/utils/formatters.py
import re
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation



def remove_emojis(text: str) -> str:
    """Удаляет эмодзи и лишние пробелы в начале/конце"""
    import re
    cleaned = re.sub(r'[^\w\s,.!?;:()\-@#%&*+=/\\|"\'<>$€£¥₹₽]', '', str(text))
    return cleaned.strip()


def format_phone(phone):
    """Форматирует телефон в красивый вид: +7 (999) 954-43-32"""
    if not phone:
        return ""
    phone = str(phone).replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    if len(phone) == 11 and phone.startswith('8'):
        phone = '7' + phone[1:]
    if len(phone) == 11 and phone.startswith('7'):
        return f"+7 ({phone[1:4]}) {phone[4:7]}-{phone[7:9]}-{phone[9:]}"
    return phone


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


# def safe_decimal(value) -> Decimal | None:
#     """Безопасное преобразование в Decimal."""
#     try:
#         if isinstance(value, (Decimal, int, float)):
#             num = Decimal(str(value))
#         else:
#             num = Decimal(str(value).strip())
        
#         # Абсолютное значение
#         num = num.copy_abs()
        
#         return num
#     except (InvalidOperation, ValueError, TypeError, AttributeError):
#         return None


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