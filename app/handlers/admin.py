#! app/handler/admin.py
from handlers.common import typing, is_manager
from logs.set_logger import set_logger
logger = set_logger(name="admin")
from aiogram import Router, types, F
from aiogram.filters import Command
# from aiogram.fsm.state import State, StatesGroup
# from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
# from aiogram.fsm.context import FSMContext
from database.orders import OrderService
from config import ADMIN_ID, PATH_LOGS #, DONE, CHANGE_ORDER, CURRENCY, DEVICE_ICO, ORDER_STATUS_COLOR, ORDER_STATUS_RU, ORDER_STATUS, EDIT_ORDER, CANCEL
from keyboards.workshop import build_keyboard
from database.create_tables import create_tables_in_db
from database.deleted_tables_db import drop_all_tables_and_reset_schema
from database.json_clients_db import json_clients_db
from database import db
import os
# import json
import asyncio
from pathlib import Path
from io import StringIO, BytesIO
# from datetime import datetime
# from decimal import Decimal, InvalidOperation




router = Router()
order = OrderService(db)


# CHECK RIGHTS USER TELEGRAM
async def rights_verification(user_id: int, lang: str, message: types.Message) -> bool:
    """ Проверка прав доступа """
    if user_id in {ADMIN_ID}:
        return True
    
    if lang == "ru": await message.answer("🔐 Вы не имеете доступа!")
    else: await message.answer("🔐 You don't have access")

    logger.error(f"This {user_id} shit made an attempt to enter to Admin Panel.")
    return False
 



#### ADMIN MENU ####
####################

# ADMIN MENU:
@router.message(Command('admin'))
async def admin_menu(message: types.Message):
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id
    if not await rights_verification(user_id, lang, message): return
    
    admin_menu_text = (
        f"<b>🎛 ADMIN MENU:</b>\n\n"
        f"<b>📊 STATISTICS:</b>\n"
        f"        Info Users – /allUs\n"
        f"        Money – /allPay\n\n"
        f"<b>📝 LOGS:</b>\n"
        f"        Get logs – /logs\n\n"
        f"<b>🗳 BACKUP & RESTORE:</b>\n"
        # f"        Backup DB – /bupDb\n"
        # f"        Restore DB – /resDb\n"
        f"        Create Tab DB ☠️ – /crTabDb\n"
        f"        Down users – /dnlUsers\n"
        f"        Restore Users – /resUs\n"
        f"        Down Orders – /dnlOrd\n"
        f"        Restore Orders – /resOrd\n\n"
        # f"<b>💳 METHODS PAY:</b>\n"
        # f"        Add Metod – /addMe\n"
        # f"        Select Met – /selMet\n"
        # f"        Delete Met – /delMe\n\n"
        f"<b>🗑 CLEAR:</b>\n"
        f"        All Tabs DB ☠️ – /allDel\n"
        f"        Logs – /dLogs\n\n"
        # f"<b>📩 SENDING NEWS:</b>\n"
        # f"        Mailing – /sendN\n\n"
        # f"<b>🧪 SPECIAL:</b>\n"
        # f"        Paranoi mode – /blok!\n"
    )

    await message.answer(admin_menu_text, parse_mode="HTML")


# GET LOGS
@router.message(Command("logs"))
async def get_logs_bot(message: types.Message):
    """ Отдает все файлы логов в папке logs """
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id
    if not await rights_verification(user_id, lang, message): return

    log_dir = Path(PATH_LOGS)
    sent_any = False

    async def send_as_utf8(path: Path):
        # читаем файл
        raw = path.read_bytes()
        try:
            text = raw.decode('utf-8')
        except UnicodeDecodeError:
            text = raw.decode('cp1251', errors='replace')

        # кладём в буфер
        buf = BytesIO(text.encode('utf-8'))
        buf.name = path.stem + '_utf8.txt'   # чтоб iOS показал превью

        await message.reply_document(
            document=types.input_file.BufferedInputFile(buf.getvalue(), filename=buf.name),
            caption=path.stem
        )

    for entry in log_dir.iterdir():
        if entry.is_file() and entry.stat().st_size:
            try:
                await send_as_utf8(entry)
                sent_any = True
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"cant send {entry}: {e}")

    if not sent_any:
        if lang == "ru": await message.answer("🚫 Файлов ведения журнала нет или они пусты")
        else: await message.answer("🚫 There are no logging files or they are empty")

    
# CREATE TABLES in DB
@router.message(Command('crTabDb'))
async def create_tebles_in_db_admin(message: types.Message):
    """ Нарезает таблицы в базе """
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id
    if not await rights_verification(user_id, lang, message): return

    if create_tables_in_db(): # Синхронная
        if lang == "ru": await message.answer("🎉 Таблицы в базе данных были успешно созданы")
        else: await message.answer("🎉 Tables in the DB were created successfully")
    else:
        if lang == "ru": await message.answer("🚫 Ошибка при создании таблиц базы данных. Проверьте логи для получения подробной информации")
        else: await message.answer("🚫 Error creating DB tables. Check logs for details")
        

# FAST DELETING all TABLES in DB
@router.message(Command('allDel'))
async def delete_all_tables_in_db_admin(message: types.Message):
    """ Быстрое удаление всех таблиц базы данных """
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id
    if not await rights_verification(user_id, lang, message): return

    if await drop_all_tables_and_reset_schema():
        if lang == "ru": await message.answer("🎉 Таблицы в базе данных были успешно удалены")
        else: await message.answer("🎉 The tables in the database were successfully deleted")
    else:
        if lang == "ru": await message.answer("🚫 Ошибка при удалении всех таблиц")
        else: await message.answer("🚫 Error deleting all tables")
        

# CLEAR LOGS
@router.message(Command("dLogs"))
async def admin_clear_logs(message: types.Message):
    """ Очищение всех фалов в папке logs """
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id
    if not await rights_verification(user_id, lang, message): return

    data_folder = Path(PATH_LOGS)
    for entry in data_folder.iterdir():
        if entry.is_file() and entry.stat().st_size > 0:  # Проверяем, что файл не пустой
            file_path = str(entry.absolute())  # Получаем абсолютный путь

            try:
                with open(file_path, 'w'):
                    pass
                if lang == "ru": await message.answer(f"🗑 Файл '{file_path}' был очищен")
                else: await message.answer(f"🗑 The '{file_path}' file has been clearing.")
                await asyncio.sleep(0.5)

            except Exception as e:
                logger.error(f"Error clearing file log: {file_path}: {e}")
                if lang == "ru": await message.answer("🚫 Ошибка при удалении логов")
                else: await message.answer("🚫 Error deleting logs")



# GET CLIENTS to JSON:
@router.message(Command('dnlUsers'))
async def get_on_json_old_users(message: types.Message):
    """ Вытягиваю из DB всех клиентов в JSON """
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id
    if not await rights_verification(user_id, lang, message): return

    name_file = await json_clients_db()
    # if not name_file:
    #     await message.answer(f"No users found with money > {MIN_PAY}$ or one more pay")
    #     return

    # if os.path.exists(name_file) and os.path.getsize(name_file) > 0:
    #     await bot.send_document(message.chat.id, document=types.input_file.FSInputFile(name_file))
    # else:
    #     await bot.send_message(message.chat.id, "File (name_file) is empty or missing.")  
