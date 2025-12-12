import sys
from PySide6.QtWidgets import QApplication
from views.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    app.setStyle("Fusion")

    window = MainWindow()

    # Увеличить шрифт во всем приложении
    font = app.font()
    font.setPointSize(10)  # Размер шрифта 10 или 12
    app.setFont(font)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
