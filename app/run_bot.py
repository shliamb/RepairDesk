from config import TELEGRAM_BOT_TOKEN, ADMIN_ID
from logs.set_logger import set_logger
logger = set_logger(name="bot")
from routers import ALL_ROUTERS
from database import db
import asyncio
from aiogram import Bot, Dispatcher, Router, types, F
# from aiogram.filters import CommandStart, Command
# from aiogram.types import Message, BotCommand, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
# from aiogram.fsm.context import FSMContext
# from aiogram.fsm.state import State, StatesGroup
# from common import day_utcnow
# import asyncpg
# import json
# from pathlib import Path
# import csv
# import docx
# import PyPDF2
# import io
# import random





bot = Bot(TELEGRAM_BOT_TOKEN, parse_mode="markdown")
dp = Dispatcher()


# Инициализация роутеров автоматом из routers.py
main_router = Router()
for router in ALL_ROUTERS:
    main_router.include_router(router)
dp.include_router(main_router)


# logger.error("HI")




# stats = await db.get_pool_stats()
# print(f"Свободно: {stats['free']}/{stats['total']} ({stats['free_percent']:.1f}%)")



#########
# Get User_ID
def user_id(action) -> int:
    return action.from_user.id


# Show Typing bot
async def typing(action) -> None:
    await bot.send_chat_action(action.chat.id, action='typing')


# Forced Start:
async def forced_start(message: types.Message)-> None:
    language_code = message.from_user.language_code
    await message.answer("🪔 Обновлен бот. Для продолжения нажмите /start." if language_code == "ru" else "🪔 Updated the bot. To continue, press /start", parse_mode="HTML")


########





# # START:
# class FormStart(StatesGroup):
#     captcha = State()


# @dp.message(FormStart.captcha)
# async def registration_telegram_user(message: Message, state: FSMContext) -> None:
#     send_data = await state.get_data()
#     cldata = send_data.get("send_data")
#     answerq = str(cldata.get("answerq"))
#     user_data = cldata.get("user_data")
#     language = user_data.get("language")

#     if message.text != answerq:
#         logger_bot.error(f"Error: user wrong captcha to registration.")
#         await message.answer("🚨 Не верный ответ, попробуй еще раз - /start" if language == "ru" else "🚨 Wrong answer, try again - /start")
#         await state.clear()
#         return

#     # confirm = await add_user(user_data)
#     # if not confirm:
#     #     logger_bot.error(f"Error bot: Don't save new user")
#     #     return

#     en_intro = (
#         "🚬 <b>Please note!</b>\n\n"
#         "The bot does not collect or store any of your personal data.\n"
#         "Even your Telegram user_id is used only in an encrypted (HMAC) and irreversible form.\n"
#         "This means that linking your identity to any data in the bot is technically impossible without your direct involvement.\n"
#     )
#     ru_intro = (
#         "🚬 <b>Обратите внимание!</b>\n\n"
#         "Бот не собирает и не хранит ваши персональные данные.\n"
#         "Даже Telegram user_id используется только в зашифрованном (HMAC) в необратимом виде.\n"
#         "Это означает, что связь между вами и данными в боте технически невозможна без вашего участия.\n"
#     )
#     await message.answer(ru_intro if language == "ru" else en_intro, parse_mode="HTML")

#     en_reg = (
#         "🎉 <b>Congratulations, you are logged in!</b>\n\n"
#         "Now you can start managing the context of your website.\n"
#     )
#     ru_reg = (
#         "🎉 <b>Поздравляю, вы в системе!</b>\n\n"
#         "Теперь можно приступить к управлению контекстом вашего сайта.\n"
#     )
#     await message.answer(ru_reg if language == "ru" else en_reg, parse_mode="HTML")
#     await state.clear()


# #### Push /start ####
# @dp.message(CommandStart())
# async def command_start_handler(message: Message, state: FSMContext) -> None:
#     await typing(message)

#     if message.from_user.is_bot:
#         await message.answer("🚔 Sorry, the bot only works with humans.")
#         return

#     # # Menu bot
#     # bot_commands = [
#     #     BotCommand(command="/forget", description="CLEAR DIALOG"),
#     #     BotCommand(command="/menu", description="MENU"),
#     #     BotCommand(command="/help", description="GUIDE"),
#     # ]
#     # await bot.set_my_commands(bot_commands)

#     user_id_value: int = user_id(message)
#     language_code = message.from_user.language_code  # ??

#     logger_bot.info(f"User_id: {user_id_value}")

#     # Не использую, не собираю, даже не знаю ..
#     # is_premium = message.from_user.is_premium  # Telegram Premium (True/False)
#     # name = message.from_user.username
#     # full_name = message.from_user.full_name
#     # first_name = message.from_user.first_name
#     # last_name = message.from_user.last_name

#     # is_on_user = await read_user(user_id_value)  # Получаем из базы

#     # if is_on_user:
#     #     lan = is_on_user.get("language")
#     #     await message.answer("🧼 Вы уже зарегистрированны." if lan == "ru" else "🧼 You are already registered.")
#     #     return

#     # Тупейшая проверка на бота
#     a, b = random.randint(1, 10), random.randint(1, 10)
#     op = random.choice(['+', '-'])
#     answerq = eval(f"{a}{op}{b}")
#     question = f'{a} {op} {b} = ?'

#     user_data = {
#         "user_id": user_id_value,
#         "last_visit": await day_utcnow(),
#         "language": language_code,
#     }

#     send_data = {'answerq': answerq, 'user_data': user_data}

#     await state.update_data(send_data=send_data)
#     await message.answer(f"{question}")
#     await state.set_state(FormStart.captcha)












async def main_bot() -> None:
    # 1. Подключаемся к БД
    await db.connect()
    #logger_bot.info("Database connected")
    
    # # 2. Можно добавить db в контекст диспетчера
    # dp['db'] = db

    
    # 3. Запускаем бота
    try:
        await dp.start_polling(bot, skip_updates=False)


    finally:
        # 4. Всегда закрываем соединение
        await db.close()
        #logger_bot.info("Database connection closed")


if __name__ == "__main__":
    try:
        asyncio.run(main_bot())
    except KeyboardInterrupt:
        #logger_bot.info("Bot stopped by user")
        pass
    except Exception as e:
        #logger_bot.error(f"Unexpected error: {e}")
        print(f"An error occurred: {e}")