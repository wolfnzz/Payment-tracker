import sys
from PySide6.QtWidgets import QApplication
from views.invoice_view import InvoiceView


def main():
    app = QApplication(sys.argv)

    window = InvoiceView()
    window.setWindowTitle("Журнал счетов")
    window.resize(800, 500)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()