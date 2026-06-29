import sys
from PySide6.QtWidgets import QApplication
from views.pages.driver_tasks_page import DriverTasksPage


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = DriverTasksPage()
    window.resize(1540, 900)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()