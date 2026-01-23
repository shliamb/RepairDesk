#! app/handler/admin.py
from handlers.common import typing, is_manager
from logs.set_logger import set_logger
logger = set_logger(name="admin")
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from database.orders import OrderService
from config import DOWNLOAD, PATH_JSON, ADMIN_ID, PATH_LOGS #, DONE, CHANGE_ORDER, CURRENCY, DEVICE_ICO, ORDER_STATUS_COLOR, ORDER_STATUS_RU, ORDER_STATUS, EDIT_ORDER, CANCEL
from keyboards.workshop import build_keyboard
from database.create_tables import create_tables_in_db
from database.deleted_tables_db import drop_all_tables_and_reset_schema
from database.json_clients_db import get_json_clients_db, push_json_clients_in_db
from database.json_orders_db import get_json_orders_db, push_json_orders_in_db
from database.migration_livesklad import parse_xls_get_json
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
        f"        • Info Users – /allUs\n"
        f"        • Money – /allPay\n\n"
        f"<b>📝 LOGS:</b>\n"
        f"        • Get logs – /logs\n\n"
        f"<b>🗳 BACKUP & RESTORE:</b>\n"
        # f"        Backup DB – /bupDb\n"
        # f"        Restore DB – /resDb\n"
        f"        • Create Tab DB – /crTabDb\n"
        f"        • Down users – /dnlUsers\n"
        f"        • Add Users – /resUs\n"
        f"        • Down Orders – /dnlOrd\n"
        f"        • Add Orders – /resOrd\n"
        f"        • Get JSON from livesklad – /Skl\n\n"
        # f"<b>💳 METHODS PAY:</b>\n"
        # f"        Add Metod – /addMe\n"
        # f"        Select Met – /selMet\n"
        # f"        Delete Met – /delMe\n\n"
        f"<b>🗑 CLEAR:</b>\n"
        f"        • All Tabs DB ☠️ – /allDel\n"
        f"        • Logs – /dLogs\n\n"
        # f"<b>📩 SENDING NEWS:</b>\n"
        # f"        Mailing – /sendN\n\n"
        # f"<b>🧪 SPECIAL:</b>\n"
        # f"        Paranoi mode – /blok!\n"
    )

    admin_menu_text_ru = (
        f"<b>🎛 АДМИН МЕНЮ:</b>\n\n"
        f"<b>📊 СТАТИСТИКА:</b>\n"
        f"        • Инф. Польз. – /allUs\n"
        f"        • Деньги – /allPay\n\n"
        f"<b>📝 ЛОГИ:</b>\n"
        f"        • Получить логи – /logs\n\n"
        f"<b>🗳 БЕКАП и ЗАПИСЬ:</b>\n"
        # f"        Backup DB – /bupDb\n"
        # f"        Restore DB – /resDb\n"
        f"        • Созд. Таблицы Базы – /crTabDb\n"
        f"        • Скачать Польз. – /dnlUsers\n"
        f"        • Доб. Польз. – /resUs\n"
        f"        • Скачать Заказы – /dnlOrd\n"
        f"        • Доб. Заказы – /resOrd\n"
        f"        • Созд. JSON из livesklad – /Skl\n\n"
        # f"<b>💳 METHODS PAY:</b>\n"
        # f"        Add Metod – /addMe\n"
        # f"        Select Met – /selMet\n"
        # f"        Delete Met – /delMe\n\n"
        f"<b>🗑 ОЧИСТИТЬ:</b>\n"
        f"        • Все Табл. Базы ☠️ – /allDel\n"
        f"        • Логи – /dLogs\n\n"
        # f"<b>📩 SENDING NEWS:</b>\n"
        # f"        Mailing – /sendN\n\n"
        # f"<b>🧪 SPECIAL:</b>\n"
        # f"        Paranoi mode – /blok!\n"
    )

    if lang == "ru": await message.answer(admin_menu_text_ru, parse_mode="HTML")
    else: await message.answer(admin_menu_text, parse_mode="HTML")


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
async def get_json_users(message: types.Message):
    """ Вытягиваю из DB всех клиентов в JSON """
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id
    if not await rights_verification(user_id, lang, message): return

    filepath = await get_json_clients_db()

    if not filepath:
        if lang == "ru": await message.answer("🚫 Ошибка при сборе данных пользователей в JSON файл")
        else: await message.answer("🚫 Error when collecting user data in a JSON file")
        return

    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:

        await message.reply_document(
            document=types.input_file.FSInputFile(filepath),
            caption="Get JSON file an USERS DATA"
        )


