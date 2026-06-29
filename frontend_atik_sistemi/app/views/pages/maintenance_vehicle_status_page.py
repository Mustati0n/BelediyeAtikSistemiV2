from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QLineEdit,
    QComboBox,
    QScrollArea,
)

from services.maintenance_service import MaintenanceService


class MaintenanceVehicleStatusPage(QWidget):
    def __init__(self):
        super().__init__()
        self.service = MaintenanceService()
        self.vehicle_data = self.service.get_all_vehicles()
        self.filtered_data = list(self.vehicle_data)

        self.build_ui()
        self.apply_styles()
        self.populate_filters()
        self.refresh_rows()
        self.update_summary()

    def build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(46, 34, 46, 34)
        self.content_layout.setSpacing(18)

        # Header
        header_row = QHBoxLayout()
        header_row.setSpacing(28)

        left_header = QVBoxLayout()
        left_header.setSpacing(8)

        title = QLabel("Araç Listesi ve Durum")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Bakım yapılacak araçları seçin, plaka ve tip bilgilerini görüntüleyin,\n"
            "mevcut operasyonel durumlarını filtreleyerek takip edin."
        )
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)

        left_header.addWidget(title)
        left_header.addWidget(subtitle)

        right_header = QVBoxLayout()
        right_header.setSpacing(14)

        summary_card = QFrame()
        summary_card.setObjectName("statusCard")
        summary_card.setFixedHeight(136)

        summary_layout = QHBoxLayout(summary_card)
        summary_layout.setContentsMargins(28, 18, 28, 18)

        summary_text_col = QVBoxLayout()
        summary_text_col.setSpacing(0)

        self.summary_value = QLabel("0")
        self.summary_value.setObjectName("statusValue")

        summary_label = QLabel("Bakımdaki Araç")
        summary_label.setObjectName("statusLabel")

        summary_text_col.addStretch()
        summary_text_col.addWidget(self.summary_value)
        summary_text_col.addWidget(summary_label)
        summary_text_col.addStretch()

        ghost_icon = QLabel("🛠")
        ghost_icon.setObjectName("statusGhostIcon")
        ghost_icon.setAlignment(Qt.AlignCenter)

        summary_layout.addLayout(summary_text_col)
        summary_layout.addStretch()
        summary_layout.addWidget(ghost_icon)

        right_header.addWidget(summary_card)

        header_row.addLayout(left_header, 3)
        header_row.addLayout(right_header, 1.2)

        self.content_layout.addLayout(header_row)

        # Filter panel
        filter_panel = QFrame()
        filter_panel.setObjectName("filterPanel")

        filter_layout = QHBoxLayout(filter_panel)
        filter_layout.setContentsMargins(28, 26, 28, 26)
        filter_layout.setSpacing(18)

        search_col = QVBoxLayout()
        search_col.setSpacing(8)

        search_label = QLabel("ARAMA")
        search_label.setObjectName("filterLabel")

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Plaka veya araç tipi ile ara...")
        self.search_input.setObjectName("searchInput")
        self.search_input.textChanged.connect(self.apply_filters)

        search_col.addWidget(search_label)
        search_col.addWidget(self.search_input)

        type_col = QVBoxLayout()
        type_col.setSpacing(8)

        type_label = QLabel("ARAÇ TİPİ")
        type_label.setObjectName("filterLabel")

        self.type_filter = QComboBox()
        self.type_filter.setObjectName("filterCombo")
        self.type_filter.currentIndexChanged.connect(self.apply_filters)

        type_col.addWidget(type_label)
        type_col.addWidget(self.type_filter)

        status_col = QVBoxLayout()
        status_col.setSpacing(8)

        status_label = QLabel("DURUM")
        status_label.setObjectName("filterLabel")

        self.status_filter = QComboBox()
        self.status_filter.setObjectName("filterCombo")
        self.status_filter.currentIndexChanged.connect(self.apply_filters)

        status_col.addWidget(status_label)
        status_col.addWidget(self.status_filter)

        filter_layout.addLayout(search_col, 2)
        filter_layout.addLayout(type_col, 1.2)
        filter_layout.addLayout(status_col, 1.2)

        self.content_layout.addWidget(filter_panel)

        # List panel
        self.list_panel = QFrame()
        self.list_panel.setObjectName("listPanel")

        list_layout = QVBoxLayout(self.list_panel)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(0)

        header = self.build_table_header()
        list_layout.addWidget(header)

        self.rows_container = QVBoxLayout()
        self.rows_container.setContentsMargins(0, 0, 0, 0)
        self.rows_container.setSpacing(0)

        rows_host = QWidget()
        rows_host.setLayout(self.rows_container)

        list_layout.addWidget(rows_host)

        footer_row = QHBoxLayout()
        footer_row.setContentsMargins(30, 20, 30, 20)
        footer_row.setSpacing(12)

        self.count_label = QLabel("Toplam 0 araçtan 0-0 arası gösteriliyor")
        self.count_label.setObjectName("countLabel")

        footer_row.addWidget(self.count_label)
        footer_row.addStretch()
        list_layout.addLayout(footer_row)

        self.content_layout.addWidget(self.list_panel)

        scroll.setWidget(content)
        root_layout.addWidget(scroll)

    def build_table_header(self):
        header = QFrame()
        header.setObjectName("tableHeader")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(28, 18, 28, 18)
        layout.setSpacing(12)

        layout.addWidget(self.make_header_label("PLAKA"), 1.4)
        layout.addWidget(self.make_header_label("ARAÇ TİPİ"), 1.8)
        layout.addWidget(self.make_header_label("KAPASİTE"), 1.2)
        layout.addWidget(self.make_header_label("DURUM"), 1.2)
        layout.addWidget(self.make_header_label("SON BAKIM"), 1.4)

        return header

    def make_header_label(self, text, align=Qt.AlignLeft):
        label = QLabel(text)
        label.setObjectName("tableHeaderLabel")
        label.setAlignment(align | Qt.AlignVCenter)
        return label

    def populate_filters(self):
        types = sorted({vehicle["type"] for vehicle in self.vehicle_data})

        self.type_filter.clear()
        self.type_filter.addItem("Tüm Tipler")
        self.type_filter.addItems(types)

        self.status_filter.clear()
        self.status_filter.addItems(["Tüm Durumlar", "Aktif", "Pasif", "Bakımda"])

    def clear_rows(self):
        while self.rows_container.count():
            item = self.rows_container.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def refresh_rows(self):
        self.clear_rows()

        for vehicle in self.filtered_data:
            self.rows_container.addWidget(self.build_vehicle_row(vehicle))

        self.rows_container.addStretch()

        total = len(self.filtered_data)
        if total == 0:
            self.count_label.setText("Toplam 0 araçtan 0-0 arası gösteriliyor")
        else:
            self.count_label.setText(f"Toplam {total} araçtan 1-{total} arası gösteriliyor")

    def build_vehicle_row(self, vehicle):
        row = QFrame()
        row.setObjectName("vehicleRow")
        row.setFixedHeight(94)

        layout = QHBoxLayout(row)
        layout.setContentsMargins(28, 18, 28, 18)
        layout.setSpacing(12)

        plate = QLabel(vehicle["plate"])
        plate.setObjectName("mainText")

        vtype = QLabel(vehicle["type"])
        vtype.setObjectName("mainText")

        capacity = QLabel(f'{vehicle["capacity_kg"]} kg')
        capacity.setObjectName("subText")

        status = QLabel(f'●  {vehicle["status"]}')
        status.setAlignment(Qt.AlignCenter)

        if vehicle["status"] == "Aktif":
            status.setObjectName("statusActive")
        elif vehicle["status"] == "Bakımda":
            status.setObjectName("statusMaintenance")
        else:
            status.setObjectName("statusPassive")

        maintenance = QLabel(vehicle["last_maintenance"])
        maintenance.setObjectName("subText")

        layout.addWidget(plate, 1.4)
        layout.addWidget(vtype, 1.8)
        layout.addWidget(capacity, 1.2)
        layout.addWidget(status, 1.2)
        layout.addWidget(maintenance, 1.4)

        return row

    def apply_filters(self):
        search_text = self.search_input.text().strip().lower()
        selected_type = self.type_filter.currentText()
        selected_status = self.status_filter.currentText()

        self.vehicle_data = self.service.get_all_vehicles()
        self.filtered_data = []

        for vehicle in self.vehicle_data:
            matches_search = (
                search_text in vehicle["plate"].lower()
                or search_text in vehicle["type"].lower()
            )
            matches_type = selected_type == "Tüm Tipler" or vehicle["type"] == selected_type
            matches_status = selected_status == "Tüm Durumlar" or vehicle["status"] == selected_status

            if matches_search and matches_type and matches_status:
                self.filtered_data.append(vehicle)

        self.refresh_rows()
        self.update_summary()

    def update_summary(self):
        maintenance_count = len([v for v in self.vehicle_data if v["status"] == "Bakımda"])
        self.summary_value.setText(str(maintenance_count))

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

            #statusCard {
                background: #005E10;
                border-radius: 18px;
            }

            #statusValue {
                font-size: 34px;
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

            #filterPanel, #listPanel {
                background: white;
                border: 1px solid #ECEEEA;
                border-radius: 20px;
            }

            #filterLabel, #tableHeaderLabel {
                font-size: 12px;
                font-weight: 900;
                letter-spacing: 1px;
                color: #374151;
                background: transparent;
            }

            #searchInput, #filterCombo {
                background: #FAFBF9;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
                padding: 12px 14px;
                font-size: 14px;
                min-height: 24px;
            }

            #tableHeader {
                background: #FAFBF9;
                border-top-left-radius: 20px;
                border-top-right-radius: 20px;
                border-bottom: 1px solid #ECEEEA;
            }

            #vehicleRow {
                background: white;
                border: none;
                border-bottom: 1px solid #ECEEEA;
            }

            #mainText {
                font-size: 15px;
                font-weight: 800;
                color: #111827;
                background: transparent;
            }

            #subText {
                font-size: 13px;
                color: #475569;
                background: transparent;
            }

            #statusActive {
                background: #DCFCE7;
                color: #166534;
                border-radius: 14px;
                padding: 6px 14px;
                font-size: 13px;
                font-weight: 800;
            }

            #statusMaintenance {
                background: #FEF3C7;
                color: #92400E;
                border-radius: 14px;
                padding: 6px 14px;
                font-size: 13px;
                font-weight: 800;
            }

            #statusPassive {
                background: #E5E7EB;
                color: #374151;
                border-radius: 14px;
                padding: 6px 14px;
                font-size: 13px;
                font-weight: 800;
            }

            #countLabel {
                font-size: 13px;
                color: #374151;
                background: transparent;
            }
        """)