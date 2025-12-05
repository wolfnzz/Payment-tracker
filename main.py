import sys
from PySide6.QtWidgets import QApplication
# Импортируем наше новое окно
from views.counterparty_view import CounterpartyView


def main():
    app = QApplication(sys.argv)

    # Создаем и показываем окно справочника
    window = CounterpartyView()
    window.setWindowTitle("Справочник Контрагентов")
    window.resize(600, 400)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
