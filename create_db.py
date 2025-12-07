import os
from models.database import Base, engine
from models.entities import Counterparty, Invoice


def create_database():
    db_name = "records.db"

    if os.path.exists(db_name):
        os.remove(db_name)
        print(f"Старый файл {db_name} удален.")

    print(f"Создаем базу данных {db_name}...")

    # берем все классы, унаследованные от Base, и создаем для них таблицы
    Base.metadata.create_all(bind=engine)

    print("Готово! Таблицы успешно созданы.")


if __name__ == "__main__":
    create_database()
