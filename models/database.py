from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# имя файла базы данных
DATABASE_URL = "sqlite:///records.db"

# управление подключением
engine = create_engine(DATABASE_URL, echo=True)

# создание фабрики сессий для выполнения запросов (добавление, удаление)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# класс, от которого наследуются модели (таблицы)
Base = declarative_base()