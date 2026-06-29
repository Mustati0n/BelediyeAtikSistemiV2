import sys
from PySide6.QtWidgets import QApplication
from views.pages.driver_delivery_page import DriverDeliveryPage


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = DriverDeliveryPage()
    window.resize(1500, 880)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()