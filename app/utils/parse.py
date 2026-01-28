import re
# from utils.formatters import format_phone





def format_phone_parse(phone_str: str, country_code: str = "7") -> str:
    """Нормализации телефона"""
    digits = re.sub(r'\D', '', phone_str)
    if digits.startswith('8'):
        digits = country_code + digits[1:]
    if digits.startswith(country_code) and len(digits) == 11:
        return f"+{country_code} ({digits[1:4]}) {digits[4:7]}-{digits[7:9]}-{digits[9:]}"
    raise ValueError("Invalid phone number")


def detect_search_field(
    input_str: str,
    country_code: str = "7",
    min_phone_digits: int = 10,
    require_at_for_telegram: bool = True
) -> tuple[str, str]:
    """
    Определяет поле для поиска клиента.
    
    Args:
        input_str: Ввод пользователя
        country_code: Код страны по умолчанию (7 для РФ)
        min_phone_digits: Минимальное количество цифр для телефона
        require_at_for_telegram: Обязателен ли @ для Telegram username
    
    Returns:
        tuple: (field_name, normalized_value)
    """
    text = input_str.strip()
    
    # 1. Проверка на телефон
    digits = re.sub(r'\D', '', text)
    if len(digits) >= min_phone_digits:
        try:
            normalized = format_phone_parse(text, country_code)
            return 'phone', normalized
        except Exception:
            # Если format_phone не смог нормализовать, продолжаем
            pass
    
    # 2. Проверка на Telegram
    if require_at_for_telegram:
        if text.startswith('@'):
            username = text[1:].strip()
            if username:  # Не пустой после @
                return 'username_telegram', username
    else:
        # Без обязательного @ проверяем по паттерну
        if text.startswith('@'):
            username = text[1:].strip()
            if username:
                return 'username_telegram', username
        elif re.fullmatch(r'[a-zA-Z0-9_]{5,32}', text):
            return 'username_telegram', text
    
    # 3. По умолчанию - имя
    return 'name', text