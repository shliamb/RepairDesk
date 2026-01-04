from config import PATH_LOGS, HOST, ADMIN_ID, USER_DB, PASSWORD_DB, DB_NAME
from logs.set_logger import set_logger
import json
import asyncpg
import asyncio
from contextlib import asynccontextmanager

 
logger = set_logger(name="db")


class WorkerDB:
    """ Work to data in DB """
    def __init__(self):
        self.pool = None


    async def connect(self):
        """ Создаем пул при запуске бота """
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                host=HOST,
                database=DB_NAME,
                user=USER_DB,
                password=PASSWORD_DB,
                min_size=5, # 5 соединений всегда готовы
                max_size=50, # максимум 50 одновременных
                max_queries=50000, # после 50к запросов - пересоздать соединение
                timeout=30 # ждать свободное соединение 30 секунд
            )
            logger.info("Database pool created")
        return self.pool
    
    
    async def close(self):
        """ Закрываем пул при остановке """
        if self.pool:
            await self.pool.close()
            self.pool = None
            logger.info("Database pool closed")


    async def get_pool_stats(self):
        """Получить статистику пула"""
        if not self.pool:
            return "Пул не инициализирован. Вызовите await db.connect()"
        
        size = await self.pool.get_size()
        used = await self.pool.get_current_connection_count()
        free = size - used
        
        return {
            "total": size,
            "used": used,
            "free": free,
            "free_percent": (free / size * 100) if size > 0 else 0
        }


    @asynccontextmanager
    async def get_connection(self):
        """ Контекстный менеджер для удобства """
        if not self.pool:
            raise RuntimeError("Database pool not initialized. Call db.connect() first")
        
        async with self.pool.acquire() as conn:
            yield conn
    

    async def add_user(self, user_data: dict) -> bool:
        """ Adding User data to Db """
        if not user_data:
            logger.error("Error add_user: User_data is empty.")
            return False
        
        user_id = user_data.get("user_id")
        if not user_id:
            logger.error("Error add_user: Where is user_id?")
            return False
        
        # Подготавливаем запрос
        keys = []
        values = []
        placeholders = []
        
        for i, (key, value) in enumerate(user_data.items(), 1):
            keys.append(key)
            values.append(value)
            placeholders.append(f"${i}")
        
        columns = ", ".join(keys)
        ph = ", ".join(placeholders)
        
        try:
            # Используем контекстный менеджер
            async with self.get_connection() as conn:
                await conn.execute(
                    f"INSERT INTO users ({columns}) VALUES ({ph})",
                    *values
                )
            return True
        except Exception as e:
            logger.error(f"Error add_user: {e}")
            return False











# # # Asinc onnection to DB:
# # async def get_connection():
# #     connection = await asyncpg.connect(
# #         host=HOST,
# #         database=DB_NAME,
# #         user=USER_DB,
# #         password=PASSWORD_DB
# #     )
# #     return connection


# # #### USERS TABLE: ####
# # ######################


# # Add user:
# async def add_user(user_data):
#     keys_list, values_list, num_list, i, connection = [], [], [], 1, None

#     user_id = user_data.get("user_id")

#     if not user_id:
#         logger.error("Error add_user: Where is user_id?")
#         return False

#     if len(user_data) < 1:  # if there is at least a user_id, let's go
#         logger.error("Error add_user: User_data is empty.")
#         return False

#     for key, value in user_data.items():
#         keys_list.append(key)
#         values_list.append(value)
#         num_list.append(f"${i}")
#         i += 1

#     keys = ", ".join(keys_list)  # <-- в строку, а * распоковывает поотдельности
#     nums = ", ".join(num_list)

#     try:
#         connection = await get_connection()
#         await connection.execute(
#             f'''
#             INSERT INTO users ({keys}) VALUES ({nums})
#             ''',
#             *values_list  # Оператор распоковки *
#         )
#         return True

#     except Exception as e:
#         logger.error(f"Error add_user: {e}")
#         return False

#     finally:
#         if connection:
#             await connection.close()


# # #Add user:
# # user_data = {
# #     "user_id": 485435943,
# #     "name": "Julia",
# #     "money": 5.0,
# # }

