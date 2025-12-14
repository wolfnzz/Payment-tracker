from PySide6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget, QMessageBox, QHBoxLayout, QLabel, \
    QPushButton
from PySide6.QtCore import QTimer
from PySide6.QtCore import Signal, Qt
from views.invoice_view import InvoiceView
from views.counterparty_view import CounterpartyView
from services.notification_service import get_urgent_invoices, format_alert_message


class MainWindow(QMainWindow):
    # Создаем сигнал, который скажет main.py, что мы хотим выйти
    logout_signal = Signal()

    def __init__(self, db_name):
        super().__init__()
        self.setWindowTitle("Учет: {db_name}")
        self.resize(1000, 600)  # Сделаем окно пошире

        # Создаем центральный виджет и лейаут
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()

        # верхняя панель с кнопкой выхода
        top_bar = QHBoxLayout()
        # Можно добавить название текущей базы или просто заголовок
        header_label = QLabel(f"<b>{db_name}</b>")
        header_label.setStyleSheet("font-size: 16px; color: white; margin-left: 5px;")
        top_bar.addWidget(header_label)
        top_bar.addStretch()  # Растяжка сдвинет кнопку вправо

        # Сама кнопка
        self.btn_logout = QPushButton("Сменить базу")
        # self.btn_logout.setStyleSheet("background-color: #ffccbc; padding: 5px;")
        self.btn_logout.setStyleSheet("""
                    QPushButton {
                        border: 1px solid #ffab91;
                        border-radius: 4px;
                        padding: 5px 10px;
                    }
                    QPushButton:hover {
                        background-color: #ffab91;
                    }
                """)
        self.btn_logout.setCursor(Qt.PointingHandCursor)

        top_bar.addWidget(self.btn_logout)

        main_layout.addLayout(top_bar)

        # 1. Создаем виджет вкладок
        self.tabs = QTabWidget()

        # Настройка вкладок (опционально: можно сделать их покрупнее)
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setMovable(False)  # Запрещаем перетаскивать вкладки местами

        # Создаем экземпляры ваших окон
        self.invoice_tab = InvoiceView()
        self.counterparty_tab = CounterpartyView()

        # Добавляем их во вкладки
        self.tabs.addTab(self.invoice_tab, "Журнал счетов")
        self.tabs.addTab(self.counterparty_tab, "Справочник контрагентов")

        # Добавляем вкладки в главный слой (ПОД кнопкой)
        main_layout.addWidget(self.tabs)

        # Применяем главный слой к центральному виджету
        central_widget.setLayout(main_layout)

        # Логика обновления
        # Если добавили нового поставщика во второй вкладке,
        # хорошо бы, чтобы при возвращении на первую вкладку данные обновились.
        self.tabs.currentChanged.connect(self.on_tab_change)

        # Запуск проверки уведомлений через 0,1 сек после запуска
        QTimer.singleShot(100, self.check_notifications)

        self.btn_logout.clicked.connect(self.logout)

    def on_tab_change(self, index):
        """
        Этот метод срабатывает, когда пользователь переключает вкладку.
        index - это номер вкладки (0 - Счета, 1 - Контрагенты)
        """
        # Если перешли на вкладку счетов (индекс 0)
        if index == 0:
            self.invoice_tab.refresh_suppliers_combo()

            # (Опционально) Можно таблицу обновить
            self.invoice_tab.apply_filter()

        # Если перешли на вкладку контрагентов (индекс 1)
        if index == 1:
            self.counterparty_tab.load_data()

    def logout(self):
        """Метод вызывается при нажатии кнопки Сменить базу"""
        self.close()
        self.logout_signal.emit()  # Посылаем сигнал "наверх"

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