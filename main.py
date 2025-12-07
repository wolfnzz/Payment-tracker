import sys
from PySide6.QtWidgets import QApplication
from views.invoice_view import InvoiceView
# Импортируем наше новое окно
from views.counterparty_view import CounterpartyView


def main():
    app = QApplication(sys.argv)

    window = InvoiceView()
    window.setWindowTitle("Журнал счетов")
    window.resize(800, 500)
    # Создаем и показываем окно справочника
    window = CounterpartyView()
    window.setWindowTitle("Справочник Контрагентов")
    window.resize(800, 500)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
