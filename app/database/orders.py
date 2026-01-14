#! database/orders.py
from logs.set_logger import set_logger
logger = set_logger(name="db")
from config import PREFIXES
from datetime import datetime







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
        order_type = order_data.get('order_type', 'general')
        prefix = PREFIXES.get(order_type, 'OR')
        order_number = await self._generate_order_number(prefix)

        order_data['order_number'] = order_number
        # order_data['order_number'] = "A-32354324"
        # print(order_data)

        keys = list(order_data.keys())
        values = list(order_data.values())

        columns = ", ".join(keys)
        placeholders = ", ".join([f"${i+1}" for i in range(len(values))])

        query = f"INSERT INTO orders ({columns}) VALUES ({placeholders}) RETURNING order_number"

        try:
            result = await self.db.fetchrow(query, *values)
            return result['order_number'] # result.order_number
        
        except Exception as e:
            logger.error(f"Error adding order: {e}")
            return "Error"


    async def get_order_id(self, id: int) -> dict:
        """ Получить заказ по его ID"""
        query = "SELECT * FROM orders WHERE id = $1"
        record = await self.db.fetchrow(query, id)
        if record:
            return dict(record)
        return {}
    

    async def get_order_order_number(self, order_number: str) -> dict:
        """ Получить заказ по его order_number"""
        query = "SELECT * FROM orders WHERE order_number = $1"
        record = await self.db.fetchrow(query, order_number)
        if record:
            return dict(record)
        return {}
    

    async def get_orders_by_statuses(self, statuses: list) -> list[dict]:
        """Получить заказы с нужными статусами"""
        if not statuses:
            return []
        
        # Создаем плейсхолдеры: $1, $2, $3...
        placeholders = ', '.join([f'${i+1}' for i in range(len(statuses))])
        
        query = f"SELECT * FROM orders WHERE status IN ({placeholders})"
        
        records = await self.db.fetch(query, *statuses)  # распаковываем статусы
        return [dict(rec) for rec in records]






    # if not records:  # список пустой
    #     return {}
    
    # # Берём первый Record и преобразуем в dict
    # first_record = records[0]
    # return dict(first_record)
    
