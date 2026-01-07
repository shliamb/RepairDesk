#! handlers/workshop.py python3
from logs.set_logger import set_logger
logger = set_logger(name="handlers")
from handlers.common import typing, is_manager
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
# from keyboards import wskey
from keyboards.workshop import build_keyboard



router = Router()

# class startWorkshop(StatesGroup):
#     choice = State()


@router.message(Command("workshop"))
async def workshop_panel(message: types.Message, state: FSMContext):
    """ Вход в workshop """
    await state.clear()
    await typing(message)
    user_id = message.from_user.id

    if not await is_manager(user_id):
        logger.error(f"{user_id} пытался войти в workshop")
        return
    
    await message.answer (
        "🎛 Выберите действие:\n\n",
        reply_markup = build_keyboard(["📝 Новый заказ", "📋 Активные заказы", "🔧 В работе", "✅ Готовые", "📊 Статистика"]) # стоит вынести для удобства 
    )


@router.message(F.text == "✖️ Отмена")
async def cancel(message: types.Message, state: FSMContext):
    """ Отмена """
    await state.clear() # Лишнее..
    await message.answer(
        "Отменено. Состояние сброшено.",
        reply_markup=ReplyKeyboardRemove()
    )



























# @router.message(F.text == "📝 Новый заказ")
# async def new_order(message: types.Message): #, state: FSMContext):
#     """ Новый заказ """
#     await message.answer(
#         "Выберите тип устройства:",
#         reply_markup = build_keyboard(["💻 Ноутбук", "🖥 ПК", "Планшет", "Видеокарта", "Материнка", "🎮 Приставка", "Процессор", "Акустика"]) # стоит вынести для удобства
#     )
