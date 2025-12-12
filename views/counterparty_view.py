from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QTableWidget, QTableWidgetItem, QPushButton,
                               QHeaderView, QMessageBox, QInputDialog, QLineEdit)
from PySide6.QtCore import Qt
from viewmodels.counterparty_viewmodel import CounterpartyViewModel
from views.add_counterparty_dialog import AddCounterpartyDialog


class CounterpartyView(QWidget):
    def __init__(self):
        super().__init__()

        # 1. Инициализируем ViewModel (наш "мозг")
        self.table = None
        self.btn_delete = None  # Тестово добавлено как базовые поля
        self.btn_add = None
        self.view_model = CounterpartyViewModel()

        self.setup_ui()
        self.load_data()  # Сразу загружаем данные при старте

    def setup_ui(self):
        # Основной вертикальный слой
        layout = QVBoxLayout()

        # --- Кнопки управления (сверху) ---
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Добавить контрагента")
        self.btn_edit = QPushButton("Редактировать название")
        self.btn_delete = QPushButton("Удалить выбранного")

        # Стили
        self.btn_add.setStyleSheet("background-color: #11a629; padding: 5px;")
        self.btn_edit.setStyleSheet("background-color: #cacc62; padding: 5px;")
        self.btn_delete.setStyleSheet("background-color: #d61313; padding: 5px;")

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()  # Сдвигаем кнопки влево

        # --- Таблица ---
        self.table = QTableWidget()
        self.table.setColumnCount(2)  # ID, Имя
        self.table.setHorizontalHeaderLabels(["ID", "Название"])

        # Скрываем колонку ID (пользователю она не нужна, но нам нужна для удаления)
        self.table.hideColumn(0)

        # Растягиваем таблицу красиво
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Имя растягивается

        # Выделение всей строки, а не одной ячейки
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)

        # --- Сборка ---
        layout.addLayout(btn_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)

        # --- Подключение событий ---
        self.btn_add.clicked.connect(self.open_add_dialog)
        self.btn_edit.clicked.connect(self.edit_counterparty)
        self.btn_delete.clicked.connect(self.delete_selected)

    def load_data(self):
        """Запрашиваем данные у ViewModel и рисуем таблицу"""
        data = self.view_model.get_all_counterparties()

        self.table.setRowCount(0)  # Очистить старое

        for row_idx, person in enumerate(data):
            self.table.insertRow(row_idx)

            # ID (скрытый столбец)
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(person.id)))

            # Видимые данные
            self.table.setItem(row_idx, 1, QTableWidgetItem(person.name))

    def open_add_dialog(self):
        """Открыть диалоговое окно добавления"""
        dialog = AddCounterpartyDialog(self)
        if dialog.exec():  # Если нажали "Сохранить" (accept)
            data = dialog.get_data()
            if not data["name"]:
                QMessageBox.warning(self, "Ошибка", "Название не может быть пустым!")
                return

            # Отправляем в ViewModel
            success = self.view_model.add_counterparty(data["name"])
            if success:
                self.load_data()  # Обновляем таблицу
            else:
                QMessageBox.critical(self, "Ошибка", "Не удалось добавить (возможно, такое имя уже есть)")

    def delete_selected(self):
        """Удаление выделенной строки"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Внимание", "Выберите строку для удаления")
            return
        # Окно удаления поставщика
        rmv_box = QMessageBox(self)
        rmv_box.setWindowTitle("Удаление")
        rmv_box.setText("Удалить выбранного поставщика?")
        rmv_box.setIcon(QMessageBox.Question)
        rmv_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        rmv_box.button(QMessageBox.Yes).setText("Да")
        rmv_box.button(QMessageBox.No).setText("Нет")

        # Запускаем окно и ждем ответа
        reply = rmv_box.exec()

        if reply == QMessageBox.Yes:
            row_idx = selected_rows[0].row()
            # Берем ID из скрытого 0-го столбца
            c_id = int(self.table.item(row_idx, 0).text())

            self.view_model.delete_counterparty(c_id)
            self.load_data()

    def edit_counterparty(self):
        """Редактирование названия"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Внимание", "Выберите строку для редактирования")
            return

        row_idx = selected_rows[0].row()


        c_id = int(self.table.item(row_idx, 0).text())
        old_name = self.table.item(row_idx, 1).text()

        dialog = QInputDialog(self)
        dialog.setWindowTitle("Редактирование")
        dialog.setLabelText("Изменить название:")
        dialog.setTextValue(old_name)
        dialog.setInputMode(QInputDialog.TextInput)

        dialog.setOkButtonText("Сохранить")
        dialog.setCancelButtonText("Отмена")

        if dialog.exec():
            new_name = dialog.textValue()

            if new_name.strip():
                stripped_name = new_name.strip()

                if stripped_name == old_name:
                    return

                # Пытаемся обновить
                success = self.view_model.update_counterparty(c_id, stripped_name)

                if success:
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Ошибка",
                                        f"Не удалось переименовать в '{stripped_name}'.\nВозможно, имя уже занято.")