# GET ORDERS to JSON:
@router.message(Command('dnlOrd'))
async def get_json_orders(message: types.Message):
    """ Вытягиваю из DB все Заказы в JSON """
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id
    if not await rights_verification(user_id, lang, message): return

    filepath = await get_json_orders_db()

    if not filepath:
        if lang == "ru": await message.answer("🚫 Ошибка при сборе данных заказов в JSON файл")
        else: await message.answer("🚫 Error when collecting orders data in a JSON file")
        return

    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:

        await message.reply_document(
            document=types.input_file.FSInputFile(filepath),
            caption="Get JSON file an ORDERS DATA"
        )




# PUSH JSON DATA to DB:
class Restore_json(StatesGroup):
    load_json = State()


# PARSE JSON DATA and SAVE to DB
@router.message(Restore_json.load_json)
async def json_to_db(message: types.Message, state: FSMContext):
    """ Запуск переноса из JSON/XLSX в DB """
    await typing(message)
    lang = message.from_user.language_code
    send_data = await state.get_data()
    restore = send_data.get("restore")
    os.makedirs(DOWNLOAD, exist_ok=True)

    # await message.bot.session.close() # Сбрасываю все сессии бота, перед работой с DB, не уверен что необходимо..

    # USERS
    if restore == "users":
        if not message.document or not message.document.file_name.endswith('.json'):
            if lang == "ru": await message.answer("🚫 Прикрепите JSON файл пользователей")
            else: await message.answer("🚫 Attach a JSON file users")
            return
        
        filename = os.path.join(DOWNLOAD, f"uploaded-json-users.json")
        filepath = os.path.join(os.getcwd(), filename)
        await message.bot.download(message.document, filepath)

        good_case, bad_case = await push_json_clients_in_db(filepath)
        if good_case is not False or bad_case is not False:
            if lang == "ru": await message.answer(f"🎉 Результаты переноса из JSON пользователей: успешно ({good_case}), ошибка ({bad_case})")
            else: await message.answer(f"🎉 The results of transferring users from JSON: successful ({good_case}), error ({bad_case})")
        else:
            if lang == "ru": await message.answer("🚫 Ошибка переноса из JSON пользователей")
            else: await message.answer("🚫 Error transferring users from JSON")

    # ORFDERS
    elif restore == "orders":
        if not message.document or not message.document.file_name.endswith('.json'):
            if lang == "ru": await message.answer("🚫 Прикрепите JSON файл заказов")
            else: await message.answer("🚫 Attach a JSON file orders")
            return
        
        filename = os.path.join(DOWNLOAD, f"uploaded-json-orders.json")
        filepath = os.path.join(os.getcwd(), filename)
        await message.bot.download(message.document, filepath)

        good_case, bad_case = await push_json_orders_in_db(filepath)
        if good_case is not False or bad_case is not False:
            if lang == "ru": await message.answer(f"🎉 Результаты переноса из JSON заказов: успешно ({good_case}), ошибка ({bad_case})")
            else: await message.answer(f"🎉 The results of transferring orders from JSON: successful ({good_case}), error ({bad_case})")
        else:
            if lang == "ru": await message.answer("🚫 Ошибка переноса из JSON заказов")
            else: await message.answer("🚫 Error transferring orders from JSON")

    # LIVESKLAD
    elif restore == "livesklad":
        if not message.document or not message.document.file_name.lower().endswith(('.xlsx', '.xls')):
            if lang == "ru": await message.answer("🚫 Прикрепите XLSX файл из livesklad")
            else: await message.answer("🚫 Attach a XLSX file orders from livesklad")
            return
        
        filename = os.path.join(DOWNLOAD, f"uploaded-xlsx-livesklad.xlsx")
        filepath = os.path.join(os.getcwd(), filename)
        await message.bot.download(message.document, filepath)

        users_filepath, orders_filepath = await parse_xls_get_json(filepath)

        for file_path in [users_filepath, orders_filepath]:
            await message.reply_document(
                document=types.input_file.FSInputFile(file_path),
                caption="Get JSON file livesklad"
            )
    
    await state.clear()


