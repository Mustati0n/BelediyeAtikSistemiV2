from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QMessageBox,
)

from services.api_client import ApiError
from services.driver_service import DriverService


class DriverShiftPage(QWidget):
    def __init__(self):
        super().__init__()
        self.service = DriverService()
        self.shift_info = self.service.get_shift_info()

        self.build_ui()
        self.apply_styles()
        self.load_data()

    def build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(46, 34, 46, 34)
        self.content_layout.setSpacing(22)

        # Header
        header_row = QHBoxLayout()
        header_row.setSpacing(28)

        left_header = QVBoxLayout()
        left_header.setSpacing(8)

        title = QLabel("Vardiya ve Araç Bilgisi")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Şoförün güne başlamadan önce atanmış araç bilgilerini kontrol ettiği,\n"
            "vardiya başlatma ve günlük rota çağırma işlemlerini yaptığı ekran."
        )
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)

        left_header.addWidget(title)
        left_header.addWidget(subtitle)

        right_header = QVBoxLayout()
        right_header.setSpacing(14)

        self.start_shift_btn = QPushButton("▶  Vardiyayı Başlat")
        self.start_shift_btn.setObjectName("primaryButton")
        self.start_shift_btn.setCursor(Qt.PointingHandCursor)
        self.start_shift_btn.setFixedHeight(56)
        self.start_shift_btn.clicked.connect(self.start_shift)

        self.get_route_btn = QPushButton("🗺  Günlük Rotayı Getir")
        self.get_route_btn.setObjectName("secondaryButton")
        self.get_route_btn.setCursor(Qt.PointingHandCursor)
        self.get_route_btn.setFixedHeight(48)
        self.get_route_btn.clicked.connect(self.show_route_summary)

        summary_card = QFrame()
        summary_card.setObjectName("statusCard")
        summary_card.setFixedHeight(136)

        summary_layout = QHBoxLayout(summary_card)
        summary_layout.setContentsMargins(28, 18, 28, 18)

        summary_text_col = QVBoxLayout()
        summary_text_col.setSpacing(0)

        self.shift_status_value = QLabel("Hazır")
        self.shift_status_value.setObjectName("statusValue")

        self.shift_status_label = QLabel("Vardiya Durumu")
        self.shift_status_label.setObjectName("statusLabel")

        summary_text_col.addStretch()
        summary_text_col.addWidget(self.shift_status_value)
        summary_text_col.addWidget(self.shift_status_label)
        summary_text_col.addStretch()

        ghost_icon = QLabel("🚚")
        ghost_icon.setObjectName("statusGhostIcon")
        ghost_icon.setAlignment(Qt.AlignCenter)

        summary_layout.addLayout(summary_text_col)
        summary_layout.addStretch()
        summary_layout.addWidget(ghost_icon)

        right_header.addWidget(self.start_shift_btn)
        right_header.addWidget(self.get_route_btn)
        right_header.addWidget(summary_card)

        header_row.addLayout(left_header, 3)
        header_row.addLayout(right_header, 1.35)

        self.content_layout.addLayout(header_row)

        # Main cards
        cards_row = QHBoxLayout()
        cards_row.setSpacing(24)

        self.driver_panel = self.build_driver_panel()
        self.vehicle_panel = self.build_vehicle_panel()

        cards_row.addWidget(self.driver_panel, 1)
        cards_row.addWidget(self.vehicle_panel, 1.2)

        self.content_layout.addLayout(cards_row)

        # Info panel
        info_panel = QFrame()
        info_panel.setObjectName("infoPanel")

        info_layout = QVBoxLayout(info_panel)
        info_layout.setContentsMargins(28, 24, 28, 24)
        info_layout.setSpacing(12)

        info_title = QLabel("Operasyon Notları")
        info_title.setObjectName("panelTitle")

        info_1 = QLabel("• Vardiya başlamadan önce atanmış aracın aktif ve uygun durumda olduğundan emin olunuz.")
        info_2 = QLabel("• Günlük rota, görev havuzundaki atanan işlere göre sonradan backend ile üretilecektir.")
        info_3 = QLabel("• Bu ekran şu aşamada frontend mock akışı için hazırlanmıştır.")

        for label in [info_1, info_2, info_3]:
            label.setObjectName("infoText")
            label.setWordWrap(True)
            info_layout.addWidget(label)

        self.content_layout.addWidget(info_panel)

        root_layout.addWidget(content)

    def build_driver_panel(self):
        panel = QFrame()
        panel.setObjectName("cardPanel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

        title = QLabel("Şoför Bilgisi")
        title.setObjectName("panelTitle")

        self.driver_name = QLabel("-")
        self.driver_name.setObjectName("bigValue")

        self.driver_role = QLabel("Şoför")
        self.driver_role.setObjectName("subValue")

        layout.addWidget(title)
        layout.addSpacing(6)
        layout.addWidget(self.driver_name)
        layout.addWidget(self.driver_role)
        layout.addStretch()

        return panel

    def build_vehicle_panel(self):
        panel = QFrame()
        panel.setObjectName("cardPanel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        title = QLabel("Atanmış Araç Bilgisi")
        title.setObjectName("panelTitle")

        self.vehicle_name = self.build_info_row(layout, "Araç", "-")
        self.vehicle_plate = self.build_info_row(layout, "Plaka", "-")
        self.vehicle_capacity = self.build_info_row(layout, "Kapasite", "-")
        self.vehicle_type = self.build_info_row(layout, "Araç Tipi", "-")
        self.vehicle_region = self.build_info_row(layout, "Bölge", "-")
        self.vehicle_status = self.build_info_row(layout, "Durum", "-")

        layout.insertWidget(0, title)

        return panel

    def build_info_row(self, parent_layout, label_text, value_text):
        row = QFrame()
        row.setObjectName("infoRow")

        layout = QHBoxLayout(row)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(12)

        label = QLabel(label_text)
        label.setObjectName("rowLabel")

        value = QLabel(value_text)
        value.setObjectName("rowValue")
        value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(value)

        parent_layout.addWidget(row)
        return value

    def load_data(self):
        self.shift_info = self.service.get_shift_info()

        self.driver_name.setText(self.shift_info["driver_name"])
        self.shift_status_value.setText(self.shift_info["shift_status"])

        vehicle = self.shift_info["assigned_vehicle"]
        self.vehicle_name.setText(vehicle["vehicle_name"])
        self.vehicle_plate.setText(vehicle["plate"])
        self.vehicle_capacity.setText(f'{vehicle["capacity_kg"]} kg')
        self.vehicle_type.setText(vehicle["vehicle_type"])
        self.vehicle_region.setText(vehicle["region"])
        self.vehicle_status.setText(vehicle["status"])

    def start_shift(self):
        try:
            self.service.start_shift()
            self.load_data()
            QMessageBox.information(self, "Bilgi", "Vardiya başarıyla başlatıldı.")
        except ApiError as exc:
            QMessageBox.warning(self, "API Hatası", str(exc))

    def show_route_summary(self):
        try:
            route = self.service.get_daily_route_summary()
            QMessageBox.information(
                self,
                "Günlük Rota Özeti",
                f"Toplam görev: {route['task_count']}\n"
                f"Öncelikli görev: {route['priority_tasks']}\n"
                f"Bölge: {route['region']}"
            )
        except ApiError as exc:
            QMessageBox.warning(self, "API Hatası", str(exc))

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background: #F7F7F5;
                font-family: Segoe UI, Arial, sans-serif;
                color: #1F2937;
            }

            #pageTitle {
                font-size: 40px;
                font-weight: 900;
                color: #0B5B19;
                background: transparent;
            }

            #pageSubtitle {
                font-size: 16px;
                color: #334155;
                background: transparent;
            }

            #primaryButton {
                background: #005E10;
                color: white;
                border: none;
                border-radius: 16px;
                font-size: 16px;
                font-weight: 800;
                padding: 0 24px;
            }

            #primaryButton:hover {
                background: #004A0C;
            }

            #secondaryButton {
                background: white;
                color: #374151;
                border: 1px solid #D8DDD7;
                border-radius: 14px;
                font-size: 14px;
                font-weight: 700;
                padding: 0 18px;
            }

            #secondaryButton:hover {
                background: #F4F5F2;
            }

            #statusCard {
                background: #005E10;
                border-radius: 18px;
            }

            #statusValue {
                font-size: 30px;
                font-weight: 900;
                color: white;
                background: transparent;
            }

            #statusLabel {
                font-size: 13px;
                font-weight: 700;
                color: rgba(255, 255, 255, 0.82);
                background: transparent;
            }

            #statusGhostIcon {
                font-size: 70px;
                color: rgba(255, 255, 255, 0.10);
                background: transparent;
            }

            #cardPanel, #infoPanel {
                background: white;
                border: 1px solid #ECEEEA;
                border-radius: 20px;
            }

            #panelTitle {
                font-size: 20px;
                font-weight: 800;
                color: #111827;
                background: transparent;
            }

            #bigValue {
                font-size: 28px;
                font-weight: 900;
                color: #0B5B19;
                background: transparent;
            }

            #subValue {
                font-size: 14px;
                color: #475569;
                background: transparent;
            }

            #infoRow {
                background: #FAFBF9;
                border: 1px solid #ECEEEA;
                border-radius: 14px;
            }

            #rowLabel {
                font-size: 14px;
                font-weight: 700;
                color: #374151;
                background: transparent;
            }

            #rowValue {
                font-size: 14px;
                font-weight: 800;
                color: #111827;
                background: transparent;
            }

            #infoText {
                font-size: 14px;
                color: #5B7085;
                background: transparent;
            }

            QLabel {
                background: transparent;
            }

            QMessageBox {
                background: white;
            }
        """)
