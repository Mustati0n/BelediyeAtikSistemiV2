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
    QProgressBar,
)

from services.container_service import ContainerService


class ContainerDialog(QDialog):
    def __init__(self, parent=None, container=None):
        super().__init__(parent)
        self.container = container
        self.setWindowTitle("Konteyner Ekle / Düzenle")
        self.setModal(True)
        self.resize(420, 320)
        self.build_ui()

        if self.container:
            self.load_container_data()

    def build_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()
        form.setSpacing(12)

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("KNT-1005")

        self.region_combo = QComboBox()
        self.region_combo.addItems([
            "Merkez Bölge",
            "Kuzey Bölge",
            "Güney Bölge",
            "Doğu Bölge",
            "Batı Bölge",
        ])

        self.fill_input = QLineEdit()
        self.fill_input.setPlaceholderText("0-100")

        self.status_combo = QComboBox()
        self.status_combo.addItems([
            "Normal",
            "İzleniyor",
            "Kritik",
            "Göreve Atandı",
            "Boşaltıldı",
        ])

        self.lat_input = QLineEdit()
        self.lat_input.setPlaceholderText("40.9912")

        self.lng_input = QLineEdit()
        self.lng_input.setPlaceholderText("29.0277")

        form.addRow("Konteyner Kodu:", self.code_input)
        form.addRow("Bölge:", self.region_combo)
        form.addRow("Doluluk (%):", self.fill_input)
        form.addRow("Durum:", self.status_combo)
        form.addRow("Enlem:", self.lat_input)
        form.addRow("Boylam:", self.lng_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)

        layout.addLayout(form)
        layout.addSpacing(12)
        layout.addWidget(buttons)

    def load_container_data(self):
        self.code_input.setText(self.container["code"])
        self.region_combo.setCurrentText(self.container["region"])
        self.fill_input.setText(str(self.container["fill_rate"]))
        self.status_combo.setCurrentText(self.container["status"])
        self.lat_input.setText(self.container["lat"])
        self.lng_input.setText(self.container["lng"])

    def validate_and_accept(self):
        if not self.code_input.text().strip():
            QMessageBox.warning(self, "Uyarı", "Konteyner kodu boş bırakılamaz.")
            return

        if not self.fill_input.text().strip().isdigit():
            QMessageBox.warning(self, "Uyarı", "Doluluk oranı sayısal olmalıdır.")
            return

        fill_rate = int(self.fill_input.text().strip())
        if fill_rate < 0 or fill_rate > 100:
            QMessageBox.warning(self, "Uyarı", "Doluluk oranı 0 ile 100 arasında olmalıdır.")
            return

        if not self.lat_input.text().strip() or not self.lng_input.text().strip():
            QMessageBox.warning(self, "Uyarı", "Koordinat alanları boş bırakılamaz.")
            return

        self.accept()

    def get_data(self):
        return {
            "code": self.code_input.text().strip(),
            "region": self.region_combo.currentText(),
            "fill_rate": int(self.fill_input.text().strip()),
            "status": self.status_combo.currentText(),
            "lat": self.lat_input.text().strip(),
            "lng": self.lng_input.text().strip(),
        }


