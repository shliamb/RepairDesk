# Центральное место управления роутерами
from handlers.start import router as start
from handlers.menu import router as menu
# from handlers.reception import router as reception
from handlers.workshop import router as workshop
from handlers.new_order import router as new_order
from handlers.viewing_orders import router as viewing_orders
# from handlers.reports import router as reports

# Порядок имеет значение! Роутеры проверяются сверху вниз
ALL_ROUTERS = [
    start,       # /start - самый важный
    menu,        # Основное меню
    workshop,
    new_order,
    viewing_orders
    # reception,   # Приёмка
    # workshop,    # Мастерская
    # reports,     # Отчёты
]

# Можно группировать:
# CLIENT_ROUTERS = [start, menu, workshop, new_order] #, reception]
# STAFF_ROUTERS = [workshop, reports]

