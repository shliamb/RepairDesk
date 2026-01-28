#! app/handlers/__init__.py
# Центральное место управления роутерами
from handlers.start import router as start
# from handlers.menu import router as menu
from handlers.workshop import router as workshop
from handlers.new_order import router as new_order
from handlers.viewing_orders import router as viewing_orders
from handlers.edit_order import router as edit_order
from handlers.edit_client import router as edit_client
from handlers.admin import router as admin
from handlers.search import router as search

# from handlers.reports import router as reports

# Порядок имеет значение! Роутеры проверяются сверху вниз
ALL_ROUTERS = [
    start,
    # menu,
    search,
    workshop,
    new_order,
    viewing_orders,
    edit_order,
    edit_client,
    admin
    # reports,     # Отчёты
]

# Можно группировать:
# CLIENT_ROUTERS = [start, menu, workshop, new_order] #, reception]
# STAFF_ROUTERS = [workshop, reports]