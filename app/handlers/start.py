from aiogram import Router, types
from aiogram.filters import Command, CommandStart
from app.database.worker_db import WorkerDB  # Только для аннотации типа!
import uuid

router = Router()

@router.message(CommandStart())
async def start_router(message: types.Message, db: WorkerDB):
    await message.answer("Я теперь в отдельном файле!")
    # # db автоматически придет из контекста dp['db']
    # user_exists = await db.check_user(message.from_user.id)
    
    # if not user_exists:
    #     await db.add_user({
    #         'user_id': str(uuid.uuid4()),
    #         'user_telegram': message.from_user.id,
    #         'name': message.from_user.first_name
    #     })

    # data = {
    #     'user_id': str(uuid.uuid4()),
    #     'user_telegram': message.from_user.id,
    #     'name': message.from_user.first_name
    # }
    # print(data)
    
    # await message.answer("Привет!")



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