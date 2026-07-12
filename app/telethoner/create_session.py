from telethon import TelegramClient

api_id = 380000       # Твой старый api_id
api_hash = 'e45...'  # Твой старый api_hash

# 2. Создаем объект клиента
client = TelegramClient('repair_desk_bot', api_id, api_hash)

# 3. Она сама поймет, что сессии нет, подключится к Telegram 
# и попросит тебя ввести телефон и код в терминале.
client.start()

print("Ура! Файл repair_desk_bot.session успешно создан и авторизован.")