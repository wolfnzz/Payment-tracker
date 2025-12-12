from PySide6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget, QMessageBox
from PySide6.QtCore import QTimer

# Импортируем ваши готовые окна (View)
from views.invoice_view import InvoiceView
from views.counterparty_view import CounterpartyView
from services.notification_service import get_urgent_invoices, format_alert_message


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

        # Запуск проверки уведомлений через 0,1 сек после запуска
        QTimer.singleShot(100, self.check_notifications)

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

    def check_notifications(self):
        """
        Вызывает сервис проверки дат и показывает окно, если есть долги.
        """
        # 1. Получаем список "горящих" счетов
        urgent_invoices = get_urgent_invoices()

        # 2. Если список не пуст — показываем сообщение
        if urgent_invoices:
            message_text = format_alert_message(urgent_invoices)

            msg = QMessageBox(self)
            msg.setWindowTitle("Напоминание об оплате")
            msg.setText(message_text)
            msg.setIcon(QMessageBox.Warning)
            msg.exec()