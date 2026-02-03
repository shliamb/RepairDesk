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
# PATH_LOGS = "/logs/" if DOCKER else "../logs/"
DOWNLOAD = "/downloads/" if DOCKER else "downloads"
PATH_JSON = "/json/" if DOCKER else "json"
# OUTPUT = "/output/" if DOCKER else "../output/"
# SYST_CONT_FOLDER = "/" if DOCKER else "../"


################ NEW ORDER CONST #####################

# STATUS_ORDER = ["new", "diagnosis", "repair", "waiting_parts", "testing" 
#                 "ready", "completed", "canceled", "rejected", "postponed"]

ORDER_STATUS_RU = {
    'new': 'Новый',
    'diagnosis': 'Диагностика',
    'repair': 'В ремонте',
    'waiting_parts': 'Ожидающие запчасти',
    'waiting_decision': 'Ожидание решения',
    'testing': 'На тестах',
    'ready': 'Готов',
    'issued': 'Выдан',
    'issued_not_paid': 'Выдан, но не оплачен',
    'paid_not_issued': 'Оплачен но не выдан',
    'cancelled': 'Отказ от ремонта',
    'unsuccessful_repair': 'Неудачный ремонт'
}

ORDER_STATUS = {
    'new': 'New',
    'diagnosis': 'Diagnostics',
    'repair': 'In repair',
    'waiting_parts': 'Pending parts',
    'waiting_decision': 'Waiting a decision',
    'testing': 'Testing',
    'ready': 'Ready',
    'issued': 'Issued',
    'issued_not_paid': 'Issued, not paid',
    'paid_not_issued': 'Paid, not issued',
    'cancelled': 'Refusal to repair',
    'unsuccessful_repair': 'Unsuccessful repair'
}

# Активные = все кроме ready, completed, canceled, rejected
NEW = ["new"]
ACTIVE_STATUSES = ["new", "diagnosis", "repair", "waiting_parts", "waiting_decision", "testing", "ready", "issued_not_paid"]
IN_PROGRESS_STATUSES = ["testing", "repair", "diagnostics", "waiting_parts"]
READY_STATUSES = ["ready", "paid_not_issued"]
COMPLETED_STATUSES = ["issued"]



ORDER_STATUS_COLOR = {
    'new': '🟢',
    'diagnosis': '🟡',
    'repair': '🟠',
    'waiting_parts': '⏳',
    'waiting_decision': '🤔',
    'testing': '🔵',
    'ready': '🟣',
    'issued': '📤',
    'issued_not_paid': '💸',
    'paid_not_issued': '💰',
    'cancelled': '❌',
    'unsuccessful_repair': '🚫'
}

HUMAN_QUALITY = {
    "ru": {
        "excellent": "😍 Отличный",
        "good": "🙂 Хороший",
        "normal": "😐 Нормальный",
        "bad": "😠 Проблемный",
        "terrible": "🤬 Ужасный"
    },
    "en": {
        "excellent": "😍 Excellent",
        "good": "🙂 Good",
        "normal": "😐 Normal",
        "bad": "😠 Troublesome",
        "terrible": "🤬 Terrible"
    }
}


