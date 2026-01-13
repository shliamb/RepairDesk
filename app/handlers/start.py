#! handlers/start.py
from config import ADMIN_ID
from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommand
from logs.set_logger import set_logger
logger = set_logger(name="handlers")
from database.users import add_user, get_user_by_tg
from handlers.common import typing
from common import day_utcnow
import uuid
import random


router = Router()



async def bot_menu(message):
    """ Меню бота телеграмм """
    bot_commands = [
        BotCommand(command="/workshop", description="MANAG PANEL"),
        BotCommand(command="/help", description="GUIDE"),
    ]
    await message.bot.set_my_commands(bot_commands)





# START:
class FormStart(StatesGroup):
    captcha = State()


@router.message(FormStart.captcha)
async def registration_telegram_user(message: types.Message, state: FSMContext) -> None:
    """ Проверка капчи тупой и добавление пользователя """
    await typing(message)
    send_data = await state.get_data()
    answerq = str(send_data.get("answerq"))

    user_id = message.from_user.id
    lang = message.from_user.language_code

    if message.text != answerq:
        logger.error(f"Error: user wrong captcha to registration.")
        await message.answer("🚨 Не верный ответ, попробуй еще раз - /start" if lang == "ru" else "🚨 Wrong answer, try again - /start")
        await state.clear()
        return
    
    success = await add_user({
        'user_id': uuid.uuid4(),
        'user_telegram': user_id,
        'name': message.from_user.first_name,
        'language': lang,
        'admin': user_id == ADMIN_ID,
        'time_reg': await day_utcnow(),
        'real_name': message.from_user.first_name, # Админ будет менять в админке для менеджеров
    })

    if not success:
        await message.answer("Ошибка при регистрации" if lang == "ru" else "Error to registration")
        logger.error(f"Error bot: Don't save new user")
        return

    en_intro = (
        "🚬 <b>Please note!</b>\n\n"
        "The bot does not collect or store any of your personal data.\n"
        "Even your Telegram user_id is used only in an encrypted (HMAC) and irreversible form.\n"
        "This means that linking your identity to any data in the bot is technically impossible without your direct involvement.\n"
    )
    ru_intro = (
        "🚬 <b>Обратите внимание!</b>\n\n"
        "Бот не собирает и не хранит ваши персональные данные.\n"
        "Даже Telegram user_id используется только в зашифрованном (HMAC) в необратимом виде.\n"
        "Это означает, что связь между вами и данными в боте технически невозможна без вашего участия.\n"
    )
    #await message.answer(ru_intro if lang == "ru" else en_intro, parse_mode="HTML")

    en_reg = (
        "🎉 <b>Congratulations, you are logged in!</b>\n\n"
        # "Now you can start managing the context of your website.\n"
    )
    ru_reg = (
        "🎉 <b>Поздравляю, вы в системе!</b>\n\n"
        # "Теперь можно приступить к управлению контекстом вашего сайта.\n"
    )
    await message.answer(ru_reg if lang == "ru" else en_reg, parse_mode="HTML")
    await state.clear()



#### Push /start ####
@router.message(CommandStart())
async def start_router(message: types.Message, state: FSMContext):
    """ Нажатие /start """
    await typing(message)

    if message.from_user.is_bot:
        await message.answer("🚔 Sorry, the bot only works with humans.")
        return
    
    await bot_menu(message)

    user_id = message.from_user.id
    user = await get_user_by_tg(user_id)

    # print(user)

    if user:
        lang = user.get("language", message.from_user.language_code)
        await message.answer("🧼 Вы уже зарегистрированны." if lang == "ru" else "🧼 You are already registered.")
        return

    # Тупейшая проверка на бота
    a, b = random.randint(1, 10), random.randint(1, 10)
    op = random.choice(['+', '-'])
    answerq = eval(f"{a}{op}{b}")
    question = f'{a} {op} {b} = ?'

    await state.update_data(answerq=answerq)
    await message.answer(f"{question}")
    await state.set_state(FormStart.captcha)

















# @router.message(CommandStart())
# async def start_router(message: types.Message):

#     await message.bot.send_chat_action(message.chat.id, action='typing')

#     if message.from_user.is_bot:
#         await message.answer("🚔 Sorry, the bot only works with humans.")
#         return

#     user_id = message.from_user.id
#     user = await get_user_by_tg(user_id)
    
#     if user:
#         lang = user.get("language", message.from_user.language_code)
#         answer = f"{user.get("name", "Пользователь")} уже зарегистрирован" if lang == "ru" else f"{user.get("name", "User")} is already registered"
#         await message.answer(answer)
#         return

#     success = await add_user({
#         'user_id': str(uuid.uuid4()),
#         'user_telegram': user_id,
#         'name': message.from_user.first_name,
#         'language': message.from_user.language_code,
#         'admin': user_id == ADMIN_ID,
#         'time_reg': await day_utcnow()
#     })
    
#     if success:
#         await message.answer("Добавлен в базу!")
#     else:
#         await message.answer("Ошибка добавления")

