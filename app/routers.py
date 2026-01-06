# Центральное место управления роутерами
from handlers.start import router as start
from handlers.menu import router as menu
# from handlers.reception import router as reception
from handlers.workshop import router as workshop
# from handlers.reports import router as reports

# Порядок имеет значение! Роутеры проверяются сверху вниз
ALL_ROUTERS = [
    start,       # /start - самый важный
    menu,        # Основное меню
    workshop,
    # reception,   # Приёмка
    # workshop,    # Мастерская
    # reports,     # Отчёты
]

# Можно группировать:
CLIENT_ROUTERS = [start, menu, workshop] #, reception]
# STAFF_ROUTERS = [workshop, reports]