# # confirm = asyncio.run(add_user(user_data))
# # print(confirm)


# async def update_jsonb_field(user_id: str, field: str, key: str, value):
#     """
#     Обновляет конкретное поле в JSONB.

#     :param user_id: ID пользователя
#     :param field: Название JSONB-поля (например, "system_contents")
#     :param key: Ключ внутри JSON (например, "plan_prompt")
#     :param value: Новое значение (будет преобразовано в JSONB)
#     """
#     connection = None
#     try:
#         connection = await get_connection()
#         await connection.execute(
#             f"""
#             UPDATE users 
#             SET {field} = jsonb_set(
#                 {field},
#                 $1::text[],
#                 $2::jsonb,
#                 true  -- создать ключ, если его нет
#             )
#             WHERE user_id = $3
#             """,
#             [key],  # Путь в виде массива ['plan_prompt']
#             json.dumps(value),  # Значение преобразуется в JSON
#             user_id
#         )
#         return True
#     except Exception as e:
#         logger.error(f"Error update_jsonb_field: {e}")
#         return False
#     finally:
#         if connection:
#             await connection.close()


# # Обновляем Значения внутри system_contents если нет ключа - создаем
# #
# # data_user = asyncio.run(
# #     update_jsonb_field(
# #         user_id="647ad3aacdb5798410e87a6f6cdf96908508bcc0ac833ffcba9205ddfae7112c",
# #         field="system_contents",
# #         key="plan_prompt",
# #         value=system_plan
# #     )
# # )

# # print(data_user)


# # Добавляем новый ключ personal_prompt в sysstem_content
# # Пример: 'system_contents': '{"one_prompt": "Judge", "plan_prompt": "Еще новее", "check_prompt": null, "generate_prompt": null, "personal_prompt": {"text": "Привет", "active": true}}
# # data_user = asyncio.run(
# #     update_jsonb_field(
# #         user_id="647ad3aacdb5798410e87a6f6cdf96908508bcc0ac833ffcba9205ddfae7112c",
# #         field="system_contents",
# #         key="personal_prompt",
# #         value={"text": "Привет", "active": True}
# #     )
# # )

# # print(data_user)


# # Read user:
# async def read_user(user_id):
#     connection = None
#     try:
#         connection = await get_connection()
#         result = await connection.fetch(
#             '''
#                 SELECT * FROM users WHERE user_id = $1;
#             ''',
#             user_id,
#         )

#         if not result:
#             return False

#         return dict(*result)

#     except Exception as e:
#         logger.error(f"Error read_user: {e}")
#         return False

#     finally:
#         if connection:
#             await connection.close()


# # Read user:
# # data_user = asyncio.run(read_user("647ad3aacdb5798410e87a6f6cdf96908508bcc0ac833ffcba9205ddfae7112c"))
# # print(data_user)
# # print(data_user.get("user_id"), data_user.get("name"), data_user.get("money"))


# async def get_jsonb_field(user_id: str, field: str, key: str):
#     connection = None
#     try:
#         connection = await get_connection()
#         result = await connection.fetchval(
#             f"SELECT {field}->$1 FROM users WHERE user_id = $2",
#             key,
#             user_id
#         )
#         return json.loads(result) if result else None
#     except Exception as e:
#         logger.error(f"Error get_jsonb_field: {e}")
#         return None
#     finally:
#         if connection:
#             await connection.close()


# # data_user = asyncio.run(get_jsonb_field("647ad3aacdb5798410e87a6f6cdf96908508bcc0ac833ffcba9205ddfae7112c", "system_contents", "plan_prompt"))
# # print(data_user)


# # Update user:
# async def update_user(user_data):
#     keys_list, values_list, i, connection = [], [], 1, None

#     user_id = user_data.get("user_id")

#     if not user_id:
#         logger.error("Error update_user: Where is user_id?")
#         return False

#     if len(user_data) <= 1:  # At a minimum, we need user_id + at least one element of the change.
#         logger.error("Error update_user: User_data is empty or contains a single entry.")
#         return False

