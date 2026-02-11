#! database/orders.py
from logs.set_logger import set_logger
logger = set_logger(name="db")
from config import PREFIXES
from datetime import datetime
import uuid







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
    
    
    async def delete_order_cascade(self, order_id: int) -> bool:
        """Удалить заказ и связанные с ним записи"""
        async with self.db.pool.acquire() as conn:
            async with conn.transaction():
                # Удаляем связанные записи (финансы..)
                await conn.execute("DELETE FROM fin_stats WHERE order_id = $1", order_id)
                #await conn.execute("DELETE FROM order_photos WHERE order_id = $1", order_id)
                # Удаляем сам заказ
                result = await conn.execute("DELETE FROM orders WHERE id = $1 RETURNING id", order_id)
                return 'DELETE' in result

    
    async def get_order_order_number(self, order_number: str) -> dict:
        """ Получить заказ по его order_number"""
        query = "SELECT * FROM orders WHERE order_number = $1"
        record = await self.db.fetchrow(query, order_number)
        if record:
            return dict(record)
        return {}
    

    async def get_orders_by_user(self, client_id: uuid) -> list[dict]:
        """Получить заказы с по client_id UUID"""
        if not client_id:
            return []
        
        query = f"SELECT * FROM orders WHERE client_id = $1"
        
        records = await self.db.fetch(query, client_id) 
        return [dict(rec) for rec in records]
    

    async def get_orders_by_statuses(self, statuses: list) -> list[dict]:
        """Получить заказы с нужными статусами"""
        if not statuses:
            return []
        
        # Создаем плейсхолдеры: $1, $2, $3...
        placeholders = ', '.join([f'${i+1}' for i in range(len(statuses))])
        
        query = f"SELECT * FROM orders WHERE status IN ({placeholders}) ORDER BY id DESC"
        
        records = await self.db.fetch(query, *statuses)  # распаковываем статусы
        return [dict(rec) for rec in records]
    

    async def get_last_orders(self, count: int = 30) -> list[dict]:
        """Получить последние N заказов (по убыванию ID)"""
        if not count:
            return []
        
        query = """SELECT * FROM orders ORDER BY id ASC LIMIT $1""" # DESC
        records = await self.db.fetch(query, count)
        return [dict(rec) for rec in records]
    

    async def get_last_orders_all(self) -> list[dict]:
        """Получить последние заказы (по убыванию ID)"""
        query = """SELECT * FROM orders ORDER BY id DESC""" # DESC ASC
        records = await self.db.fetch(query)
        return [dict(rec) for rec in records]


    async def edit_order(self, order_data: dict) -> bool:
        """Обновить данные заказа (id должен быть в order_data)"""
        
        if 'id' not in order_data:
            logger.error("No id in order_data")
            return False
        
        order_id = order_data.pop('id')  # вынимаем id
        if not order_data:  # если кроме id ничего нет
            return False
        
        # Формируем SET
        set_parts = [f"{key} = ${i+1}" for i, key in enumerate(order_data.keys())]
        values = list(order_data.values())
        values.append(order_id)  # id для WHERE в конце
        
        query = f"""
            UPDATE orders 
            SET {', '.join(set_parts)}
            WHERE id = ${len(values)}
        """
        
        try:
            await self.db.execute(query, *values)
            return True
        except Exception as e:
            logger.error(f"Error updating order {order_id}: {e}")
            return False



    async def get_all_orders(self) -> list[dict]:
        """Получить все заказы"""
        query = f"SELECT * FROM orders"
        
        records = await self.db.fetch(query)
        return [dict(rec) for rec in records]



    async def search_order_pattern(self, field: str, search_term: str) -> list[dict]:
        """
        Универсальный поиск заказов
        
        Args:
            field: Поле для поиска
            search_term: Что ищем
            exact: True для точного совпадения, False для частичного (LIKE)
        """
        query = f"SELECT * FROM orders WHERE LOWER({field}) LIKE LOWER($1)"
        params = [f"%{search_term}%"]
        
        records = await self.db.fetch(query, *params)
        return [dict(rec) for rec in records]



    async def search_by_order_suffix(self, suffix: str) -> list[dict]:
        """Поиск по последним цифрам номера заказа (17 → PD-2024-0017)"""
        normalized = suffix.zfill(4)  # 17 → 0017
        query = "SELECT * FROM orders WHERE order_number LIKE $1"
        params = [f"%-{normalized}"]  # PD-2024-0017
        
        records = await self.db.fetch(query, *params)
        return [dict(rec) for rec in records]
    


    async def count_orders_by_statuses(self, statuses: list) -> int:
        """Получить количество заказов по статусам (быстрее чем SELECT *)"""
        if not statuses:
            return 0
        
        placeholders = ', '.join([f'${i+1}' for i in range(len(statuses))])
        query = f"SELECT COUNT(*) FROM orders WHERE status IN ({placeholders})"
        
        count = await self.db.fetchval(query, *statuses)  # fetchval возвращает одно значение
        return count or 0
    

    async def count_orders_all(self) -> int:
        """Получить количество всех заказов (быстрее чем SELECT *)"""
        query = "SELECT COUNT(*) FROM orders"
        
        count = await self.db.fetchval(query)
        return count or 0






























    
