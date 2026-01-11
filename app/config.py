import os
from dotenv import load_dotenv
load_dotenv()



#### BASIC CONFIG (set it up manually): ####
DOCKER = False 
LOG_TO_FILE = False
HOST = "app_postgres" if DOCKER else  "localhost" # app_postgres localhost
TIME_CORRECTION = + 3
MAX_SIZE_DOC = 2 # 2 мегабайт
########


# Folders:
PATH_LOGS = "/logs" if DOCKER else "logs"
#PATH_LOGS = "/logs/" if DOCKER else "../logs/"
# DOWNLOAD = "/downloads/" if DOCKER else "../downloads/"
# PATH_JSON_USERS = "/json/" if DOCKER else "../json/"
# OUTPUT = "/output/" if DOCKER else "../output/"
# SYST_CONT_FOLDER = "/" if DOCKER else "../"


################ NEW ORDER #####################


PROBLEMS = {"ru": ["Не включается", "Не заряжается", "Нет изображения", "Греется", "Шумит", "Тормозит", "Зависает"], "en": ["Won't turn on", "Won't charge", "No image", "Heats up", "Makes noise", "Slows down", "Freezes"]}
CANCEL =  {"ru": "🚫 Отмена", "en": "🚫 Cancellation"}
ORDER = {"new_ru": "📝 Новый заказ", "new_en": "📝 New order"}
CLIENT = {"new_ru": "👨🏻‍💼 Создать клиента", "new_en": "👨🏻‍💼 Create a client", "serch_ru": "🔎 Найти клиента", "serch_en": "🔎 Find a client"}
MISS = {"ru": "🎲 Пропустить", "en": "🎲 Miss"}
TYPE_ORDER = {"paid_ru": "🤑 Платный", "guarant_ru": "🤬 Гарантийный", "paid_en": "🤑 Paid", "guarant_en": "🤬 Warranty period"}
DONE = {"ru": "✅ Готово", "en": "✅ Done"}
OWN_VERSION = {"ru": "📝 Свой вариант", "en": "📝 Your own version"}
EQUIPMENT = {"ru": ["Устройство", "Зарядка", "Пакет", "Сумка", "Кошка", "Ребенок"], "en": ["Device", "Charging", "Package", "Bag", "Cat", "Child"]} # Комплектация
APPEARANCE = {"ru": ["Потёртости", "Царапины", "Сколы"], "en": ["Scuffs", "Scratches", "Chips"]}
DIAGNOSTIC_TIME = {"ru": ["Без диагностики", "1 день", "2 дня", "3 дня", "Без ограничений"], "en": ["No diagnosis", "1 day", "2 days", "3 days", "Unlimited"]}
COST_DIAGNOSTIC = {"ru": ["1000 RUB", "0 RUB", "2000 RUB", "2500 RUB"], "en": ["1000 RUB", "0 RUB", "2000 RUB", "2500 RUB"]}

LAPTOP_BRANDS = ["Asus", "Lenovo", "HP", "Dell", "Acer", "Apple", "MSI", "Toshiba", "Sony", "LG", "Microsoft", "Fujitsu", "Alienware", "Razer", "DEXP", "IRU", "Huawei", "Xiaomi", "Honor", "Samsung", "Prestigio", "DNS"]
PHONE_BRANDS = ["Samsung", "Apple", "Xiaomi", "Huawei", "Honor", "Realme", "Vivo", "Oppo", "OnePlus", "Nokia", "Sony", "Google", "ZTE", "Motorola", "Alcatel", "Philips", "Texet", "BQ", "Meizu", "Asus"]
GPU_BRANDS = ["NVIDIA", "AMD", "Asus", "MSI", "Gigabyte", "Palit", "Zotac", "Sapphire", "PowerColor", "EVGA", "ASRock", "KFA2", "PNY", "Inno3D", "Gainward"]
MOTHERBOARD_BRANDS = ["Asus", "MSI", "Gigabyte", "ASRock", "Biostar", "Intel", "HP", "Dell", "Lenovo", "Acer"]
MONITOR_BRANDS = ["Samsung", "LG", "Asus", "Acer", "BenQ", "Dell", "HP", "MSI", "ViewSonic", "Philips", "AOC", "Huawei", "Xiaomi"]
TABLET_BRANDS = ["Apple", "Samsung", "Lenovo", "Huawei", "Xiaomi", "Asus", "Microsoft", "Amazon", "Prestigio", "DNS"]
PRINTER_BRANDS = ["HP", "Canon", "Epson", "Brother", "Xerox", "Kyocera", "Ricoh", "Samsung", "Pantum", "Lexmark"]
CONSOLE_BRANDS = ["Sony", "Microsoft", "Nintendo", "Sega", "Atari"]
PC = ["PC"]

DEVICE_BRANDS_RU = {
    "💻 Ноутбук": LAPTOP_BRANDS,
    "🖥 ПК": PC,
    # "Телефон": PHONE_BRANDS, # Комментирую если не использую
    "Видеокарта": GPU_BRANDS,
    "Материнская плата": MOTHERBOARD_BRANDS,
    # "Монитор": MONITOR_BRANDS,
    "Планшет": TABLET_BRANDS,
    # "Принтер": PRINTER_BRANDS,
    "Игровая консоль": CONSOLE_BRANDS
}

DEVICE_BRANDS_EN = {
    "💻 Laptop": LAPTOP_BRANDS,
    "🖥 PC": PC,
    # "Phone": PHONE_BRANDS,
    "Gpu": GPU_BRANDS,
    "Motherboard": MOTHERBOARD_BRANDS,
    # "Monitor": MONITOR_BRANDS,
    "Tablet": TABLET_BRANDS,
    # "Printer": PRINTER_BRANDS,
    "Console": CONSOLE_BRANDS
}

def get_devices(DEVICES) -> list:
    return list(DEVICES.keys())

DEVICES_RU = get_devices(DEVICE_BRANDS_RU)
DEVICES_EN = get_devices(DEVICE_BRANDS_EN)

def has_cyrillic_simple(devise: str) -> bool:
    for ch in devise:
        if 'А' <= ch <= 'я':  # русские буквы
            return True
    return False

def get_brands(device: str) -> list:
    if not device:
        return ["Another"]
    
    if has_cyrillic_simple(device):
        return DEVICE_BRANDS_RU.get(device, ["Другой"]).copy()
    else:
        return DEVICE_BRANDS_EN.get(device, ["Another"]).copy()




PREFIXES = {
    'guarant': 'GR',    # гарантийный
    'paid': 'PD',       # платный
    'express': 'EX',    # срочный
    'general': 'GE'     # Если что то пошло не так..  
}

# Номера: GR-2024-0001, PD-2024-0001, EX-2024-0001


# .env:
TELEGRAM_BOT_TOKEN = os.environ.get('telegram_bot_token')
USER_DB = os.environ.get('USER_DB')
PASSWORD_DB = os.environ.get('PASSWORD_DB')
DB_NAME = os.environ.get('POSTGRES_DB')
ADMIN_ID = int(os.environ.get('admin_id'))
KEY_API_DEEPSEEK = os.environ.get('key_api_deepseek')








# class Settings(BaseSettings):
#     BOT_TOKEN: str
#     ADMINS: list[int] = []
#     DB_HOST: str = "localhost"
#     DB_PORT: int = 5432
#     DB_NAME: str
#     DB_USER: str
#     DB_PASS: str
    
#     class Config:
#         env_file = ".env"

# settings = Settings()

