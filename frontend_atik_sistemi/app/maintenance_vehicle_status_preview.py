import sys
from PySide6.QtWidgets import QApplication
from views.pages.maintenance_vehicle_status_page import MaintenanceVehicleStatusPage


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MaintenanceVehicleStatusPage()
    window.resize(1500, 880)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()