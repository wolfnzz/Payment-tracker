import pandas as pd

def save_invoices_to_excel(invoices, filename):
    """
    Принимает список объектов Invoice и путь к файлу.
    Сохраняет данные в Excel.
    """
    # Превращаем объекты базы данных в список словарей (строк таблицы)
    data_list = []

    for inv in invoices:
        # Рассчитываем дедлайн
        deadline = inv.deadline_date

        # Безопасное получение имени поставщика
        supplier_name = inv.counterparty.name if inv.counterparty else "<Удален>"

        pay_date_str = inv.payment_date.strftime("%d.%m.%Y") if inv.payment_date else "-"

        # Формируем строку
        row = {
            "Номер счета": inv.invoice_number,
            "Дата счета": inv.invoice_date.strftime("%d.%m.%Y"),
            "Поставщик": supplier_name,
            "Дата поставки": inv.supply_date.strftime("%d.%m.%Y"),
            "Сумма": inv.amount,
            "Оплатить до": deadline.strftime("%d.%m.%Y"),
            "Статус": "Оплачено" if inv.is_paid else "Не оплачено",
            "Дата оплаты": pay_date_str
        }
        data_list.append(row)


    df = pd.DataFrame(data_list)

    # Сохраняем в файл
    try:
        df.to_excel(filename, index=False)
        return True, "Успешно сохранено!"
    except Exception as e:
        return False, f"Ошибка при сохранении: {e}"