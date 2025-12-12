from PySide6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget
from PySide6.QtGui import QIcon

# Импортируем ваши готовые окна (View)
from views.invoice_view import InvoiceView
from views.counterparty_view import CounterpartyView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Учет расчетов с контрагентами")
        self.resize(1000, 600)  # Сделаем окно пошире

        # 1. Создаем виджет вкладок
        self.tabs = QTabWidget()

        # Настройка вкладок (опционально: можно сделать их покрупнее)
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setMovable(False)  # Запрещаем перетаскивать вкладки местами

        # 2. Создаем экземпляры ваших окон
        self.invoice_tab = InvoiceView()
        self.counterparty_tab = CounterpartyView()

        # 3. Добавляем их во вкладки
        self.tabs.addTab(self.invoice_tab, "Журнал счетов")
        self.tabs.addTab(self.counterparty_tab, "Справочник контрагентов")

        # 4. Устанавливаем вкладки как центральный элемент окна
        self.setCentralWidget(self.tabs)

        # ДОПОЛНИТЕЛЬНО: Логика обновления
        # Если вы добавили нового поставщика во второй вкладке,
        # хорошо бы, чтобы при возвращении на первую вкладку данные обновились.
        self.tabs.currentChanged.connect(self.on_tab_change)

    def on_tab_change(self, index):
        """
        Этот метод срабатывает, когда пользователь переключает вкладку.
        index - это номер вкладки (0 - Счета, 1 - Контрагенты)
        """
        # Если перешли на вкладку счетов (индекс 0)
        if index == 0:
            # Можно вызвать обновление таблицы, если нужно
            self.invoice_tab.load_data()
            pass

        # Если перешли на вкладку контрагентов (индекс 1)
        if index == 1:
            self.counterparty_tab.load_data()