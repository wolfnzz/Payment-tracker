import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

# Импортируем наши окна
from views.startup_view import StartupView
from views.main_window import MainWindow

# Импортируем функцию настройки базы
from models.database import initialize_db, close_connection

try:
    from ctypes import windll  # Только для Windows
    myappid = 'mycompany.myproduct.subproduct.version' # Любой уникальный текст
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Стиль

    icon_path = os.path.join("assets", "icon2.png")
    app.setWindowIcon(QIcon(icon_path))

    # 1. Создаем окно выбора
    startup_window = StartupView()

    # Переменная для хранения главного окна (чтобы сборщик мусора не удалил)
    # Используем список или просто переменную в области видимости main
    windows_storage = {"main": None}

    def on_db_chosen(filename):
        """Эта функция сработает, когда пользователь выберет базу"""
        print(f"Выбрана база: {filename}")

        # 1. Инициализируем движок базы данных (создаем таблицы если надо)
        initialize_db(filename)

        # 2. Закрываем окно выбора
        startup_window.close()

        clean_name = filename.removesuffix(".db")
        # 3. Создаем и показываем главное окно
        # Важно: MainWindow создается ТОЛЬКО ПОСЛЕ initialize_db
        main_win = MainWindow(clean_name)

        main_win.setWindowTitle(f"Организация: {clean_name}")  # Можно вывести имя базы в заголовок

        main_win.setWindowIcon(QIcon(icon_path))

        # Когда нажмут "Сменить базу" -> запустится функция on_logout
        main_win.logout_signal.connect(on_logout)

        main_win.show()

        # Сохраняем ссылку, чтобы окно не исчезло
        windows_storage["main"] = main_win

    def on_logout():
        """Когда нажали Выход -> открываем снова StartupView"""
        print("Возврат в меню выбора базы...")

        close_connection()
        # Главное окно уже закрылось само (мы вызвали self.close() внутри него)
        windows_storage["main"] = None  # Очищаем ссылку

        # Обновляем список баз (вдруг создали новую) и показываем окно
        startup_window.refresh_db_list()
        startup_window.show()

    # Подключаем сигнал из окна выбора к нашей функции
    startup_window.db_selected.connect(on_db_chosen)

    # Показываем стартовое окно
    startup_window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()