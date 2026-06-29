from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QFrame,
    QLabel,
    QPushButton,
    QLineEdit,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QScrollArea,
    QSizePolicy,
)


class AdminDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Yönetici Paneli - Urban Eco-System")
        self.resize(1600, 900)
        self.build_ui()
        self.apply_styles()

    def build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        sidebar = self.build_sidebar()
        right_side = self.build_right_side()

        main_layout.addWidget(sidebar)
        main_layout.addWidget(right_side)

    def build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(300)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(26, 28, 26, 24)
        layout.setSpacing(18)

        brand_row = QHBoxLayout()
        brand_row.setSpacing(14)

        brand_icon = QLabel("🍃")
        brand_icon.setObjectName("brandIcon")
        brand_icon.setAlignment(Qt.AlignCenter)
        brand_icon.setFixedSize(46, 46)

        brand_text_col = QVBoxLayout()
        brand_text_col.setSpacing(2)

        brand_title = QLabel("City Admin")
        brand_title.setObjectName("brandTitle")

        brand_subtitle = QLabel("SUSTAINED URBAN PULSE")
        brand_subtitle.setObjectName("brandSubtitle")

        brand_text_col.addWidget(brand_title)
        brand_text_col.addWidget(brand_subtitle)

        brand_row.addWidget(brand_icon)
        brand_row.addLayout(brand_text_col)
        brand_row.addStretch()

        layout.addLayout(brand_row)
        layout.addSpacing(28)

        layout.addWidget(self.create_sidebar_button("▦   Dashboard", active=True))
        layout.addWidget(self.create_sidebar_button("🚌   Fleet Status"))
        layout.addWidget(self.create_sidebar_button("🗑   Waste Analytics"))
        layout.addWidget(self.create_sidebar_button("💵   Financials"))
        layout.addWidget(self.create_sidebar_button("📊   Reports"))

        layout.addStretch()

        new_report_btn = QPushButton("＋  New Report")
        new_report_btn.setObjectName("newReportButton")
        new_report_btn.setCursor(Qt.PointingHandCursor)
        new_report_btn.setFixedHeight(52)

        layout.addWidget(new_report_btn)

        return sidebar

    def create_sidebar_button(self, text, active=False):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedHeight(54)
        btn.setCheckable(True)
        btn.setChecked(active)

        if active:
            btn.setObjectName("sidebarButtonActive")
        else:
            btn.setObjectName("sidebarButton")

        return btn

    def build_right_side(self):
        right_side = QFrame()
        right_side.setObjectName("rightSide")

        layout = QVBoxLayout(right_side)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        topbar = self.build_topbar()
        content_scroll = self.build_content_area()

        layout.addWidget(topbar)
        layout.addWidget(content_scroll)

        return right_side

    def build_topbar(self):
        topbar = QFrame()
        topbar.setObjectName("topbar")
        topbar.setFixedHeight(86)

        layout = QHBoxLayout(topbar)
        layout.setContentsMargins(34, 18, 34, 18)
        layout.setSpacing(18)

        search_frame = QFrame()
        search_frame.setObjectName("searchFrame")
        search_frame.setFixedHeight(42)
        search_frame.setMaximumWidth(460)

        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(16, 0, 16, 0)
        search_layout.setSpacing(10)

        search_icon = QLabel("⌕")
        search_icon.setObjectName("searchIcon")

        search_input = QLineEdit()
        search_input.setPlaceholderText("Sistem genelinde ara...")
        search_input.setObjectName("searchInput")
        search_input.setFrame(False)

        search_layout.addWidget(search_icon)
        search_layout.addWidget(search_input)

        notif_btn = QPushButton("🔔")
        notif_btn.setObjectName("topIconButton")
        notif_btn.setCursor(Qt.PointingHandCursor)
        notif_btn.setFixedSize(40, 40)

        settings_btn = QPushButton("⚙")
        settings_btn.setObjectName("topIconButton")
        settings_btn.setCursor(Qt.PointingHandCursor)
        settings_btn.setFixedSize(40, 40)

        separator = QFrame()
        separator.setObjectName("topSeparator")
        separator.setFixedWidth(1)

        profile_row = QHBoxLayout()
        profile_row.setSpacing(12)

        profile_text_col = QVBoxLayout()
        profile_text_col.setSpacing(0)

        profile_name = QLabel("Admin Panel")
        profile_name.setObjectName("profileName")
        profile_role = QLabel("SÜPER YETKİLİ")
        profile_role.setObjectName("profileRole")

        profile_text_col.addWidget(profile_name, alignment=Qt.AlignRight)
        profile_text_col.addWidget(profile_role, alignment=Qt.AlignRight)

        avatar = QLabel("A")
        avatar.setObjectName("avatar")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFixedSize(44, 44)

        profile_container = QWidget()
        profile_container_layout = QHBoxLayout(profile_container)
        profile_container_layout.setContentsMargins(0, 0, 0, 0)
        profile_container_layout.setSpacing(12)
        profile_container_layout.addLayout(profile_text_col)
        profile_container_layout.addWidget(avatar)

        layout.addWidget(search_frame, 1)
        layout.addStretch()
        layout.addWidget(notif_btn)
        layout.addWidget(settings_btn)
        layout.addWidget(separator)
        layout.addWidget(profile_container)

        return topbar

    def build_content_area(self):
        scroll = QScrollArea()
        scroll.setObjectName("contentScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        content.setObjectName("contentWidget")

        layout = QVBoxLayout(content)
        layout.setContentsMargins(42, 34, 42, 30)
        layout.setSpacing(26)

        title = QLabel("Yönetici Paneli")
        title.setObjectName("pageTitle")

        subtitle = QLabel("Sistemin operasyonel ve finansal genel durum özeti.")
        subtitle.setObjectName("pageSubtitle")

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # İstatistik kartları
        stats_row = QHBoxLayout()
        stats_row.setSpacing(18)

        stats_row.addWidget(
            self.create_stat_card(
                title="GÜNLÜK TOPLANAN ATIK",
                value="42.850",
                suffix="kg",
                icon="♻",
                icon_bg="#E5F4E9",
                icon_color="#166534",
                badge_text="+12% vs dün",
                badge_bg="#E8F7EB",
                badge_color="#166534",
                left_border="#1B7A35",
                big=True,
                value_color="#0F172A",
            ),
            2,
        )

        stats_row.addWidget(
            self.create_stat_card(
                title="AKTİF FİLO",
                value="118",
                icon="🚚",
                icon_bg="#DCECF7",
                icon_color="#4C7A99",
                value_color="#0F172A",
            ),
            1,
        )

        stats_row.addWidget(
            self.create_stat_card(
                title="BAKIMDAKİ ARAÇ",
                value="6",
                icon="🛠",
                icon_bg="#EEDDE3",
                icon_color="#7A3551",
                value_color="#0F172A",
            ),
            1,
        )

        stats_row.addWidget(
            self.create_stat_card(
                title="VATANDAŞ RAPORLARI",
                value="24",
                icon="💬",
                icon_bg="#DDE8FB",
                icon_color="#3B63C7",
                value_color="#0F172A",
            ),
            1,
        )

        stats_row.addWidget(
            self.create_stat_card(
                title="KRİTİK DOLULUK",
                value="12",
                icon="⚠",
                icon_bg="#F9DEDA",
                icon_color="#C62828",
                value_color="#C62828",
                border_color="#F3C8C1",
            ),
            1,
        )

        layout.addLayout(stats_row)

        # Orta bölüm
        mid_row = QHBoxLayout()
        mid_row.setSpacing(22)

        mid_row.addWidget(self.create_financial_panel(), 3)
        mid_row.addWidget(self.create_approvals_panel(), 1.25)

        layout.addLayout(mid_row)

        # Alt bölüm
        layout.addWidget(self.create_alerts_panel())

        footer = QLabel("© 2024 URBAN ECO-SYSTEM MANAGEMENT • SUSTAINED CITY SOLUTIONS • V 2.4.1-STABLE")
        footer.setObjectName("footerLabel")
        footer.setAlignment(Qt.AlignCenter)

        layout.addWidget(footer)

        scroll.setWidget(content)
        return scroll

    def create_stat_card(
        self,
        title,
        value,
        icon,
        icon_bg,
        icon_color,
        value_color,
        suffix="",
        badge_text=None,
        badge_bg="#EEF2F7",
        badge_color="#334155",
        left_border=None,
        border_color="#E7EBE6",
        big=False,
    ):
        card = QFrame()
        card.setObjectName("statCard")
        card.setMinimumHeight(170 if big else 170)

        if left_border:
            card.setStyleSheet(
                f"""
                QFrame {{
                    background: white;
                    border: 1px solid {border_color};
                    border-left: 6px solid {left_border};
                    border-radius: 22px;
                }}
                """
            )
        elif border_color != "#E7EBE6":
            card.setStyleSheet(
                f"""
                QFrame {{
                    background: white;
                    border: 1px solid {border_color};
                    border-radius: 22px;
                }}
                """
            )

        layout = QVBoxLayout(card)
        layout.setContentsMargins(26, 22, 26, 22)
        layout.setSpacing(14)

        top_row = QHBoxLayout()
        top_row.setSpacing(10)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(46, 46)
        icon_label.setStyleSheet(
            f"""
            background: {icon_bg};
            color: {icon_color};
            border-radius: 12px;
            font-size: 20px;
            font-weight: 700;
            """
        )

        top_row.addWidget(icon_label)
        top_row.addStretch()

        if badge_text:
            badge = QLabel(badge_text)
            badge.setObjectName("statBadge")
            badge.setStyleSheet(
                f"""
                background: {badge_bg};
                color: {badge_color};
                border-radius: 14px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: 700;
                """
            )
            top_row.addWidget(badge)

        title_label = QLabel(title)
        title_label.setObjectName("statTitle")

        value_row = QHBoxLayout()
        value_row.setSpacing(6)

        value_label = QLabel(value)
        value_label.setStyleSheet(
            f"""
            font-size: 28px;
            font-weight: 800;
            color: {value_color};
            background: transparent;
            """
        )

        value_row.addWidget(value_label)

        if suffix:
            suffix_label = QLabel(suffix)
            suffix_label.setStyleSheet(
                """
                font-size: 16px;
                color: #0F172A;
                background: transparent;
                margin-top: 10px;
                """
            )
            value_row.addWidget(suffix_label)

        value_row.addStretch()

        layout.addLayout(top_row)
        layout.addWidget(title_label)
        layout.addLayout(value_row)
        layout.addStretch()

        return card

    def create_financial_panel(self):
        panel = QFrame()
        panel.setObjectName("whitePanel")
        panel.setMinimumHeight(340)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(18)

        header_row = QHBoxLayout()

        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        title = QLabel("Finansal Özet")
        title.setObjectName("panelTitle")

        subtitle = QLabel("Aylık Gelir vs. Gider Analizi")
        subtitle.setObjectName("panelSubtitle")

        title_col.addWidget(title)
        title_col.addWidget(subtitle)

        legend_row = QHBoxLayout()
        legend_row.setSpacing(16)

        gelir_dot = QLabel("●")
        gelir_dot.setStyleSheet("color: #1F7A32; font-size: 16px; background: transparent;")
        gelir_text = QLabel("Gelir")
        gelir_text.setObjectName("legendLabel")

        gider_dot = QLabel("●")
        gider_dot.setStyleSheet("color: #8C375F; font-size: 16px; background: transparent;")
        gider_text = QLabel("Gider")
        gider_text.setObjectName("legendLabel")

        legend_row.addWidget(gelir_dot)
        legend_row.addWidget(gelir_text)
        legend_row.addWidget(gider_dot)
        legend_row.addWidget(gider_text)

        legend_widget = QWidget()
        legend_widget.setLayout(legend_row)

        header_row.addLayout(title_col)
        header_row.addStretch()
        header_row.addWidget(legend_widget)

        chart_placeholder = QFrame()
        chart_placeholder.setObjectName("chartPlaceholder")

        chart_layout = QVBoxLayout(chart_placeholder)
        chart_layout.setContentsMargins(0, 0, 0, 0)

        place_text = QLabel("Grafik alanı\n\nBu bölüme daha sonra çizgi / bar chart eklenecek.")
        place_text.setObjectName("chartPlaceholderText")
        place_text.setAlignment(Qt.AlignCenter)

        chart_layout.addStretch()
        chart_layout.addWidget(place_text)
        chart_layout.addStretch()

        layout.addLayout(header_row)
        layout.addWidget(chart_placeholder)

        return panel

    def create_approvals_panel(self):
        panel = QFrame()
        panel.setObjectName("whitePanel")
        panel.setMinimumHeight(340)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(18)

        header_row = QHBoxLayout()

        title = QLabel("Bekleyen Onaylar")
        title.setObjectName("panelTitle")

        badge = QLabel("4 Bekliyor")
        badge.setStyleSheet(
            """
            background: #D9ECFA;
            color: #567A95;
            border-radius: 14px;
            padding: 6px 12px;
            font-size: 11px;
            font-weight: 700;
            """
        )

        header_row.addWidget(title)
        header_row.addStretch()
        header_row.addWidget(badge)

        layout.addLayout(header_row)

        layout.addWidget(
            self.create_approval_item(
                title="AKARYAKIT GİDERİ",
                amount="₺14.250",
                desc="Lojistik Birimi - Plaka: 34 ABC 123",
            )
        )

        layout.addWidget(
            self.create_approval_item(
                title="EKİPMAN ONARIMI",
                amount="₺8.400",
                desc="Bakım Atölyesi - Kompresör Değişimi",
            )
        )

        layout.addWidget(
            self.create_approval_item(
                title="SERVİS FATURASI",
                amount="₺5.620",
                desc="Araç Servisi - Periyodik Kontrol",
            )
        )

        layout.addStretch()

        return panel

    def create_approval_item(self, title, amount, desc):
        item = QFrame()
        item.setObjectName("approvalItem")

        layout = QVBoxLayout(item)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        top_row = QHBoxLayout()

        title_label = QLabel(title)
        title_label.setObjectName("approvalTitle")

        amount_label = QLabel(amount)
        amount_label.setObjectName("approvalAmount")

        top_row.addWidget(title_label)
        top_row.addStretch()
        top_row.addWidget(amount_label)

        desc_label = QLabel(desc)
        desc_label.setObjectName("approvalDesc")

        buttons_row = QHBoxLayout()
        buttons_row.setSpacing(10)

        approve_btn = QPushButton("ONAYLA")
        approve_btn.setObjectName("approveButton")
        approve_btn.setCursor(Qt.PointingHandCursor)
        approve_btn.setFixedHeight(34)

        reject_btn = QPushButton("REDDET")
        reject_btn.setObjectName("rejectButton")
        reject_btn.setCursor(Qt.PointingHandCursor)
        reject_btn.setFixedHeight(34)

        buttons_row.addWidget(approve_btn)
        buttons_row.addWidget(reject_btn)

        layout.addLayout(top_row)
        layout.addWidget(desc_label)
        layout.addLayout(buttons_row)

        return item

    def create_alerts_panel(self):
        panel = QFrame()
        panel.setObjectName("whitePanel")
        panel.setMinimumHeight(320)

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(18)

        header_row = QHBoxLayout()

        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        title = QLabel("Kritik Sistem Uyarıları")
        title.setObjectName("panelTitle")

        subtitle = QLabel("Son 24 saat içindeki acil durumlar")
        subtitle.setObjectName("panelSubtitle")

        title_col.addWidget(title)
        title_col.addWidget(subtitle)

        see_all = QPushButton("Tümünü Gör  →")
        see_all.setObjectName("seeAllButton")
        see_all.setCursor(Qt.PointingHandCursor)

        header_row.addLayout(title_col)
        header_row.addStretch()
        header_row.addWidget(see_all)

        layout.addLayout(header_row)

        table_head = QHBoxLayout()
        table_head.setSpacing(10)
        table_head.addWidget(self.create_table_head("VARLIK / KONUM"), 4)
        table_head.addWidget(self.create_table_head("UYARI TİPİ"), 2.8)
        table_head.addWidget(self.create_table_head("DURUM"), 2.0)
        table_head.addWidget(self.create_table_head("ZAMAN"), 1.8)
        table_head.addWidget(self.create_table_head("İŞLEM", align=Qt.AlignCenter), 1.8)

        head_widget = QWidget()
        head_widget.setLayout(table_head)

        layout.addWidget(head_widget)

        layout.addWidget(
            self.create_alert_row(
                icon="🗑",
                icon_bg="#F4DEE5",
                asset_title="Konteyner #8842",
                asset_subtitle="Bahçelievler Mah. 4. Sokak",
                warning="Aşırı Doluluk (95%)",
                status="●  Acil Tahliye",
                status_color="#D64545",
                time_text="12 dk önce",
                action_text="ARAÇ ATA",
            )
        )

        layout.addWidget(
            self.create_alert_row(
                icon="🚚",
                icon_bg="#DCECF7",
                asset_title="Plaka 06 XYZ 99",
                asset_subtitle="Rota Dışı Sapma Tespit Edildi",
                warning="Güvenlik İhlali",
                status="●  İnceleniyor",
                status_color="#D9930D",
                time_text="45 dk önce",
                action_text="TAKİP ET",
            )
        )

        layout.addWidget(
            self.create_alert_row(
                icon="🌡",
                icon_bg="#F9DEDA",
                asset_title="Sensör İstasyonu S-12",
                asset_subtitle="Merkez Depolama Alanı",
                warning="Yüksek Isı Uyarısı",
                status="●  Kritik",
                status_color="#C62828",
                time_text="1 saat önce",
                action_text="İTFAİYE BİLDİR",
            )
        )

        return panel

    def create_table_head(self, text, align=Qt.AlignLeft):
        label = QLabel(text)
        label.setObjectName("tableHeadLabel")
        label.setAlignment(align | Qt.AlignVCenter)
        return label

    def create_alert_row(
        self,
        icon,
        icon_bg,
        asset_title,
        asset_subtitle,
        warning,
        status,
        status_color,
        time_text,
        action_text,
    ):
        row = QFrame()
        row.setObjectName("alertRow")

        layout = QHBoxLayout(row)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        # Varlık / konum
        asset_widget = QWidget()
        asset_layout = QHBoxLayout(asset_widget)
        asset_layout.setContentsMargins(0, 0, 0, 0)
        asset_layout.setSpacing(12)

        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(38, 38)
        icon_label.setStyleSheet(
            f"""
            background: {icon_bg};
            border-radius: 10px;
            font-size: 16px;
            """
        )

        asset_text_col = QVBoxLayout()
        asset_text_col.setSpacing(2)

        asset_title_label = QLabel(asset_title)
        asset_title_label.setObjectName("alertAssetTitle")

        asset_subtitle_label = QLabel(asset_subtitle)
        asset_subtitle_label.setObjectName("alertAssetSubtitle")

        asset_text_col.addWidget(asset_title_label)
        asset_text_col.addWidget(asset_subtitle_label)

        asset_layout.addWidget(icon_label)
        asset_layout.addLayout(asset_text_col)

        warning_label = QLabel(warning)
        warning_label.setObjectName("alertWarning")

        status_label = QLabel(status)
        status_label.setStyleSheet(
            f"""
            color: {status_color};
            font-size: 13px;
            font-weight: 700;
            background: transparent;
            """
        )

        time_label = QLabel(time_text)
        time_label.setObjectName("alertTime")

        action_btn = QPushButton(action_text)
        action_btn.setObjectName("alertActionButton")
        action_btn.setCursor(Qt.PointingHandCursor)
        action_btn.setFixedHeight(36)
        action_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout.addWidget(asset_widget, 4)
        layout.addWidget(warning_label, 3)
        layout.addWidget(status_label, 2)
        layout.addWidget(time_label, 2)
        layout.addWidget(action_btn, 1.6)

        return row

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background: #F5F6F3;
                font-family: Segoe UI, Arial, sans-serif;
                color: #0F172A;
            }

            #sidebar {
                background: #F7F8F6;
                border-right: 1px solid #E3E7E1;
            }

            #brandIcon {
                background: #176B23;
                color: white;
                border-radius: 14px;
                font-size: 22px;
                font-weight: 700;
            }

            #brandTitle {
                font-size: 18px;
                font-weight: 800;
                color: #163025;
                background: transparent;
            }

            #brandSubtitle {
                font-size: 11px;
                letter-spacing: 1px;
                color: #7A8188;
                background: transparent;
            }

            #sidebarButton, #sidebarButtonActive {
                border: none;
                border-radius: 14px;
                text-align: left;
                padding-left: 16px;
                font-size: 15px;
                font-weight: 600;
            }

            #sidebarButton {
                background: transparent;
                color: #6C7380;
            }

            #sidebarButton:hover {
                background: #EEF3EE;
                color: #174A2A;
            }

            #sidebarButtonActive {
                background: #F1F7F1;
                color: #14532D;
                border-right: 4px solid #1B7A35;
            }

            #newReportButton {
                background: #0E611C;
                color: white;
                border: none;
                border-radius: 16px;
                font-size: 15px;
                font-weight: 700;
            }

            #newReportButton:hover {
                background: #0B4E17;
            }

            #rightSide {
                background: #F5F6F3;
            }

            #topbar {
                background: white;
                border-bottom: 1px solid #E8ECE7;
            }

            #searchFrame {
                background: #F0F1EF;
                border-radius: 20px;
            }

            #searchIcon {
                color: #808894;
                font-size: 18px;
                background: transparent;
            }

            #searchInput {
                background: transparent;
                border: none;
                font-size: 15px;
                color: #475569;
            }

            #searchInput::placeholder {
                color: #8A93A0;
            }

            #topIconButton {
                background: transparent;
                border: none;
                font-size: 20px;
            }

            #topIconButton:hover {
                background: #F3F5F3;
                border-radius: 12px;
            }

            #topSeparator {
                background: #E6EAE5;
                margin-top: 6px;
                margin-bottom: 6px;
            }

            #profileName {
                font-size: 15px;
                font-weight: 800;
                color: #212529;
                background: transparent;
            }

            #profileRole {
                font-size: 11px;
                color: #8A93A0;
                font-weight: 700;
                background: transparent;
            }

            #avatar {
                background: #D9ECFA;
                color: #2D5E88;
                border-radius: 22px;
                font-size: 18px;
                font-weight: 800;
            }

            #contentWidget {
                background: #F5F6F3;
            }

            #pageTitle {
                font-size: 40px;
                font-weight: 900;
                color: #0C5A17;
                background: transparent;
            }

            #pageSubtitle {
                font-size: 16px;
                color: #334155;
                background: transparent;
                margin-bottom: 8px;
            }

            #statCard, #whitePanel, #alertRow, #approvalItem {
                background: white;
                border: 1px solid #E7EBE6;
                border-radius: 22px;
            }

            #statTitle {
                font-size: 14px;
                font-weight: 800;
                color: #263238;
                letter-spacing: 1px;
                background: transparent;
            }

            #panelTitle {
                font-size: 18px;
                font-weight: 800;
                color: #111827;
                background: transparent;
            }

            #panelSubtitle {
                font-size: 13px;
                color: #475569;
                background: transparent;
            }

            #legendLabel {
                font-size: 13px;
                color: #111827;
                background: transparent;
            }

            #chartPlaceholder {
                background: #FCFCFB;
                border: 1px dashed #D8DDD7;
                border-radius: 18px;
                min-height: 210px;
            }

            #chartPlaceholderText {
                background: transparent;
                color: #98A2B3;
                font-size: 14px;
                font-weight: 600;
            }

            #approvalItem {
                background: #FAFBF9;
                border-radius: 18px;
            }

            #approvalTitle {
                font-size: 14px;
                font-weight: 800;
                color: #4B5563;
                background: transparent;
            }

            #approvalAmount {
                font-size: 15px;
                font-weight: 800;
                color: #111827;
                background: transparent;
            }

            #approvalDesc {
                font-size: 13px;
                color: #475569;
                background: transparent;
            }

            #approveButton {
                background: #A5ED91;
                color: #164E1A;
                border: none;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 800;
                padding: 8px 12px;
            }

            #approveButton:hover {
                background: #8EE379;
            }

            #rejectButton {
                background: #F3F4F6;
                color: #4B5563;
                border: none;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 800;
                padding: 8px 12px;
            }

            #rejectButton:hover {
                background: #E8EAED;
            }

            #seeAllButton {
                background: transparent;
                border: none;
                color: #0C5A17;
                font-size: 14px;
                font-weight: 800;
            }

            #seeAllButton:hover {
                color: #084112;
            }

            #tableHeadLabel {
                font-size: 12px;
                font-weight: 900;
                letter-spacing: 1px;
                color: #334155;
                background: transparent;
                padding-left: 6px;
                padding-right: 6px;
            }

            #alertRow {
                background: #FAFBF9;
                border-radius: 18px;
            }

            #alertAssetTitle {
                font-size: 14px;
                font-weight: 800;
                color: #111827;
                background: transparent;
            }

            #alertAssetSubtitle {
                font-size: 12px;
                color: #64748B;
                background: transparent;
            }

            #alertWarning {
                font-size: 13px;
                color: #8A1538;
                font-weight: 700;
                background: transparent;
            }

            #alertTime {
                font-size: 13px;
                color: #334155;
                background: transparent;
            }

            #alertActionButton {
                background: white;
                color: #1F2937;
                border: 1px solid #D1D5DB;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 800;
                padding: 8px 12px;
            }

            #alertActionButton:hover {
                background: #F6F7F8;
            }

            #footerLabel {
                font-size: 11px;
                letter-spacing: 1px;
                color: #98A2B3;
                background: transparent;
                margin-top: 6px;
            }
        """)