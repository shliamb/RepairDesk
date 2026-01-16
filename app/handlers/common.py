from database.users import get_user_by_tg

async def typing(action):
    """ Визуализация подготовки ответа бота """
    await action.bot.send_chat_action(action.chat.id, action='typing')


async def is_manager(user_id):
    """ Проверка прав для входа в workshop """
    user = await get_user_by_tg(user_id)
    if user.get("is_admin") or user.get("is_manager"):
        return True
    return False