# PUSH JSON USERS DATA to DB:
@router.message(Command('resUs'))
async def push_json_users_to_db(message: types.Message, state: FSMContext):
    """ Перенос JSON данных клиентов в базу """
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id
    if not await rights_verification(user_id, lang, message): return

    await state.update_data(restore="users")
    if lang == "ru": await message.answer("📎 Прикрепите JSON файл:", reply_markup=ReplyKeyboardRemove())
    else: await message.answer("📎 Attach a JSON file:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Restore_json.load_json)


# PUSH JSON ORDERS DATA to DB:
@router.message(Command('resOrd'))
async def push_json_orders_to_db(message: types.Message, state: FSMContext):
    """ Перенос JSON данных заказов в базу """
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id
    if not await rights_verification(user_id, lang, message): return

    await state.update_data(restore="orders")
    if lang == "ru": await message.answer("📎 Прикрепите JSON файл:", reply_markup=ReplyKeyboardRemove())
    else: await message.answer("📎 Attach a JSON file:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Restore_json.load_json)


# PUSH PARSE DATA FROM XLSX LIVESKLAD:
@router.message(Command('Skl'))
async def parse_livesklad(message: types.Message, state: FSMContext):
    """ Парсинг файла xlsx от LiveSklad 
        сбор клиентов и заказов в отдельные JSON файлы, 
        их через админку можно длбавить в базу """
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id
    if not await rights_verification(user_id, lang, message): return

    await state.update_data(restore="livesklad")
    if lang == "ru": await message.answer("📎 Прикрепите XLSX файл от livesklad:", reply_markup=ReplyKeyboardRemove())
    else: await message.answer("📎 Attach a XLSX file from livesklad:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Restore_json.load_json)
















# # Admin Restore Users to DB in Json
# class Restore_json(StatesGroup):
#     load_json = State()

# # Resore OLD users to DB:
# @dp.message(Command('resUs'))
# async def restore_old_users_admin(message: types.Message, state: FSMContext):
#     await typing(message)
#     id = user_id(message)

#     if id != ADMIN_ID:
#         logger_bot.error(f"This {id} shit made an attempt to enter to Admin Panel.")
#         return

#     await bot.send_message(message.chat.id, "Attach and send the necessary json file for recovery Users to DB.", parse_mode="Markdown", reply_markup=ReplyKeyboardRemove()) 
#     await state.set_state(Restore_json.load_json)


# @dp.message(Restore_json.load_json)
# async def load_json_users_to_db(message: Message, state: FSMContext):
#     await typing(message)
#     id = user_id(message)
    
#     if not isinstance(message.document, types.Document):
#         await message.answer("It's not a documents")
#         return

#     file_extension = message.document.file_name.split('.')[-1]
#     allowed_extensions = ['json']

#     if file_extension not in allowed_extensions:
#         await message.answer("You have sent a non-json extension file.")
#         return 

#     file_name = f"uploaded-json-restore-users.json"
#     file_path = f"{PATH_JSON_USERS}{file_name}"
#     await bot.download(message.document, file_path)

#     await bot.session.close()
#     await dp.storage.close()


#     res_update_db = await restore_loyal_users_to_db(file_path)

#     if res_update_db:
#         await message.answer(f"Results of adding regular Users to DB:\n{res_update_db}")
#     else:
#         await message.answer(f"Error of adding regular Users to DB:\n{res_update_db}")

#     await state.clear()