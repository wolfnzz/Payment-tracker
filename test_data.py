from datetime import date
from models.database import SessionLocal
from models.entities import Counterparty, Invoice


def populate_test_data():
    # 1. Открываем сессию (соединение) с базой
    db = SessionLocal()

    try:
        print("Добавляем тестовые данные...")

        # --- Создаем Контрагента (Поставщика) ---
        supplier_1 = Counterparty(
            name="ООО Абоба Индастрис"
        )

        # Добавляем в сессию
        db.add(supplier_1)
        # Делаем commit, чтобы данные улетели в базу
        db.commit()
        # Делаем refresh, чтобы получить присвоенный ID (он создается базой)
        db.refresh(supplier_1)

        print(f"-> Добавлен поставщик: {supplier_1.name} (ID: {supplier_1.id})")

        # --- Создаем Счета для этого поставщика ---

        # Счет №1 (Нужно оплатить через 2 недели)
        invoice_1 = Invoice(
            counterparty_id=supplier_1.id,  # Ссылаемся на ID созданного выше поставщика
            invoice_number="ТК-001/24",
            amount=150000.00,
            invoice_date=date(2025, 12, 1),
            supply_date=date(2025, 12, 5),  # Поставка 5 декабря
            payment_term_days=14,  # Оплата через 14 дней (до 19 декабря)
            is_paid=False
        )

        # Счет №2 (Уже оплачен)
        invoice_2 = Invoice(
            counterparty_id=supplier_1.id,
            invoice_number="ТК-002/24",
            amount=5600.50,
            invoice_date=date(2025, 11, 20),
            supply_date=date(2025, 11, 22),
            payment_term_days=5,
            is_paid=True  # Галочка "Оплачено"
        )

        db.add(invoice_1)
        db.add(invoice_2)
        db.commit()

        print(f"-> Добавлены счета: {invoice_1.invoice_number} и {invoice_2.invoice_number}")

        # --- Проверка чтения ---
        print("\nПроверяем, что записалось в базу:")
        saved_supplier = db.query(Counterparty).first()
        print(f"Поставщик: {saved_supplier.name}")
        for inv in saved_supplier.invoices:
            print(f"   - Счет {inv.invoice_number} на сумму {inv.amount} руб. (Оплатить до: {inv.deadline_date})")

    except Exception as e:
        print(f"ОШИБКА: {e}")
        db.rollback()  # Если ошибка, отменяем изменения
    finally:
        db.close()  # Закрываем соединение


if __name__ == "__main__":
    populate_test_data()