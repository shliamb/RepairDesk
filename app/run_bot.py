from config import TELEGRAM_BOT_TOKEN, ADMIN_ID
from logs.set_logger import set_logger
logger = set_logger(name="bot")
from handlers import ALL_ROUTERS
from database import db
import asyncio
from aiogram import Bot, Dispatcher, Router, types, F




bot = Bot(TELEGRAM_BOT_TOKEN, parse_mode="markdown")
dp = Dispatcher()



async def init_router() -> None:
    """Инициализация роутеров автоматом 
        из handlers/__init__.py"""
    main_router = Router()
    for router in ALL_ROUTERS:
        main_router.include_router(router)
    dp.include_router(main_router)



async def main_bot() -> None:
    await init_router()
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


