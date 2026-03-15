# настройки взаимодействия с базой данных
from models.post import Post
from models.user import User
from models.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from config import DATABASE_URI

engine = create_engine(DATABASE_URI,connect_args={"ssl": {"check_hostname": False}})

SessionLocal = sessionmaker(autocommit = False, autoflush=False, bind = engine)

Session_safe = scoped_session(SessionLocal)

def get_db_session():
    return Session_safe()

def init_db():
    Base.metadata.create_all(bind = engine)
    print("База данных инициализированна")