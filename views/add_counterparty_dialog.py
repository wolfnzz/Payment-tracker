from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox


class AddCounterpartyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Новый контрагент")
        self.setFixedSize(300, 200)

        layout = QVBoxLayout()

        # Поля ввода
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Название (обязательно)")

        # Кнопки
        self.save_btn = QPushButton("Сохранить")
        self.cancel_btn = QPushButton("Отмена")

        # Добавляем на экран
        layout.addWidget(QLabel("Введите данные поставщика:"))
        layout.addWidget(self.name_input)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.cancel_btn)

        self.setLayout(layout)

        # Подключаем кнопки
        self.save_btn.clicked.connect(self.accept)  # accept закрывает окно с результатом "ОК"
        self.cancel_btn.clicked.connect(self.reject)  # reject закрывает с результатом "Отмена"

    def get_data(self):
        """Возвращает данные, которые ввел пользователь"""
        return {
            "name": self.name_input.text().strip()
        }
