import asyncpg
from typing import Optional

class Database:
    def __init__(self):
        self.pool = None
    
    # async def connect(self):
    #     if not self.pool:
    #         self.pool = await asyncpg.create_pool(...)
    
    # async def close(self):
    #     if self.pool:
    #         await self.pool.close()
    
    # # Общие методы
    # async def execute(self, query: str, *args):
    #     async with self.pool.acquire() as conn:
    #         return await conn.execute(query, *args)
    
    # async def fetch(self, query: str, *args):
    #     async with self.pool.acquire() as conn:
    #         return await conn.fetch(query, *args)