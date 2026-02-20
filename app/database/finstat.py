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





async def get_fin_stats_db() -> list[dict]:
    """Выгрузить все записи fin_stats"""

    query = "SELECT * FROM fin_stats ORDER BY payment_id"
    records = await db.fetch(query)
    return [dict(rec) for rec in records]




async def get_payments(period: str = "years") -> list[dict]:
    """
    Получить список заказов за период.
    
    Args:
        period: 'today' | 'month' | 'year' | 'years'
    
    Returns:
        Список словарей с полями: id, payment_date, amount, category, description
    
    Raises:
        ValueError: если period некорректен
    """
    ALLOWED_PERIODS = {"today", "month", "year", "years"}
    if period not in ALLOWED_PERIODS:
        raise ValueError(f"Invalid period: {period}. Allowed: {ALLOWED_PERIODS}")
    
    query = """
        SELECT 
            *
        FROM fin_stats
        WHERE 1=1
    """
    
    if period == "today":
        query += " AND payment_date::date = CURRENT_DATE"
    elif period == "month":
        query += """
            AND payment_date >= DATE_TRUNC('month', CURRENT_DATE)
            AND payment_date < DATE_TRUNC('month', CURRENT_DATE) + INTERVAL '1 month'
        """
    elif period == "year":
        query += """
            AND payment_date >= DATE_TRUNC('year', CURRENT_DATE)
            AND payment_date < DATE_TRUNC('year', CURRENT_DATE) + INTERVAL '1 year'
        """
    # period == "years" → без дополнительных условий
    
    query += " ORDER BY payment_date ASC" # DESC ASC
    
    records = await db.fetch(query)
    return [dict(rec) for rec in records]






