from PySide6.QtCore import QDate
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QTableWidget, QTableWidgetItem, QPushButton,
                               QHeaderView, QMessageBox, QAbstractItemView, QFileDialog, QGroupBox, QLabel, QComboBox, QDateEdit)
from PySide6.QtGui import QColor
from viewmodels.invoice_viewmodel import InvoiceViewModel
from views.add_invoice_dialog import AddInvoiceDialog


class InvoiceView(QWidget):
    def __init__(self):
        super().__init__()
        self.view_model = InvoiceViewModel()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()

        # панель фильтров
        self.filter_group = QGroupBox("Фильтры поиска")
        filter_layout = QHBoxLayout()

        # Фильтр по поставщику
        filter_layout.addWidget(QLabel("Поставщик:"))
        self.filter_supplier_combo = QComboBox()
        self.filter_supplier_combo.addItem("Все поставщики", None)  # Первый пункт - "Все"
        # Загружаем список поставщиков в комбобокс
        suppliers = self.view_model.get_counterparties_for_combo()
        for s in suppliers:
            self.filter_supplier_combo.addItem(s.name, s.id)
        filter_layout.addWidget(self.filter_supplier_combo)

        # Тип даты
        filter_layout.addWidget(QLabel("   По дате:"))  # Отступ пробелами для красоты
        self.filter_date_type = QComboBox()
        self.filter_date_type.addItem("Не учитывать дату", None)
        self.filter_date_type.addItem("Дата поставки", "supply")
        self.filter_date_type.addItem("Срок оплаты (Дедлайн)", "deadline")
        filter_layout.addWidget(self.filter_date_type)

        # Сама дата
        self.filter_date_edit = QDateEdit()
        self.filter_date_edit.setCalendarPopup(True)
        self.filter_date_edit.setDate(QDate.currentDate())
        # По умолчанию выключим выбор даты, пока не выбран тип
        self.filter_date_edit.setEnabled(False)
        filter_layout.addWidget(self.filter_date_edit)

        # Кнопки Применить / Сбросить
        self.btn_apply_filter = QPushButton("Найти")
        self.btn_reset_filter = QPushButton("Сброс")

        filter_layout.addWidget(self.btn_apply_filter)
        filter_layout.addWidget(self.btn_reset_filter)
        filter_layout.addStretch()  # Сдвигаем всё влево

        self.filter_group.setLayout(filter_layout)
        layout.addWidget(self.filter_group)

        # Кнопки управления счетами
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Добавить счет")
        self.btn_delete = QPushButton("Удалить счет")
        self.btn_status = QPushButton("Изменить статус оплаты")

        #self.btn_add.setStyleSheet("background-color: #11a629; padding: 5px;")

        self.btn_export = QPushButton("Выгрузить в Excel")


        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_status)
        btn_layout.addWidget(self.btn_export)
        btn_layout.addStretch()

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "Номер",
            "Дата счета",
            "Поставщик",
            "Дата поставки",
            "Оплатить до",
            "Сумма",
            "Статус",
            "Дата оплаты"
        ])
        self.table.hideColumn(0)  # Скрываем ID

        # Растягивание
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Поставщик растягивается

        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)

        # запрет на редактирование ячеек напрямую
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        layout.addLayout(btn_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)

        # События
        self.btn_add.clicked.connect(self.open_add_dialog)
        self.btn_delete.clicked.connect(self.delete_current_invoice)
        self.btn_status.clicked.connect(self.toggle_status)
        self.btn_export.clicked.connect(self.export_to_excel)

        # Когда дважды кликаем по ячейке -> вызываем edit_current_invoice
        self.table.cellDoubleClicked.connect(self.edit_current_invoice)

        # Кнопки фильтров
        self.btn_apply_filter.clicked.connect(self.apply_filter)
        self.btn_reset_filter.clicked.connect(self.reset_filter)
        # Если меняем тип даты, включаем/выключаем поле даты
        self.filter_date_type.currentIndexChanged.connect(self.toggle_date_edit)

    def load_data(self, invoices_list=None):
        invoices = self.view_model.get_all_invoices()
        if not (invoices_list is None): invoices = invoices_list
        self.table.setRowCount(0)

        for row, inv in enumerate(invoices):
            self.table.insertRow(row)

            self.table.setItem(row, 0, QTableWidgetItem(str(inv.id)))

            self.table.setItem(row, 1, QTableWidgetItem(inv.invoice_number))

            self.table.setItem(row, 2, QTableWidgetItem(inv.invoice_date.strftime("%d.%m.%Y")))

            # Если поставщик был удален, может возникнуть ошибка, поэтому проверяем
            name = inv.counterparty.name if inv.counterparty else "<Удален>"
            self.table.setItem(row, 3, QTableWidgetItem(name))

            self.table.setItem(row, 4, QTableWidgetItem(inv.supply_date.strftime("%d.%m.%Y")))

            self.table.setItem(row, 5, QTableWidgetItem(inv.deadline_date.strftime("%d.%m.%Y")))

            self.table.setItem(row, 6, QTableWidgetItem(str(inv.amount)))

            status_text = "Оплачено" if inv.is_paid else "Не оплачено"
            status_item = QTableWidgetItem(status_text)

            # Зеленый если оплачено, красный если нет
            if inv.is_paid:
                status_item.setBackground(QColor("#11a629"))
            else:
                status_item.setBackground(QColor("#d61313"))

            self.table.setItem(row, 7, status_item)

            pay_date_str = inv.payment_date.strftime("%d.%m.%Y") if inv.payment_date else "-"
            self.table.setItem(row, 8, QTableWidgetItem(pay_date_str))

    def open_add_dialog(self):
        # получаем список поставщиков для выпадающего списка
        suppliers = self.view_model.get_counterparties_for_combo()

        dialog = AddInvoiceDialog(suppliers, self)
        if dialog.exec():
            data = dialog.get_data()
            self.view_model.add_invoice(
                data["counterparty_id"], data["number"], data["invoice_date"], data["supply_date"],
                data["amount"], data["deadline_date"], data["is_paid"], data["payment_date"]
            )
            #self.load_data()
            self.apply_filter()

    def toggle_status(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            return

        row = selected[0].row()
        inv_id = int(self.table.item(row, 0).text())

        self.view_model.toggle_payment_status(inv_id)
        #self.load_data()
        self.apply_filter()

    def edit_current_invoice(self):
        """Метод для редактирования выбранного счета"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return

        row_idx = selected_rows[0].row()

        # Получаем ID счета из скрытого 0-го столбца
        inv_id = int(self.table.item(row_idx, 0).text())

        # Получаем актуальный список из базы, чтобы найти нужный объект
        all_invoices = self.view_model.get_all_invoices()
        target_invoice = None
        for inv in all_invoices:
            if inv.id == inv_id:
                target_invoice = inv
                break

        if not target_invoice:
            return

        # Формируем словарь данных для диалога
        data_for_dialog = {
            'counterparty_id': target_invoice.counterparty_id,
            'number': target_invoice.invoice_number,
            'invoice_date': target_invoice.invoice_date,
            'supply_date': target_invoice.supply_date,
            'amount': target_invoice.amount,
            'deadline_date': target_invoice.deadline_date,
            'is_paid': target_invoice.is_paid,
            'payment_date': target_invoice.payment_date
        }

        # Открываем диалог, передавая эти данные
        suppliers = self.view_model.get_counterparties_for_combo()
        dialog = AddInvoiceDialog(suppliers, self, invoice_data=data_for_dialog)

        if dialog.exec():
            # Если нажали сохранить
            new_data = dialog.get_data()

            # Вызываем метод обновления
            self.view_model.update_invoice(
                inv_id,
                new_data["counterparty_id"],
                new_data["number"],
                new_data["invoice_date"],
                new_data["supply_date"],
                new_data["amount"],
                new_data["deadline_date"],
                new_data["is_paid"],
                new_data["payment_date"]
            )

            # Перерисовываем таблицу
            #self.load_data()
            self.apply_filter()

    def delete_current_invoice(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите счет для удаления")
            return

        row = selected[0].row()
        inv_id = int(self.table.item(row, 0).text())  # 0 - это скрытый столбец ID
        inv_number = self.table.item(row, 1).text()

        reply = QMessageBox.question(self, "Удаление",
                                     f"Удалить счет № {inv_number}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.view_model.delete_invoice(inv_id)
            self.apply_filter()

    def export_to_excel(self):
        """Обработка нажатия на кнопку экспорта"""

        # Открываем системное окно "Сохранить как"

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить отчет",  # Заголовок окна
            "Отчет_счета.xlsx",  # Имя файла по умолчанию
            "Excel Files (*.xlsx)"
        )

        # Если пользователь нажал "Отмена"
        if not filename:
            return

        # Передаем задачу во ViewModel
        success, message = self.view_model.export_data(filename)


        if success:
            QMessageBox.information(self, "Экспорт", message)
        else:
            QMessageBox.critical(self, "Ошибка", message)
            #self.load_data()
            self.apply_filter()

    def toggle_date_edit(self):
        """Включает поле даты только если выбран тип фильтрации по дате"""
        is_date_selected = self.filter_date_type.currentData() is not None
        self.filter_date_edit.setEnabled(is_date_selected)

    def apply_filter(self):
        """Считывает фильтры и обновляет таблицу"""
        # 1. Поставщик
        supplier_id = self.filter_supplier_combo.currentData()  # Вернет ID или None

        # 2. Тип даты
        date_type = self.filter_date_type.currentData()  # "supply", "deadline" или None

        # 3. Значение даты
        py_date = self.filter_date_edit.date().toPython()

        # 4. Загружаем отфильтрованные данные
        # (Передаем этот список в load_data)
        filtered_list = self.view_model.get_filtered_invoices(supplier_id, date_type, py_date)
        self.load_data(invoices_list=filtered_list)

    def reset_filter(self):
        """Сброс всех настроек в исходное"""
        self.filter_supplier_combo.setCurrentIndex(0)  # Все
        self.filter_date_type.setCurrentIndex(0)  # Не учитывать
        self.filter_date_edit.setDate(QDate.currentDate())
        self.load_data()  # Загружаем всё
