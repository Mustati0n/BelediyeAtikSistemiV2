from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from services.api_client import ApiError, api_client
from views.driver_window import DriverWindow
from views.main_window import MainWindow
from views.maintenance_window import MaintenanceWindow


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Akilli Sehir Atik Yonetimi Sistemi")
        self.resize(1200, 760)
        self.password_visible = False

        self.build_ui()
        self.apply_styles()

    def build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(0)

        background_frame = QFrame()
        background_frame.setObjectName("backgroundFrame")

        background_layout = QVBoxLayout(background_frame)
        background_layout.setContentsMargins(0, 0, 0, 0)
        background_layout.setSpacing(0)

        overlay = QFrame()
        overlay.setObjectName("overlayFrame")

        overlay_layout = QVBoxLayout(overlay)
        overlay_layout.setContentsMargins(40, 20, 40, 20)
        overlay_layout.setSpacing(0)

        content_wrapper = QVBoxLayout()
        content_wrapper.setAlignment(Qt.AlignCenter)
        content_wrapper.setSpacing(16)

        logo_box = QLabel("S")
        logo_box.setObjectName("logoBox")
        logo_box.setAlignment(Qt.AlignCenter)
        logo_box.setFixedSize(44, 44)

        title = QLabel("AKILLI SEHIR ATIK YONETIMI SISTEMI")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignCenter)

        subtitle = QLabel("SURDURULEBILIR KENT OPERASYONLARI PORTALI")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setAlignment(Qt.AlignCenter)

        content_wrapper.addWidget(logo_box, alignment=Qt.AlignCenter)
        content_wrapper.addWidget(title)
        content_wrapper.addWidget(subtitle)

        card = QFrame()
        card.setObjectName("loginCard")
        card.setFixedWidth(500)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 10)
        card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 28, 28, 28)
        card_layout.setSpacing(18)

        username_label = QLabel("KULLANICI ADI VEYA E-POSTA")
        username_label.setObjectName("fieldLabel")
        self.username_input = self.create_input("adiniz@kurum.gov.tr", "K")

        password_label = QLabel("SIFRE")
        password_label.setObjectName("fieldLabel")
        self.password_input, self.password_toggle_btn = self.create_password_input("••••••••")

        self.error_box = QFrame()
        self.error_box.setObjectName("errorBox")
        error_layout = QHBoxLayout(self.error_box)
        error_layout.setContentsMargins(12, 10, 12, 10)
        error_layout.setSpacing(8)

        error_icon = QLabel("!")
        error_icon.setObjectName("errorIcon")

        self.error_label = QLabel("Hatali kullanici adi veya sifre. Lutfen bilgilerinizi kontrol edin.")
        self.error_label.setObjectName("errorLabel")
        self.error_label.setWordWrap(True)

        error_layout.addWidget(error_icon)
        error_layout.addWidget(self.error_label)
        self.error_box.hide()

        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(8)

        self.remember_checkbox = QCheckBox("Beni hatirla")
        self.remember_checkbox.setObjectName("rememberCheck")

        forgot_btn = QPushButton("Sifremi Unuttum?")
        forgot_btn.setObjectName("forgotButton")
        forgot_btn.setCursor(Qt.PointingHandCursor)
        forgot_btn.clicked.connect(self.forgot_password)

        bottom_row.addWidget(self.remember_checkbox)
        bottom_row.addStretch()
        bottom_row.addWidget(forgot_btn)

        login_btn = QPushButton("Portala Giris Yap   ->")
        login_btn.setObjectName("loginButton")
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.setFixedHeight(44)
        login_btn.clicked.connect(self.attempt_login)

        corporate_label = QLabel("KURUMSAL KIMLIK")
        corporate_label.setObjectName("sectionLabel")
        corporate_label.setAlignment(Qt.AlignCenter)

        corporate_buttons_row = QHBoxLayout()
        corporate_buttons_row.setSpacing(12)

        biometric_btn = QPushButton("BIYOMETRIK")
        biometric_btn.setObjectName("secondaryButton")
        biometric_btn.setFixedHeight(36)
        biometric_btn.clicked.connect(self.show_secondary_info)

        sso_btn = QPushButton("SSO GIRIS")
        sso_btn.setObjectName("secondaryButton")
        sso_btn.setFixedHeight(36)
        sso_btn.clicked.connect(self.show_secondary_info)

        corporate_buttons_row.addWidget(biometric_btn)
        corporate_buttons_row.addWidget(sso_btn)

        demo_info = QLabel(
            "Demo hesaplar: admin@belediye.local, sofor@belediye.local, bakim@belediye.local"
        )
        demo_info.setObjectName("infoLabel")
        demo_info.setAlignment(Qt.AlignCenter)

        card_layout.addWidget(username_label)
        card_layout.addWidget(self.username_input)
        card_layout.addWidget(password_label)
        card_layout.addWidget(self.password_input)
        card_layout.addWidget(self.error_box)
        card_layout.addLayout(bottom_row)
        card_layout.addWidget(login_btn)
        card_layout.addSpacing(8)
        card_layout.addWidget(corporate_label)
        card_layout.addLayout(corporate_buttons_row)
        card_layout.addWidget(demo_info)

        content_wrapper.addSpacing(8)
        content_wrapper.addWidget(card, alignment=Qt.AlignCenter)
        content_wrapper.addSpacing(14)

        info_row = QHBoxLayout()
        info_row.setSpacing(24)
        info_row.setAlignment(Qt.AlignCenter)

        info_left = QLabel("END-TO-END ENCRYPTED")
        info_left.setObjectName("infoLabel")

        info_right = QLabel("MARMARA BOLGE MUDURLUGU")
        info_right.setObjectName("infoLabel")

        info_row.addWidget(info_left)
        info_row.addWidget(info_right)

        content_wrapper.addLayout(info_row)
        content_wrapper.addStretch()

        footer = QFrame()
        footer.setObjectName("footerBar")
        footer.setFixedHeight(64)

        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(26, 0, 26, 0)
        footer_layout.setSpacing(18)

        footer_items = [
            "GIZLILIK POLITIKASI",
            "KULLANIM SARTLARI",
            "GUVENLIK MIMARISI",
            "DESTEK",
            "DOKUMANTASYON",
            "© 2026 SUSTAINED URBAN ECOSYSTEMS",
        ]

        for index, text in enumerate(footer_items):
            label = QLabel(text)
            label.setObjectName("footerLabel")
            if index == 3:
                footer_layout.addStretch()
            footer_layout.addWidget(label)

        overlay_layout.addLayout(content_wrapper, stretch=1)
        overlay_layout.addWidget(footer)

        background_layout.addWidget(overlay)
        main_layout.addWidget(background_frame)

    def create_input(self, placeholder_text, icon_text):
        wrapper = QFrame()
        wrapper.setObjectName("inputWrapper")
        wrapper.setFixedHeight(48)

        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(10)

        icon = QLabel(icon_text)
        icon.setObjectName("inputIcon")
        icon.setFixedWidth(18)
        icon.setAlignment(Qt.AlignCenter)

        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder_text)
        line_edit.setObjectName("textInput")
        line_edit.setFrame(False)

        layout.addWidget(icon)
        layout.addWidget(line_edit)
        wrapper.line_edit = line_edit
        return wrapper

    def create_password_input(self, placeholder_text):
        wrapper = QFrame()
        wrapper.setObjectName("inputWrapper")
        wrapper.setFixedHeight(48)

        layout = QHBoxLayout(wrapper)
        layout.setContentsMargins(14, 0, 14, 0)
        layout.setSpacing(10)

        icon = QLabel("*")
        icon.setObjectName("inputIcon")
        icon.setFixedWidth(18)
        icon.setAlignment(Qt.AlignCenter)

        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder_text)
        line_edit.setEchoMode(QLineEdit.Password)
        line_edit.setObjectName("textInput")
        line_edit.setFrame(False)

        toggle_btn = QToolButton()
        toggle_btn.setText("Goster")
        toggle_btn.setObjectName("toggleButton")
        toggle_btn.setCursor(Qt.PointingHandCursor)
        toggle_btn.clicked.connect(self.toggle_password_visibility)

        layout.addWidget(icon)
        layout.addWidget(line_edit)
        layout.addWidget(toggle_btn)

        wrapper.line_edit = line_edit
        return wrapper, toggle_btn

    def toggle_password_visibility(self):
        line_edit = self.password_input.line_edit
        if self.password_visible:
            line_edit.setEchoMode(QLineEdit.Password)
            self.password_toggle_btn.setText("Goster")
            self.password_visible = False
        else:
            line_edit.setEchoMode(QLineEdit.Normal)
            self.password_toggle_btn.setText("Gizle")
            self.password_visible = True

    def attempt_login(self):
        username = self.username_input.line_edit.text().strip()
        password = self.password_input.line_edit.text().strip()

        if not username or not password:
            self.error_label.setText("Kullanıcı adı ve şifre alanları zorunludur.")
            self.error_box.show()
            return

        if username.endswith("@test.local"):
            self.error_label.setText(
                "Bu masaustu canli backend'e bagli. Test hesabi yerine "
                "admin@belediye.local, sofor@belediye.local veya bakim@belediye.local kullan."
            )
            self.error_box.show()
            return

        try:
            api_client.login(username, password)
        except ApiError as exc:
            self.error_label.setText(str(exc))
            self.error_box.show()
            return

        self.error_box.hide()
        current_user = api_client.current_user or {}
        role = current_user.get("rol")

        if role == "Sofor":
            window_class = DriverWindow
        elif role == "Bakim Teknisyeni":
            window_class = MaintenanceWindow
        elif role == "Sistem Yoneticisi":
            window_class = MainWindow
        else:
            api_client.logout()
            self.error_label.setText(
                "Bu rol icin masaustu ekrani henuz baglanmadi. Simdilik admin, sofor veya bakim kullanin."
            )
            self.error_box.show()
            return

        self.next_window = window_class()
        self.next_window.show()
        self.close()

    def forgot_password(self):
        QMessageBox.information(
            self,
            "Bilgi",
            "Sifre sifirlama akisi backend ile birlikte sonraki adimda eklenecek.",
        )

    def show_secondary_info(self):
        QMessageBox.information(
            self,
            "Bilgi",
            "Biyometrik ve SSO giris butonlari bu asamada tasarim yer tutucusu olarak hazir.",
        )

    def apply_styles(self):
        self.setStyleSheet(
            """
            QWidget {
                background: transparent;
                font-family: Segoe UI, Arial, sans-serif;
                color: #1F2937;
            }

            #backgroundFrame {
                border-radius: 26px;
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #DFE4E8,
                    stop: 0.35 #EEF1EF,
                    stop: 0.7 #D8DDD9,
                    stop: 1 #CFD5D2
                );
                border: 6px solid #A8B0BB;
            }

            #overlayFrame {
                border-radius: 20px;
                background: rgba(255, 255, 255, 0.60);
            }

            #logoBox {
                background: #176B23;
                color: white;
                border-radius: 12px;
                font-size: 22px;
                font-weight: 700;
            }

            #titleLabel {
                font-size: 20px;
                font-weight: 800;
                color: #202223;
                margin-top: 6px;
            }

            #subtitleLabel {
                font-size: 11px;
                color: #5F6660;
                margin-bottom: 16px;
            }

            #loginCard {
                background: rgba(255, 255, 255, 0.88);
                border-radius: 16px;
            }

            #fieldLabel {
                font-size: 11px;
                font-weight: 700;
                color: #6F746F;
                margin-bottom: 4px;
            }

            #inputWrapper {
                background: #E9E9E9;
                border: 1px solid #DDDDDD;
                border-radius: 10px;
            }

            #inputIcon {
                color: #737373;
                font-size: 14px;
                background: transparent;
                font-weight: 700;
            }

            #textInput {
                background: transparent;
                border: none;
                font-size: 14px;
                color: #222222;
            }

            #textInput::placeholder {
                color: #8B8F96;
            }

            #toggleButton {
                border: none;
                background: transparent;
                font-size: 12px;
                color: #2C7A3F;
                font-weight: 700;
                padding: 0 4px;
            }

            #errorBox {
                background: #FDE8E8;
                border-radius: 10px;
                border: 1px solid #F5C2C2;
            }

            #errorIcon {
                background: transparent;
                color: #C53030;
                font-size: 14px;
                font-weight: 800;
            }

            #errorLabel {
                background: transparent;
                color: #C53030;
                font-size: 12px;
                font-weight: 600;
            }

            #rememberCheck {
                font-size: 12px;
                color: #6B7280;
                background: transparent;
            }

            #forgotButton {
                border: none;
                background: transparent;
                color: #2C7A3F;
                font-size: 12px;
                font-weight: 700;
                padding: 0;
            }

            #forgotButton:hover {
                color: #1E5E30;
            }

            #loginButton {
                background: #0F6A1F;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 700;
                padding: 10px 18px;
            }

            #loginButton:hover {
                background: #0C5719;
            }

            #sectionLabel {
                font-size: 11px;
                font-weight: 700;
                color: #B1B5B9;
                margin-top: 8px;
            }

            #secondaryButton {
                background: #F1F1F1;
                color: #5E6368;
                border: 1px solid #E1E1E1;
                border-radius: 10px;
                font-size: 12px;
                font-weight: 700;
            }

            #secondaryButton:hover {
                background: #E8E8E8;
            }

            #infoLabel {
                font-size: 11px;
                color: #6B7280;
                background: transparent;
            }

            #footerBar {
                background: rgba(255, 255, 255, 0.82);
                border-bottom-left-radius: 18px;
                border-bottom-right-radius: 18px;
                border-top: 1px solid rgba(150, 150, 150, 0.15);
            }

            #footerLabel {
                font-size: 10px;
                color: #84888F;
                background: transparent;
                font-weight: 600;
            }
            """
        )
