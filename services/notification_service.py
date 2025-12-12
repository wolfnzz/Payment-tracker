from datetime import date, timedelta
from sqlalchemy.orm import joinedload
from models.database import SessionLocal
from models.entities import Invoice


def get_urgent_invoices():
    """
    Возвращает список счетов, которые нужно оплатить в ближайшие 5 дней.
    Также возвращает просроченные счета.
    """
    db = SessionLocal()
    urgent_list = []

    try:
        # Берем только неоплаченные счета
        unpaid_invoices = db.query(Invoice).filter(Invoice.is_paid == False).options(
            joinedload(Invoice.counterparty)).all()

        today = date.today()

        for inv in unpaid_invoices:
            # Считаем дату дедлайна
            deadline = inv.supply_date + timedelta(days=inv.payment_term_days)

            # Считаем, сколько дней осталось
            #
            days_left = (deadline - today).days


            # Показываем то, что нужно платить сегодня-завтра (0-5 дней).
            if 0 <= days_left <= 5:
                urgent_list.append(inv)

    finally:
        db.close()

    return urgent_list


def format_alert_message(invoices):
    if not invoices:
        return ""

    text = "Внимание! Необходимо оплатить следующие счета:\n\n"

    for inv in invoices:
        # Вычисляем дедлайн для отображения
        deadline = inv.supply_date + timedelta(days=inv.payment_term_days)
        deadline_str = deadline.strftime("%d.%m.%Y")

        row = f"• {inv.counterparty.name} (Счет {inv.invoice_number}) До {deadline_str}\n"
        text += row + "\n"


    return text