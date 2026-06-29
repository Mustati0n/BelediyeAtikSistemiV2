from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from services.api_client import api_client
from views.pages.driver_delivery_page import DriverDeliveryPage
from views.pages.driver_shift_page import DriverShiftPage
from views.pages.driver_tasks_page import DriverTasksPage


class DriverWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sofor Operasyon Paneli")
        self.resize(1520, 900)
        self.menu_buttons = {}

        self.build_ui()
        self.apply_styles()

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.build_topbar())
        layout.addWidget(self.build_body())

    def build_topbar(self):
        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar.setFixedHeight(74)

        layout = QHBoxLayout(topbar)
        layout.setContentsMargins(22, 10, 22, 10)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title = QLabel("Sofor Operasyon Paneli")
        title.setObjectName("brandLabel")
        subtitle = QLabel("Vardiya, gorev ve teslim akisi")
        subtitle.setObjectName("brandSubtitle")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)

        self.status_pill = QLabel("Canlı API")
        self.status_pill.setObjectName("statusPill")

        layout.addLayout(title_col)
        layout.addStretch()
        layout.addWidget(self.status_pill)

        return topbar

    def build_body(self):
        body = QWidget()
        layout = QHBoxLayout(body)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.build_sidebar())
        layout.addWidget(self.build_pages())
        return body

    def build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(260)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(20, 26, 20, 24)
        layout.setSpacing(14)

        layout.addWidget(self.build_menu_button("Vardiya", "shift", 0))
        layout.addWidget(self.build_menu_button("Gunluk Gorevler", "tasks", 1))
        layout.addWidget(self.build_menu_button("Teslim ve Kapanis", "delivery", 2))
        layout.addStretch()

        logout = self.build_menu_button("Cikis Yap", "logout", None)
        logout.clicked.connect(self.logout)
        layout.addWidget(logout)
        self.menu_buttons.pop("logout")
        return sidebar

    def build_menu_button(self, text, key, index):
        button = QPushButton(text)
        button.setObjectName("sidebarButton")
        button.setCheckable(index is not None)
        button.setCursor(Qt.PointingHandCursor)
        button.setFixedHeight(56)
        if index is not None:
            button.clicked.connect(lambda _=False, i=index, k=key: self.change_page(i, k))
            self.menu_buttons[key] = button
        return button

    def build_pages(self):
        self.pages = QStackedWidget()
        self.pages.setObjectName("stackedPages")
        self.pages.addWidget(DriverShiftPage())
        self.pages.addWidget(DriverTasksPage())
        self.pages.addWidget(DriverDeliveryPage())
        self.change_page(0, "shift")
        return self.pages

    def change_page(self, index, key):
        self.pages.setCurrentIndex(index)
        for button_key, button in self.menu_buttons.items():
            button.setChecked(button_key == key)
            button.setObjectName("sidebarButtonActive" if button_key == key else "sidebarButton")
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()

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
                background: #E8F7EB;
                color: #166534;
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
            """
        )
