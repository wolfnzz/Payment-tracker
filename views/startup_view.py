import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, QPushButton,
                               QLabel, QInputDialog, QMessageBox, QHBoxLayout, QMenu)
from PySide6.QtCore import Signal, Qt, QPoint


class StartupView(QWidget):
    # Сигнал, который мы отправим в main.py, когда база выбрана
    # Он передаст имя файла
    db_selected = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Выбор организации")
        self.resize(400, 300)
        self.setup_ui()
        self.refresh_db_list()

    def setup_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Выберите базу данных организации или создайте новую:"))

        # Список баз
        self.db_list_widget = QListWidget()
        # --- НАСТРОЙКА КОНТЕКСТНОГО МЕНЮ (ПКМ) ---
        # 1. Разрешаем вызов своего меню
        self.db_list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        # 2. Подключаем сигнал нажатия ПКМ к нашей функции
        self.db_list_widget.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.db_list_widget)

        # Кнопки
        btn_layout = QHBoxLayout()
        self.btn_open = QPushButton("Открыть выбранную")
        self.btn_create = QPushButton("Создать новую")

        #self.btn_open.setStyleSheet("background-color: #e3f2fd;")
        #self.btn_create.setStyleSheet("background-color: #d1ffd6;")

        btn_layout.addWidget(self.btn_open)
        btn_layout.addWidget(self.btn_create)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # События
        self.btn_open.clicked.connect(self.open_db)
        self.btn_create.clicked.connect(self.create_db)
        # Двойной клик по списку тоже открывает
        self.db_list_widget.itemDoubleClicked.connect(self.open_db)

    def refresh_db_list(self):
        """Сканирует папку и ищет файлы .db"""
        self.db_list_widget.clear()
        files = [f for f in os.listdir('.') if f.endswith('.db')]
        self.db_list_widget.addItems(files)

    def open_db(self):
        # Смотрим, что выбрано
        current_item = self.db_list_widget.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Ошибка", "Выберите базу из списка!")
            return

        db_name = current_item.text()
        # Испускаем сигнал: "Мы готовы, вот имя базы"
        self.db_selected.emit(db_name)

    def create_db(self):
        name, ok = QInputDialog.getText(self, "Новая организация", "Введите название:")
        if ok and name.strip():
            # Добавляем .db если пользователь забыл
            if not name.endswith(".db"):
                filename = name.strip() + ".db"
            else:
                filename = name.strip()

            # Проверяем, нет ли такой уже
            if os.path.exists(filename):
                QMessageBox.warning(self, "Ошибка", "Такая база уже существует!")
                return

            # Испускаем сигнал с новым именем
            # База создастся автоматически благодаря initialize_db
            self.db_selected.emit(filename)

    def show_context_menu(self, pos: QPoint):
        """Создает и показывает меню при клике правой кнопкой"""
        # Узнаем, на какой элемент нажали
        item = self.db_list_widget.itemAt(pos)

        if item is None:
            return  # Нажали на пустое место - ничего не делаем

        # Создаем меню
        menu = QMenu(self)

        rename_action = menu.addAction("Переименовать")
        delete_action = menu.addAction("Удалить")

        # Запускаем меню и ждем выбора пользователя
        # mapToGlobal переводит координаты внутри окна в координаты экрана
        action = menu.exec(self.db_list_widget.mapToGlobal(pos))

        if action == rename_action:
            self.rename_db(item.text())
        elif action == delete_action:
            self.delete_db(item.text())

    def rename_db(self, filename):
        """Логика переименования"""
        old_name_clean = filename.removesuffix(".db")

        new_name, ok = QInputDialog.getText(
            self, "Переименование", "Новое название:", text=old_name_clean
        )

        if ok and new_name.strip():
            # Формируем новое имя файла
            new_filename = new_name.strip()
            if not new_filename.endswith(".db"):
                new_filename += ".db"

            # Проверка: не занято ли имя
            if os.path.exists(new_filename):
                QMessageBox.warning(self, "Ошибка", "Файл с таким именем уже существует!")
                return

            try:
                os.rename(filename, new_filename)  # Переименовываем физически
                self.refresh_db_list()  # Обновляем список
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось переименовать:\n{e}")

    def delete_db(self, filename):
        """Логика удаления"""
        reply = QMessageBox.question(
            self, "Удаление",
            f"Вы уверены, что хотите БЕЗВОЗВРАТНО удалить базу:\n{filename}?\n\nВсе данные будут потеряны!",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                os.remove(filename)  # Удаляем физически
                self.refresh_db_list()  # Обновляем список
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить:\n{e}")
