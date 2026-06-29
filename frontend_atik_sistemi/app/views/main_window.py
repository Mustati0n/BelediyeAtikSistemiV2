from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from services.api_client import api_client
from views.pages.audit_log_page import AuditLogPage
from views.pages.containers_page import ContainersPage
from views.pages.dashboard_page import DashboardPage
from views.pages.parameters_page import ParametersPage
from views.pages.personnel_page import PersonnelPage
from views.pages.vehicles_page import VehiclesPage


class MainWindow(QMainWindow):
    PAGE_META = [
        ("dashboard", "Panelde ara..."),
        ("personnel", "Personel ara..."),
        ("vehicles", "Arac veya plaka ara..."),
        ("containers", "Konteyner veya bolge ara..."),
        ("parameters", "Parametre ara..."),
        ("audit", "Log veya kullanici ara..."),
    ]

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Akilli Sehir Atik Yonetimi Sistemi")
        self.resize(1650, 920)

        self.menu_buttons = {}
        self.page_widgets = {}
        self.current_page_key = "dashboard"

        self.build_ui()
        self.apply_styles()

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        root_layout.addWidget(self.build_topbar())
        root_layout.addWidget(self.build_body())

    def build_topbar(self):
        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar.setFixedHeight(74)

        layout = QHBoxLayout(topbar)
        layout.setContentsMargins(22, 10, 22, 10)
        layout.setSpacing(16)

        brand = QLabel("Akilli Sehir Atik Yonetimi")
        brand.setObjectName("brandLabel")

        subtitle = QLabel("Operasyon Kontrol Merkezi")
        subtitle.setObjectName("brandSubtitle")

        brand_col = QVBoxLayout()
        brand_col.setSpacing(2)
        brand_col.addWidget(brand)
        brand_col.addWidget(subtitle)

        search_frame = QFrame()
        search_frame.setObjectName("searchFrame")
        search_frame.setFixedHeight(44)
        search_frame.setMaximumWidth(420)

        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(16, 0, 16, 0)
        search_layout.setSpacing(10)

        search_icon = QLabel("Ara")
        search_icon.setObjectName("searchIcon")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Panelde ara...")
        self.search_input.setObjectName("searchInput")
        self.search_input.setFrame(False)
        self.search_input.textChanged.connect(self.apply_global_search)

        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)

        notif_btn = QPushButton("Bildirim")
        notif_btn.setObjectName("topIconButton")
        notif_btn.setFixedHeight(38)
        notif_btn.clicked.connect(self.show_notifications)

        settings_btn = QPushButton("Ayarlar")
        settings_btn.setObjectName("topIconButton")
        settings_btn.setFixedHeight(38)
        settings_btn.clicked.connect(self.show_settings)

        avatar = QLabel("SA")
        avatar.setObjectName("topAvatar")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFixedSize(42, 42)

        layout.addLayout(brand_col)
        layout.addSpacing(14)
        layout.addWidget(search_frame)
        layout.addStretch()
        layout.addWidget(notif_btn)
        layout.addWidget(settings_btn)
        layout.addWidget(avatar)

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
        sidebar.setFixedWidth(280)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(22, 26, 18, 24)
        layout.setSpacing(16)

        team_title = QLabel("Fleet Control")
        team_title.setObjectName("teamTitle")

        team_subtitle = QLabel("SEKTOR 7-G ADMIN")
        team_subtitle.setObjectName("teamSubtitle")

        layout.addWidget(team_title)
        layout.addWidget(team_subtitle)
        layout.addSpacing(20)

        menu_items = [
            ("dashboard", "Dashboard", 0),
            ("personnel", "Personel", 1),
            ("vehicles", "Filo", 2),
            ("containers", "Konteyner", 3),
            ("parameters", "Parametre", 4),
            ("audit", "Loglar", 5),
        ]

        for key, label, index in menu_items:
            button = self.create_sidebar_button(label)
            button.clicked.connect(lambda _=False, i=index, k=key: self.change_page(i, k))
            self.menu_buttons[key] = button
            layout.addWidget(button)

        layout.addStretch()

        support_btn = self.create_sidebar_button("Destek")
        support_btn.clicked.connect(self.show_support)
        logout_btn = self.create_sidebar_button("Cikis Yap")
        logout_btn.clicked.connect(self.logout)

        layout.addWidget(support_btn)
        layout.addWidget(logout_btn)

        return sidebar

    def create_sidebar_button(self, text):
        btn = QPushButton(text)
        btn.setObjectName("sidebarButton")
        btn.setCheckable(True)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(58)
        return btn

    def build_pages(self):
        self.pages = QStackedWidget()
        self.pages.setObjectName("stackedPages")

        self.page_widgets = {
            "dashboard": DashboardPage(),
            "personnel": PersonnelPage(),
            "vehicles": VehiclesPage(),
            "containers": ContainersPage(),
            "parameters": ParametersPage(),
            "audit": AuditLogPage(),
        }

        for key, _placeholder in self.PAGE_META:
            self.pages.addWidget(self.page_widgets[key])

        self.change_page(0, "dashboard")
        return self.pages

    def change_page(self, index, active_key):
        self.current_page_key = active_key
        self.pages.setCurrentIndex(index)

        placeholder = dict(self.PAGE_META).get(active_key, "Ara...")
        self.search_input.setPlaceholderText(placeholder)
        self.search_input.blockSignals(True)
        self.search_input.clear()
        self.search_input.blockSignals(False)
        self.apply_global_search("")

        active_page = self.page_widgets.get(active_key)
        if hasattr(active_page, "refresh_dashboard"):
            active_page.refresh_dashboard()

        for key, button in self.menu_buttons.items():
            if key == active_key:
                button.setChecked(True)
                button.setObjectName("sidebarButtonActive")
            else:
                button.setChecked(False)
                button.setObjectName("sidebarButton")

            button.style().unpolish(button)
            button.style().polish(button)
            button.update()

    def apply_global_search(self, text):
        page = self.page_widgets.get(self.current_page_key)
        if page is None or not hasattr(page, "search_input"):
            return

        page_search = page.search_input
        if page_search.text() == text:
            return

        page_search.blockSignals(True)
        page_search.setText(text)
        page_search.blockSignals(False)

        if hasattr(page, "apply_filters"):
            page.apply_filters()

    def show_notifications(self):
        QMessageBox.information(
            self,
            "Bildirimler",
            "Mock modda 3 operasyon bildirimi ve 1 kritik doluluk uyarisi bulunuyor.",
        )

    def show_settings(self):
        QMessageBox.information(
            self,
            "Ayarlar",
            "Frontend demo modunda profil ve sistem ayarlari sonraki adimda detaylandirilacak.",
        )

    def show_support(self):
        QMessageBox.information(
            self,
            "Destek",
            "Destek ekibi: support@kurum.gov.tr\nDahili hat: 2214",
        )

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

            #topbar {
                background: white;
                border-bottom: 1px solid #E8EBE6;
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

            #searchFrame {
                background: #F0F1EF;
                border-radius: 22px;
            }

            #searchIcon {
                font-size: 13px;
                color: #6B7280;
                font-weight: 700;
                background: transparent;
            }

            #searchInput {
                background: transparent;
                border: none;
                font-size: 14px;
                color: #334155;
            }

            #searchInput::placeholder {
                color: #6B7280;
            }

            #topIconButton {
                background: #F8FAF7;
                border: 1px solid #E2E8E0;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 700;
                color: #334155;
                padding: 0 14px;
            }

            #topIconButton:hover {
                background: #F3F5F2;
            }

            #topAvatar {
                background: #0B5B19;
                color: white;
                border-radius: 21px;
                font-size: 14px;
                font-weight: 800;
            }

            #sidebar {
                background: white;
                border-right: 1px solid #E8EBE6;
            }

            #teamTitle {
                font-size: 18px;
                font-weight: 800;
                color: #0B5B19;
                background: transparent;
                margin-top: 12px;
            }

            #teamSubtitle {
                font-size: 13px;
                font-weight: 800;
                letter-spacing: 1px;
                color: #263238;
                background: transparent;
                margin-bottom: 10px;
            }

            #sidebarButton, #sidebarButtonActive {
                border: none;
                border-radius: 14px;
                text-align: left;
                padding-left: 18px;
                font-size: 16px;
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

            #stackedPages {
                background: #F7F7F5;
            }
            """
        )
