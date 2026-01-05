



class OrderService:
    def __init__(self, db):
        self.db = db
    
    async def create_order_with_check(self, user_data, device_data):
        """Создание заказа с проверками"""
        # 1. Проверяем клиента
        client = await self.db.users.get_by_phone(user_data['phone'])
        if not client:
            client = await self.db.users.create(user_data)
        
        # 2. Создаем заказ
        order_id = await self.db.orders.create(
            client_id=client['id'],
            device_data=device_data
        )
        
        # 3. Отправляем уведомления
        await self.notify_manager(order_id)
        await self.notify_client(order_id)
        
        return order_id