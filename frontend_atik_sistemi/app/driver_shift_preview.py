import sys
from PySide6.QtWidgets import QApplication
from views.pages.driver_shift_page import DriverShiftPage


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = DriverShiftPage()
    window.resize(1500, 880)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()