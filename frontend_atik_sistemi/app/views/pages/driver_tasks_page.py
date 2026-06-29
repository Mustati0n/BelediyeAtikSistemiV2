from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
)

from services.api_client import ApiError
from services.driver_service import DriverService
from views.pages.task_result_dialog import TaskResultDialog


class DriverTasksPage(QWidget):
    def __init__(self):
        super().__init__()
        self.service = DriverService()
        self.tasks = self.service.get_tasks()
        self.selected_task = None

        self.build_ui()
        self.apply_styles()
        self.load_tasks()

    def build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(46, 34, 46, 34)
        layout.setSpacing(20)

        # Header
        title = QLabel("Günlük Görev ve Rota")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Şoförün günlük görevlerini, öncelik durumlarını ve rota üzerindeki iş noktalarını "
            "takip ettiği ana operasyon ekranı."
        )
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(subtitle)

        # Main split
        main_row = QHBoxLayout()
        main_row.setSpacing(24)

        # Left side
        left_col = QVBoxLayout()
        left_col.setSpacing(18)

        map_panel = QFrame()
        map_panel.setObjectName("mapPanel")
        map_layout = QVBoxLayout(map_panel)
        map_layout.setContentsMargins(24, 24, 24, 24)

        map_title = QLabel("Harita Alanı")
        map_title.setObjectName("panelTitle")

        map_text = QLabel("Görev noktaları ve pinler burada gösterilecek.")
        map_text.setObjectName("subText")

        map_placeholder = QLabel("🗺")
        map_placeholder.setObjectName("mapGhost")
        map_placeholder.setAlignment(Qt.AlignCenter)

        map_layout.addWidget(map_title)
        map_layout.addWidget(map_text)
        map_layout.addStretch()
        map_layout.addWidget(map_placeholder)
        map_layout.addStretch()

        task_list_panel = QFrame()
        task_list_panel.setObjectName("listPanel")
        task_list_layout = QVBoxLayout(task_list_panel)
        task_list_layout.setContentsMargins(20, 20, 20, 20)
        task_list_layout.setSpacing(12)

        list_title = QLabel("Görev Listesi")
        list_title.setObjectName("panelTitle")

        self.task_list = QListWidget()
        self.task_list.setObjectName("taskList")
        self.task_list.currentRowChanged.connect(self.on_task_selected)

        task_list_layout.addWidget(list_title)
        task_list_layout.addWidget(self.task_list)

        left_col.addWidget(map_panel, 1.1)
        left_col.addWidget(task_list_panel, 1)

        # Right side
        right_panel = QFrame()
        right_panel.setObjectName("detailPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(24, 24, 24, 24)
        right_layout.setSpacing(16)

        detail_title = QLabel("Seçili Görev Detayı")
        detail_title.setObjectName("panelTitle")

        self.task_title = self.build_detail_row(right_layout, "Görev", "-")
        self.task_type = self.build_detail_row(right_layout, "Tip", "-")
        self.task_priority = self.build_detail_row(right_layout, "Öncelik", "-")
        self.task_status = self.build_detail_row(right_layout, "Durum", "-")
        self.task_location = self.build_detail_row(right_layout, "Konum", "-")
        self.task_coords = self.build_detail_row(right_layout, "Koordinat", "-")
        self.task_desc = self.build_detail_row(right_layout, "Açıklama", "-")

        right_layout.insertWidget(0, detail_title)

        button_row = QVBoxLayout()
        button_row.setSpacing(12)

        self.start_btn = QPushButton("▶  Görevi Başlat")
        self.start_btn.setObjectName("primaryButton")
        self.start_btn.setFixedHeight(50)
        self.start_btn.clicked.connect(self.start_task)

        self.complete_btn = QPushButton("✓  Görevi Tamamla")
        self.complete_btn.setObjectName("successButton")
        self.complete_btn.setFixedHeight(50)
        self.complete_btn.clicked.connect(self.complete_task)

        self.fail_btn = QPushButton("⚠  Sorunlu / Başarısız İşaretle")
        self.fail_btn.setObjectName("warningButton")
        self.fail_btn.setFixedHeight(50)
        self.fail_btn.clicked.connect(self.fail_task)

        button_row.addWidget(self.start_btn)
        button_row.addWidget(self.complete_btn)
        button_row.addWidget(self.fail_btn)

        right_layout.addStretch()
        right_layout.addLayout(button_row)

        main_row.addLayout(left_col, 1.45)
        main_row.addWidget(right_panel, 1.0)

        layout.addLayout(main_row)
        root_layout.addWidget(content)

    def build_detail_row(self, parent_layout, label_text, value_text):
        row = QFrame()
        row.setObjectName("infoRow")

        layout = QHBoxLayout(row)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        label = QLabel(label_text)
        label.setObjectName("rowLabel")

        value = QLabel(value_text)
        value.setObjectName("rowValue")
        value.setWordWrap(True)
        value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        layout.addWidget(label)
        layout.addStretch()
        layout.addWidget(value)

        parent_layout.addWidget(row)
        return value

    def load_tasks(self):
        self.tasks = self.service.get_tasks()
        self.task_list.clear()

        for task in self.tasks:
            item = QListWidgetItem(f'{task["title"]} | {task["priority"]} | {task["status"]}')
            item.setData(Qt.UserRole, task["id"])
            self.task_list.addItem(item)

        if self.tasks:
            self.task_list.setCurrentRow(0)

    def on_task_selected(self, row_index):
        if row_index < 0 or row_index >= len(self.tasks):
            self.selected_task = None
            return

        task = self.tasks[row_index]
        self.selected_task = task

        self.task_title.setText(task["title"])
        self.task_type.setText(task["task_type"])
        self.task_priority.setText(task["priority"])
        self.task_status.setText(task["status"])
        self.task_location.setText(task["location"])
        self.task_coords.setText(f'{task["lat"]}, {task["lng"]}')
        self.task_desc.setText(task["description"])

    def start_task(self):
        if not self.selected_task:
            QMessageBox.warning(self, "Uyarı", "Önce bir görev seçmelisiniz.")
            return

        try:
            self.service.start_task(self.selected_task["id"])
            self.load_tasks()
            QMessageBox.information(self, "Bilgi", "Görev işlemde olarak işaretlendi.")
        except ApiError as exc:
            QMessageBox.warning(self, "API Hatası", str(exc))

    def complete_task(self):
        if not self.selected_task:
            QMessageBox.warning(self, "Uyarı", "Önce bir görev seçmelisiniz.")
            return

        try:
            self.service.complete_task(self.selected_task["id"])
            self.load_tasks()
            QMessageBox.information(self, "Bilgi", "Görev tamamlandı.")
        except ApiError as exc:
            QMessageBox.warning(self, "API Hatası", str(exc))

    def fail_task(self):
        if not self.selected_task:
            QMessageBox.warning(self, "Uyarı", "Önce bir görev seçmelisiniz.")
            return

        dialog = TaskResultDialog(self)
        if dialog.exec():
            result = dialog.get_data()
            try:
                self.service.fail_task(self.selected_task["id"], result["result_type"], result["note"])
                self.load_tasks()
                QMessageBox.information(
                    self,
                    "Bilgi",
                    f'Görev "{result["result_type"]}" sonucu ile işaretlendi.'
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

            #mapPanel, #listPanel, #detailPanel {
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

            #subText {
                font-size: 13px;
                color: #475569;
                background: transparent;
            }

            #mapGhost {
                font-size: 80px;
                color: rgba(11, 91, 25, 0.16);
                background: transparent;
            }

            #taskList {
                background: #FAFBF9;
                border: 1px solid #ECEEEA;
                border-radius: 14px;
                padding: 8px;
                font-size: 14px;
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

            #primaryButton {
                background: #005E10;
                color: white;
                border: none;
                border-radius: 16px;
                font-size: 15px;
                font-weight: 800;
            }

            #primaryButton:hover {
                background: #004A0C;
            }

            #successButton {
                background: #DCFCE7;
                color: #166534;
                border: none;
                border-radius: 16px;
                font-size: 15px;
                font-weight: 800;
            }

            #successButton:hover {
                background: #c9f7d8;
            }

            #warningButton {
                background: #FEF3C7;
                color: #92400E;
                border: none;
                border-radius: 16px;
                font-size: 15px;
                font-weight: 800;
            }

            #warningButton:hover {
                background: #fde7aa;
            }

            QLabel {
                background: transparent;
            }
        """)
