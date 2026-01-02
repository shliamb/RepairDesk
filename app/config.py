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