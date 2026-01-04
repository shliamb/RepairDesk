# database/users.py
from common import Database

# Функции, а не классы
async def add_user(db: Database, user_data: dict) -> bool:
    """Добавить пользователя"""
    return await db.insert("users", user_data)

async def get_user_by_tg(db: Database, tg_id: int):
    """Найти пользователя по Telegram ID"""
    query = "SELECT * FROM users WHERE user_telegram = $1"
    return await db.fetchrow(query, tg_id)