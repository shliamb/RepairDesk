from keys import USER_DB, PASSWORD_DB, DB_NAME
from config import HOST, PATH_LOGS
import psycopg2
from set_logger import setup_logger

logger_db = setup_logger('db', f'{PATH_LOGS}db.log')


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
            user_id UUID PRIMARY KEY,       -- UUID value
            user_glotmax VARCHAR(50) UNIQUE,
            user_whatsapp VARCHAR(50) UNIQUE,
            user_telegram BIGINT UNIQUE,                    -- telegram id
            phone VARCHAR(20) UNIQUE,
            email VARCHAR(100) UNIQUE,
            surname VARCHAR(50),                            -- фамилия
            name VARCHAR(50),
            description_user VARCHAR(200),
            source VARCHAR(200),                            -- источник рекламы
            block BOOLEAN DEFAULT FALSE,                    -- блок пид..ов
            hum_quality VARCHAR(50),          
            last_visit TIMESTAMP,
            time_reg TIMESTAMP,
            time_zone VARCHAR(10), 
            language VARCHAR(10),
            system JSONB
        );
        '''
        # Executing an SQL query:
        cursor.execute(create_table_users)


        create_table_managers = '''
        CREATE TABLE IF NOT EXISTS managers (
            manager_id BIGINT PRIMARY KEY,                  -- manager_id = telegram id
            surname VARCHAR(50) NOT NULL,                   -- фамилия
            name VARCHAR(50),
            description_manager VARCHAR(200),       
            last_visit TIMESTAMP,
            time_reg TIMESTAMP,
            time_zone VARCHAR(10), 
            language VARCHAR(10),
            admin BOOLEAN DEFAULT FALSE,
            system JSONB
        );
        '''
        cursor.execute(create_table_managers)

        create_table_orders = '''
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            serial_number VARCHAR(50),
            status VARCHAR(50) DEFAULT 'new',
            device_type VARCHAR(50),
            device VARCHAR(100),
            description TEXT,                               -- описание проблемы
            date TIMESTAMP,
            cost DECIMAL(10, 2),
            user_id UUID NOT NULL,
            manager_id BIGINT NOT NULL,
            FOREIGN KEY (manager_id) REFERENCES managers(manager_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );
            CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
            CREATE INDEX IF NOT EXISTS idx_orders_manager_id ON orders(manager_id);
            CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
            CREATE INDEX IF NOT EXISTS idx_orders_serial ON orders(serial_number);
        '''
        cursor.execute(create_table_orders)


        # Saving changes:
        connection.commit()
        logger_db.info("Adding tables is done!")
        print("Adding tables is done!")
        return True

    except Exception as error:
        logger_db.error(f"Error Create Tables in DB: {error}")
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