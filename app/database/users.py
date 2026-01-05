from logs.set_logger import set_logger
logger = set_logger(name="db")
# import asyncpg



# database/users.py
from database import db



# async def add_user(user_data: dict) -> bool:
#     """Добавить пользователя"""
#     return await db.insert("users", user_data)
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



# async def get_user_by_tg(tg_id: int):
#     """Найти пользователя по Telegram ID"""
#     query = "SELECT * FROM users WHERE user_telegram = $1"
#     return await db.execute(query, tg_id)



async def get_user_by_tg(tg_id: int):
    query = "SELECT * FROM users WHERE user_telegram = $1"
    return await db.fetchrow(query, tg_id)  # ← использовать fetchrow