#     for key, value in user_data.items():
#         if key != "user_id":
#             keys_list.append(f"{key} = ${i}")
#             values_list.append(value)  # user_data[key])
#             i += 1

#     update_string = ", ".join(keys_list)  # <-- в строку, а * распоковывает поотдельности
#     values_list.append(user_id)

#     try:
#         connection = await get_connection()
#         await connection.execute(
#             f'''
#             UPDATE users SET {update_string} WHERE user_id = ${i};
#             ''',
#             *values_list
#         )
#         return True

#     except Exception as e:
#         logger.error(f"Error update_user: {e}")
#         return False
#     finally:
#         if connection:
#             await connection.close()


# # system_data = {
# #     "plan_prompt": None,
# #     "generate_prompt": None,
# #     "check_prompt": None,
# #     "personal_prompt": None
# # }

# # data = {
# #     "user_id": "647ad3aacdb5798410e87a6f6cdf96908508bcc0ac833ffcba9205ddfae7112c",
# #     "system_contents": json.dumps(system_data),
# # }
# # data_user = asyncio.run(update_user(data))
# # print(data_user)


# #### METHOD_PAY TABLE: ####
# ###########################

# # Read all methods_pay:
# async def read_all_methods_pay():
#     connection = None
#     try:
#         connection = await get_connection()
#         result = await connection.fetch(
#             '''
#                 SELECT * FROM methods_pay;
#             '''
#         )

#         if not result:
#             logger.error("The methodt pay is empty, sorry.")
#             return False

#         data = []
#         for record in result:
#             data.append(dict(record))
#         return data

#     except Exception as e:
#         logger.error(f"Error read_all_methods_pay: {e}")
#         return False
#     finally:
#         if connection:
#             await connection.close()


# # data = asyncio.run(read_all_methods_pay())
# # print(data)

# # if data:
# #     for n in data:
# #         print(n.get("id"))
# #         #print(n)

# # Read one methods_pay by title:
# async def read_one_methods_pay(title: str):
#     connection = None
#     try:
#         if type(title) != str:
#             logger.error("Error: input data is not str (title method pay.)")
#             return False

#         if not title:
#             logger.error("Error: Title method pay is Empty or None.")
#             return False

#         connection = await get_connection()
#         result = await connection.fetch(
#             '''
#                 SELECT * FROM methods_pay WHERE title_method_pay = $1;
#             ''',
#             title,
#         )

#         if not result:
#             return False

#         return dict(*result)

#     except Exception as e:
#         logger.error(f"Error read_one_methods_pay: {e}")
#         return False
#     finally:
#         if connection:
#             await connection.close()


# # Read one methods_pay by id:
# async def read_one_methods_pay_by_id(id: int):
#     connection = None
#     try:
#         if type(id) != int:
#             logger.error("Error: input data is not int (id method pay.)")
#             return False

#         connection = await get_connection()
#         result = await connection.fetch(
#             '''
#                 SELECT * FROM methods_pay WHERE id = $1;
#             ''',
#             id,
#         )

#         if not result:
#             return False

#         return dict(*result)

#     except Exception as e:
#         logger.error(f"Error read_one_methods_pay_by_id: {e}")
#         return False
#     finally:
#         if connection:
#             await connection.close()


# # Read one methods_pay by use == True:
# async def read_one_methods_pay_by_use(place_of_use):
#     connection = None
#     try:
#         connection = await get_connection()
#         result = await connection.fetch(
#             f'''
#                 SELECT * FROM methods_pay WHERE {place_of_use} = $1;
#             ''',
#             True,
#         )

#         if not result:
#             return False

#         return dict(*result)

#     except Exception as e:
#         logger.error(f"Error read_one_methods_pay_by_use: {e}")
#         return False
#     finally:
#         if connection:
#             await connection.close()


# # Read one method pay by USE:
# # i = "use_mircard"
# # data = asyncio.run(read_one_methods_pay_by_use(i))
# # print(data)
# # print(data.get(f"counts"))


# # Deleted one methods_pay:
# async def deleted_one_methods_pay(id):
#     connection = None
#     try:
#         if type(id) != int:
#             logger.error("Error: input data is not int (id method pay.)")
#             return False

