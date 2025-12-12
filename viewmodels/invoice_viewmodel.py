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
            return db.query(Counterparty).order_by(Counterparty.name).all()
        finally:
            db.close()

    def add_invoice(self, counterparty_id, number, invoice_date, supply_date, amount, terms, is_paid):
        """Создать счет"""
        db = SessionLocal()
        try:
            # Если сразу ставим галочку "Оплачено", то дата оплаты = сегодня
            pay_date = date.today() if is_paid else None

            new_inv = Invoice(
                counterparty_id=counterparty_id,
                invoice_number=number,
                invoice_date=invoice_date, #date.today()
                supply_date=supply_date,
                amount=amount,
                payment_term_days=terms,
                is_paid=is_paid,
                payment_date=pay_date
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

    def update_invoice(self, invoice_id, counterparty_id, number, invoice_date, supply_date, amount, terms, is_paid):
        """Обновить существующий счет"""
        db = SessionLocal()
        try:
            # Ищем счет по ID
            inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
            if inv:
                # Обновляем поля
                inv.counterparty_id = counterparty_id
                inv.invoice_number = number
                inv.invoice_date = invoice_date
                inv.supply_date = supply_date
                inv.amount = amount
                inv.payment_term_days = terms

                # Логика даты оплаты при редактировании
                if is_paid and not inv.is_paid:
                    # Если стало оплачено, а было нет -> ставим сегодня
                    inv.payment_date = date.today()
                elif not is_paid:
                    # Если сняли оплату -> убираем дату
                    inv.payment_date = None

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
                # Если стал оплачен -> ставим сегодня, иначе очищаем
                inv.payment_date = date.today() if inv.is_paid else None
                db.commit()
        finally:
            db.close()

    def delete_invoice(self, invoice_id):
        """Удалить счет"""
        db = SessionLocal()
        try:
            inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
            if inv:
                db.delete(inv)
                db.commit()
        except Exception as e:
            db.rollback()
        finally:
            db.close()