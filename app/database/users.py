# database/users.py
from logs.set_logger import set_logger
logger = set_logger(name="db")
from database import db
import uuid
# import asyncpg




async def add_user(user_data: dict) -> bool:
    """Добавить пользователя"""
    keys = list(user_data.keys())
    values = list(user_data.values())
    
    columns = ", ".join(keys)
    placeholders = ", ".join([f"${i+1}" for i in range(len(values))])
    
    query = f"INSERT INTO users ({columns}) VALUES ({placeholders})"
    
    try:
        await db.execute(query, *values)
        return True
    except Exception as e:
        logger.error(f"Error adding user: {e}")
        return False


async def get_user_by_tg(tg_id: int) -> dict:
    """Найти пользователя по Telegram ID"""
    query = "SELECT * FROM users WHERE user_telegram = $1"
    record = await db.fetchrow(query, tg_id)
    if record:
        return dict(record)
    return {}


async def get_user_by_user_id(user_id: uuid) -> dict:
    """Найти пользователя по UUID ID"""
    query = "SELECT * FROM users WHERE user_id = $1"
    record = await db.fetchrow(query, user_id)
    if record:
        return dict(record)
    return {}


async def get_all_users() -> list:
    """Получить всех пользователей users"""
    query = f"SELECT * FROM users"
    records = await db.fetch(query)
    return [dict(rec) for rec in records]



async def edit_client(client_data: dict) -> bool:
    """Обновить данные клиента (user_id должен быть в client_data)"""
    
    if 'user_id' not in client_data:
        logger.error("No user_id in client_data")
        return False
    
    user_id = client_data.pop('user_id')  # вынимаем user_id: UUID
    if not client_data:  # если кроме user_id ничего нет
        return False
    
    # Формируем SET
    set_parts = [f"{key} = ${i+1}" for i, key in enumerate(client_data.keys())]
    values = list(client_data.values())
    values.append(user_id)  # user_id для WHERE в конце
    
    query = f"""
        UPDATE users 
        SET {', '.join(set_parts)}
        WHERE user_id = ${len(values)}
    """
    
    try:
        await db.execute(query, *values)
        return True
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        return False


async def search_clients(field: str, search_term: str, exact_match: bool = False) -> list[dict]:
    """
    Поиск клиентов по полю.
    
    Args:
        field: 'name', 'username_telegram', 'phone'
        search_term: что ищем
        exact_match: True для точного совпадения (=), False для частичного (LIKE)
    """
    if exact_match:
        query = f"SELECT * FROM users WHERE {field} = $1"
        params = [search_term]
    else:
        # Для частичного совпадения (регистронезависимо)
        query = f"SELECT * FROM users WHERE LOWER({field}) LIKE LOWER($1)"
        params = [f"%{search_term}%"]
    
    records = await db.fetch(query, *params)
    return [dict(rec) for rec in records]



async def get_user_by_phone(phone: str) -> dict:
    """Найти пользователя по телефону"""
    query = "SELECT * FROM users WHERE phone = $1"
    record = await db.fetchrow(query, phone)
    if record:
        return dict(record)
    return {}



async def get_user_by_telegram_name(telegram_name: str) -> dict:
    """Найти пользователя по telegram name"""
    query = "SELECT * FROM users WHERE username_telegram = $1"
    record = await db.fetchrow(query, telegram_name)
    if record:
        return dict(record)
    return {}