# __init__.py
from database.common import Database

db = Database() # Создаём глобальный экземпляр на весь проект

__all__ = ['db'] # Говорим Python: "из этого модуля экспортируй только 'db'"