from datetime import date
from sqlalchemy.orm import joinedload
from models.database import SessionLocal
from models.entities import Invoice, Counterparty

class InvoiceViewModel:
    def get_all_invoices(self):
        """Получить все счета с подгрузкой поставщика"""
        db = SessionLocal()
        try:
            # joinedload нужен, чтобы сразу загрузить данные из связанной таблицы counterparties
            # иначе, когда закроем сессию, программа упадет при попытке узнать имя поставщика
            invoices = db.query(Invoice).options(joinedload(Invoice.counterparty)).all()
            return invoices
        finally:
            db.close()

    def get_counterparties_for_combo(self):
        """Получить список поставщиков для выпадающего списка (id и имя)"""
        db = SessionLocal()
        try:
            return db.query(Counterparty).all()
        finally:
            db.close()

    def add_invoice(self, counterparty_id, number, amount, supply_date, terms, is_paid):
        """Создать счет"""
        db = SessionLocal()
        try:
            new_inv = Invoice(
                counterparty_id=counterparty_id,
                invoice_number=number,
                amount=amount,
                supply_date=supply_date,
                invoice_date=date.today(),
                payment_term_days=terms,
                is_paid=is_paid
            )
            db.add(new_inv)
            db.commit()
            return True
        except Exception as e:
            print(f"Ошибка создания счета: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    def update_invoice(self, invoice_id, counterparty_id, number, amount, supply_date, terms, is_paid):
        """Обновить существующий счет"""
        db = SessionLocal()
        try:
            # Ищем счет по ID
            inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
            if inv:
                # Обновляем поля
                inv.counterparty_id = counterparty_id
                inv.invoice_number = number
                inv.amount = amount
                inv.supply_date = supply_date
                inv.payment_term_days = terms
                inv.is_paid = is_paid

                db.commit()  # Сохраняем изменения
                return True
            return False
        except Exception as e:
            print(f"Ошибка обновления: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    def toggle_payment_status(self, invoice_id):
        """Переключить статус оплаты (Оплачено <-> Не оплачено)"""
        db = SessionLocal()
        try:
            inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
            if inv:
                inv.is_paid = not inv.is_paid # Инвертируем
                db.commit()
        finally:
            db.close()