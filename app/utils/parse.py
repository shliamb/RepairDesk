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






def detect_search_field_order(text: str) -> tuple[str, str]:
    text = text.strip()
    
    # 1. Номер заказа
    order_pattern = r'^([A-Z]{2})-(\d{4})-(\d{4})$'
    order_match = re.match(order_pattern, text, re.IGNORECASE)
    if order_match:
        prefix, year, num = order_match.groups()
        return 'order_number', f"{prefix.upper()}-{year}-{num}"
    
    # 2. Только цифры номера
    if re.match(r'^\d{1,4}$', text):
        return 'order_number_suffix', text.zfill(4)
    
    # 3. Проверка на бренд ВНАЧАЛЕ (самый важный!)
    brands = [
            # Ноутбуки/ПК
            'asus', 'acer', 'lenovo', 'hp', 'dell', 'msi', 'toshiba', 'fujitsu',
            'panasonic', 'samsung', 'lg', 'sony', 'vaio', 'medion', 'packard bell',
            'chuwi', 'huawei', 'xiaomi', 'microsoft', 'surface', 'razer', 'alienware',
            
            # Видеокарты
            'nvidia', 'geforce', 'amd', 'radeon', 'gigabyte', 'asus', 'msi', 'zotac',
            'palit', 'gainward', 'sapphire', 'powercolor', 'xfx', 'evga', 'pny',
            'kfa2', 'inno3d', 'leadtek', 'maxsun',
            
            # Телефоны/планшеты
            'apple', 'iphone', 'ipad', 'samsung', 'galaxy', 'huawei', 'honor',
            'xiaomi', 'redmi', 'poco', 'realme', 'oppo', 'vivo', 'oneplus',
            'motorola', 'nokia', 'sony', 'xperia', 'lg', 'google', 'pixel',
            'htc', 'blackberry', 'zte', 'meizu', 'alcatel', 'tecno', 'infinix',
            
            # Комплектующие ПК
            'intel', 'amd', 'ryzen', 'core i', 'pentium', 'celeron', 'athlon',
            'asus', 'gigabyte', 'asrock', 'msi', 'biostar', 'evga',
            'kingston', 'crucial', 'samsung', 'wd', 'seagate', 'toshiba',
            'corsair', 'g.skill', 'hyperx', 'teamgroup', 'adata',
            'cooler master', 'be quiet', 'noctua', 'arctic', 'thermalright',
            
            # Мониторы
            'dell', 'asus', 'acer', 'samsung', 'lg', 'philips', 'benq', 'viewsonic',
            'aoc', 'msi', 'gigabyte', 'huawei',
            
            # Периферия
            'logitech', 'razer', 'steelseries', 'hyperx', 'corsair', 'asus rog',
            'msi', 'dell', 'hp', 'lenovo', 'microsoft', 'apple', 'samsung',
            
            # Игровые консоли
            'sony', 'playstation', 'microsoft', 'xbox', 'nintendo', 'switch',
            
            # Сетевое оборудование
            'tp-link', 'd-link', 'asus', 'xiaomi', 'huawei', 'ubiquiti', 'mikrotik',
            'cisco', 'netgear', 'zyxel',
            
            # Прочее
            'dyson', 'bosch', 'philips', 'braun', 'remington', 'panasonic',
            'lg', 'samsung', 'sony', 'canon', 'epson', 'hp', 'brother'
        ]
    
    text_lower = text.lower()
    for brand in brands:
        if brand in text_lower:
            # Удаляем бренд из текста, оставляем только модель
            model_text = re.sub(r'\b' + re.escape(brand) + r'\b', '', text_lower, flags=re.IGNORECASE)
            model_text = re.sub(r'\s+', ' ', model_text).strip()  # Убираем лишние пробелы
            if model_text:
                return 'device_model', model_text.title()  # Первые буквы заглавные
            else:
                # Если только бренд без модели
                return 'device_model', text
        
    
    # 4. Серийник/IMEI (только если нет пробелов и содержит буквы+цифры)
    if ' ' not in text:
        serial_clean = re.sub(r'[^A-Z0-9]', '', text.upper())
        if (len(serial_clean) >= 8 and 
            re.match(r'^[A-Z0-9]+$', serial_clean) and
            not re.match(r'^\d+$', serial_clean)):  # не только цифры
            return 'sn_imei', text.upper()
    
    # 5. По умолчанию - проблема
    return 'problem', text[:100]

