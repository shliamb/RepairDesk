#! handlers/workshop.py python3
from logs.set_logger import set_logger
logger = set_logger(name="handlers")
from handlers.common import typing, is_manager
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup
# from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
# from keyboards import wskey
from keyboards.workshop import build_keyboard
from config import CANCEL



router = Router()


# WORKSHOP
@router.message(Command("workshop"))
async def workshop_panel(message: types.Message, state: FSMContext):
    """ Вход в workshop """
    await state.clear()
    await typing(message)
    lang = message.from_user.language_code
    user_id = message.from_user.id

    if not await is_manager(user_id):
        logger.error(f"{user_id} You don't have access")
        await message.answer("🔐 You don't have access")
        return
    
    if lang == "ru": await message.answer("⚙️ Выберите действие:", reply_markup = build_keyboard(["📝 Новый заказ", "📋 Активные заказы", "🔧 В работе", "✅ Готовые", "📊 Статистика", CANCEL["en"]])) 
    else: await message.answer("👨🏻‍💼 Find a client or create anew:", reply_markup = build_keyboard(["📝 New order", "📋 Active orders", "🔧 In progress", "✅ Ready", "📊 Statistics", CANCEL["en"]])) 

# CANCEL STATE & KEYBOARD
@router.message((F.text == CANCEL["ru"]) | (F.text == CANCEL["en"]))
async def cancel(message: types.Message, state: FSMContext): 
    """ Отмена / Cancelled """
    await typing(message)
    lang = message.from_user.language_code
    await state.clear()
    if lang == "ru": await message.answer("🚫 Отменено", reply_markup=ReplyKeyboardRemove())
    else: await message.answer("🚫 Cancelled", reply_markup=ReplyKeyboardRemove())

























# @router.message(F.text == "📝 Новый заказ")
# async def new_order(message: types.Message): #, state: FSMContext):
#     """ Новый заказ """
#     await message.answer(
#         "Выберите тип устройства:",
#         reply_markup = build_keyboard(["💻 Ноутбук", "🖥 ПК", "Планшет", "Видеокарта", "Материнка", "🎮 Приставка", "Процессор", "Акустика"]) # стоит вынести для удобства
#     )
