from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QLineEdit,
    QPushButton,
    QComboBox,
    QDialog,
    QFormLayout,
    QMessageBox,
    QDialogButtonBox,
    QScrollArea,
)

from services.api_client import ApiError
from services.vehicle_service import VehicleService


class VehicleDialog(QDialog):
    def __init__(self, parent=None, vehicle=None):
        super().__init__(parent)
        self.vehicle = vehicle
        self.setWindowTitle("Araç Ekle / Düzenle")
        self.setModal(True)
        self.resize(420, 280)
        self.build_ui()

        if self.vehicle:
            self.load_vehicle_data()

    def build_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()
        form.setSpacing(12)

        self.plate_input = QLineEdit()
        self.plate_input.setPlaceholderText("34 ABC 123")

        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Çöp Kamyonu",
            "Geri Dönüşüm Kamyonu",
            "Konteyner Taşıyıcı",
        ])

        self.capacity_input = QLineEdit()
        self.capacity_input.setPlaceholderText("12000")

        self.status_combo = QComboBox()
        self.status_combo.addItems(["Aktif", "Bakımda", "Pasif"])

        self.region_combo = QComboBox()
        self.region_combo.addItems([
            "Merkez Bölge",
            "Kuzey Bölge",
            "Güney Bölge",
            "Doğu Bölge",
            "Batı Bölge",
        ])

        self.maintenance_input = QLineEdit()
        self.maintenance_input.setPlaceholderText("12.05.2026")

        form.addRow("Plaka:", self.plate_input)
        form.addRow("Araç Tipi:", self.type_combo)
        form.addRow("Kapasite (kg):", self.capacity_input)
        form.addRow("Durum:", self.status_combo)
        form.addRow("Bölge:", self.region_combo)
        form.addRow("Son Bakım:", self.maintenance_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)

        layout.addLayout(form)
        layout.addSpacing(12)
        layout.addWidget(buttons)

    def load_vehicle_data(self):
        self.plate_input.setText(self.vehicle["plate"])
        self.type_combo.setCurrentText(self.vehicle["type"])
        self.capacity_input.setText(str(self.vehicle["capacity_kg"]))
        self.status_combo.setCurrentText(self.vehicle["status"])
        self.region_combo.setCurrentText(self.vehicle["region"])
        self.maintenance_input.setText(self.vehicle["last_maintenance"])

    def validate_and_accept(self):
        if not self.plate_input.text().strip():
            QMessageBox.warning(self, "Uyarı", "Plaka alanı boş bırakılamaz.")
            return

        if not self.capacity_input.text().strip().isdigit():
            QMessageBox.warning(self, "Uyarı", "Kapasite sayısal olmalıdır.")
            return

        self.accept()

    def get_data(self):
        return {
            "plate": self.plate_input.text().strip(),
            "type": self.type_combo.currentText(),
            "capacity_kg": int(self.capacity_input.text().strip()),
            "status": self.status_combo.currentText(),
            "region": self.region_combo.currentText(),
            "last_maintenance": self.maintenance_input.text().strip() or "-",
        }


class VehiclesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.service = VehicleService()
        self.vehicle_data = self.service.get_all()
        self.filtered_data = list(self.vehicle_data)

        self.build_ui()
        self.apply_styles()
        self.populate_filters()
        self.refresh_rows()

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

        header_row = QHBoxLayout()
        header_row.setSpacing(28)

        left_header = QVBoxLayout()
        left_header.setSpacing(8)

        title = QLabel("Araç ve Filo Yönetimi")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Belediye filosundaki araçları yönetin, plaka ve kapasite bilgilerini takip edin,\naktif / pasif / bakımda durumlarını kontrol edin."
        )
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)

        left_header.addWidget(title)
        left_header.addWidget(subtitle)

        right_header = QVBoxLayout()
        right_header.setSpacing(14)

        add_btn = QPushButton("＋  Yeni Araç Ekle")
        add_btn.setObjectName("addButton")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setFixedHeight(56)
        add_btn.clicked.connect(self.add_vehicle)

        active_card = QFrame()
        active_card.setObjectName("activeFleetCard")
        active_card.setFixedHeight(136)

        active_card_layout = QHBoxLayout(active_card)
        active_card_layout.setContentsMargins(28, 18, 28, 18)

        active_text_col = QVBoxLayout()
        active_text_col.setSpacing(0)

        active_count = QLabel("118")
        active_count.setObjectName("activeCount")

        active_label = QLabel("Operasyonel Araç")
        active_label.setObjectName("activeLabel")

        active_text_col.addStretch()
        active_text_col.addWidget(active_count)
        active_text_col.addWidget(active_label)
        active_text_col.addStretch()

        ghost_icon = QLabel("🚚")
        ghost_icon.setObjectName("activeGhostIcon")
        ghost_icon.setAlignment(Qt.AlignCenter)

        active_card_layout.addLayout(active_text_col)
        active_card_layout.addStretch()
        active_card_layout.addWidget(ghost_icon)

        right_header.addWidget(add_btn)
        right_header.addWidget(active_card)

        header_row.addLayout(left_header, 3)
        header_row.addLayout(right_header, 1.35)

        self.content_layout.addLayout(header_row)

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
        self.search_input.setPlaceholderText("Plaka veya tip ile ara...")
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

        self.content_layout.addWidget(self.list_panel)
        list_layout.addLayout(footer_row)

        scroll.setWidget(content)
        root_layout.addWidget(scroll)

    def build_table_header(self):
        header = QFrame()
        header.setObjectName("tableHeader")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(28, 18, 28, 18)
        layout.setSpacing(12)

        layout.addWidget(self.make_header_label("PLAKA / ARAÇ"), 2.6)
        layout.addWidget(self.make_header_label("KAPASİTE"), 1.2)
        layout.addWidget(self.make_header_label("BÖLGE"), 1.4)
        layout.addWidget(self.make_header_label("DURUM"), 1.2)
        layout.addWidget(self.make_header_label("SON BAKIM"), 1.4)
        layout.addWidget(self.make_header_label("İŞLEMLER", Qt.AlignRight), 1.0)

        return header

    def make_header_label(self, text, align=Qt.AlignLeft):
        label = QLabel(text)
        label.setObjectName("tableHeaderLabel")
        label.setAlignment(align | Qt.AlignVCenter)
        return label

    def populate_filters(self):
        types = sorted({v["type"] for v in self.vehicle_data})

        self.type_filter.clear()
        self.type_filter.addItem("Tüm Tipler")
        self.type_filter.addItems(types)

        self.status_filter.clear()
        self.status_filter.addItems(["Tüm Durumlar", "Aktif", "Bakımda", "Pasif"])

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

        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)

        plate = QLabel(vehicle["plate"])
        plate.setObjectName("mainText")

        vtype = QLabel(vehicle["type"])
        vtype.setObjectName("subText")

        info_layout.addWidget(plate)
        info_layout.addWidget(vtype)

        capacity = QLabel(f'{vehicle["capacity_kg"]} kg')
        capacity.setObjectName("mainText")

        region = QLabel(vehicle["region"])
        region.setObjectName("mainText")

        status = QLabel(f'●  {vehicle["status"]}')
        status.setAlignment(Qt.AlignCenter)
        if vehicle["status"] == "Aktif":
            status.setObjectName("statusActive")
        elif vehicle["status"] == "Bakımda":
            status.setObjectName("statusMaintenance")
        else:
            status.setObjectName("statusPassive")

        maintenance = QLabel(vehicle["last_maintenance"])
        maintenance.setObjectName("mainText")

        actions = QWidget()
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(10)

        edit_btn = QPushButton("✎")
        edit_btn.setObjectName("iconActionButton")
        edit_btn.setFixedSize(34, 34)
        edit_btn.clicked.connect(lambda _, v=vehicle: self.edit_vehicle(v))

        status_btn = QPushButton("↺")
        status_btn.setObjectName("iconActionButton")
        status_btn.setFixedSize(34, 34)
        status_btn.clicked.connect(lambda _, v=vehicle: self.change_status(v))

        actions_layout.addStretch()
        actions_layout.addWidget(edit_btn)
        actions_layout.addWidget(status_btn)

        layout.addWidget(info_widget, 2.6)
        layout.addWidget(capacity, 1.2)
        layout.addWidget(region, 1.4)
        layout.addWidget(status, 1.2)
        layout.addWidget(maintenance, 1.4)
        layout.addWidget(actions, 1.0)

        return row

    def apply_filters(self):
        search_text = self.search_input.text().strip().lower()
        selected_type = self.type_filter.currentText()
        selected_status = self.status_filter.currentText()

        self.vehicle_data = self.service.get_all()
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

    def add_vehicle(self):
        dialog = VehicleDialog(self)
        if dialog.exec():
            try:
                self.service.add_vehicle(dialog.get_data())
                self.vehicle_data = self.service.get_all()
                self.populate_filters()
                self.apply_filters()
            except ApiError as exc:
                QMessageBox.warning(self, "API Hatası", str(exc))

    def edit_vehicle(self, vehicle):
        dialog = VehicleDialog(self, vehicle)
        if dialog.exec():
            try:
                self.service.update_vehicle(vehicle["id"], dialog.get_data())
                self.vehicle_data = self.service.get_all()
                self.populate_filters()
                self.apply_filters()
            except ApiError as exc:
                QMessageBox.warning(self, "API Hatası", str(exc))

    def change_status(self, vehicle):
        try:
            self.service.cycle_status(vehicle["id"])
            self.vehicle_data = self.service.get_all()
            self.apply_filters()
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

            #addButton {
                background: #005E10;
                color: white;
                border: none;
                border-radius: 16px;
                font-size: 16px;
                font-weight: 800;
                padding: 0 24px;
            }

            #addButton:hover {
                background: #004A0C;
            }

            #activeFleetCard {
                background: #005E10;
                border-radius: 18px;
            }

            #activeCount {
                font-size: 34px;
                font-weight: 900;
                color: white;
                background: transparent;
            }

            #activeLabel {
                font-size: 13px;
                font-weight: 700;
                color: rgba(255, 255, 255, 0.82);
                background: transparent;
            }

            #activeGhostIcon {
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
                background: #A6F08C;
                color: #104B14;
                border-radius: 14px;
                padding: 6px 14px;
                font-size: 13px;
                font-weight: 800;
            }

            #statusMaintenance {
                background: #FDE68A;
                color: #854D0E;
                border-radius: 14px;
                padding: 6px 14px;
                font-size: 13px;
                font-weight: 800;
            }

            #statusPassive {
                background: #E5E5E5;
                color: #374151;
                border-radius: 14px;
                padding: 6px 14px;
                font-size: 13px;
                font-weight: 800;
            }

            #iconActionButton {
                border: none;
                background: transparent;
                font-size: 18px;
                font-weight: 700;
            }

            #iconActionButton:hover {
                background: #F3F4F6;
                border-radius: 10px;
            }

            #countLabel {
                font-size: 13px;
                color: #374151;
                background: transparent;
            }

            QDialog {
                background: white;
            }
        """)
