from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QTableWidget, QTableWidgetItem, QPushButton,
                               QHeaderView, QMessageBox, QAbstractItemView, QFileDialog)
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

        # Кнопки
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

    def load_data(self):
        invoices = self.view_model.get_all_invoices()
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

            deadline_str = inv.deadline_date.strftime("%d.%m.%Y")
            self.table.setItem(row, 5, QTableWidgetItem(deadline_str))

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
                data["amount"], data["terms"], data["is_paid"]
            )
            self.load_data()

    def toggle_status(self):
        selected = self.table.selectionModel().selectedRows()
        if not selected:
            return

        row = selected[0].row()
        inv_id = int(self.table.item(row, 0).text())

        self.view_model.toggle_payment_status(inv_id)
        self.load_data()

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
            'terms': target_invoice.payment_term_days,
            'is_paid': target_invoice.is_paid
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
                new_data["terms"],
                new_data["is_paid"]
            )

            # Перерисовываем таблицу
            self.load_data()

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
            self.load_data()

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