UI_TEXTS = {
    "ru": {
        "yes": "👍 Да", 
        "no": "👎 Нет", 
        "miss": "⏩ Пропустить", 
        "cancel": "🚫 Отмена", 
        "done": "✅ Готово",
        "new_cli": "👨🏻‍💼 Создать клиента",
        "role": "👥 Роль",
        "contact": "📋 Контактные данные",
        "status": "⭐ Рейтинг и статус",
        "accdevice": "📦 Принять устройство",
        "qserv": "⚡ Быстрая услуга",
        "serch_cli": "🔎 Найти клиента",
        "serch_order": "🔎 Найти заказ",
        "open": "📂 Открыть",
        "new_order": "📝 Новый заказ",
        "ready_orders": "✅ Готовые",
        "last_orders": "📋 Последние 30",
        "stat": "📊 Статистика",
        "activ_orders": "📋 Активные заказы",
        "in_work_orders": "🔧 В работе",
        "get_photo": "📸 Фото",
        "get_pdf": "📄 PDF",
        "payd": "📤 Выдать заказ",
        "order": "📋 Заказ",
        "client": "🙋 Клиент",
        "status": "📊 Статус",
        "card": "💳 Перевод",
        "cash": "💵 Наличность",
        "crypto": "₿ Крипта",
        "no_payment": "🆓 Без оплаты"
    },
    "en": {
        "yes": "👍 Yes", 
        "no": "👎 No", 
        "miss": "⏩ Miss", 
        "cancel": "🚫 Cancellation", 
        "done": "✅ Done",
        "new_cli": "👨🏻‍💼 Create a client",
        "role": "👥 User role",
        "contact": "📋 Contact info",
        "status": "⭐ Rating & status",
        "accdevice": "📦 Accept device",
        "qserv": "⚡ Quick service",
        "serch_cli": "🔎 Find a client",
        "serch_order": "🔎 Search Order",
        "open": "📂 Open",
        "new_order": "📝 New order",
        "ready_orders": "✅ Ready",
        "last_orders": "📋 Last 30",
        "stat": "📊 Statistics",
        "activ_orders": "📋 Active orders",
        "in_work_orders": "🔧 In progress",
        "get_photo": "📸 Photo",
        "get_pdf": "📄 PDF",
        "payd": "📤 Hand Over",
        "order": "📋 Order",
        "client": "🙋 Client",
        "status": "📊 Status",
        "card": "💳 Card / Transfer",
        "cash": "💵 Cash",
        "crypto": "₿ Crypto",
        "no_payment": "🆓 No payment"

    },
}



PROBLEMS = {"ru": ["Не включается", "Не заряжается", "Нет изображения", "Греется", "Шумит", "Тормозит", "Зависает"], "en": ["Won't turn on", "Won't charge", "No image", "Heats up", "Makes noise", "Slows down", "Freezes"]}
CANCEL =  {"ru": "🚫 Отмена", "en": "🚫 Cancellation"}
ORDER = {"new_ru": "📝 Новый заказ", "new_en": "📝 New order", "activ_ru": "📋 Активные заказы", "activ_en": "📋 Active orders", "in_work_ru": "🔧 В работе", "in_work_en": "🔧 In progress", "ready_ru": "✅ Готовые", "ready_en": "✅ Ready", "stat_ru": "📊 Статистика", "stat_en": "📊 Statistics", "last_ru": "📋 Последние 30", "last": "📋 Last 30"}

CLIENT = {"new_ru": "👨🏻‍💼 Создать клиента", "new_en": "👨🏻‍💼 Create a client", 
            "serch_ru": "🔎 Найти клиента", "serch_en": "🔎 Find a client", "qserv_ru": "⚡ Быстрая услуга", 
            "qserv": "⚡ Quick service", "accdevice_ru": "📦 Принять устройство", 
            "accdevice": "📦 Accept device", "contact_ru": "📋 Контактные данные", "contact": "📋 Contact info",
            "role_ru": "👥 Роль", "role": "👥 User role", "status_ru": "⭐ Рейтинг и статус", "status": "⭐ Rating & status"}

MISS = {"ru": "🎲 Пропустить", "en": "🎲 Miss"}
TYPE_ORDER = {"paid_ru": "🤑 Платный", "guarant_ru": "🤬 Гарантийный", "paid_en": "🤑 Paid", "guarant_en": "🤬 Warranty period"}
DONE = {"ru": "✅ Готово", "en": "✅ Done"}
OWN_VERSION = {"ru": "📝 Свой вариант", "en": "📝 Your own version"}
EQUIPMENT = {"ru": ["Устройство", "Зарядка", "Пакет", "Сумка", "Кошка", "Ребенок"], "en": ["Device", "Charging", "Package", "Bag", "Cat", "Child"]} # Комплектация
APPEARANCE = {"ru": ["Потёртости", "Царапины", "Сколы"], "en": ["Scuffs", "Scratches", "Chips"]}
DIAGNOSTIC_TIME = {"ru": ["Без диагностики", "1 день", "2 дня", "3 дня", "Без ограничений"], "en": ["No diagnosis", "1 day", "2 days", "3 days", "Unlimited"]}
COST_DIAGNOSTIC = {"ru": ["1000 RUB", "0 RUB", "2000 RUB", "2500 RUB"], "en": ["1000 RUB", "0 RUB", "2000 RUB", "2500 RUB"]}
VIEW_ORDER = {"change_ru": "📂 Открыть", "change_en": "📂 Open", "action_ru": "⚡ Действия", "action_en": "⚡ Actions"}
CHANGE_ORDER = {"order_ru": "📋 Заказ", "order_en": "📋 Order", "client_ru": "🙋 Клиент", "client_en": "🙋 Client", "status_ru": "📊 Статус", "status_en": "📊 Status"}
ACTION_ORDER = {"get_photo_ru": "📸 Фото", "get_photo_en": "📸 Photo", "get_pdf_ru": "📄 PDF", "get_pdf_en": "📄 PDF", "issue_ru": "📤 Выдать заказ", "issue_en": "📤 Hand Over"}

