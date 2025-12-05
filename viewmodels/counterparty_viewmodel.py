from models.database import SessionLocal
from models.entities import Counterparty


class CounterpartyViewModel:
    def __init__(self):

        pass

    def get_all_counterparties(self):
        """Получить список всех поставщиков"""
        db = SessionLocal()
        try:
            # Запрос: дай всех, отсортируй по имени
            return db.query(Counterparty).order_by(Counterparty.name).all()
        finally:
            db.close()

    def add_counterparty(self, name):
        """Добавить нового поставщика"""
        db = SessionLocal()
        try:
            new_c = Counterparty(name=name)
            db.add(new_c)
            db.commit()
            return True  # Успех
        except Exception as e:
            print(f"Ошибка при добавлении: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    def delete_counterparty(self, counterparty_id):
        """Удалить поставщика по ID"""
        db = SessionLocal()
        try:
            # Ищем по ID
            c = db.query(Counterparty).filter(Counterparty.id == counterparty_id).first()
            if c:
                db.delete(c)
                db.commit()
        except Exception as e:
            print(f"Ошибка удаления: {e}")
            db.rollback()
        finally:
            db.close()
