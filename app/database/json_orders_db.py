#! app/database/json_clients_db.py
from logs.set_logger import set_logger
logger = set_logger(name="jsonCli")
from config import PATH_JSON
from datetime import datetime
from database.users import get_all_users
from utils.serialize import json_serializer, json_serializer, custom_json_decoder
from database.orders import OrderService
from database import db
import json
import os
import asyncio


orders = OrderService(db)


async def get_json_orders_db():
    """ Получение всех заказов и 
        формирование JSON файла с заказами"""
    orders_data = await orders.get_all_orders()

    if not orders_data:
        return False

    try:
        json_orders_data = {}
        for order in orders_data:
            order_id = order.get("id")
            json_orders_data[order_id] = order

        # Проверяем и создаём папку
        os.makedirs(PATH_JSON, exist_ok=True)

        # Создаем имя файла с текущей датой-временем
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Безопасно создаём файл
        filename = os.path.join(PATH_JSON, f"orders_data_{timestamp}.json")
        
        # Полный путь к файлу в рабочей директории
        filepath = os.path.join(os.getcwd(), filename)
        
        # Сохраняем с обработкой специальных типов
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(
                json_orders_data, 
                f, 
                ensure_ascii=False, 
                indent=4,
                default=json_serializer
            )
        return filepath

    except Exception as e:
        logger.error(f"Error save file to JSON: {e}")
        return False
    


async def push_json_orders_in_db(file_path):
    """ Получение из JSON данных заказов и
        занесение в базу данных каждого заказа """
    # Открытие файла и в файл:
    with open(file_path, "r") as file:

        if not file:
            return False

        orders_json = json.load(file, object_hook=custom_json_decoder)
        print(orders_json)
        return True