LAPTOP_BRANDS = ["Asus", "Lenovo", "HP", "Dell", "Acer", "Apple", "MSI", "Toshiba", "Sony", "LG", "Microsoft", "Fujitsu", "Alienware", "Razer", "DEXP", "IRU", "Huawei", "Xiaomi", "Honor", "Samsung", "Prestigio", "DNS"]
PHONE_BRANDS = ["Samsung", "Apple", "Xiaomi", "Huawei", "Honor", "Realme", "Vivo", "Oppo", "OnePlus", "Nokia", "Sony", "Google", "ZTE", "Motorola", "Alcatel", "Philips", "Texet", "BQ", "Meizu", "Asus"]
GPU_BRANDS = ["NVIDIA", "AMD", "Asus", "MSI", "Gigabyte", "Palit", "Zotac", "Sapphire", "PowerColor", "EVGA", "ASRock", "KFA2", "PNY", "Inno3D", "Gainward"]
MOTHERBOARD_BRANDS = ["Asus", "MSI", "Gigabyte", "ASRock", "Biostar", "Intel", "HP", "Dell", "Lenovo", "Acer"]
MONITOR_BRANDS = ["Samsung", "LG", "Asus", "Acer", "BenQ", "Dell", "HP", "MSI", "ViewSonic", "Philips", "AOC", "Huawei", "Xiaomi"]
TABLET_BRANDS = ["Apple", "Samsung", "Lenovo", "Huawei", "Xiaomi", "Asus", "Microsoft", "Amazon", "Prestigio", "DNS"]
PRINTER_BRANDS = ["HP", "Canon", "Epson", "Brother", "Xerox", "Kyocera", "Ricoh", "Samsung", "Pantum", "Lexmark"]
CONSOLE_BRANDS = ["Sony", "Microsoft", "Nintendo", "Sega", "Atari"]
PC = ["PC"]

EDIT_ORDER = {"stat_ru": "📊 Статус", "stat": "📊 Status", "dia_ru": "🔍 Диагностика", "dia": "🔍 Diagnostics", "add_serv_ru": "➕ Услуга", "add_serv": "➕ Service", "add_part_ru": "➕ Запчасть", "add_part": "➕ Part", "clear_ru": "🗑️ Очистить", "clear": "🗑️ Clear", "notes_ru": "💬 Комментарии", "notes": "💬 Comments", "prepayment_ru": "💵 Предоплата", "prepayment": "💵 Prepayment"}


DEVICE_ICO = {

    # RU:
    "Ноутбук": "💻",
    "ПК": "🖥",
    "Телефон": "📱",
    "Видеокарта": "👾",
    "Материнская плата": "🧩",
    "Монитор": "🖥️",
    "Планшет": "📟",
    "Принтер": "🖨️",
    "Игровая консоль": "🎮",
    "Другое": "⚙️",

    # EN:
    "Laptop": "💻",
    "PC": "🖥",
    "Phone": "📱",
    "GPU": "👾",
    "Motherboard": "🧩",
    "Monitor": "🖥️",
    "Tablet": "📟",
    "Printer": "🖨️",
    "Console": "🎮",
    "other": "⚙️"
}


DEVICE_BRANDS_RU = {
    "Ноутбук": LAPTOP_BRANDS,
    "ПК": PC,
    # "Телефон": PHONE_BRANDS,
    "Видеокарта": GPU_BRANDS,
    "Материнская плата": MOTHERBOARD_BRANDS,
    # "Монитор": MONITOR_BRANDS,
    "Планшет": TABLET_BRANDS,
    # "Принтер": PRINTER_BRANDS,
    "Игровая консоль": CONSOLE_BRANDS,
}