#         if not id:
#             logger.error("Error: Title method pay is Empty or None.")
#             return False

#         connection = await get_connection()
#         await connection.execute(
#             '''
#                 DELETE FROM methods_pay WHERE id = $1;
#             ''',
#             id,
#         )

#         return True

#     except Exception as e:
#         logger.error(f"Error deleted_one_methods_pay: {e}")
#         return False
#     finally:
#         if connection:
#             await connection.close()


# # Add methods_pay:
# async def add_methods_pay(pay_data):
#     keys_list, values_list, num_list, i, connection = [], [], [], 1, None

#     if len(pay_data) <= 1:
#         logger.error("Error: User_data is empty.")
#         return False

#     for key, value in pay_data.items():
#         keys_list.append(key)
#         values_list.append(value)
#         num_list.append(f"${i}")
#         i += 1

#     keys = ", ".join(keys_list)  # <-- в строку, а * распоковывает поотдельности
#     nums = ", ".join(num_list)

#     try:
#         connection = await get_connection()
#         await connection.execute(
#             f'''
#             INSERT INTO methods_pay ({keys}) VALUES ({nums})
#             ''',
#             *values_list  # Оператор распоковки *
#         )
#         return True

#     except Exception as e:
#         logger.error(f"Error add_methods_pay: {e}")
#         return False

#     finally:
#         if connection:
#             await connection.close()


# # Update methods_pay by id:
# async def update_methods_pay(pay_data):
#     keys_list, values_list, i, connection = [], [], 1, None

#     id = pay_data.get("id")

#     if not id:
#         logger.error("Error update_methods_pay: Where is id?")
#         return False

#     if len(pay_data) <= 1:  # At a minimum, we need id + at least one element of the change.
#         logger.error("Error update_methods_pay: pay_data is empty or contains a single entry.")
#         return False

#     for key, value in pay_data.items():
#         if key != "id":
#             keys_list.append(f"{key} = ${i}")
#             values_list.append(value)  # user_data[key])
#             i += 1

#     update_string = ", ".join(keys_list)  # <-- в строку, а * распоковывает поотдельности
#     values_list.append(id)

#     try:
#         connection = await get_connection()
#         await connection.execute(
#             f'''
#             UPDATE methods_pay SET {update_string} WHERE id = ${i};
#             ''',
#             *values_list
#         )
#         return True


#     except Exception as e:
#         logger.error(f"Error update_methods_pay: {e}")
#         return False

#     finally:
#         if connection:
#             await connection.close()


# # # Add methods_pay:
# # pay_data = {
# #     # "date": ,
# #     "title_method_pay": "White",
# #     "counts": 1,
# #     "method_pay": "С вас 3 пирожка и это официально, я нарисую чек!",
# # }

# # Deleted:
# # confirm = asyncio.run(deleted_one_methods_pay("White"))
# # print(confirm)

# # # Add:
# # confirm = asyncio.run(add_methods_pay(pay_data))
# # print(confirm)

# # Read all:
# # data = asyncio.run(read_all_methods_pay())
# # print(data)

# # # Read one method pay by USE:
# # data = asyncio.run(read_one_methods_pay_by_use())
# # print(data)

# # # Update row use to id:
# # pay_data = {
# #     "id": 1,
# #     "use": True,
# # }
# # data1 = asyncio.run(update_methods_pay(pay_data))
# # print(data1)

# # # Read by id:
# # data = asyncio.run(read_one_methods_pay_by_id(1))
# # print(data)

# # # Read for title record:
# # data = asyncio.run(read_one_methods_pay("White"))
# # print(data)


# #### PAYMENTS TABLE: ####
# #########################


# # # Read all payments for one user_id:
# # async def read_all_payments_for_user_id(user_id):
# #     connection = None
# #     try:
# #         connection = await get_connection()
# #         result = await connection.fetch(
# #             '''
# #                 SELECT * FROM payments WHERE user_id = $1;
# #             ''',
# #             user_id
# #         )

# #         if not result:
# #             print(f"User {user_id} not pay.")
# #             return False

