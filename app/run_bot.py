from config import TELEGRAM_BOT_TOKEN, USE_PROXY
from proxy.socks5proxy import SOCKS5PROXY_STRINGS
import asyncio
import aiohttp
from bot_instance import AioBot
from python_socks._errors import ProxyError
from logs.set_logger import set_logger
logger = set_logger(name="bot")
# import logging
# logging.basicConfig(level=logging.DEBUG)
# logging.getLogger('aiogram').setLevel(logging.DEBUG)
from handlers import ALL_ROUTERS
from database import db
from aiogram import Dispatcher, Router 
from telethoner import mytelethon



# В AioBot производится ротирование прокси
# При обрыве, прокси должен сам переподключиться к лушему по ping
bot_instance = AioBot(USE_PROXY, SOCKS5PROXY_STRINGS, TELEGRAM_BOT_TOKEN)

dp = Dispatcher()



    


async def init_router() -> None:
    """Инициализация роутеров автоматом 
        из handlers/__init__.py"""
    main_router = Router()
    for router in ALL_ROUTERS:
        main_router.include_router(router)
    dp.include_router(main_router)


#### Запуск Телеграмм Бота #####
async def main_bot() -> None:
    """ Главная ффункция запуска всего бота """
    await bot_instance.create_bot()
    dp.bot = bot_instance.bot
    await init_router()
    await db.connect()
    telethon_obj = asyncio.create_task(mytelethon.run())


    try:
        while True:
            try:
                if bot_instance.bot is None:
                    print("Бот не создан, ждём...")
                    await asyncio.sleep(5)
                    continue

                # Запускаем бота и Telethon одновременно
                await asyncio.gather(
                    await dp.start_polling(dp.bot, skip_updates=False),
                    telethon_obj,
                )

            except (aiohttp.ClientConnectorError, aiohttp.ClientProxyConnectionError, ProxyError):
                print("Прокси ошибка, переподключаемся...")
                await bot_instance.reconnect()
                dp.bot = bot_instance.bot
                await asyncio.sleep(5)
            except Exception as e:
                print(f"Другая ошибка: {e}")
                await bot_instance.reconnect()
                dp.bot = bot_instance.bot
                await asyncio.sleep(5)
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


