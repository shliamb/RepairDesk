from aiogram import Router, types
from aiogram.filters import Command
# from database.worker_db import WorkerDB  # Только для аннотации типа!

router = Router()

@router.message(Command("menu"))
async def menu(message: types.Message):
    await message.answer("MENU: Я теперь в отдельном файле!")