# #         data = []
# #         for record in result:
# #             data.append(dict(record))

# #         # if len(data) == 1:
# #         #     data = dict(*result)

# #         return data

# #     except Exception as e:
# #         print(f"Error read_all_payments_for_user_id: {e}")
# #         return False
# #     finally:
# #         if connection is not None:
# #             await connection.close()


# # Read all payments:
# async def read_all_payments():
#     connection = None
#     try:
#         connection = await get_connection()
#         result = await connection.fetch(
#             '''
#                 SELECT * FROM payments;
#             '''
#         )

#         if not result:
#             logger.error("Users not pay.")
#             return False

#         data = []
#         for record in result:
#             data.append(dict(record))

#         # if len(data) == 1:
#         #     data = dict(*result)

#         return data

#     except Exception as e:
#         logger.error(f"Error read_all_payments: {e}")
#         return False
#     finally:
#         if connection:
#             await connection.close()


# # # Read all payments:
# # data = asyncio.run(read_all_payments())
# # print(data)


# # Add payments:
# async def add_payments(payments):
#     keys_list, values_list, num_list, i, connection = [], [], [], 1, None

#     if len(payments) <= 1:
#         logger.error("Error: User_data is empty.")
#         return False

#     if payments.get("user_id") is None:
#         logger.error("Error: User_id is empty.")
#         return False

#     for key, value in payments.items():
#         keys_list.append(key)
#         values_list.append(value)
#         num_list.append(f"${i}")
#         i += 1

#     keys = ", ".join(keys_list)  # <-- в строку, а * распоковывает поотдельности
#     nums = ", ".join(num_list)

#     try:
#         connection = await get_connection()
#         await connection.execute(
#             f'''
#             INSERT INTO payments ({keys}) VALUES ({nums})
#             ''',
#             *values_list  # Оператор распоковки *
#         )
#         return True

#     except Exception as e:
#         logger.error(f"Error add_payments: {e}")
#         return False

#     finally:
#         if connection:
#             await connection.close()


# # Deleted all payments:
# async def deleted_all_payments():
#     connection = None
#     try:
#         connection = await get_connection()
#         await connection.execute(
#             '''
#                 DELETE FROM payments;
#             '''
#         )
#         return True

#     except Exception as e:
#         logger.error(f"Error deleted_all_payments: {e}")
#         return False
#     finally:
#         if connection:
#             await connection.close()


# # # Add payments:
# # payments = {
# #     "user_id": 1666495,
# #     # "date": ,
# #     "title_method_pay": "White",
# #     "sum": 126,
# # }

# # # Add payments:
# # data = asyncio.run(add_payments(payments))
# # print(data)

# # # Resd one payments for her user_id:
# # data = asyncio.run(read_all_payments_for_user_id(1666495))
# # print(data)

# # # Deleted all records payments:
# # data = asyncio.run(deleted_all_payments())
# # print(data)

# # # Read all payments:
# # data = asyncio.run(read_all_payments())
# # print(data)


# #### STATISTICS TABLE: ####
# ###########################


# # Add statistics:
# async def add_statistics(statistics_data):
#     keys_list, values_list, num_list, i, connection = [], [], [], 1, None

#     user_id = statistics_data.get("user_id")

#     if not user_id:
#         logger.error("Error add_statistics: Where is user_id?")
#         return False

#     if len(statistics_data) < 1:  # if there is at least a user_id, let's go
#         logger.error("Error add_statistics: Statistics_data is empty.")
#         return False

#     for key, value in statistics_data.items():
#         keys_list.append(key)
#         values_list.append(value)
#         num_list.append(f"${i}")
#         i += 1

#     keys = ", ".join(keys_list)  # <-- в строку, а * распоковывает поотдельности
#     nums = ", ".join(num_list)

#     try:
#         connection = await get_connection()
#         await connection.execute(
#             f'''
#             INSERT INTO statistics ({keys})
#             VALUES ({nums})
#             ''', *values_list  # Оператор распоковки *
#         )
#         return True

#     except Exception as e:
#         logger.error(f"Error add_statistics: {e}")
#         return False

#     finally:
#         if connection:
#             await connection.close()


