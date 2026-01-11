from config import HOST, USER_DB, PASSWORD_DB, DB_NAME
from logs.set_logger import set_logger
logger = set_logger(name="db")
import asyncpg



# database/common.py

class Database:
    """ Work to data in DB """
    def __init__(self):
        self.pool = None
    

    async def connect(self):
        """ Создаем пул при запуске бота """
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                host=HOST,
                database=DB_NAME,
                user=USER_DB,
                password=PASSWORD_DB,
                min_size=5, # 5 соединений всегда готовы
                max_size=50, # максимум 50 одновременных
                max_queries=50000, # после 50к запросов - пересоздать соединение
                timeout=30 # ждать свободное соединение 30 секунд
            )
            logger.info("Database pool created")
        return self.pool


    async def close(self):
        """ Закрываем пул при остановке """
        if self.pool:
            await self.pool.close()
            self.pool = None
            logger.info("Database pool closed")


    async def _ensure_connected(self):
        """Внутренний метод: убедиться что подключены"""
        if self.pool is None:
            await self.connect()


    async def get_pool_stats(self):
        """Получить статистику пула"""
        if not self.pool:
            return "Пул не инициализирован. Вызовите await db.connect()"
        size = await self.pool.get_size()
        used = await self.pool.get_current_connection_count()
        free = size - used
        return {
            "total": size,
            "used": used,
            "free": free,
            "free_percent": (free / size * 100) if size > 0 else 0
        }
    

    async def fetch(self, query, *args):
        """Получить данные (SELECT)"""
        await self._ensure_connected()
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)
    

    async def fetchrow(self, query, *args):
        """Получить одну строку"""
        await self._ensure_connected()
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)
    

    async def execute(self, query, *args):
        """Выполнить запрос (INSERT/UPDATE/DELETE)"""
        await self._ensure_connected()
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)


    async def fetchval(self, query, *args, column=0):
        """Получить одно значение из результата"""
        await self._ensure_connected()
        async with self.pool.acquire() as conn:
            # asyncpg имеет conn.fetchval
            return await conn.fetchval(query, *args)









    
    # async def insert(self, table: str, data: dict) -> bool:
    #     """Вставить данные в таблицу (твой старый метод)"""
    #     if not data:
    #         return False
        
    #     keys = []
    #     values = []
    #     placeholders = []
        
    #     for i, (key, value) in enumerate(data.items(), 1):
    #         keys.append(key)
    #         values.append(value)
    #         placeholders.append(f"${i}")
        
    #     columns = ", ".join(keys)
    #     ph = ", ".join(placeholders)
        
    #     query = f"INSERT INTO {table} ({columns}) VALUES ({ph})"
        
    #     try:
    #         await self.execute(query, *values)
    #         return True
    #     except Exception as e:
    #         logger.error(f"Error inserting into {table}: {e}")
    #         return False





    # # Общие методы
    # async def execute(self, query: str, *args):
    #     async with self.pool.acquire() as conn:
    #         return await conn.execute(query, *args)
    
    # async def fetch(self, query: str, *args):
    #     async with self.pool.acquire() as conn:
    #         return await conn.fetch(query, *args)