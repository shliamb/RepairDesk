import os
from dotenv import load_dotenv
load_dotenv()



#### BASIC CONFIG (set it up manually): ####
DOCKER = False # True or False
HOST = "app_postgres" if DOCKER else  "localhost" # app_postgres localhost
TIME_CORRECTION = + 3
MAX_SIZE_DOC = 2 # 2 мегабайт
########


# Folders:
PATH_LOGS = "/logs/" if DOCKER else "logs/"
#PATH_LOGS = "/logs/" if DOCKER else "../logs/"
# DOWNLOAD = "/downloads/" if DOCKER else "../downloads/"
# PATH_JSON_USERS = "/json/" if DOCKER else "../json/"
# OUTPUT = "/output/" if DOCKER else "../output/"
# SYST_CONT_FOLDER = "/" if DOCKER else "../"



# .env:
TELEGRAM_BOT_TOKEN = os.environ.get('telegram_bot_token')
USER_DB = os.environ.get('USER_DB')
PASSWORD_DB = os.environ.get('PASSWORD_DB')
DB_NAME = os.environ.get('POSTGRES_DB')
ADMIN_ID = int(os.environ.get('admin_id'))
KEY_API_DEEPSEEK = os.environ.get('key_api_deepseek')




# class Settings(BaseSettings):
#     BOT_TOKEN: str
#     ADMINS: list[int] = []
#     DB_HOST: str = "localhost"
#     DB_PORT: int = 5432
#     DB_NAME: str
#     DB_USER: str
#     DB_PASS: str
    
#     class Config:
#         env_file = ".env"

# settings = Settings()