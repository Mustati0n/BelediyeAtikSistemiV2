import sys
from PySide6.QtWidgets import QApplication
from views.login_window import LoginWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = LoginWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()