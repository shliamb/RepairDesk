#! app/database/migration_livesklad.py
# pip install pandas openpyxl
from logs.set_logger import set_logger
logger = set_logger(name="jsonsklad")
from config import PATH_JSON, ADMIN_ID
from datetime import datetime
from utils.serialize import json_serializer, json_decoder
from utils.formatters import convert_date_format, format_phone
from database.users import get_user_by_phone, get_user_by_tg
# from database.users import get_user_by_tg
import pandas as pd
from database.orders import OrderService
from database import db
import json
import uuid
import os


orders = OrderService(db)



# SAVE JSON
async def save_json_file(name: str, json_data: list) -> str | bool:
    """ Сохранение файла JSON """
    try:
        # Проверяем и создаём папку
        os.makedirs(PATH_JSON, exist_ok=True)
        # Создаем имя файла с текущей датой-временем
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        # Безопасно создаём файл
        filename = os.path.join(PATH_JSON, f"{name}_{timestamp}.json")
        # Полный путь к файлу в рабочей директории
        filepath = os.path.join(os.getcwd(), filename)
        
        # Сохраняем с обработкой специальных типов
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(
                json_data, 
                f, 
                ensure_ascii=False, 
                indent=4,
                default=json_serializer
            )
        return filepath

    except Exception as e:
        logger.error(f"Error save file to JSON: {e}")
        return False



# PARSE XLSX
def parse_xlsx(file_path: str) -> list[dict]:
    """ Парсинг xlsx """
    df = pd.read_excel(file_path, dtype=str)  # Все данные как строки
    df = df.fillna('')  # Заменяем NaN на пустые строки
    return df.to_dict('records')



# GET JSON FROM XLSX SKLAD
async def parse_xls_get_json(filepath: str) -> tuple:
    """ Получение xlsx файла от livesklad, 
        парсинг, сбор клиентов и заказов для 
        формирования JSON фалов для добавления в базу """
    json_users_data, json_orders_data, json_finstat_data = [], [], []
    next_id_order = await orders.get_next_order_id()
    dat_admin = await get_user_by_tg(ADMIN_ID)
    admin_uuid = dat_admin.get("user_id") 



    data = parse_xlsx(filepath)
    for row in data:

        user_id = None

        phone_client = format_phone(row['Телефон'])
        if phone_client:
            data_client = await get_user_by_phone(phone_client)

            if data_client:
                user_id = data_client.get("user_id")

            else:
                for one_row in json_users_data:
                    if phone_client == one_row.get("phone"):
                        user_id = one_row.get("user_id")

        if not user_id:
            user_id = uuid.uuid4() # Генерирую сразу что бы связать с заказом

        name_client = row['Имя']

        # CLIENT DATA:
        user_data = {
            "user_id": user_id,
            "name": name_client,
            "phone": phone_client,
            "real_name": name_client,
            "total_spent": None,
            "repair_count_total": None,
            "description_user": "moved from live sklad"
        }

        json_users_data.append(user_data)


        # ORDER DATA:
        order_data = {
            "id": next_id_order,
            "phone": phone_client,
            "sn_imei": row['Серийный номер / IMEI'],
            "status": "issued", #row['Статус'],
            "order_type": "paid", # row['Тип заказа'],
            "device_type": row['Тип устройства'],
            "device_brand": row['Марка'],
            "device_model": row['Модель'],
            # "equipment": row['Комплектация'],
            "problem": f"[{row['Неисправность']}]",
            # "services": row['Выполненные работы'],
            "cost_repair": row['Оплачено по заказу'],
            "created_date": convert_date_format(row['Дата создания']),
            "date_of_issue": convert_date_format(row['Дата выдачи']),
            "created_by": ADMIN_ID, # telegram id ого, кто создал запись
            # "order_id": 555, # Попробую так..
            "client_id": user_id,
            "real_name_client": name_client,
        }

        json_orders_data.append(order_data)

        # FINSTAT DATA:
        finstat_data = {
            "order_id": next_id_order, # ! INTEGER
            "client_id": user_id, # ! UUID users table
            "master_id": admin_uuid, # ! UUID users table

            "payment_amount": row['Оплачено по заказу'], # ! DECIMAL(10,2)
            "net_profit": row['Оплачено по заказу'], # ! DECIMAL(10,2)
            "payment_method": "cash", # ! STR

            "payment_date": convert_date_format(row['Дата выдачи']), # DEFAULT TIMESTAMP
            "order_created_date": convert_date_format(row['Дата создания']), # DEFAULT
            "order_completed_date": convert_date_format(row['Дата выдачи']), # DEFAULT
            "who_issued": admin_uuid, # ! UUID users table

            "device_type": row['Тип устройства'],
            "device_model": row['Модель'],
            "repair_type": "paid"
        }

        json_finstat_data.append(finstat_data)

        next_id_order += 1

    if json_users_data:
        users_filepath = await save_json_file("users_livesklad",json_users_data)

    
    if json_orders_data:
        orders_filepath = await save_json_file("orders_livesklad", json_orders_data)

    if json_finstat_data:
        finstat_filepath = await save_json_file("finstat_livesklad", json_finstat_data)

    return users_filepath, orders_filepath, finstat_filepath






















        # name = row['Имя']
        # phone = row['Телефон']
        # old_order = row['Номер заказа']
        # type_order = row['Тип заказа']
        # type_device = row['Тип устройства']
        # brand = row['Марка']
        # model = row['Модель']
        # sn_imei = row['Серийный номер / IMEI']
        # date_create = row['Дата создания']
        # date_of_issue = row['Дата выдачи']
        # equipment = row['Комплектация']
        # problem = row['Неисправность']
        # completed_works = row['Выполненные работы']
        # status = row['Статус']
        # paid = row['Оплачено по заказу']



# {
#     'Имя': 'Соломатин Павел', 
#     'Телефон': '+7 (962) 935-55-00',

#     'Номер заказа': 'A1453', 
#     'Тип заказа': 'Платный', 
#     'Тип устройства': 'Ноутбук', 
#     'Марка': 'Acer', 
#     'Модель': 'n17c1', 
#     'Серийный номер / IMEI': 'nhq3mer0469350553193400', 
#     'Дата создания': '06.01.2026 15:07', 
#     'Дата выдачи': '', 
#     'Комплектация': 'Устройство, Зарядка', 
#     'Неисправность': 'Не включается, садился, моргал экран, от зарядки перестал заряжаться, петли выгибаются при открытии крышки, крепления петль не держат, так как корпус не имеет части креплений, матрица немного сдвинута, на левой петле есть стяжки, клавишы стерты часть, попала влага, но не точно, диагностика', 
#     'Выполненные работы': '', 
#     'Статус': 'Новый', 
#     'Оплачено по заказу': '0'
# }
