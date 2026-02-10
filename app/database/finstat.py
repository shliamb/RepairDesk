# database/finstat.py
from logs.set_logger import set_logger
logger = set_logger(name="db")
from database import db
import uuid
# import asyncpg




async def add_stat(fin_data: dict) -> bool:
    """Добавить финансовую транзакцию"""
    keys = list(fin_data.keys())
    values = list(fin_data.values())
    
    columns = ", ".join(keys)
    placeholders = ", ".join([f"${i+1}" for i in range(len(values))])
    
    query = f"INSERT INTO fin_stats ({columns}) VALUES ({placeholders})"
    
    try:
        await db.execute(query, *values)
        return True
    except Exception as e:
        logger.error(f"Error adding fin stat: {e}")
        return False

