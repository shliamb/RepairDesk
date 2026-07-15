from telethon import TelegramClient
from config import API_ID, API_HASH

# 1. Создаем объект клиента
client = TelegramClient('repair_desk_bot', API_ID, API_HASH)

# 2. Она сама поймет, что сессии нет, подключится к Telegram 
# и попросит ввести телефон и код в терминале.
client.start()

print("Файл repair_desk_bot.session успешно создан и авторизован.")