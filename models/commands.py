from models.database import get_db
from models.entities import Invoice
from datetime import date


class Command:
    """Базовый класс команды"""

    def execute(self): pass

    def undo(self): pass


# добавление
class AddInvoiceCommand(Command):
    def __init__(self, data_dict):
        self.data = data_dict
        self.created_id = None  # Сюда запомним ID созданного счета

    def execute(self):
        db = get_db()
        try:
            new_inv = Invoice(
                counterparty_id=self.data['counterparty_id'],
                invoice_number=self.data['number'],
                amount=self.data['amount'],
                invoice_date=self.data['invoice_date'],
                supply_date=self.data['supply_date'],
                deadline_date=self.data['deadline_date'],
                is_paid=self.data['is_paid'],
                payment_date=self.data['payment_date']
            )
            db.add(new_inv)
            db.commit()
            db.refresh(new_inv)
            self.created_id = new_inv.id  # Запоминаем ID, чтобы потом удалить
            return True
        except Exception as e:
            print(f"Error executing Add: {e}")
            db.rollback()
            return False
        finally:
            db.close()

    def undo(self):
        # Отмена добавления = Удаление
        if not self.created_id: return False

        db = get_db()
        try:
            inv = db.query(Invoice).filter(Invoice.id == self.created_id).first()
            if inv:
                db.delete(inv)
                db.commit()
            return True
        except Exception as e:
            print(f"Error undoing Add: {e}")
            db.rollback()
            return False
        finally:
            db.close()


# удаление
class DeleteInvoiceCommand(Command):
    def __init__(self, invoice_id):
        self.invoice_id = invoice_id
        self.backup_data = None  # Сюда сохраним данные перед удалением

    def execute(self):
        db = get_db()
        try:
            inv = db.query(Invoice).filter(Invoice.id == self.invoice_id).first()
            if inv:
                # Сохраняем копию данных
                self.backup_data = {
                    'counterparty_id': inv.counterparty_id,
                    'number': inv.invoice_number,
                    'amount': inv.amount,
                    'invoice_date': inv.invoice_date,
                    'supply_date': inv.supply_date,
                    'deadline_date': inv.deadline_date,
                    'is_paid': inv.is_paid,
                    'payment_date': inv.payment_date
                }
                db.delete(inv)
                db.commit()
                return True
            return False
        except Exception as e:
            print(e)
            db.rollback()
            return False
        finally:
            db.close()

    def undo(self):
        # Отмена удаления = Создание заново (восстановление)
        if not self.backup_data: return False

        db = get_db()
        try:
            # Восстанавливаем объект
            # Примечание: ID может измениться (будет новый), но данные те же
            restored_inv = Invoice(
                counterparty_id=self.backup_data['counterparty_id'],
                invoice_number=self.backup_data['number'],
                amount=self.backup_data['amount'],
                invoice_date=self.backup_data['invoice_date'],
                supply_date=self.backup_data['supply_date'],
                deadline_date=self.backup_data['deadline_date'],
                is_paid=self.backup_data['is_paid'],
                payment_date=self.backup_data['payment_date']
            )
            db.add(restored_inv)
            db.commit()
            return True
        except Exception as e:
            print(e)
            db.rollback()
            return False
        finally:
            db.close()


# редактирование
class EditInvoiceCommand(Command):
    def __init__(self, invoice_id, new_data):
        self.invoice_id = invoice_id
        self.new_data = new_data
        self.old_data = None  # Сюда сохраним старые данные

    def execute(self):
        db = get_db()
        try:
            inv = db.query(Invoice).filter(Invoice.id == self.invoice_id).first()
            if inv:
                # 1. Запоминаем старое
                self.old_data = {
                    'counterparty_id': inv.counterparty_id,
                    'number': inv.invoice_number,
                    'amount': inv.amount,
                    'invoice_date': inv.invoice_date,
                    'supply_date': inv.supply_date,
                    'deadline_date': inv.deadline_date,
                    'is_paid': inv.is_paid,
                    'payment_date': inv.payment_date
                }

                # 2. Применяем новое
                inv.counterparty_id = self.new_data['counterparty_id']
                inv.invoice_number = self.new_data['number']
                inv.amount = self.new_data['amount']
                inv.invoice_date = self.new_data['invoice_date']
                inv.supply_date = self.new_data['supply_date']
                inv.deadline_date = self.new_data['deadline_date']
                inv.is_paid = self.new_data['is_paid']
                inv.payment_date = self.new_data['payment_date']

                db.commit()
                return True
            return False
        except Exception as e:
            print(e)
            db.rollback()
            return False
        finally:
            db.close()

    def undo(self):
        # Отмена редактирования = Возврат старых данных
        if not self.old_data: return False

        db = get_db()
        try:
            inv = db.query(Invoice).filter(Invoice.id == self.invoice_id).first()
            if inv:
                inv.counterparty_id = self.old_data['counterparty_id']
                inv.invoice_number = self.old_data['number']
                inv.amount = self.old_data['amount']
                inv.invoice_date = self.old_data['invoice_date']
                inv.supply_date = self.old_data['supply_date']
                inv.deadline_date = self.old_data['deadline_date']
                inv.is_paid = self.old_data['is_paid']
                inv.payment_date = self.old_data['payment_date']

                db.commit()
                return True
            return False
        except Exception as e:
            print(e)
            db.rollback()
            return False
        finally:
            db.close()