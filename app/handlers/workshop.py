#! handlers/workshop.py python3
from logs.set_logger import set_logger
logger = set_logger(name="handlers")
from handlers.common import typing, is_manager
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from keyboards.workshop import build_keyboard
from config import UI_TEXTS



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
    else:
        desc_text = "⚙️ Select an action:"

    buttons.extend([
        UI_TEXTS[lang]["new_order"], 
        UI_TEXTS[lang]["serch_order"], 
        # UI_TEXTS[lang]["activ_orders"], 
        # UI_TEXTS[lang]["in_work_orders"], 
        UI_TEXTS[lang]["ready_orders"], 
        UI_TEXTS[lang]["last_orders"], 
        UI_TEXTS[lang]["stat"],
        UI_TEXTS[lang]["cancel"]
    ])

    await message.answer(desc_text, reply_markup = build_keyboard(buttons)) 
     






















# @router.message(F.text == "📝 Новый заказ")
# async def new_order(message: types.Message): #, state: FSMContext):
#     """ Новый заказ """
#     await message.answer(
#         "Выберите тип устройства:",
#         reply_markup = build_keyboard(["💻 Ноутбук", "🖥 ПК", "Планшет", "Видеокарта", "Материнка", "🎮 Приставка", "Процессор", "Акустика"]) # стоит вынести для удобства
#     )
