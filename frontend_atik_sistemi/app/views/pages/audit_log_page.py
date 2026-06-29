from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from services.audit_log_service import AuditLogService


class AuditLogPage(QWidget):
    def __init__(self):
        super().__init__()
        self.service = AuditLogService()
        self.log_data = self.service.get_all()
        self.filtered_data = list(self.log_data)

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

        header_row = QHBoxLayout()
        header_row.setSpacing(28)

        left_header = QVBoxLayout()
        left_header.setSpacing(8)

        title = QLabel("Audit Log / Islem Loglari")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Sistemde gerceklesen kritik islemleri izleyin, kullanici bazli hareketleri inceleyin\n"
            "ve denetim izi kayitlarini filtreleyin."
        )
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)

        left_header.addWidget(title)
        left_header.addWidget(subtitle)

        right_header = QVBoxLayout()
        right_header.setSpacing(14)

        self.export_btn = QPushButton("Disa Aktar")
        self.export_btn.setObjectName("addButton")
        self.export_btn.setCursor(Qt.PointingHandCursor)
        self.export_btn.setFixedHeight(56)
        self.export_btn.clicked.connect(self.export_logs)

        summary_card = QFrame()
        summary_card.setObjectName("summaryCard")
        summary_card.setFixedHeight(136)

        summary_layout = QHBoxLayout(summary_card)
        summary_layout.setContentsMargins(28, 18, 28, 18)

        summary_text_col = QVBoxLayout()
        summary_text_col.setSpacing(0)

        self.summary_value = QLabel("0")
        self.summary_value.setObjectName("summaryValue")

        summary_label = QLabel("Kritik Islem Kaydi")
        summary_label.setObjectName("summaryLabel")

        summary_text_col.addStretch()
        summary_text_col.addWidget(self.summary_value)
        summary_text_col.addWidget(summary_label)
        summary_text_col.addStretch()

        ghost_icon = QLabel("LOG")
        ghost_icon.setObjectName("summaryGhostIcon")
        ghost_icon.setAlignment(Qt.AlignCenter)

        summary_layout.addLayout(summary_text_col)
        summary_layout.addStretch()
        summary_layout.addWidget(ghost_icon)

        right_header.addWidget(self.export_btn)
        right_header.addWidget(summary_card)

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
        self.search_input.setPlaceholderText("Kullanici, aciklama veya islem tipi ile ara...")
        self.search_input.setObjectName("searchInput")
        self.search_input.textChanged.connect(self.apply_filters)

        search_col.addWidget(search_label)
        search_col.addWidget(self.search_input)

        user_col = QVBoxLayout()
        user_col.setSpacing(8)
        user_label = QLabel("KULLANICI")
        user_label.setObjectName("filterLabel")

        self.user_filter = QComboBox()
        self.user_filter.setObjectName("filterCombo")
        self.user_filter.currentIndexChanged.connect(self.apply_filters)

        user_col.addWidget(user_label)
        user_col.addWidget(self.user_filter)

        type_col = QVBoxLayout()
        type_col.setSpacing(8)
        type_label = QLabel("ISLEM TIPI")
        type_label.setObjectName("filterLabel")

        self.type_filter = QComboBox()
        self.type_filter.setObjectName("filterCombo")
        self.type_filter.currentIndexChanged.connect(self.apply_filters)

        type_col.addWidget(type_label)
        type_col.addWidget(self.type_filter)

        filter_layout.addLayout(search_col, 2)
        filter_layout.addLayout(user_col, 1.2)
        filter_layout.addLayout(type_col, 1.2)
        self.content_layout.addWidget(filter_panel)

        self.list_panel = QFrame()
        self.list_panel.setObjectName("listPanel")

        list_layout = QVBoxLayout(self.list_panel)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(0)
        list_layout.addWidget(self.build_table_header())

        self.rows_container = QVBoxLayout()
        self.rows_container.setContentsMargins(0, 0, 0, 0)
        self.rows_container.setSpacing(0)

        rows_host = QWidget()
        rows_host.setLayout(self.rows_container)
        list_layout.addWidget(rows_host)

        footer_row = QHBoxLayout()
        footer_row.setContentsMargins(30, 20, 30, 20)
        self.count_label = QLabel("Toplam 0 islem kaydindan 0-0 arasi gosteriliyor")
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

        for text, stretch in [
            ("ISLEM TARIHI", 1.5),
            ("KULLANICI", 1.4),
            ("ISLEM TIPI", 1.7),
            ("ACIKLAMA", 3.0),
            ("VARLIK", 1.3),
        ]:
            label = QLabel(text)
            label.setObjectName("tableHeaderLabel")
            layout.addWidget(label, stretch)

        return header

    def populate_filters(self):
        users = sorted({log["user"] for log in self.log_data})
        types = sorted({log["action_type"] for log in self.log_data})

        self.user_filter.clear()
        self.user_filter.addItem("Tum Kullanicilar")
        self.user_filter.addItems(users)

        self.type_filter.clear()
        self.type_filter.addItem("Tum Islem Tipleri")
        self.type_filter.addItems(types)

    def clear_rows(self):
        while self.rows_container.count():
            item = self.rows_container.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def refresh_rows(self):
        self.clear_rows()

        for log in self.filtered_data:
            self.rows_container.addWidget(self.build_log_row(log))

        self.rows_container.addStretch()
        total = len(self.filtered_data)
        if total == 0:
            self.count_label.setText("Toplam 0 islem kaydindan 0-0 arasi gosteriliyor")
        else:
            self.count_label.setText(f"Toplam {total} islem kaydindan 1-{total} arasi gosteriliyor")

    def build_log_row(self, log):
        row = QFrame()
        row.setObjectName("logRow")
        row.setFixedHeight(102)

        layout = QHBoxLayout(row)
        layout.setContentsMargins(28, 18, 28, 18)
        layout.setSpacing(12)

        date_label = QLabel(log["date"])
        date_label.setObjectName("mainText")

        user_col = QVBoxLayout()
        user_label = QLabel(log["user"])
        user_label.setObjectName("mainText")
        user_sub = QLabel("Islemi yapan kullanici")
        user_sub.setObjectName("subText")
        user_col.addWidget(user_label)
        user_col.addWidget(user_sub)

        action_type = QLabel(log["action_type"])
        action_type.setObjectName("actionTypePill")
        action_type.setAlignment(Qt.AlignCenter)

        desc_label = QLabel(log["description"])
        desc_label.setObjectName("subText")
        desc_label.setWordWrap(True)

        entity_label = QLabel(f'{log["entity_type"]} #{log["entity_id"]}')
        entity_label.setObjectName("entityPill")
        entity_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(date_label, 1.5)
        layout.addLayout(user_col, 1.4)
        layout.addWidget(action_type, 1.7)
        layout.addWidget(desc_label, 3.0)
        layout.addWidget(entity_label, 1.3)
        return row

    def apply_filters(self):
        search_text = self.search_input.text().strip().lower()
        selected_user = self.user_filter.currentText()
        selected_type = self.type_filter.currentText()

        self.log_data = self.service.get_all()
        self.filtered_data = []

        for log in self.log_data:
            matches_search = (
                search_text in log["user"].lower()
                or search_text in log["action_type"].lower()
                or search_text in log["description"].lower()
            )
            matches_user = selected_user == "Tum Kullanicilar" or log["user"] == selected_user
            matches_type = selected_type == "Tum Islem Tipleri" or log["action_type"] == selected_type

            if matches_search and matches_user and matches_type:
                self.filtered_data.append(log)

        self.refresh_rows()
        self.update_summary()

    def update_summary(self):
        self.summary_value.setText(str(len(self.filtered_data)))

    def export_logs(self):
        filename, _selected_filter = QFileDialog.getSaveFileName(
            self,
            "Loglari Disa Aktar",
            "audit-loglari.csv",
            "CSV Files (*.csv)",
        )
        if not filename:
            return

        with open(filename, "w", encoding="utf-8") as handle:
            handle.write("date,user,action_type,description,entity_type,entity_id\n")
            for log in self.filtered_data:
                row = [
                    log["date"],
                    log["user"],
                    log["action_type"],
                    log["description"],
                    log["entity_type"],
                    str(log["entity_id"]),
                ]
                safe_row = [value.replace('"', "'") for value in row]
                handle.write(",".join(f'"{value}"' for value in safe_row) + "\n")

        self.export_btn.setText("Disa Aktarildi")

    def apply_styles(self):
        self.setStyleSheet(
            """
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

            #summaryCard {
                background: #005E10;
                border-radius: 18px;
            }

            #summaryValue {
                font-size: 34px;
                font-weight: 900;
                color: white;
                background: transparent;
            }

            #summaryLabel {
                font-size: 13px;
                font-weight: 700;
                color: rgba(255, 255, 255, 0.82);
                background: transparent;
            }

            #summaryGhostIcon {
                font-size: 28px;
                font-weight: 900;
                color: rgba(255, 255, 255, 0.22);
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

            #logRow {
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

            #actionTypePill {
                background: #E8F1FB;
                color: #1D4ED8;
                border-radius: 14px;
                padding: 6px 14px;
                font-size: 13px;
                font-weight: 800;
            }

            #entityPill {
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
            """
        )
