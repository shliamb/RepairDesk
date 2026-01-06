

async def typing(action):
    """ Визуализация подготовки ответа бота """
    await action.bot.send_chat_action(action.chat.id, action='typing')