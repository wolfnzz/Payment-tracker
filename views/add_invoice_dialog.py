from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QPushButton,
                               QLabel, QComboBox, QDateEdit, QSpinBox, QCheckBox, QMessageBox, QHBoxLayout)
from PySide6.QtCore import QDate


class AddInvoiceDialog(QDialog):
    def __init__(self, counterparties_list, parent=None, invoice_data=None):
        super().__init__(parent)

        # Меняем заголовок в зависимости от режима
        if invoice_data:
            self.setWindowTitle("Редактирование счета")
        else:
            self.setWindowTitle("Новый счет")

        #self.setWindowTitle("Новый счет")
        self.setFixedSize(350, 400)

        layout = QVBoxLayout()

        # Выбор поставщика
        layout.addWidget(QLabel("Поставщик:"))
        self.combo_supplier = QComboBox()
        # Заполнение списка
        for c in counterparties_list:
            self.combo_supplier.addItem(c.name, c.id)
        layout.addWidget(self.combo_supplier)

        # Номер счета
        self.number_input = QLineEdit()
        self.number_input.setPlaceholderText("Номер счета (напр. №123)")
        layout.addWidget(QLabel("Номер счета:"))
        layout.addWidget(self.number_input)

        # Сумма
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Сумма (руб)")
        layout.addWidget(QLabel("Сумма:"))
        layout.addWidget(self.amount_input)

        # Дата поставки
        layout.addWidget(QLabel("Дата поставки:"))
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)  # календарь
        self.date_input.setDate(QDate.currentDate())
        layout.addWidget(self.date_input)

        # Срок оплаты (дни)
        layout.addWidget(QLabel("Срок оплаты (дней после поставки):"))
        self.term_input = QSpinBox()
        self.term_input.setRange(0, 365)
        self.term_input.setValue(14)  # По умолчанию 2 недели
        layout.addWidget(self.term_input)

        # Галочка "уже оплачено"
        self.paid_check = QCheckBox("Счет уже оплачен")
        layout.addWidget(self.paid_check)

        # Кнопки
        # self.save_btn = QPushButton("Сохранить")
        # self.save_btn.clicked.connect(self.validate_and_accept)
        # layout.addWidget(self.save_btn)
        #
        # self.setLayout(layout)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")

        #self.save_btn.setStyleSheet("background-color: #11a629; font-weight: bold;")

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # Подключение событий кнопок
        self.save_btn.clicked.connect(self.validate_and_accept)
        self.cancel_btn.clicked.connect(self.reject)

        # заполняем данными (если режим редактирования)
        if invoice_data:
            self.fill_fields(invoice_data)

    def fill_fields(self, data):
        """Заполняет поля данными из существующего счета"""
        self.number_input.setText(data['number'])

        self.amount_input.setText(str(data['amount']))

        py_date = data['supply_date']
        q_date = QDate(py_date.year, py_date.month, py_date.day)
        self.date_input.setDate(q_date)

        self.term_input.setValue(data['terms'])

        self.paid_check.setChecked(data['is_paid'])

        target_id = data['counterparty_id']
        for i in range(self.combo_supplier.count()):
            # itemData(i) достает скрытый ID, который положили при создании
            if self.combo_supplier.itemData(i) == target_id:
                self.combo_supplier.setCurrentIndex(i)
                break

    def validate_and_accept(self):
        if self.combo_supplier.count() == 0:
            QMessageBox.warning(self, "Ошибка", "Нет поставщиков! Сначала добавьте их в справочник.")
            return

        try:
            float(self.amount_input.text())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Сумма должна быть числом (через точку)")
            return

        if not self.number_input.text():
            QMessageBox.warning(self, "Ошибка", "Введите номер счета")
            return

        self.accept()

    def get_data(self):
        """Возвращает готовые данные для сохранения"""
        return {
            "counterparty_id": self.combo_supplier.currentData(),
            "number": self.number_input.text(),
            "amount": float(self.amount_input.text()),
            "supply_date": self.date_input.date().toPython(),
            "terms": self.term_input.value(),
            "is_paid": self.paid_check.isChecked()
        }