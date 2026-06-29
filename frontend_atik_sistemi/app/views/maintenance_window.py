from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from services.api_client import api_client
from views.pages.maintenance_vehicle_status_page import MaintenanceVehicleStatusPage


class MaintenanceWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bakim Operasyon Paneli")
        self.resize(1460, 900)
        self.build_ui()
        self.apply_styles()

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self.build_topbar())

        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(260)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(20, 26, 20, 24)
        sidebar_layout.setSpacing(14)

        active = QPushButton("Arac Durum Takibi")
        active.setObjectName("sidebarButtonActive")
        active.setFixedHeight(56)

        info = QLabel(
            "Bakım ekibi şu anda canlı araç listesini,\ndurum filtrelerini ve bakım öncesi\nuygunluk görünümünü backend üzerinden izliyor."
        )
        info.setObjectName("infoLabel")
        info.setWordWrap(True)

        logout = QPushButton("Cikis Yap")
        logout.setObjectName("sidebarButton")
        logout.setFixedHeight(56)
        logout.setCursor(Qt.PointingHandCursor)
        logout.clicked.connect(self.logout)

        sidebar_layout.addWidget(active)
        sidebar_layout.addWidget(info)
        sidebar_layout.addStretch()
        sidebar_layout.addWidget(logout)

        content_layout.addWidget(sidebar)
        content_layout.addWidget(MaintenanceVehicleStatusPage())
        root.addWidget(content)

    def build_topbar(self):
        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar.setFixedHeight(74)

        layout = QHBoxLayout(topbar)
        layout.setContentsMargins(22, 10, 22, 10)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        title = QLabel("Bakim Operasyon Paneli")
        title.setObjectName("brandLabel")
        subtitle = QLabel("Arac uygunlugu ve servis takibi")
        subtitle.setObjectName("brandSubtitle")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)

        status = QLabel("Canlı API")
        status.setObjectName("statusPill")

        layout.addLayout(title_col)
        layout.addStretch()
        layout.addWidget(status)

        return topbar

    def logout(self):
        api_client.logout()
        from views.login_window import LoginWindow

        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

    def apply_styles(self):
        self.setStyleSheet(
            """
            QMainWindow, QWidget {
                background: #F7F7F5;
                font-family: Segoe UI, Arial, sans-serif;
                color: #1F2937;
            }

            #topbar, #sidebar {
                background: white;
            }

            #topbar {
                border-bottom: 1px solid #E8EBE6;
            }

            #sidebar {
                border-right: 1px solid #E8EBE6;
            }

            #brandLabel {
                font-size: 20px;
                font-weight: 900;
                color: #0B5B19;
                background: transparent;
            }

            #brandSubtitle {
                font-size: 12px;
                font-weight: 700;
                color: #64748B;
                background: transparent;
            }

            #statusPill {
                background: #FEF3C7;
                color: #92400E;
                border-radius: 14px;
                padding: 8px 14px;
                font-size: 12px;
                font-weight: 800;
            }

            #sidebarButton, #sidebarButtonActive {
                border: none;
                border-radius: 14px;
                text-align: left;
                padding-left: 18px;
                font-size: 15px;
                font-weight: 700;
            }

            #sidebarButton {
                background: transparent;
                color: #374151;
            }

            #sidebarButton:hover {
                background: #F4F5F2;
            }

            #sidebarButtonActive {
                background: #F3F4F1;
                color: #0B5B19;
            }

            #infoLabel {
                background: #FAFBF9;
                border: 1px solid #ECEEEA;
                border-radius: 16px;
                color: #475569;
                font-size: 13px;
                line-height: 1.4;
                padding: 14px;
            }
            """
        )
