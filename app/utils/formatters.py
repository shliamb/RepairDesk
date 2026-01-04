# Красивые сообщения
def format_order_info(order: dict) -> str:
    """Красивый вывод информации о заказе"""
    return f"""
📋 *Заказ #{order['id']}*
——————————————
👤 Клиент: {order['client_name']}
📱 Телефон: {order['phone']}
💻 Устройство: {order['device']}
🔧 Неисправность: {order['problem']}
⏱ Статус: {order['status']}
💵 Стоимость: {order['cost']} руб.
——————————————
    """