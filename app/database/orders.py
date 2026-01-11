#! database/orders.py
from logs.set_logger import set_logger
logger = set_logger(name="db")
from config import PREFIXES
import datetime







class OrderService:
    def __init__(self, db):
        self.db = db


    async def _generate_order_number(self, prefix: str) -> str:
        """Генерирует номер заказа: R-2024-0001"""
        
        # 1. Получаем последний номер с этим префиксом
        query = """
            SELECT order_number FROM orders 
            WHERE order_number LIKE $1 || '-%'
            ORDER BY id DESC LIMIT 1
        """
        
        last = await self.db.fetchval(query, prefix)
        
        if not last:
            # Первый заказ с этим префиксом
            return f"{prefix}-{datetime.now().year}-0001"
        
        # 2. Парсим номер и инкрементируем
        # last = "R-2024-0123"
        try:
            parts = last.split('-')
            if len(parts) == 3:
                year, num = parts[1], int(parts[2])
                if year == str(datetime.now().year):
                    new_num = num + 1
                else:
                    new_num = 1  # новый год — сбрасываем счётчик
            else:
                new_num = 1
        except:
            new_num = 1
        
        # 3. Формируем новый
        return f"{prefix}-{datetime.now().year}-{new_num:04d}"


    async def create_order(self, order_data: dict) -> str:
        """Создать заказ и вернуть его номер"""

        # Генерируем номер
        prefix = PREFIXES.get(order_data.get('order_type', 'general'), 'OR')
        order_number = await self._generate_order_number(prefix)

        order_data['order_number'] = order_number

        keys = list(order_data.keys())
        values = list(order_data.values())

        columns = ", ".join(keys)
        placeholders = ", ".join([f"${i+1}" for i in range(len(values))])

        query = f"INSERT INTO orders ({columns}) VALUES ({placeholders}) RETURNING order_number"

        try:
            result = await self.db.execute(query, *values)
            return result['order_number']
        
        except Exception as e:
            logger.error(f"Error adding order: {e}")
            return "Error"


    async def get_order(self, id: int):
        """ Получить заказ по его ID"""
        query = "SELECT * FROM orders WHERE id = $1"
        return await self.db.fetch(query, id)