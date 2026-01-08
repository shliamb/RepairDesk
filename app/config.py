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


# NEW ORDER
# BRANDS

DEVICES_RU = ["💻 Ноутбук", "🖥 ПК", "Телефон", "Видеокарта", "Материнская плата", "Монитор", "Планшет", "Принтер", "Игровая консоль", "📝 Свой вариант"]
DEVICES_EN = ["💻 Laptop", "🖥 PC", "Phone", "Gpu", "Motherboard", "Monitor", "Tablet", "Printer", "Console", "📝 Your own version"]

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
    "Телефон": PHONE_BRANDS,
    "Видеокарта": GPU_BRANDS,
    "Материнская плата": MOTHERBOARD_BRANDS,
    "Монитор": MONITOR_BRANDS,
    "Планшет": TABLET_BRANDS,
    "Принтер": PRINTER_BRANDS,
    "Игровая консоль": CONSOLE_BRANDS
}

DEVICE_BRANDS_EN = {
    "💻 Laptop": LAPTOP_BRANDS,
    "🖥 PC": PC,
    "Phone": PHONE_BRANDS,
    "Gpu": GPU_BRANDS,
    "Motherboard": MOTHERBOARD_BRANDS,
    "Monitor": MONITOR_BRANDS,
    "Tablet": TABLET_BRANDS,
    "Printer": PRINTER_BRANDS,
    "Console": CONSOLE_BRANDS
}


def has_cyrillic_simple(devise: str) -> bool:
    for ch in devise:
        if 'А' <= ch <= 'я':  # русские буквы
            return True
    return False

def get_brands(devise: str) -> list:
    if not devise:
        return ["Another"]
    elif has_cyrillic_simple(devise):
        return DEVICE_BRANDS_RU.get(devise, ["Другой"])
    else:
        return DEVICE_BRANDS_EN.get(devise, ["Another"])

# print(get_brands("💻 Laptop"))

EQUIPMENT_RU = ["Устройство", "Зарядка", "Пакет", "Сумка"]






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

