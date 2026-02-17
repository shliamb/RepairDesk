import os
import json
from datetime import datetime
from app.database import db  # предполагаем, что db доступен
from app.utils.helpers import json_serializer, json_decoder  # твои функции
from config import PATH_JSON
import logging

logger = logging.getLogger(__name__)





async def get_json_fin_stats_db() -> str | bool:
    """Выгрузить все записи fin_stats в JSON-файл"""
    query = "SELECT * FROM fin_stats ORDER BY payment_id"
    records = await db.fetch(query)
    if not records:
        return False

    # Преобразуем Record -> dict
    data = [dict(r) for r in records]

    try:
        os.makedirs(PATH_JSON, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(PATH_JSON, f"fin_stats_data_{timestamp}.json")
        filepath = os.path.join(os.getcwd(), filename)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4, default=json_serializer)

        return filepath
    except Exception as e:
        logger.error(f"Error saving fin_stats to JSON: {e}")
        return False
    



async def push_json_fin_stats_in_db(file_path: str) -> tuple[int, int]:
    """Импортировать записи fin_stats из JSON-файла"""
    good_case, bad_case = 0, 0

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            records = json.load(f)
    except Exception as e:
        logger.error(f"Error reading JSON file: {e}")
        return 0, 0

    if not records:
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
            if not all([order_id, client_id, master_id, who_issued,
                        payment_amount, net_profit, payment_method]):
                bad_case += 1
                continue

            # Проверка существования связанных записей (опционально, но желательно)
            # Проверяем заказ
            order_exists = await db.fetchval("SELECT 1 FROM orders WHERE id = $1", order_id)
            if not order_exists:
                logger.warning(f"Order {order_id} not found, skipping fin_stats record")
                bad_case += 1
                continue

            # Проверяем клиента
            client_exists = await db.fetchval("SELECT 1 FROM users WHERE user_id = $1", client_id)
            if not client_exists:
                logger.warning(f"Client {client_id} not found, skipping fin_stats record")
                bad_case += 1
                continue

            # Проверяем мастера
            master_exists = await db.fetchval("SELECT 1 FROM users WHERE user_id = $1", master_id)
            if not master_exists:
                logger.warning(f"Master {master_id} not found, skipping fin_stats record")
                bad_case += 1
                continue

            # Проверяем who_issued
            issuer_exists = await db.fetchval("SELECT 1 FROM users WHERE user_id = $1", who_issued)
            if not issuer_exists:
                logger.warning(f"Issuer {who_issued} not found, skipping fin_stats record")
                bad_case += 1
                continue

            # Вставляем запись (без payment_id – пусть serial сам проставится)
            insert_query = """
                INSERT INTO fin_stats (
                    order_id, client_id, master_id, payment_amount, net_profit,
                    payment_method, payment_date, order_created_date, order_completed_date,
                    who_issued, device_type, device_model, repair_type
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            """
            await db.execute(
                insert_query,
                order_id, client_id, master_id, payment_amount, net_profit,
                payment_method, payment_date, order_created_date, order_completed_date,
                who_issued, device_type, device_model, repair_type
            )
            good_case += 1

        except Exception as e:
            logger.error(f"Error inserting fin_stats record: {e}")
            bad_case += 1

    logger.info(f"Fin_stats import: good={good_case}, bad={bad_case}")
    return good_case, bad_case