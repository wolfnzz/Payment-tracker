from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Указываем имя файла базы данных.
DATABASE_URL = "sqlite:///records.db"

# 2. Создаем "движок", который управляет подключением
engine = create_engine(DATABASE_URL, echo=True)

# 3. Создаем фабрику сессий. Через SessionLocal мы будем делать запросы (добавлять, удалять)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Базовый класс, от которого будут наследоваться наши модели (таблицы)
Base = declarative_base()