# # # Add statistics:
# # statistics_data = {
# #     "user_id": 485435943,
# #     "model": "gpt-o",
# #     "tokens": 10,
# # }

# # confirm = asyncio.run(add_statistics(statistics_data))
# # print(confirm)


# # # Read statistics by user_id:
# async def read_statistics(user_id):
#     connection = None
#     try:
#         connection = await get_connection()
#         result = await connection.fetch(
#             f'''
#                 SELECT * FROM statistics WHERE user_id = $1 ORDER BY id DESC LIMIT {LIMIT_STAT};
#             ''',
#             user_id,
#         )

#         if not result:
#             return False

#         data = []
#         for record in result:
#             data.append(dict(record))
#         return data

#     except Exception as e:
#         logger.error(f"Error read_statistics: {e}")
#     finally:
#         if connection:
#             await connection.close()


# # # Read statistics by user_id:
# # data_user = asyncio.run(read_statistics(1666495))
# # #print(data_user)
# # for one in data_user:
# #     print(one.get("user_id"), one.get("model"), one.get("tokens"))


# # Clear statistics:
# async def clear_statistics():
#     connection = None

#     date_now = None
#     # date_now = функция получения даты + какое то условие, что бы давался лимит 3 месяца допустим

#     if not date_now:
#         logger.error("Error date: Today's date has not been received")
#         return False

#     try:
#         connection = await get_connection()
#         await connection.execute(
#             f'''
#             DELETE FROM statistics WHERE date < $1;
#             ''',
#             (date_now,)
#         )
#         return True

#     except Exception as e:
#         logger.error(f"Error clear_statistics {e}")
#         return False

#     finally:
#         if connection:
#             await connection.close()


# # Fast delete Tab Statistic:
# async def fast_delete_statistics_tab():
#     connection = None

#     try:
#         connection = await get_connection()
#         await connection.execute(
#             f'''
#             TRUNCATE TABLE statistics;
#             ''',
#         )
#         return True

#     except Exception as e:
#         logger.error(f"Error fast_delete_statistics_tab {e}")
#         return False

#     finally:
#         if connection:
#             await connection.close()


# #### ADMIN PARSE TABLE: ####
# ###########################

# # Read all users:
# async def read_all_users():
#     connection = None
#     try:
#         connection = await get_connection()
#         result = await connection.fetch(
#             '''
#                 SELECT * FROM users;
#             '''
#         )

#         if not result:
#             return False

#         data = []
#         for record in result:
#             data.append(dict(record))

#         return data

#     except Exception as e:
#         logger.error(f"Error read_all_users: {e}")
#     finally:
#         if connection:
#             await connection.close()


# # data_all_users = asyncio.run(read_all_users())
# # print(data_all_users)

# # for user in data_all_users:
# #     print(user.get("user_id"), user.get("name"), user.get("money"))


# # Read all users whu pay and have money:
# async def json_old_users():
#     connection = None
#     try:
#         connection = await get_connection()
#         result = await connection.fetch(
#             '''
#                 SELECT * FROM users WHERE paid > $1 OR money > $2;
#             ''',
#             0, GIFT
#         )

#         if not result:
#             return False

#         data = []
#         for record in result:
#             data.append(dict(record))

#         return data

#     except Exception as e:
#         logger.error(f"Error json_old_users: {e}")
#         return False
#     finally:
#         if connection:
#             await connection.close()


# # print(asyncio.run(json_old_users()))


# # Fast delete ALL Tabs:
# async def drop_all_tables_and_reset_schema():
#     connection = None
#     try:
#         connection = await get_connection()
#         # Удаляем схему public со всеми объектами и создаём её заново
#         await connection.execute("DROP SCHEMA public CASCADE;")
#         await connection.execute("CREATE SCHEMA public;")
#         # Возвращаем стандартные права (без указания конкретной роли)
#         await connection.execute("GRANT ALL ON SCHEMA public TO PUBLIC;")
#         return True
#     except Exception as e:
#         logger.error(f"Error in drop_all_tables_and_reset_schema: {e}")
#         return False
#     finally:
#         if connection:
#             await connection.close()