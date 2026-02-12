from config import TELEGRAM_BOT_TOKEN, ADMIN_ID, PROXY
# from logs.set_logger import set_logger
# logger = set_logger(name="bot")
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('aiogram').setLevel(logging.DEBUG)
from handlers import ALL_ROUTERS
from database import db
import asyncio
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.client.session.aiohttp import AiohttpSession


session = AiohttpSession(proxy=PROXY) if PROXY else None

bot = Bot(
    TELEGRAM_BOT_TOKEN,
    session=session,
    parse_mode="markdown"
)


dp = Dispatcher()





async def get_public_ip(proxy_url: str = None) -> str:
    """
    Получает внешний IP.
    Если proxy_url указан — через прокси, иначе — напрямую.
    """

    from aiohttp import ClientSession
    from aiohttp_socks import ProxyConnector

    connector = None
    if proxy_url:
        try:
            connector = ProxyConnector.from_url(proxy_url)
        except Exception as e:
            print(f"⚠️ Proxy connector failed: {e}")
    
    async with ClientSession(connector=connector) as session:
        try:
            async with session.get('https://api.ipify.org') as resp:
                ip = await resp.text()
                return ip
        except Exception as e:
            print(f"⚠️ Failed to get IP: {e}")
            return "unknown"
        
        

async def check_proxy():
    """Проверяет IP через прокси (если есть)"""
    if PROXY:
        ip = await get_public_ip(PROXY)
        print(f"🤖 Bot IP through proxy: {ip}")
        return ip
    else:
        ip = await get_public_ip()
        print(f"🤖 Bot IP (direct): {ip}")
        return ip
    


async def init_router() -> None:
    """Инициализация роутеров автоматом 
        из handlers/__init__.py"""
    main_router = Router()
    for router in ALL_ROUTERS:
        main_router.include_router(router)
    dp.include_router(main_router)



async def main_bot() -> None:
    await check_proxy()
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


