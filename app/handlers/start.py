from config import ADMIN_ID
from aiogram import Router, types
from aiogram.filters import CommandStart
from logs.set_logger import set_logger
logger = set_logger(name="handlers")
from database.users import add_user, get_user_by_tg
import uuid


router = Router()




@router.message(CommandStart())
async def start_router(message: types.Message):

    await message.bot.send_chat_action(message.chat.id, action='typing')

    if message.from_user.is_bot:
        await message.answer("🚔 Sorry, the bot only works with humans.")
        return

    user_id = message.from_user.id
    user = await get_user_by_tg(user_id)
    
    if user:
        lang = user.get("language", message.from_user.language_code)
        answer = f"{user.get("name", "Пользователь")} уже зарегистрирован" if lang == "ru" else f"{user.get("name", "User")} is already registered"
        await message.answer(answer)
        return


    success = await add_user({
        'user_id': str(uuid.uuid4()),
        'user_telegram': user_id,
        'name': message.from_user.first_name,
        'language': message.from_user.language_code,
        'admin': user_id == ADMIN_ID,
        'time_reg': 
    })
    
    if success:
        await message.answer("Добавлен в базу!")
    else:
        await message.answer("Ошибка добавления")

