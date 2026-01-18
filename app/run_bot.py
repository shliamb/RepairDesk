from config import TELEGRAM_BOT_TOKEN, ADMIN_ID
from logs.set_logger import set_logger
logger = set_logger(name="bot")
from handlers import ALL_ROUTERS
from database import db
import asyncio
from aiogram import Bot, Dispatcher, Router, types, F
# from aiogram.filters import CommandStart, Command
# from aiogram.types import Message, BotCommand, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import State, StatesGroup
# from common import day_utcnow
# import asyncpg
# import json
# from pathlib import Path
# import csv
# import docx
# import PyPDF2
# import io
# import random
from database.create_tables import create_tables_in_db




bot = Bot(TELEGRAM_BOT_TOKEN, parse_mode="markdown")
dp = Dispatcher()


# Инициализация роутеров автоматом из routers.py
main_router = Router()
for router in ALL_ROUTERS:
    main_router.include_router(router)
dp.include_router(main_router)

# logger.error("HI")
# create_tables_in_db()


async def main_bot() -> None:
    await db.connect()

    try:
        await dp.start_polling(bot, skip_updates=False)
    except asyncio.CancelledError:
        print("📢 Бот получил сигнал остановки")
        raise
    finally:
        print("🔒 Закрываем пул БД...")
        await db.close()



if __name__ == "__main__":
    try:
        asyncio.run(main_bot())
    except KeyboardInterrupt:
        print("\n🛑 Ctrl+C - остановка")
    finally:
        print("Завершение работы...")


