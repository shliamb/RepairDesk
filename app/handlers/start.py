
from aiogram import Router, types
from aiogram.filters import CommandStart
from logs.set_logger import set_logger
logger = set_logger(name="handlers")
from database.users import add_user, get_user_by_tg
# from database import db
# from database.create_tables import create_tables_in_db
import uuid


router = Router()



# @router.message(CommandStart())
# async def start_router(message: types.Message):
#     await message.answer("Я теперь в отдельном файле!")
#     logger.info("Я теперь в отдельном файле!")

#     user_exists = await get_user_by_tg(message.from_user.id)
    
#     if not user_exists:
#         await add_user({
#             'user_id': str(uuid.uuid4()),
#             'user_telegram': message.from_user.id,
#             'name': message.from_user.first_name
#         })
    
#     await message.answer("Готово, ты в базе!")


# Временно добавь в хендлер
@router.message(CommandStart())
async def start_router(message: types.Message):
    
    #user = await get_user_by_tg(message.from_user.id)
    user = await get_user_by_tg(message.from_user.id)
    print(user)
    
    if user:
        await message.answer(f"Уже в базе: {user['name']}")
    else:
        success = await add_user({
            'user_id': str(uuid.uuid4()),
            'user_telegram': message.from_user.id,
            'name': message.from_user.first_name
        })
        
        if success:
            await message.answer("Добавлен в базу!")
        else:
            await message.answer("Ошибка добавления")




# from database import db
# from database import users, orders

# await db.connect()

# # Работа с пользователями
# await users.add_user(db, {...})
# user = await users.get_user_by_tg(db, 12345)

# # Работа с заказами
# order_id = await orders.create_order(db, {...})














# from aiogram import Router, types
# from aiogram.filters import CommandStart

# router = Router()

# @router.message(CommandStart())
# async def start_handler(message: types.Message):
#     # Копируешь сюда свою логику
#     await message.answer("Я теперь в отдельном файле!")







# from database import db
# from database import users, orders

# await db.connect()

# # Работа с пользователями
# await users.add_user(db, {...})
# user = await users.get_user_by_tg(db, 12345)

# # Работа с заказами
# order_id = await orders.create_order(db, {...})




# from database.worker_db import WorkerDB  # Только для аннотации типа!

# router = Router()

# @router.message(CommandStart())
# async def start_router(message: types.Message, db: WorkerDB):
#     await message.answer("Я теперь в отдельном файле!")
#     logger.error("Я теперь в отдельном файле!")
#     logger.info("Я теперь в отдельном файле!")
#     # # db автоматически придет из контекста dp['db']
#     # user_exists = await db.check_user(message.from_user.id)