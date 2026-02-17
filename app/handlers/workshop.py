#! handlers/workshop.py python3
from logs.set_logger import set_logger
logger = set_logger(name="handlers")
from handlers.common import typing, is_manager
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from keyboards.workshop import build_keyboard
from database.orders import OrderService
from database import db
from config import UI_TEXTS, READY_STATUSES, NEW, COMPLETED_STATUSES, IN_PROGRESS_STATUSES



router = Router()
order = OrderService(db)


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


    ready = await order.count_orders_by_statuses(READY_STATUSES)
    new = await order.count_orders_by_statuses(NEW)
    complet = await order.count_orders_by_statuses(COMPLETED_STATUSES)
    in_progress = await order.count_orders_by_statuses(IN_PROGRESS_STATUSES)
    all = await order.count_orders_all()



    buttons.extend([
        UI_TEXTS[lang]["new_order"], 
        UI_TEXTS[lang]["serch_order"], 
        f"{UI_TEXTS[lang]['new_orders']} {new}", 
        f"{UI_TEXTS[lang]['in_work']} {in_progress}",
        f"{UI_TEXTS[lang]['last_orders']} {all}", 
        f"{UI_TEXTS[lang]['ready_orders']} {ready}",
        f"{UI_TEXTS[lang]['issued']} {complet}",
        UI_TEXTS[lang]['stat'], 
        UI_TEXTS[lang]["cancel"]
    ])

    await message.answer(desc_text, reply_markup = build_keyboard(buttons)) 
     
