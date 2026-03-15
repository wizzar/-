# общие настройки для нашего приложения
import os


db_host = os.environ.get("DATABASE_HOST")
db_port = os.environ.get("DATABASE_PORT")
db_user = os.environ.get("DATABASE_USER")
db_pass = os.environ.get("DATABASE_PASSWORD")
db_name = os.environ.get("DATABASE_NAME")


DATABASE_URI = f'mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'

SECRET_KEY = 'your_secret_key_here'