DEVICE_BRANDS_EN = {
    "Laptop": LAPTOP_BRANDS,
    "PC": PC,
    # "Phone": PHONE_BRANDS,
    "GPU": GPU_BRANDS,
    "Motherboard": MOTHERBOARD_BRANDS,
    # "Monitor": MONITOR_BRANDS,
    "Tablet": TABLET_BRANDS,
    # "Printer": PRINTER_BRANDS,
    "Console": CONSOLE_BRANDS
}


PREFIXES = {
    'guarant': 'GR',    # гарантийный
    'paid': 'PD',       # платный
    'express': 'EX',    # срочный
    'general': 'GE'     # Если что то пошло не так..  
}

# Номера: GR-2024-0001, PD-2024-0001, EX-2024-0001

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


CONDITIONS = {"ru": """1. Устройство принимается в мастерскую на диагностику/ремонт для определения примерных сроков, стоимости и возможности проведения ремонта заявленной клиентом неисправности.
2. При диагностике или ремонте устройства его необходимо вскрыть, что влечёт за собой потерю заводской гарантии, прошу это учитывать и самостоятельно проверять наличие гарантии от производителя.
3. Заказчик принимает на себя риск возможной полной или частичной утраты работоспособности устройства в процессе ремонта, в случае грубых нарушений пользователем условий эксплуатации, наличие следов попадания токопроводящей жидкости (коррозии), либо механических повреждений.
4. Условия хранения клиентских устройств: Максимальный срок гарантийного или платного ремонта составляет 45 дней. Срок ремонта может быть увеличен при отсутствии запчастей. 2. С момента оповещения клиента о готовности или не возможности ремонта Клиент обязуется забрать изделие в течение 30 календарных дней. По истечении 30-дневного срока бесплатного хранения за дальнейшее хранение Исполнителем взимается плата в размере 100 рублей в сутки. 3. Стороны договорились, что при неисполнении Клиентом своей обязанности забрать изделие из ремонта, по истечении двух месяцев с момента начала платного хранения, оборудование становится невостребованным Клиентом. Клиент, тем самым, отказывается от своего права на данное оборудование, и Исполнитель имеет право реализовать данное имущество в счет возмещения убытков за ремонт и хранение изделия.
5. Аппарат выдается при предъявлении «Квитанции о приеме». В случае утери квитанции выдача устройства может быть произведена при предъявлении документа, удостоверяющего личность на имя заказчика.
Заказчик ознакомлен и согласен с вышеперечисленными условиями и обработкой персональных данных, указанных в настоящей квитанции, а также несёт ответственность за их достоверность. Заказчик подтверждает, что является законным владельцем устройства.""",
"en": """1. The device is accepted to the workshop for diagnosis / repair to determine the approximate time, cost and possibility of repairing the malfunction claimed by the customer.
2. When diagnosing or repairing the device, it must be opened, which entails the loss of the factory warranty. Please take this into account and independently verify the availability of a manufacturer's warranty.
3. The customer assumes the risk of a possible complete or partial loss of operability of the device during repair, in case of gross violations of operating conditions by the user, the presence of traces of a conductive liquid (corrosion), or mechanical damage.
4. Storage conditions for client devices: The maximum warranty or paid repair period is 45 days. The repair period can be extended if there are no spare parts. 2. From the moment the customer is notified of the readiness or inability to repair, the Customer undertakes to pick up the product within 30 calendar days. After the expiration of the 30-day free storage period, the Contractor will charge a fee of 100 rubles per day for further storage. 3. The Parties agreed that if the Client fails to fulfill his obligation to pick up the product from repair, after two months from the date of the start of paid storage, the equipment becomes unclaimed by the Client. The Client thereby waives his right to this equipment, and the Contractor has the right to sell this property in compensation for damages for the repair and storage of the product.
5. The device is issued upon presentation of an "Admission receipt". In case of loss of the receipt, the device can be issued upon presentation of an identity document addressed to the customer.
The Customer has read and agrees to the above conditions and the processing of personal data specified in this receipt, and is responsible for their accuracy. The customer confirms that he is the legal owner of the device."""}

