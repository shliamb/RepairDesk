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
from config import CANCEL, ORDER



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
    
    buttons = []
    if lang == "ru":
        desc_text = "⚙️ Выберите действие:"
        buttons.extend([
            ORDER["new_ru"],
            ORDER["activ_ru"],
            ORDER["in_work_ru"],
            ORDER["ready_ru"],
            ORDER["stat_ru"],
            CANCEL["ru"],
        ])
    else:
        desc_text = "⚙️ Select an action:"
        buttons.extend([
            ORDER["new_en"],
            ORDER["activ_en"],
            ORDER["in_work_en"],
            ORDER["ready_en"],
            ORDER["stat_en"],
            CANCEL["en"]
        ])
    await message.answer(desc_text, reply_markup = build_keyboard(buttons)) 
     






















# @router.message(F.text == "📝 Новый заказ")
# async def new_order(message: types.Message): #, state: FSMContext):
#     """ Новый заказ """
#     await message.answer(
#         "Выберите тип устройства:",
#         reply_markup = build_keyboard(["💻 Ноутбук", "🖥 ПК", "Планшет", "Видеокарта", "Материнка", "🎮 Приставка", "Процессор", "Акустика"]) # стоит вынести для удобства
#     )
