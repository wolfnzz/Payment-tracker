from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QPushButton,
                               QLabel, QComboBox, QDateEdit, QSpinBox, QCheckBox, QMessageBox, QHBoxLayout)
from PySide6.QtCore import QDate


class AddInvoiceDialog(QDialog):
    def __init__(self, counterparties_list, parent=None, invoice_data=None):
        super().__init__(parent)

        self.is_edit_mode = invoice_data is not None

        # Меняем заголовок в зависимости от режима
        if invoice_data:
            self.setWindowTitle("Редактирование счета")
        else:
            self.setWindowTitle("Новый счет")

        #self.setWindowTitle("Новый счет")
        self.setFixedSize(350, 450)

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

        # Дата счета
        layout.addWidget(QLabel("Дата счета:"))
        self.invoice_date_input = QDateEdit()
        self.invoice_date_input.setCalendarPopup(True)
        self.invoice_date_input.setDate(QDate.currentDate())
        layout.addWidget(self.invoice_date_input)

        # Сумма
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Сумма (руб)")
        layout.addWidget(QLabel("Сумма:"))
        layout.addWidget(self.amount_input)

        # Дата поставки
        layout.addWidget(QLabel("Дата поставки:"))
        self.supply_date_input = QDateEdit()
        self.supply_date_input.setCalendarPopup(True)  # календарь
        self.supply_date_input.setDate(QDate.currentDate())
        layout.addWidget(self.supply_date_input)

        # Срок оплаты (дни)
        layout.addWidget(QLabel("Срок оплаты:"))
        self.deadline_date = QDateEdit()
        self.deadline_date.setCalendarPopup(True)
        self.deadline_date.setDate(QDate.currentDate())
        layout.addWidget(self.deadline_date)

        # Галочка "уже оплачено"
        self.paid_check = QCheckBox("Счет уже оплачен")
        layout.addWidget(self.paid_check)

        layout.addWidget(QLabel("Дата фактической оплаты:"))
        self.payment_date_input = QDateEdit()
        self.payment_date_input.setCalendarPopup(True)
        self.payment_date_input.setDate(QDate.currentDate())
        self.payment_date_input.setEnabled(False)  # По умолчанию выключено
        layout.addWidget(self.payment_date_input)

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

        # Включаем поле даты только если стоит галочка
        self.paid_check.toggled.connect(self.toggle_payment_date)

        # заполняем данными (если режим редактирования)
        if invoice_data:
            self.fill_fields(invoice_data)

    def fill_fields(self, data):
        """Заполняет поля данными из существующего счета"""
        self.number_input.setText(data['number'])

        self.amount_input.setText(str(data['amount']))

        # Дата поставки
        py_date = data['supply_date']
        q_date = QDate(py_date.year, py_date.month, py_date.day)
        self.supply_date_input.setDate(q_date)

        # Дата счета
        inv_date = data['invoice_date']
        self.invoice_date_input.setDate(QDate(inv_date.year, inv_date.month, inv_date.day))

        #self.term_input.setValue(data['terms'])
        # Дедлайн
        deadline_date = data['deadline_date']
        self.deadline_date.setDate(QDate(deadline_date.year, deadline_date.month, deadline_date.day))

        self.paid_check.setChecked(data['is_paid'])
        if data['payment_date']:
            pay_date = data['payment_date']
            self.payment_date_input.setDate(QDate(pay_date.year, pay_date.month, pay_date.day))
        self.payment_date_input.setEnabled(data['is_paid'])

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
        # Если галочка стоит, берем дату из календаря. Если нет - None
        p_date = self.payment_date_input.date().toPython() if self.paid_check.isChecked() else None
        return {
            "counterparty_id": self.combo_supplier.currentData(),
            "number": self.number_input.text(),
            "invoice_date": self.invoice_date_input.date().toPython(),
            "supply_date": self.supply_date_input.date().toPython(),
            "amount": float(self.amount_input.text()),
            "deadline_date": self.deadline_date.date().toPython(),
            "is_paid": self.paid_check.isChecked(),
            "payment_date": p_date
        }

    def toggle_payment_date(self, checked):
        self.payment_date_input.setEnabled(checked)
        # Если включили галочку - ставим сегодняшнюю дату (для удобства), но можно менять
        if checked and not self.is_edit_mode:
            self.payment_date_input.setDate(QDate.currentDate())
        # Если галочку убрали - очищаем дату
        if not checked:
            self.setup_empty_date(self.payment_date_input)

    def setup_empty_date(self, date_edit):
        """
        Магия пустого поля:
        1. Устанавливаем нулевую дату (0,0,0).
        2. Говорим виджету: если дата нулевая - показывай пустой текст.
        """
        # Устанавливаем "нулевую" дату (она считается невалидной)
        date_edit.setDate(QDate(0, 0, 0))
        # Говорим: отображать пробелы, если дата "минимальная"
        date_edit.setSpecialValueText("  .  .    ")