ADRES = "Москва, 3-я Парковая, дом 38, +7 (999) 832-99-34"

SITE = "www.1Rmaster.ru"

CURRENCY = "₽"





# KEYS .env:
TELEGRAM_BOT_TOKEN = os.environ.get('telegram_bot_token')
USER_DB = os.environ.get('USER_DB')
PASSWORD_DB = os.environ.get('PASSWORD_DB')
DB_NAME = os.environ.get('POSTGRES_DB')
ADMIN_ID = int(os.environ.get('admin_id'))
KEY_API_DEEPSEEK = os.environ.get('key_api_deepseek')





WORKS_RU = {
    # Дисплеи
    'screen_replacement': 'Замена экрана',
    'touchscreen_replacement': 'Замена тачскрина',
    'matrix_replacement': 'Замена матрицы',
    
    # Батареи
    'battery_replacement': 'Замена батареи',
    'battery_connector': 'Ремонт разъёма батареи',
    
    # Зарядка
    'charging_port': 'Замена разъёма зарядки',
    'charging_board': 'Замена платы зарядки',
    
    # Аудио
    'speaker_replacement': 'Замена динамика',
    'microphone_replacement': 'Замена микрофона',
    'jack_replacement': 'Замена аудиоразъёма',
    
    # Камеры
    'camera_replacement': 'Замена камеры',
    'front_camera': 'Замена фронтальной камеры',
    
    # Кнопки
    'power_button': 'Замена кнопки питания',
    'volume_buttons': 'Замена кнопок громкости',
    'home_button': 'Замена кнопки Home',
    
    # Корпус
    'housing_replacement': 'Замена корпуса',
    'back_cover': 'Замена задней крышки',
    'glass_back': 'Замена стекла задней крышки',
    
    # Разъёмы
    'usb_port': 'Замена USB-порта',
    'hdmi_port': 'Замена HDMI-порта',
    
    # Охлаждение
    'thermal_paste': 'Замена термопасты',
    'cooler_replacement': 'Замена кулера',
    
    # Материнская плата
    'motherboard_repair': 'Ремонт материнской платы',
    'bios_reflash': 'Перепрошивка BIOS',
    
    # Чистка
    'cleaning_dust': 'Чистка от пыли',
    'liquid_damage': 'Устранение последствий залития',
    
    # Программные
    'os_reinstall': 'Переустановка ОС',
    'data_recovery': 'Восстановление данных',
    'virus_removal': 'Удаление вирусов',
    
    # Диагностика
    'diagnostics': 'Диагностика',
    'stress_test': 'Стресс-тестирование',
}

WORKS_EN = {
    'screen_replacement': 'Screen Replacement',
    'touchscreen_replacement': 'Touchscreen Replacement',
    'matrix_replacement': 'Matrix Replacement',
    'battery_replacement': 'Battery Replacement',
    'battery_connector': 'Battery Connector Repair',
    'charging_port': 'Charging Port Replacement',
    'charging_board': 'Charging Board Replacement',
    'speaker_replacement': 'Speaker Replacement',
    'microphone_replacement': 'Microphone Replacement',
    'jack_replacement': 'Audio Jack Replacement',
    'camera_replacement': 'Camera Replacement',
    'front_camera': 'Front Camera Replacement',
    'power_button': 'Power Button Replacement',
    'volume_buttons': 'Volume Buttons Replacement',
    'home_button': 'Home Button Replacement',
    'housing_replacement': 'Housing Replacement',
    'back_cover': 'Back Cover Replacement',
    'glass_back': 'Back Glass Replacement',
    'usb_port': 'USB Port Replacement',
    'hdmi_port': 'HDMI Port Replacement',
    'thermal_paste': 'Thermal Paste Replacement',
    'cooler_replacement': 'Cooler Replacement',
    'motherboard_repair': 'Motherboard Repair',
    'bios_reflash': 'BIOS Reflash',
    'cleaning_dust': 'Dust Cleaning',
    'liquid_damage': 'Liquid Damage Repair',
    'os_reinstall': 'OS Reinstallation',
    'data_recovery': 'Data Recovery',
    'virus_removal': 'Virus Removal',
    'diagnostics': 'Diagnostics',
    'stress_test': 'Stress Testing',
}






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

