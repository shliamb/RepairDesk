from config import TIME_CORRECTION, PATH_LOGS
from datetime import datetime, timezone, timedelta
import random
import string
import os
import re
import base64
import aiofiles
import asyncio
# from io import BytesIO
from app.logs.set_logger import setup_logger

logger_bot = setup_logger('bot', f'{PATH_LOGS}bot.log')

# from worker_db import add_statistics, update_user


# # Для удобства получения из dict:
# class DictObj:
#     def __init__(self, d):
#         self.__dict__.update(d)  # Автоматически создаёт атрибуты

#     # Возвращает None вместо ошибки, если атрибута нет
#     def __getattr__(self, item):
#         return None


# GET DAY AND TIME
async def day_utcnow():
    utc_zone = timezone.utc
    a = datetime.now(timezone.utc).replace(tzinfo=utc_zone)
    a = a + timedelta(hours=TIME_CORRECTION)
    day_str = a.strftime("%Y-%m-%d %H:%M:%S")
    day = datetime.strptime(day_str, '%Y-%m-%d %H:%M:%S')
    # logger_bot.info("info: Getting the day and time from the server")
    return day or None


# UNFORMAT TIME
async def unformat_date(date):
    day_now = str(date.strftime("%Y-%m-%d"))
    time_now = float(date.strftime("%H.%M"))
    return day_now, time_now


# Remove File OS Async
async def remove_file_os(file_path):
    loop = asyncio.get_running_loop()

    if await loop.run_in_executor(None, os.path.exists, file_path):
        await loop.run_in_executor(None, os.remove, file_path)
        logger_bot.info(f"The {file_path} file was successfully deleted.")
        return True
    else:
        logger_bot.error(f"The {file_path} file does not exist.")
        return False


# Encode the image
async def encode_file(file_path):
    async with aiofiles.open(file_path, "rb") as file:
        content = await file.read()
        return base64.b64encode(content).decode('utf-8')


# Async save file
async def write_file(file, file_path):
    async with aiofiles.open(file_path, "wb") as buffer:
        while content := await file.read(1024):  # Читаем файл порциями по 1024 байта
            await buffer.write(content)
            return


# Random name to file:
def random_name() -> str:
    return f"{random.randint(101, 190)}-{random.choice(string.ascii_letters)}-{random.randint(101, 190)}"



# logger_bot.error("fdf")

# print(f'{PATH_LOGS}bot.log')
