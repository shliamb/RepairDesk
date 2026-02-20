#! app/database/json_fin_stat.py
from logs.set_logger import set_logger
logger = set_logger(name="jsonFinStat")
import os
import json
from datetime import datetime
# from database.orders import OrderService
# from database import db
from utils.serialize import json_serializer, json_decoder
from database.finstat import get_fin_stats_db, add_stat
from database.users import get_user_by_user_id
from config import PATH_JSON


# orders = OrderService(db)


async def get_json_fin_stats_db() -> str | bool:
    """Получение всех финансовых записей и формирование JSON файла"""
    data = await get_fin_stats_db()
    if not data:
        return False

    try:
        os.makedirs(PATH_JSON, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(PATH_JSON, f"fin_stats_{timestamp}.json")
        filepath = os.path.join(os.getcwd(), filename)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4, default=json_serializer)

        return filepath
    
    except Exception as e:
        logger.error(f"Error saving fin_stats to JSON: {e}")
        print(f"Error saving fin_stats to JSON: {e}")
        return False





async def push_json_fin_stats_in_db(file_path: str) -> tuple[int, int]:
    """Импорт финансовых записей из JSON-файла в БД"""
    good_case, bad_case = 0, 0
    #next_id_order = await orders.get_next_order_id()

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            records = json.load(f)

    except Exception as e:
        logger.error(f"Error reading JSON file: {e}")
        print(f"Error reading JSON file: {e}")
        return 0, 0

    for rec in records:
        try:
            # Декодируем специальные типы
            order_id = json_decoder(rec.get("order_id"))          # int
            client_id = json_decoder(rec.get("client_id"))        # UUID
            master_id = json_decoder(rec.get("master_id"))        # UUID
            who_issued = json_decoder(rec.get("who_issued"))      # UUID

            payment_amount = json_decoder(rec.get("payment_amount"))  # Decimal
            net_profit = json_decoder(rec.get("net_profit"))          # Decimal
            payment_method = rec.get("payment_method")

            payment_date = json_decoder(rec.get("payment_date"))               # datetime
            order_created_date = json_decoder(rec.get("order_created_date"))   # datetime
            order_completed_date = json_decoder(rec.get("order_completed_date")) # datetime

            device_type = rec.get("device_type")
            device_model = rec.get("device_model")
            repair_type = rec.get("repair_type")

            # Проверка обязательных полей
            if not all([client_id, order_id, master_id, who_issued]):
                print("Error Checking required fields: \n", "order_id:", order_id, "client_id:", client_id, "master_id:", master_id, "who_issued:", 
                      who_issued, "payment_amount:", payment_amount, "net_profit:", net_profit, "payment_method:", payment_method)
                bad_case += 1
                continue

            # Проверка существования связанных элементов
            # Проверяем заказ - безсмысленно, меняется при переносе через JSON

            # Проверяем клиента
            client_exists = await get_user_by_user_id(client_id)
            if not client_exists:
                logger.warning(f"Client {client_id} not found, skipping fin_stats record")
                print(f"Client {client_id} not found, skipping fin_stats record")
                bad_case += 1
                continue

            # Проверяем мастера
            master_exists = await get_user_by_user_id(master_id)
            if not master_exists:
                logger.warning(f"Master {master_id} not found, skipping fin_stats record")
                print(f"Master {master_id} not found, skipping fin_stats record")
                bad_case += 1
                continue

            # Проверяем who_issued
            issuer_exists = await get_user_by_user_id(who_issued)
            if not issuer_exists:
                logger.warning(f"Issuer {who_issued} not found, skipping fin_stats record")
                print(f"Issuer {who_issued} not found, skipping fin_stats record")
                bad_case += 1
                continue

            stat_data = {
                "order_id": order_id,
                "client_id": client_id,
                "master_id": master_id,
                "who_issued": who_issued,
                "payment_amount": payment_amount,
                "net_profit": net_profit,
                "payment_method": payment_method,
                "payment_date": payment_date,
                "order_created_date": order_created_date,
                "order_completed_date": order_completed_date,
                "device_type": device_type,
                "device_model": device_model,
                "repair_type": repair_type
            }
            if not await add_stat(stat_data):
                logger.error("Error add_stat")
                print("Error add_stat")
                bad_case += 1
                continue

            # next_id_order += 1
            good_case += 1

        except Exception as e:
            logger.error(f"Error inserting fin_stats record: {e}")
            print(f"Error inserting fin_stats record: {e}")
            bad_case += 1

    logger.info(f"Fin_stats import: good={good_case}, bad={bad_case}")
    print(f"Fin_stats import: good={good_case}, bad={bad_case}")
    return good_case, bad_case

