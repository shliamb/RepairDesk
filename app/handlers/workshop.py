#! handlers/workshop.py python3
from logs.set_logger import set_logger
logger = set_logger(name="handlers")
from handlers.common import typing
from database.users import get_user_by_tg
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup
# from keyboards import wskey
from keyboards.workshop import build_keyboard



router = Router()


async def is_manager(user_id):
    """ Проверка прав для входа в workshop """
    user = await get_user_by_tg(user_id)
    if user.get("admin") or user.get("manager"):
        return True
    return False




@router.message(Command("workshop"))
async def workshop_panel(message: types.Message):
    """ Вход в workshop """
    await typing(message)
    user_id = message.from_user.id

    if not await is_manager(user_id):
        logger.error(f"{user_id} пытался войти в workshop")
        return
    
    await message.answer (
        "🎛 Выберите действие:\n\n",
        reply_markup = build_keyboard(["📝 Новый заказ", "📋 Активные заказы", "🔧 В работе", "✅ Готовые", "📊 Статистика"])
    )


@router.message(F.text == "📝 Новый заказ")
async def new_order(message: types.Message): #, state: FSMContext):
    """ Новый заказ """
    await message.answer(
        "Выберите тип устройства:",
        reply_markup = build_keyboard(["💻 Ноутбук", "🖥 ПК", "Планшет", "Видеокарта", "Материнка", "🎮 Приставка", "Процессор", "Акустика"]) 
    )


@router.message(F.text == "✖️ Отмена")
async def cancel(message: types.Message): #, state: FSMContext):
    """ Отмена """
    await message.answer(
        "Отменено. Состояние сброшено.",
        reply_markup=ReplyKeyboardRemove()
    )