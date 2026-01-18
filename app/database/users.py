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