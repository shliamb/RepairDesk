#! app/database/json_clients_db.py
from logs.set_logger import set_logger
logger = set_logger(name="jsonCli")
from config import PATH_JSON
from datetime import datetime
from database.users import get_all_users, add_user, get_user_by_phone, get_user_by_telegram_name
from utils.serialize import json_serializer, json_decoder
from utils.formatters import format_phone
from database import db
import uuid
import json
import os



async def get_json_clients_db() -> str | bool:
    """ Получение всех пользователей и 
        формирование данных клиентов в JSON файл """
    users_data = await get_all_users()
    # print(users_data)

    if not users_data:
        return False

    try:
        json_users_data = []
        for user in users_data:
            json_users_data.append(user)

        # Проверяем и создаём папку
        os.makedirs(PATH_JSON, exist_ok=True)

        # Создаем имя файла с текущей датой-временем
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Безопасно создаём файл
        filename = os.path.join(PATH_JSON, f"users_data_{timestamp}.json")
        
        # Полный путь к файлу в рабочей директории
        filepath = os.path.join(os.getcwd(), filename)
        
        # Сохраняем с обработкой специальных типов
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(
                json_users_data, 
                f, 
                ensure_ascii=False, 
                indent=4,
                default=json_serializer
            )
        return filepath

    except Exception as e:
        logger.error(f"Error save file to JSON: {e}")
        return False
    


async def push_json_clients_in_db(file_path: str) -> tuple:
    """ Получение из JSON данных клиентов, ручная сериализация баля и
        занесение в базу данных каждого """
    good_case, bad_case = 0, 0

    # Открытие файла и в файл:
    with open(file_path, "r") as file:

        if not file:
            return False, False

        users_json = json.load(file) # object_hook=custom_json_decoder)

        for user in users_json:
            user_data = {
                "user_id": json_decoder(user.get("user_id")),

                "user_glotmax": user.get("user_glotmax"),
                "user_whatsapp": user.get("user_whatsapp"),
                "user_telegram": json_decoder(user.get("user_telegram")),
                "username_telegram": user.get("username_telegram"),
                
                "phone": format_phone(user.get("phone")),
                "email": user.get("email"),
                "name": user.get("name"),

                "a_tip": user.get("a_tip"),
                "total_spent": user.get("total_spent"),
                "repair_count_total": user.get("repair_count_total"),

                "real_name": user.get("real_name"),
                "description_user": user.get("description_user"),
                "source": user.get("source"),
                "block": user.get("block"),
                "hum_quality": user.get("hum_quality"),
                
                "last_visit": json_decoder(user.get("last_visit")),
                "time_reg": json_decoder(user.get("time_reg")),
                "time_zone": user.get("time_zone"),
                "language": user.get("language"),
                "parametrs": user.get("parametrs"),
                
                "is_admin": user.get("is_admin"),
                "is_manager": user.get("is_manager"),
                "is_master": user.get("is_master"),
                
                "remind": user.get("remind")
            }

            try:
                """ Проверка, есть ли уже клиент с таким телефоном и telegram name"""
                user_id = json_decoder(user.get("user_id"))

                phone = user.get("phone")
                username_telegram = user.get("username_telegram")

                if phone:
                    get_phone = await get_user_by_phone(format_phone(phone))
                    if get_phone:
                        print(f"Error клиент уже существует с номером: {format_phone(get_phone.get('phone'))}")
                        bad_case += 1
                        continue
                
                if username_telegram:
                    get_username_t = await get_user_by_telegram_name(username_telegram)
                    if get_username_t:
                        print(f"Error клиент уже существует с telegram name: {get_username_t.get('username_telegram')}")
                        bad_case += 1
                        continue

                # Добавляю пользователя
                if not user_id:
                    if phone or username_telegram:
                        user_id = uuid.uuid4()
                        user_data["user_id"] = user_id
                    else:
                        print("Not data for client")
                        bad_case += 1
                        continue


                if await add_user(user_data): good_case += 1

            except Exception as e:
                print(f"Error add_user: {e}")
                bad_case += 1

        print("good_case users:", good_case, "bad_case users:", bad_case)

        return good_case, bad_case

        # if bad_case == 0 and good_case > 0: return good_case, bad_case
        # else: return False, False