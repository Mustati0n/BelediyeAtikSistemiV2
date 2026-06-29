from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QDoubleSpinBox,
    QTextEdit,
    QMessageBox,
    QScrollArea,
)

from services.api_client import ApiError
from services.driver_service import DriverService


class DriverDeliveryPage(QWidget):
    def __init__(self):
        super().__init__()
        self.service = DriverService()
        self.shift_info = self.service.get_shift_info()
        self.delivery_history = self.service.get_delivery_history()

        self.build_ui()
        self.apply_styles()
        self.load_data()

    def build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(46, 34, 46, 34)
        self.content_layout.setSpacing(20)

        # Header
        header_row = QHBoxLayout()
        header_row.setSpacing(28)

        left_header = QVBoxLayout()
        left_header.setSpacing(8)

        title = QLabel("Tesise Teslim ve Vardiya Kapatma")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Şoförün gün sonunda topladığı atığı tesise teslim ettiği ve vardiyasını kapattığı ekran."
        )
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)

        left_header.addWidget(title)
        left_header.addWidget(subtitle)

        right_header = QVBoxLayout()
        right_header.setSpacing(14)

        self.delivery_btn = QPushButton("✓  Tesise Teslim Et")
        self.delivery_btn.setObjectName("primaryButton")
        self.delivery_btn.setFixedHeight(56)
        self.delivery_btn.clicked.connect(self.submit_delivery)

        self.close_shift_btn = QPushButton("⏹  Vardiyayı Kapat")
        self.close_shift_btn.setObjectName("warningButton")
        self.close_shift_btn.setFixedHeight(48)
        self.close_shift_btn.clicked.connect(self.close_shift)

        status_card = QFrame()
        status_card.setObjectName("statusCard")
        status_card.setFixedHeight(136)

        status_layout = QHBoxLayout(status_card)
        status_layout.setContentsMargins(28, 18, 28, 18)

        status_col = QVBoxLayout()
        status_col.setSpacing(0)

        self.shift_status_value = QLabel("Hazır")
        self.shift_status_value.setObjectName("statusValue")

        status_label = QLabel("Vardiya Durumu")
        status_label.setObjectName("statusLabel")

        status_col.addStretch()
        status_col.addWidget(self.shift_status_value)
        status_col.addWidget(status_label)
        status_col.addStretch()

        ghost_icon = QLabel("🏭")
        ghost_icon.setObjectName("statusGhostIcon")
        ghost_icon.setAlignment(Qt.AlignCenter)

        status_layout.addLayout(status_col)
        status_layout.addStretch()
        status_layout.addWidget(ghost_icon)

        right_header.addWidget(self.delivery_btn)
        right_header.addWidget(self.close_shift_btn)
        right_header.addWidget(status_card)

        header_row.addLayout(left_header, 3)
        header_row.addLayout(right_header, 1.35)

        self.content_layout.addLayout(header_row)

        # Main row
        main_row = QHBoxLayout()
        main_row.setSpacing(24)

        left_panel = self.build_delivery_form_panel()
        right_panel = self.build_delivery_history_panel()

        main_row.addWidget(left_panel, 1.1)
        main_row.addWidget(right_panel, 1.0)

        self.content_layout.addLayout(main_row)

        scroll.setWidget(content)
        root_layout.addWidget(scroll)

    def build_delivery_form_panel(self):
        panel = QFrame()
        panel.setObjectName("cardPanel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)

        title = QLabel("Teslim Formu")
        title.setObjectName("panelTitle")

        self.driver_name = self.build_info_row(layout, "Şoför", "-")
        self.vehicle_plate = self.build_info_row(layout, "Araç Plakası", "-")
        self.vehicle_capacity = self.build_info_row(layout, "Araç Kapasitesi", "-")

        kg_label = QLabel("Toplanan Toplam Atık Miktarı")
        kg_label.setObjectName("fieldLabel")

        self.total_kg_input = QDoubleSpinBox()
        self.total_kg_input.setRange(0.0, 100000.0)
        self.total_kg_input.setDecimals(1)
        self.total_kg_input.setSingleStep(50.0)
        self.total_kg_input.setSuffix(" kg")
        self.total_kg_input.setObjectName("spinInput")

        note_label = QLabel("Açıklama")
        note_label.setObjectName("fieldLabel")

        self.note_input = QTextEdit()
        self.note_input.setPlaceholderText("Teslim ile ilgili açıklama giriniz...")
        self.note_input.setFixedHeight(130)
        self.note_input.setObjectName("textArea")

        layout.insertWidget(0, title)
        layout.addSpacing(4)
        layout.addWidget(kg_label)
        layout.addWidget(self.total_kg_input)
        layout.addWidget(note_label)
        layout.addWidget(self.note_input)
        layout.addStretch()

        return panel

    def build_delivery_history_panel(self):
        panel = QFrame()
        panel.setObjectName("cardPanel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(16)

        title = QLabel("Son Teslim Kayıtları")
        title.setObjectName("panelTitle")

        subtitle = QLabel("Şoför tarafından tesise yapılan son teslim kayıtları.")
        subtitle.setObjectName("subText")

        self.history_container = QVBoxLayout()
        self.history_container.setSpacing(12)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(6)
        layout.addLayout(self.history_container)
        layout.addStretch()

        return panel

    def build_info_row(self, parent_layout, label_text, value_text):
        row = QFrame()
        row.setObjectName("infoRow")

        layout = QHBoxLayout(row)
        layout.setContentsMargins(16, 12, 16, 12)
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

    def build_history_card(self, delivery):
        card = QFrame()
        card.setObjectName("historyCard")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(6)

        top_row = QHBoxLayout()

        date_label = QLabel(delivery["date"])
        date_label.setObjectName("mainText")

        kg_label = QLabel(f'{delivery["total_kg"]:.1f} kg')
        kg_label.setObjectName("amountPill")
        kg_label.setAlignment(Qt.AlignCenter)

        top_row.addWidget(date_label)
        top_row.addStretch()
        top_row.addWidget(kg_label)

        note_label = QLabel(delivery["note"] if delivery["note"] else "Açıklama girilmedi.")
        note_label.setObjectName("subText")
        note_label.setWordWrap(True)

        layout.addLayout(top_row)
        layout.addWidget(note_label)

        return card

    def clear_history(self):
        while self.history_container.count():
            item = self.history_container.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def load_data(self):
        self.shift_info = self.service.get_shift_info()
        self.delivery_history = self.service.get_delivery_history()

        self.driver_name.setText(self.shift_info["driver_name"])
        self.shift_status_value.setText(self.shift_info["shift_status"])

        vehicle = self.shift_info["assigned_vehicle"]
        self.vehicle_plate.setText(vehicle["plate"])
        self.vehicle_capacity.setText(f'{vehicle["capacity_kg"]} kg')

        self.clear_history()
        for delivery in self.delivery_history[:5]:
            self.history_container.addWidget(self.build_history_card(delivery))
        self.history_container.addStretch()

    def submit_delivery(self):
        total_kg = self.total_kg_input.value()
        note = self.note_input.toPlainText().strip()

        if total_kg <= 0:
            QMessageBox.warning(self, "Uyarı", "Toplam atık miktarı 0'dan büyük olmalıdır.")
            return

        try:
            self.service.submit_delivery(total_kg, note)
            self.total_kg_input.setValue(0.0)
            self.note_input.clear()
            self.load_data()
            QMessageBox.information(self, "Bilgi", "Tesise teslim kaydı oluşturuldu.")
        except ApiError as exc:
            QMessageBox.warning(self, "API Hatası", str(exc))

    def close_shift(self):
        answer = QMessageBox.question(
            self,
            "Vardiya Kapat",
            "Vardiya kapatılsın mı?"
        )
        if answer == QMessageBox.Yes:
            self.service.close_shift()
            self.load_data()
            QMessageBox.information(self, "Bilgi", "Vardiya kapatıldı.")

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
            }

            #primaryButton:hover {
                background: #004A0C;
            }

            #warningButton {
                background: #FEF3C7;
                color: #92400E;
                border: none;
                border-radius: 14px;
                font-size: 14px;
                font-weight: 800;
            }

            #warningButton:hover {
                background: #fde7aa;
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

            #cardPanel {
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

            #fieldLabel {
                font-size: 13px;
                font-weight: 800;
                color: #374151;
                background: transparent;
            }

            #spinInput, #textArea {
                background: #FAFBF9;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
                padding: 10px 12px;
                font-size: 14px;
            }

            #historyCard {
                background: #FAFBF9;
                border: 1px solid #ECEEEA;
                border-radius: 14px;
            }

            #mainText {
                font-size: 14px;
                font-weight: 800;
                color: #111827;
                background: transparent;
            }

            #subText {
                font-size: 13px;
                color: #475569;
                background: transparent;
            }

            #amountPill {
                background: #DCFCE7;
                color: #166534;
                border-radius: 14px;
                padding: 6px 14px;
                font-size: 13px;
                font-weight: 800;
            }

            QLabel {
                background: transparent;
            }
        """)
