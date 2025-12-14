from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Создаем базовый класс для моделей
Base = declarative_base()

# Глобальные переменные, которые мы инициализируем позже
engine = None
SessionLocal = None


def initialize_db(db_filename):
    """
    Эта функция вызывается, когда пользователь выбрал базу.
    Она настраивает подключение и создает таблицы, если их нет.
    """
    global engine, SessionLocal

    # Формируем путь (sqlite:///имя_файла.db)
    DATABASE_URL = f"sqlite:///{db_filename}"

    # Создаем движок
    engine = create_engine(DATABASE_URL, echo=False)

    # Создаем фабрику сессий
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Импортируем модели ЗДЕСЬ, чтобы они зарегистрировались в Base
    # (иначе create_all не поймет, какие таблицы создавать)
    from models.entities import Counterparty, Invoice

    # Создаем таблицы (если это новая база)
    Base.metadata.create_all(bind=engine)

def get_db():
    """
    Функция-посредник.
    Все ViewModels будут вызывать её, чтобы получить сессию.
    """
    if SessionLocal is None:
        raise Exception("База данных не инициализирована! Сначала вызовите initialize_db.")
    return SessionLocal()


def close_connection():
    """Принудительно закрывает соединение с базой, освобождая файл"""
    global engine, SessionLocal

    if engine:
        # dispose() закрывает все пулы соединений
        engine.dispose()

    # Обнуляем переменные
    engine = None
    SessionLocal = None