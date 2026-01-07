from config import USER_DB, PASSWORD_DB, DB_NAME, HOST
import psycopg2
from logs.set_logger import set_logger
logger = set_logger(name="db")




# Create TABLES:
def create_tables_in_db():
    connection, cursor = False, False

    try:
        # Connect to db:
        connection = psycopg2.connect(host=HOST, database=DB_NAME, user=USER_DB, password=PASSWORD_DB)

        cursor = connection.cursor()

        # Create table:
        create_table_users = '''
        CREATE TABLE IF NOT EXISTS users (
            user_id UUID PRIMARY KEY,                                                           -- UUID value
            user_glotmax VARCHAR(50) UNIQUE,                                                    -- MAX ебать его в рот..
            user_whatsapp VARCHAR(50) UNIQUE,                                                   -- WatsApp земля ему пухом..
            user_telegram BIGINT UNIQUE,                                                        -- Telegram id
            username_telegram VARCHAR(50) UNIQUE,                                               -- Telegram Username @name
            phone VARCHAR(20) UNIQUE,
            email VARCHAR(100) UNIQUE,
            name VARCHAR(50),
            description_user VARCHAR(200),                                                      -- Описание пользователя, для внутреннего использования
            source VARCHAR(200),                                                                -- Источник рекламы
            block BOOLEAN DEFAULT FALSE,                                                        -- Блок для пид..ов
            hum_quality VARCHAR(50),                                                            -- Бывает полезно, когда повторные обращения - экономит время и нервы   
            last_visit TIMESTAMP,                                                               -- Последнее посещение
            time_reg TIMESTAMP,                                                                 -- Время регистрации
            time_zone VARCHAR(10), 
            language VARCHAR(10),
            parametrs JSONB,                                                                    -- На будующее, пока хз
            admin BOOLEAN DEFAULT FALSE,
            manager BOOLEAN DEFAULT FALSE,
            master BOOLEAN DEFAULT FALSE,
            remind JSONB                                                                        -- Напоминалка, позже можно замутить..
        );
        '''
        # Executing an SQL query:
        cursor.execute(create_table_users)


        create_table_orders = '''
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            serial_number VARCHAR(50),
            status VARCHAR(50),                                                                 -- Статус заказа (новый, в работе, готов..)
            order_type VARCHAR(50),                                                             -- Тип заказа (Платный, гарантийный)
            device_type VARCHAR(50),                                                            -- Тип устройства (принтер, телефон)
            device_brand VARCHAR(50),                                                           -- Бренд устройства (Asus, Apple)
            device_model VARCHAR(100),                                                          -- Модель устройства (iPhone 16)
            equipment VARCHAR(100),                                                             -- Комплектация устройства (Зарядка)
            problem TEXT,                                                                       -- Описание проблемы
            appearance VARCHAR(100),                                                            -- Внешний вид устройства
            created_date TIMESTAMP,                                                             -- Дата приема устройства
            completion_date TIMESTAMP,                                                          -- Дата выполнения заказа
            diagnosis_before TIMESTAMP,                                                         -- Дата ожидания примерной готовности диагностики
            cost_repair DECIMAL(10, 2),                                                         -- Стоимость ремонта
            cost_diagnostics DECIMAL(10, 2),                                                    -- Стоимость диагностики
            path_photo VARCHAR(100),                                                            -- Путь к фотографиям устройства
            client_id UUID NOT NULL,                                                            -- user_id клиента заказа в UUID
            created_by BIGINT NOT NULL,                                                         -- Оформил менеджер с телеграмм id
            master UUID,                                                                        -- user_id мастера в UUID
            edit_history JSONB,                                                                 -- Позже можно цепочку изменнений вносить, кто и когда менял
            comments TEXT,                                                                      -- Комментарии по ремонту
            completed_works JSONB,                                                              -- Выполненные работы в JSON
            FOREIGN KEY (client_id) REFERENCES users(user_id)
        );
            CREATE INDEX IF NOT EXISTS idx_orders_client_id ON orders(client_id);
            CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
            CREATE INDEX IF NOT EXISTS idx_orders_serial ON orders(serial_number);
        '''
        cursor.execute(create_table_orders)


        # Saving changes:
        connection.commit()
        logger.info("Adding tables is done!")
        print("Adding tables is done!")
        return True

    except Exception as error:
        logger.error(f"Error Create Tables in DB: {error}")
        print("Error Create Tables in DB:", error)
        return False

    finally:

        # Closing the cursor and database connection
        if cursor:
            cursor.close()

        if connection:
            connection.close()

# create_tables_in_db()


# VARCHAR(n) - строковый тип данных ограничение n, TEXT - строковый тип данных ограничение в 1Гб.
# iuser_id INTEGER SERIAL PRIMARY KEY , тут SERIAL - означает, что каждый последующее число в строке будет само увеличиваться..
# Если ячейка является первичным ключем, то она автоматически добавленна в индекс, CONSTRAINT unique_user_id UNIQUE (user_id)  -- Создание уникального ограничения также создает индекс
# INTEGER  BIGINT block BOOLEAN NOT NULL DEFAULT FALSE  INTEGER  VARCHAR(100) NOT NULL UNIQUE UNIQUE
# time_zone TIMESTAMP DEFAULT CURRENT_TIMESTAMP
# UNIQUE - автоматом индексируются
# INDEX idx_name (name)  -- Создание обычного индекса на колонке name