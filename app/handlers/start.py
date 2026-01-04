from config import PATH_LOGS
from aiogram import Router, types
from aiogram.filters import CommandStart
from database.worker_db import WorkerDB  # Только для аннотации типа!
import uuid


from logs.set_logger import set_logger
logger = set_logger(name="db")

router = Router()

@router.message(CommandStart())
async def start_router(message: types.Message, db: WorkerDB):
    await message.answer("Я теперь в отдельном файле!")
    logger.error("Я теперь в отдельном файле!")
    logger.info("Я теперь в отдельном файле!")
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