class ContainersPage(QWidget):
    def __init__(self):
        super().__init__()
        self.service = ContainerService()
        self.container_data = self.service.get_all()
        self.filtered_data = list(self.container_data)

        self.build_ui()
        self.apply_styles()
        self.populate_filters()
        self.refresh_rows()
        self.update_summary_cards()

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

        title = QLabel("Bölge ve Konteyner Yönetimi")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Şehirdeki konteyner noktalarını yönetin, bölge atamalarını yapın ve\n"
            "doluluk ile operasyon durumlarını izleyin."
        )
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)

        left_header.addWidget(title)
        left_header.addWidget(subtitle)

        right_header = QVBoxLayout()
        right_header.setSpacing(14)

        add_btn = QPushButton("＋  Yeni Konteyner Ekle")
        add_btn.setObjectName("addButton")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setFixedHeight(56)
        add_btn.clicked.connect(self.add_container)

        critical_card = QFrame()
        critical_card.setObjectName("criticalCard")
        critical_card.setFixedHeight(136)

        critical_layout = QHBoxLayout(critical_card)
        critical_layout.setContentsMargins(28, 18, 28, 18)

        critical_text_col = QVBoxLayout()
        critical_text_col.setSpacing(0)

        self.critical_count = QLabel("0")
        self.critical_count.setObjectName("criticalCount")

        critical_label = QLabel("Kritik Konteyner")
        critical_label.setObjectName("criticalLabel")

        critical_text_col.addStretch()
        critical_text_col.addWidget(self.critical_count)
        critical_text_col.addWidget(critical_label)
        critical_text_col.addStretch()

        ghost_icon = QLabel("🗑")
        ghost_icon.setObjectName("criticalGhostIcon")
        ghost_icon.setAlignment(Qt.AlignCenter)

        critical_layout.addLayout(critical_text_col)
        critical_layout.addStretch()
        critical_layout.addWidget(ghost_icon)

        right_header.addWidget(add_btn)
        right_header.addWidget(critical_card)

        header_row.addLayout(left_header, 3)
        header_row.addLayout(right_header, 1.35)

        self.content_layout.addLayout(header_row)

        # Üst filtre paneli
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
        self.search_input.setPlaceholderText("Konteyner kodu veya bölge ile ara...")
        self.search_input.setObjectName("searchInput")
        self.search_input.textChanged.connect(self.apply_filters)

        search_col.addWidget(search_label)
        search_col.addWidget(self.search_input)

        region_col = QVBoxLayout()
        region_col.setSpacing(8)

        region_label = QLabel("BÖLGE")
        region_label.setObjectName("filterLabel")

        self.region_filter = QComboBox()
        self.region_filter.setObjectName("filterCombo")
        self.region_filter.currentIndexChanged.connect(self.apply_filters)

        region_col.addWidget(region_label)
        region_col.addWidget(self.region_filter)

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
        filter_layout.addLayout(region_col, 1.2)
        filter_layout.addLayout(status_col, 1.2)

        self.content_layout.addWidget(filter_panel)

        # Orta iki sütun: liste + harita alanı
        middle_row = QHBoxLayout()
        middle_row.setSpacing(24)

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

        self.count_label = QLabel("Toplam 0 konteynerden 0-0 arası gösteriliyor")
        self.count_label.setObjectName("countLabel")

        footer_row.addWidget(self.count_label)
        footer_row.addStretch()
        list_layout.addLayout(footer_row)

        # Harita placeholder paneli
        map_panel = QFrame()
        map_panel.setObjectName("mapPanel")

        map_layout = QVBoxLayout(map_panel)
        map_layout.setContentsMargins(28, 24, 28, 24)
        map_layout.setSpacing(14)

        map_title = QLabel("Harita Alanı")
        map_title.setObjectName("mapTitle")

        map_subtitle = QLabel(
            "Bu bölüm, kaynak kapsamına uygun şekilde konteyner pinleri ve bölgesel dağılımın "
            "gösterileceği harita alanı için frontend placeholder olarak hazırlanmıştır."
        )
        map_subtitle.setObjectName("mapSubtitle")
        map_subtitle.setWordWrap(True)

        map_placeholder = QFrame()
        map_placeholder.setObjectName("mapPlaceholder")

        map_placeholder_layout = QVBoxLayout(map_placeholder)
        map_placeholder_layout.setContentsMargins(24, 24, 24, 24)

        map_big_icon = QLabel("🗺")
        map_big_icon.setObjectName("mapBigIcon")
        map_big_icon.setAlignment(Qt.AlignCenter)

        map_text = QLabel("Konteyner pinleri burada gösterilecek")
        map_text.setObjectName("mapText")
        map_text.setAlignment(Qt.AlignCenter)

        map_placeholder_layout.addStretch()
        map_placeholder_layout.addWidget(map_big_icon)
        map_placeholder_layout.addWidget(map_text)
        map_placeholder_layout.addStretch()

        self.summary_panel = QFrame()
        self.summary_panel.setObjectName("summaryPanel")

        summary_layout = QVBoxLayout(self.summary_panel)
        summary_layout.setContentsMargins(20, 18, 20, 18)
        summary_layout.setSpacing(12)

        summary_title = QLabel("Durum Özeti")
        summary_title.setObjectName("summaryTitle")

        self.normal_bar = self.build_summary_progress("Normal")
        self.monitor_bar = self.build_summary_progress("İzleniyor")
        self.critical_bar = self.build_summary_progress("Kritik")

        summary_layout.addWidget(summary_title)
        summary_layout.addLayout(self.normal_bar["layout"])
        summary_layout.addLayout(self.monitor_bar["layout"])
        summary_layout.addLayout(self.critical_bar["layout"])

        map_layout.addWidget(map_title)
        map_layout.addWidget(map_subtitle)
        map_layout.addWidget(map_placeholder, 1)
        map_layout.addWidget(self.summary_panel)

        middle_row.addWidget(self.list_panel, 1.6)
        middle_row.addWidget(map_panel, 1.0)

        self.content_layout.addLayout(middle_row)

        scroll.setWidget(content)
        root_layout.addWidget(scroll)

    def build_table_header(self):
        header = QFrame()
        header.setObjectName("tableHeader")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(28, 18, 28, 18)
        layout.setSpacing(12)

        layout.addWidget(self.make_header_label("KONTEYNER"), 1.8)
        layout.addWidget(self.make_header_label("BÖLGE"), 1.4)
        layout.addWidget(self.make_header_label("DOLULUK"), 1.4)
        layout.addWidget(self.make_header_label("DURUM"), 1.3)
        layout.addWidget(self.make_header_label("KONUM"), 1.6)
        layout.addWidget(self.make_header_label("İŞLEMLER", Qt.AlignRight), 1.2)

        return header

    def make_header_label(self, text, align=Qt.AlignLeft):
        label = QLabel(text)
        label.setObjectName("tableHeaderLabel")
        label.setAlignment(align | Qt.AlignVCenter)
        return label

    def build_summary_progress(self, title):
        wrapper = QVBoxLayout()
        wrapper.setSpacing(6)

        row = QHBoxLayout()
        row.setSpacing(8)

        title_label = QLabel(title)
        title_label.setObjectName("summaryRowLabel")

        count_label = QLabel("0")
        count_label.setObjectName("summaryRowCount")

        row.addWidget(title_label)
        row.addStretch()
        row.addWidget(count_label)

        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(0)
        bar.setTextVisible(False)
        bar.setObjectName("greenProgress")

        wrapper.addLayout(row)
        wrapper.addWidget(bar)

        return {
            "layout": wrapper,
            "count": count_label,
            "bar": bar,
        }

    def populate_filters(self):
        regions = sorted({c["region"] for c in self.container_data})

        self.region_filter.clear()
        self.region_filter.addItem("Tüm Bölgeler")
        self.region_filter.addItems(regions)

        self.status_filter.clear()
        self.status_filter.addItems([
            "Tüm Durumlar",
            "Normal",
            "İzleniyor",
            "Kritik",
            "Göreve Atandı",
            "Boşaltıldı",
        ])

    def clear_rows(self):
        while self.rows_container.count():
            item = self.rows_container.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def refresh_rows(self):
        self.clear_rows()

        for container in self.filtered_data:
            self.rows_container.addWidget(self.build_container_row(container))

        self.rows_container.addStretch()

        total = len(self.filtered_data)
        if total == 0:
            self.count_label.setText("Toplam 0 konteynerden 0-0 arası gösteriliyor")
        else:
            self.count_label.setText(f"Toplam {total} konteynerden 1-{total} arası gösteriliyor")

    def build_container_row(self, container):
        row = QFrame()
        row.setObjectName("containerRow")
        row.setFixedHeight(104)

        layout = QHBoxLayout(row)
        layout.setContentsMargins(28, 18, 28, 18)
        layout.setSpacing(12)

        code_col = QVBoxLayout()
        code_col.setSpacing(2)

        code_label = QLabel(container["code"])
        code_label.setObjectName("mainText")

        code_sub = QLabel("Sanal Konteyner Noktası")
        code_sub.setObjectName("subText")

        code_col.addWidget(code_label)
        code_col.addWidget(code_sub)

        region_label = QLabel(container["region"])
        region_label.setObjectName("mainText")

        fill_widget = QWidget()
        fill_layout = QVBoxLayout(fill_widget)
        fill_layout.setContentsMargins(0, 0, 0, 0)
        fill_layout.setSpacing(6)

        fill_label = QLabel(f'%{container["fill_rate"]}')
        fill_label.setObjectName("mainText")

        fill_bar = QProgressBar()
        fill_bar.setRange(0, 100)
        fill_bar.setValue(container["fill_rate"])
        fill_bar.setTextVisible(False)
        fill_bar.setObjectName("greenProgress")

        fill_layout.addWidget(fill_label)
        fill_layout.addWidget(fill_bar)

        status_label = QLabel(f'●  {container["status"]}')
        status_label.setAlignment(Qt.AlignCenter)

        if container["status"] == "Normal":
            status_label.setObjectName("statusNormal")
        elif container["status"] == "İzleniyor":
            status_label.setObjectName("statusMonitoring")
        elif container["status"] == "Kritik":
            status_label.setObjectName("statusCritical")
        elif container["status"] == "Göreve Atandı":
            status_label.setObjectName("statusAssigned")
        else:
            status_label.setObjectName("statusEmptied")

        location_label = QLabel(f'{container["lat"]}, {container["lng"]}')
        location_label.setObjectName("subText")

        actions = QWidget()
        actions_layout = QHBoxLayout(actions)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(10)

        edit_btn = QPushButton("✎")
        edit_btn.setObjectName("iconActionButton")
        edit_btn.setFixedSize(34, 34)
        edit_btn.clicked.connect(lambda _, c=container: self.edit_container(c))

        status_btn = QPushButton("↺")
        status_btn.setObjectName("iconActionButton")
        status_btn.setFixedSize(34, 34)
        status_btn.clicked.connect(lambda _, c=container: self.change_status(c))

        delete_btn = QPushButton("🗑")
        delete_btn.setObjectName("iconDeleteButton")
        delete_btn.setFixedSize(34, 34)
        delete_btn.clicked.connect(lambda _, c=container: self.delete_container(c))

        actions_layout.addStretch()
        actions_layout.addWidget(edit_btn)
        actions_layout.addWidget(status_btn)
        actions_layout.addWidget(delete_btn)

        layout.addLayout(code_col, 1.8)
        layout.addWidget(region_label, 1.4)
        layout.addWidget(fill_widget, 1.4)
        layout.addWidget(status_label, 1.3)
        layout.addWidget(location_label, 1.6)
        layout.addWidget(actions, 1.2)

        return row

    def apply_filters(self):
        search_text = self.search_input.text().strip().lower()
        selected_region = self.region_filter.currentText()
        selected_status = self.status_filter.currentText()

        self.container_data = self.service.get_all()
        self.filtered_data = []

        for container in self.container_data:
            matches_search = (
                search_text in container["code"].lower()
                or search_text in container["region"].lower()
            )
            matches_region = selected_region == "Tüm Bölgeler" or container["region"] == selected_region
            matches_status = selected_status == "Tüm Durumlar" or container["status"] == selected_status

            if matches_search and matches_region and matches_status:
                self.filtered_data.append(container)

        self.refresh_rows()
        self.update_summary_cards()

    def update_summary_cards(self):
        data = self.service.get_all()
        total = max(len(data), 1)

        normal_count = sum(1 for c in data if c["status"] == "Normal")
        monitor_count = sum(1 for c in data if c["status"] == "İzleniyor")
        critical_count = sum(1 for c in data if c["status"] == "Kritik")

        self.normal_bar["count"].setText(str(normal_count))
        self.monitor_bar["count"].setText(str(monitor_count))
        self.critical_bar["count"].setText(str(critical_count))

        self.normal_bar["bar"].setValue(int(normal_count / total * 100))
        self.monitor_bar["bar"].setValue(int(monitor_count / total * 100))
        self.critical_bar["bar"].setValue(int(critical_count / total * 100))

        self.critical_count.setText(str(critical_count))

    def add_container(self):
        dialog = ContainerDialog(self)
        if dialog.exec():
            self.service.add_container(dialog.get_data())
            self.container_data = self.service.get_all()
            self.populate_filters()
            self.apply_filters()

    def edit_container(self, container):
        dialog = ContainerDialog(self, container)
        if dialog.exec():
            self.service.update_container(container["id"], dialog.get_data())
            self.container_data = self.service.get_all()
            self.populate_filters()
            self.apply_filters()

    def change_status(self, container):
        self.service.cycle_status(container["id"])
        self.container_data = self.service.get_all()
        self.apply_filters()

    def delete_container(self, container):
        answer = QMessageBox.question(
            self,
            "Konteyner Sil",
            f'{container["code"]} kodlu konteyner silinsin mi?'
        )
        if answer == QMessageBox.Yes:
            self.service.delete_container(container["id"])
            self.container_data = self.service.get_all()
            self.populate_filters()
            self.apply_filters()

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

            #criticalCard {
                background: #005E10;
                border-radius: 18px;
            }

            #criticalCount {
                font-size: 34px;
                font-weight: 900;
                color: white;
                background: transparent;
            }

            #criticalLabel {
                font-size: 13px;
                font-weight: 700;
                color: rgba(255, 255, 255, 0.82);
                background: transparent;
            }

            #criticalGhostIcon {
                font-size: 70px;
                color: rgba(255, 255, 255, 0.10);
                background: transparent;
            }

            #filterPanel, #listPanel, #mapPanel, #summaryPanel {
                background: white;
                border: 1px solid #ECEEEA;
                border-radius: 20px;
            }

            #filterLabel, #tableHeaderLabel, #summaryTitle {
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

            #containerRow {
                background: white;
                border: none;
                border-bottom: 1px solid #ECEEEA;
            }

            #mapTitle {
                font-size: 20px;
                font-weight: 800;
                color: #111827;
                background: transparent;
            }

            #mapSubtitle, #mapText {
                font-size: 13px;
                color: #475569;
                background: transparent;
            }

            #mapPlaceholder {
                background: #FAFBF9;
                border: 1px dashed #D6DBD3;
                border-radius: 18px;
                min-height: 360px;
            }

            #mapBigIcon {
                font-size: 72px;
                color: rgba(11, 91, 25, 0.18);
                background: transparent;
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

            #statusNormal {
                background: #DCFCE7;
                color: #166534;
                border-radius: 14px;
                padding: 6px 14px;
                font-size: 13px;
                font-weight: 800;
            }

            #statusMonitoring {
                background: #E0F2FE;
                color: #075985;
                border-radius: 14px;
                padding: 6px 14px;
                font-size: 13px;
                font-weight: 800;
            }

            #statusCritical {
                background: #FEE2E2;
                color: #B91C1C;
                border-radius: 14px;
                padding: 6px 14px;
                font-size: 13px;
                font-weight: 800;
            }

            #statusAssigned {
                background: #FEF3C7;
                color: #92400E;
                border-radius: 14px;
                padding: 6px 14px;
                font-size: 13px;
                font-weight: 800;
            }

            #statusEmptied {
                background: #E5E7EB;
                color: #374151;
                border-radius: 14px;
                padding: 6px 14px;
                font-size: 13px;
                font-weight: 800;
            }

            #iconActionButton, #iconDeleteButton {
                border: none;
                background: transparent;
                font-size: 18px;
                font-weight: 700;
            }

            #iconActionButton:hover, #iconDeleteButton:hover {
                background: #F3F4F6;
                border-radius: 10px;
            }

            #iconDeleteButton {
                color: #B91C1C;
            }

            #countLabel, #summaryRowLabel, #summaryRowCount {
                font-size: 13px;
                color: #374151;
                background: transparent;
            }

            QProgressBar#greenProgress {
                border: none;
                background: #E7E7E7;
                border-radius: 6px;
                min-height: 10px;
                max-height: 10px;
            }

            QProgressBar#greenProgress::chunk {
                background: #0B5B19;
                border-radius: 6px;
            }

            QDialog {
                background: white;
            }
        """)