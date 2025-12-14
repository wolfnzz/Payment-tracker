from datetime import date
from sqlalchemy.orm import joinedload
from models.database import get_db
from models.entities import Invoice, Counterparty
from services.excel_exporter import save_invoices_to_excel

class InvoiceViewModel:
    def get_all_invoices(self):
        """Получить все счета с подгрузкой поставщика"""
        db = get_db()
        try:
            # joinedload нужен, чтобы сразу загрузить данные из связанной таблицы counterparties
            # иначе, когда закроем сессию, программа упадет при попытке узнать имя поставщика
            invoices = db.query(Invoice).options(joinedload(Invoice.counterparty)).all()
            return invoices
        finally:
            db.close()

    def get_counterparties_for_combo(self):
        """Получить список поставщиков для выпадающего списка (id и имя)"""
        db = get_db()
        try:
            return db.query(Counterparty).order_by(Counterparty.name).all()
        finally:
            db.close()

    def add_invoice(self, counterparty_id, number, invoice_date, supply_date, amount, deadline_date, is_paid, payment_date=None):
        """Создать счет"""
        db = get_db()
        try:
            # Если галочка стоит, но дату не передали -> ставим сегодня (для удобства)
            # Если передали (вручную в диалоге) -> оставляем как есть
            pay_date = None
            if is_paid:
                pay_date = payment_date if payment_date else date.today()

            new_inv = Invoice(
                counterparty_id=counterparty_id,
                invoice_number=number,
                invoice_date=invoice_date, #date.today()
                supply_date=supply_date,
                amount=amount,
                deadline_date=deadline_date,
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

    def update_invoice(self, invoice_id, counterparty_id, number, invoice_date,
                       supply_date, amount, deadline_date, is_paid, payment_date=None):
        """Обновить существующий счет"""
        db = get_db()
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
                inv.deadline_date = deadline_date

                # Логика даты оплаты:
                if is_paid:
                    # Если передали конкретную дату из диалога - берем её
                    if payment_date:
                        inv.payment_date = payment_date
                    # Если даты нет, а раньше было "не оплачено" - ставим сегодня
                    elif not inv.is_paid:
                        inv.payment_date = date.today()
                    # Иначе оставляем старую дату (если уже было оплачено)
                else:
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
        db = get_db()
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
        db = get_db()
        try:
            inv = db.query(Invoice).filter(Invoice.id == invoice_id).first()
            if inv:
                db.delete(inv)
                db.commit()
        except Exception as e:
            db.rollback()
        finally:
            db.close()

    def export_data(self, filename, supplier_id=None, date_type=None, filter_date=None, is_paid_filter=None):
        """
        Получает отфильтрованные данные из БД и отправляет их в Excel-сервис
        """
        # Берем все отфильтрованные счета
        invoices = self.get_filtered_invoices(supplier_id, date_type, filter_date, is_paid_filter)

        # Отправляем в сервис
        success, message = save_invoices_to_excel(invoices, filename)
        return success, message
    def get_filtered_invoices(self, supplier_id=None, date_type=None, filter_date=None, is_paid_filter=None):
        """
        Фильтрация счетов.
        :param supplier_id: ID поставщика (или None, если нужны все)
        :param date_type: Тип фильтра даты ("supply" - поставка, "deadline" - срок оплаты)
        :param filter_date: Сама дата (datetime.date)
        """

        all_invoices = self.get_all_invoices()
        filtered = []

        for inv in all_invoices:
            if supplier_id is not None and inv.counterparty_id != supplier_id:
                continue

            if date_type and filter_date:
                if date_type == "supply":
                    if inv.supply_date != filter_date:
                        continue

                elif date_type == "deadline":
                    if inv.deadline_date != filter_date:
                        continue

            if is_paid_filter is not None:
                if inv.is_paid != is_paid_filter:
                    continue
            filtered.append(inv)

        return filtered
