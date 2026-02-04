#! app/database/json_clients_db.py
from logs.set_logger import set_logger
logger = set_logger(name="jsonCli")
from config import PATH_JSON
from datetime import datetime
from decimal import Decimal
from utils.serialize import json_serializer, json_decoder
from utils.formatters import format_phone
from database.users import get_user_by_phone, get_user_by_user_id, edit_client
from database.orders import OrderService
from database import db
import uuid
import json
import os


orders = OrderService(db)


async def get_json_orders_db() -> str | bool:
    """ Получение всех заказов и 
        формирование JSON файла с заказами"""
    orders_data = await orders.get_all_orders()

    if not orders_data:
        return False

    try:
        json_orders_data = []
        for order in orders_data:
            json_orders_data.append(order)

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
    


async def push_json_orders_in_db(file_path: str) -> tuple:
    """ Получение из JSON данных заказов, ручная сериализация баля и
        занесение в базу данных каждого заказа """
    good_case, bad_case = 0, 0
    # Открытие файла и в файл:
    with open(file_path, "r") as file:

        if not file:
            return False, False

        orders_json = json.load(file) #, object_hook=custom_json_decoder)
        # print(orders_json)


        for order in orders_json:
            order_data = {
                "location": order.get("location"),
                
                "sn_imei": order.get("sn_imei"),
                "status": order.get("status"),
                "order_type": order.get("order_type"),
                "device_type": order.get("device_type"),
                "device_brand": order.get("device_brand"),
                "device_model": order.get("device_model"),
                "equipment": order.get("equipment"),
                
                "problem": order.get("problem"),
                "appearance": order.get("appearance"),
                "created_date": json_decoder(order.get("created_date")),
                "completion_date": order.get("completion_date"),
                "diagnosis_before": json_decoder(order.get("diagnosis_before")),

                "diagnosis": order.get("diagnosis"),
                "cost_diagnostics": order.get("cost_diagnostics"),

                "services": order.get("services"),
                "cost_repair": json_decoder(order.get("cost_repair")),
                "date_of_issue": json_decoder(order.get("date_of_issue")),

                "parts": order.get("parts"),
                "cost_of_parts": json_decoder(order.get("cost_of_parts")),
                "cost_price": json_decoder(order.get("cost_price")),

                "prepayment": order.get("prepayment"),
                "cost_prepayment": json_decoder(order.get("cost_prepayment")),
                
                "net_profit": json_decoder(order.get("net_profit")),
                "tips": json_decoder(order.get("tips")),

                "path_photo": order.get("path_photo"),
                
                "client_id": json_decoder(order.get("client_id")),  # UUID
                "real_name_client": order.get("real_name_client"),
                
                "created_by": json_decoder(order.get("created_by")),
                "real_name_created": order.get("real_name_created"),
                
                "master": order.get("master"),
                
                "edit_history": order.get("edit_history"),
                
                "comments": order.get("comments"),
            }

            try:
                # Поиск клиента в базе для привязки заказа:
                client_id: str = order.get("client_id")
                if client_id: client_id: uuid = json_decoder(client_id)
                
                phone: str = order.get("phone") # от livesklad для Join 
                if phone: phone = format_phone(phone)

                net_profit: Decimal = json_decoder(order.get("net_profit")) or 0

                tips: Decimal = json_decoder(order.get("tips")) or 0

                status: str = order.get("status")

                if not client_id and phone:
                    data_user = await get_user_by_phone(phone)
                    if data_user:
                        client_id = json_decoder(data_user.get("user_id"))
                        order_data["client_id"] = client_id

                elif not client_id and not phone:
                    print("Клиент не обнаружен в базе. Первым добавляем пользователей. Без пользователя нет смысла добавлять заказ.")
                    bad_case += 1
                    continue

                #print(order_data, "\n")
                order_number = await orders.create_order(order_data)
                if order_number:
                    print(order_number)
                    good_case += 1

                    if status != "issued":
                        continue

                    # Сбор обновленных данных клиента
                    old_data_user = await get_user_by_user_id(client_id)
                    total_spent: Decimal = json_decoder(old_data_user.get("total_spent")) or 0
                    repair_count_total: int  = json_decoder(old_data_user.get("repair_count_total")) or 0
                    a_tip: Decimal = json_decoder(old_data_user.get("a_tip")) or 0
                    

                    client_update_data = {
                        "user_id": client_id,
                        "total_spent": total_spent + net_profit,
                        "repair_count_total": repair_count_total + 1,
                        "a_tip": a_tip + tips
                    }

                    # Сохранение данных клиента
                    if not await edit_client(client_update_data):
                        print("Error ошибка обновления данных клиента")
                    
                    print("client_update_data:", client_update_data)


                else:
                    bad_case += 1

            except Exception as e:
                print(f"Error create_order: {e}")
                bad_case += 1

        print("good_case orders:", good_case, "bad_case orders:", bad_case)

        return good_case, bad_case

        # if bad_case == 0 and good_case > 0: return good_case, bad_case
        # else: return False, False