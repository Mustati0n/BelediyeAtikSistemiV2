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

from services.personnel_service import PersonnelService


class PersonnelDialog(QDialog):
    def __init__(self, parent=None, person=None):
        super().__init__(parent)
        self.person = person
        self.setWindowTitle("Personel Ekle / Düzenle")
        self.setModal(True)
        self.resize(420, 280)
        self.build_ui()

        if self.person:
            self.load_person_data()

    def build_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()
        form.setSpacing(12)

        self.name_input = QLineEdit()
        self.email_input = QLineEdit()

        self.department_combo = QComboBox()
        self.department_combo.addItems(["Lojistik", "İdari İşler", "Atık Yönetimi", "Bakım", "Muhasebe"])

        self.role_combo = QComboBox()
        self.role_combo.addItems([
            "Operasyon Sorumlusu",
            "Sistem Yöneticisi",
            "Saha Operatörü",
            "Filo Denetçisi",
            "Muhasebe Uzmanı",
        ])

        self.status_combo = QComboBox()
        self.status_combo.addItems(["Aktif", "Pasif"])

        self.last_login_input = QLineEdit()
        self.last_login_input.setPlaceholderText("Bugün, 09:42")

        form.addRow("Ad Soyad:", self.name_input)
        form.addRow("E-Posta:", self.email_input)
        form.addRow("Birim:", self.department_combo)
        form.addRow("Rol:", self.role_combo)
        form.addRow("Durum:", self.status_combo)
        form.addRow("Son Giriş:", self.last_login_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)

        layout.addLayout(form)
        layout.addSpacing(12)
        layout.addWidget(buttons)

    def load_person_data(self):
        self.name_input.setText(self.person["name"])
        self.email_input.setText(self.person["email"])
        self.department_combo.setCurrentText(self.person["department"])
        self.role_combo.setCurrentText(self.person["role"])
        self.status_combo.setCurrentText(self.person["status"])
        self.last_login_input.setText(self.person["last_login"])

    def validate_and_accept(self):
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Uyarı", "Ad Soyad alanı boş bırakılamaz.")
            return

        if not self.email_input.text().strip():
            QMessageBox.warning(self, "Uyarı", "E-posta alanı boş bırakılamaz.")
            return

        self.accept()

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "email": self.email_input.text().strip(),
            "department": self.department_combo.currentText(),
            "role": self.role_combo.currentText(),
            "status": self.status_combo.currentText(),
            "last_login": self.last_login_input.text().strip() or "Bugün, 09:00",
            "avatar_bg": "#DCEBF6",
        }


class PersonnelPage(QWidget):
    def __init__(self):
        super().__init__()
        self.service = PersonnelService()
        self.personnel_data = self.service.get_all()
        self.filtered_data = list(self.personnel_data)

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

        title = QLabel("Personel ve Rol Yönetimi")
        title.setObjectName("pageTitle")

        subtitle = QLabel("Sistem genelindeki tüm operasyonel personeli yönetin, yetki seviyelerini belirleyin ve\naktif durumlarını takip edin.")
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)

        left_header.addWidget(title)
        left_header.addWidget(subtitle)

        right_header = QVBoxLayout()
        right_header.setSpacing(14)

        add_btn = QPushButton("＋  Yeni Personel Ekle")
        add_btn.setObjectName("addButton")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setFixedHeight(56)
        add_btn.clicked.connect(self.add_person)

        active_card = QFrame()
        active_card.setObjectName("activeStaffCard")
        active_card.setFixedHeight(136)

        active_card_layout = QHBoxLayout(active_card)
        active_card_layout.setContentsMargins(28, 18, 28, 18)

        active_text_col = QVBoxLayout()
        active_text_col.setSpacing(0)

        active_count = QLabel("124")
        active_count.setObjectName("activeCount")

        active_label = QLabel("Aktif Saha Personeli")
        active_label.setObjectName("activeLabel")

        active_text_col.addStretch()
        active_text_col.addWidget(active_count)
        active_text_col.addWidget(active_label)
        active_text_col.addStretch()

        ghost_icon = QLabel("👥")
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
        self.search_input.setPlaceholderText("İsim veya e-posta ile ara...")
        self.search_input.setObjectName("searchInput")
        self.search_input.textChanged.connect(self.apply_filters)

        search_col.addWidget(search_label)
        search_col.addWidget(self.search_input)

        department_col = QVBoxLayout()
        department_col.setSpacing(8)

        department_label = QLabel("BİRİM")
        department_label.setObjectName("filterLabel")

        self.department_filter = QComboBox()
        self.department_filter.setObjectName("filterCombo")
        self.department_filter.currentIndexChanged.connect(self.apply_filters)

        department_col.addWidget(department_label)
        department_col.addWidget(self.department_filter)

        role_col = QVBoxLayout()
        role_col.setSpacing(8)

        role_label = QLabel("ROL")
        role_label.setObjectName("filterLabel")

        self.role_filter = QComboBox()
        self.role_filter.setObjectName("filterCombo")
        self.role_filter.currentIndexChanged.connect(self.apply_filters)

        role_col.addWidget(role_label)
        role_col.addWidget(self.role_filter)

        filter_layout.addLayout(search_col, 2)
        filter_layout.addLayout(department_col, 1.2)
        filter_layout.addLayout(role_col, 1.2)

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

        self.count_label = QLabel("Toplam 0 personelden 0-0 arası gösteriliyor")
        self.count_label.setObjectName("countLabel")

        footer_row.addWidget(self.count_label)
        footer_row.addStretch()

        prev_btn = QPushButton("‹")
        prev_btn.setObjectName("pageGhostButton")
        prev_btn.setFixedSize(42, 42)

        page1 = QPushButton("1")
        page1.setObjectName("pageActiveButton")
        page1.setFixedSize(42, 42)

        page2 = QPushButton("2")
        page2.setObjectName("pageGhostButton")
        page2.setFixedSize(42, 42)

        page3 = QPushButton("3")
        page3.setObjectName("pageGhostButton")
        page3.setFixedSize(42, 42)

        next_btn = QPushButton("›")
        next_btn.setObjectName("pageGhostButton")
        next_btn.setFixedSize(42, 42)

        footer_row.addWidget(prev_btn)
        footer_row.addWidget(page1)
        footer_row.addWidget(page2)
        footer_row.addWidget(page3)
        footer_row.addWidget(next_btn)

        list_layout.addLayout(footer_row)

        self.content_layout.addWidget(self.list_panel)

        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(24)

        role_panel = self.build_role_distribution_panel()
        report_panel = self.build_system_report_panel()

        bottom_row.addWidget(role_panel, 1)
        bottom_row.addWidget(report_panel, 2)

        self.content_layout.addLayout(bottom_row)

        scroll.setWidget(content)
        root_layout.addWidget(scroll)

    def build_table_header(self):
        header = QFrame()
        header.setObjectName("tableHeader")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(28, 18, 28, 18)
        layout.setSpacing(12)

        layout.addWidget(self.make_header_label("PERSONEL BİLGİSİ"), 3.6)
        layout.addWidget(self.make_header_label("BİRİM / ROL"), 2.2)
        layout.addWidget(self.make_header_label("DURUM"), 1.2)
        layout.addWidget(self.make_header_label("SON GİRİŞ"), 1.4)
        layout.addWidget(self.make_header_label("İŞLEMLER", Qt.AlignRight), 1.1)

        return header

    def make_header_label(self, text, align=Qt.AlignLeft):
        label = QLabel(text)
        label.setObjectName("tableHeaderLabel")
        label.setAlignment(align | Qt.AlignVCenter)
        return label

    def build_role_distribution_panel(self):
        panel = QFrame()
        panel.setObjectName("bottomPanel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(18)

        title = QLabel("ROL DAĞILIMI")
        title.setObjectName("miniPanelTitle")

        row1 = QHBoxLayout()
        y_label = QLabel("Yönetici")
        y_label.setObjectName("miniRowLabel")
        y_count = QLabel("12")
        y_count.setObjectName("miniRowCount")

        row1.addWidget(y_label)
        row1.addStretch()
        row1.addWidget(y_count)

        bar1 = QProgressBar()
        bar1.setObjectName("greenProgress")
        bar1.setRange(0, 100)
        bar1.setValue(30)
        bar1.setTextVisible(False)

        row2 = QHBoxLayout()
        o_label = QLabel("Operatör")
        o_label.setObjectName("miniRowLabel")
        o_count = QLabel("28")
        o_count.setObjectName("miniRowCount")

        row2.addWidget(o_label)
        row2.addStretch()
        row2.addWidget(o_count)

        bar2 = QProgressBar()
        bar2.setObjectName("greenProgress")
        bar2.setRange(0, 100)
        bar2.setValue(65)
        bar2.setTextVisible(False)

        layout.addWidget(title)
        layout.addLayout(row1)
        layout.addWidget(bar1)
        layout.addLayout(row2)
        layout.addWidget(bar2)
        layout.addStretch()

        return panel

    def build_system_report_panel(self):
        panel = QFrame()
        panel.setObjectName("reportPanel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(14)

        title = QLabel("Sistem Sağlık Raporu")
        title.setObjectName("reportTitle")

        subtitle = QLabel("Personel giriş oranları son 30 günde %15 arttı.")
        subtitle.setObjectName("reportSubtitle")

        link = QLabel("Detaylı Raporu İncele")
        link.setObjectName("reportLink")

        ghost = QLabel("📈")
        ghost.setObjectName("reportGhost")
        ghost.setAlignment(Qt.AlignRight | Qt.AlignBottom)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(8)
        layout.addWidget(link)
        layout.addStretch()
        layout.addWidget(ghost)

        return panel

    def populate_filters(self):
        departments = sorted({p["department"] for p in self.personnel_data})
        roles = sorted({p["role"] for p in self.personnel_data})

        self.department_filter.clear()
        self.department_filter.addItem("Tüm Birimler")
        self.department_filter.addItems(departments)

        self.role_filter.clear()
        self.role_filter.addItem("Tüm Roller")
        self.role_filter.addItems(roles)

    def get_initials(self, full_name):
        parts = full_name.split()
        if len(parts) >= 2:
            return (parts[0][0] + parts[1][0]).upper()
        return full_name[:2].upper()

    def clear_rows(self):
        while self.rows_container.count():
            item = self.rows_container.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def refresh_rows(self):
        self.clear_rows()

        for person in self.filtered_data:
            self.rows_container.addWidget(self.build_person_row(person))

        self.rows_container.addStretch()

        total = len(self.filtered_data)
        if total == 0:
            self.count_label.setText("Toplam 0 personelden 0-0 arası gösteriliyor")
        else:
            self.count_label.setText(f"Toplam {total} personelden 1-{total} arası gösteriliyor")

    def build_person_row(self, person):
        row = QFrame()
        row.setObjectName("personRow")
        row.setFixedHeight(102)

        layout = QHBoxLayout(row)
        layout.setContentsMargins(28, 18, 28, 18)
        layout.setSpacing(12)

        info_widget = QWidget()
        info_layout = QHBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(16)

        avatar = QLabel(self.get_initials(person["name"]))
        avatar.setObjectName("avatarCircle")
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setFixedSize(44, 44)
        avatar.setStyleSheet(f"""
            background: {person.get("avatar_bg", "#DCEBF6")};
            color: #2D3748;
            border-radius: 22px;
            font-size: 16px;
            font-weight: 800;
        """)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        name = QLabel(person["name"])
        name.setObjectName("personName")

        email = QLabel(person["email"])
        email.setObjectName("personEmail")

        text_col.addWidget(name)
        text_col.addWidget(email)

        info_layout.addWidget(avatar)
        info_layout.addLayout(text_col)

        dep_widget = QWidget()
        dep_layout = QVBoxLayout(dep_widget)
        dep_layout.setContentsMargins(0, 0, 0, 0)
        dep_layout.setSpacing(2)

        department = QLabel(person["department"])
        department.setObjectName("departmentName")

        role = QLabel(person["role"])
        role.setObjectName("roleName")

        dep_layout.addWidget(department)
        dep_layout.addWidget(role)

        status = QLabel(f"●  {person['status']}")
        status.setAlignment(Qt.AlignCenter)
        if person["status"] == "Aktif":
            status.setObjectName("statusActive")
        else:
            status.setObjectName("statusPassive")

        last_login = QLabel(person["last_login"])
        last_login.setObjectName("lastLoginLabel")

        action_widget = QWidget()
        action_layout = QHBoxLayout(action_widget)
        action_layout.setContentsMargins(0, 0, 0, 0)
        action_layout.setSpacing(10)

        edit_btn = QPushButton("✎")
        edit_btn.setObjectName("iconActionButton")
        edit_btn.setFixedSize(34, 34)
        edit_btn.clicked.connect(lambda _, p=person: self.edit_person(p))

        toggle_btn = QPushButton("⛔" if person["status"] == "Aktif" else "👤+")
        toggle_btn.setObjectName("iconActionGreenButton" if person["status"] == "Pasif" else "iconActionButton")
        toggle_btn.setFixedSize(34, 34)
        toggle_btn.clicked.connect(lambda _, p=person: self.toggle_status(p))

        action_layout.addStretch()
        action_layout.addWidget(edit_btn)
        action_layout.addWidget(toggle_btn)

        layout.addWidget(info_widget, 3.6)
        layout.addWidget(dep_widget, 2.2)
        layout.addWidget(status, 1.2)
        layout.addWidget(last_login, 1.4)
        layout.addWidget(action_widget, 1.1)

        return row

    def apply_filters(self):
        search_text = self.search_input.text().strip().lower()
        selected_department = self.department_filter.currentText()
        selected_role = self.role_filter.currentText()

        self.personnel_data = self.service.get_all()
        self.filtered_data = []

        for person in self.personnel_data:
            matches_search = (
                search_text in person["name"].lower()
                or search_text in person["email"].lower()
            )

            matches_department = selected_department == "Tüm Birimler" or person["department"] == selected_department
            matches_role = selected_role == "Tüm Roller" or person["role"] == selected_role

            if matches_search and matches_department and matches_role:
                self.filtered_data.append(person)

        self.refresh_rows()

    def add_person(self):
        dialog = PersonnelDialog(self)
        if dialog.exec():
            self.service.add_person(dialog.get_data())
            self.personnel_data = self.service.get_all()
            self.populate_filters()
            self.apply_filters()

    def edit_person(self, person):
        dialog = PersonnelDialog(self, person)
        if dialog.exec():
            self.service.update_person(person["id"], dialog.get_data())
            self.personnel_data = self.service.get_all()
            self.populate_filters()
            self.apply_filters()

    def toggle_status(self, person):
        self.service.toggle_status(person["id"])
        self.personnel_data = self.service.get_all()
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
                line-height: 1.5;
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

            #activeStaffCard {
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

            #filterPanel, #listPanel, #bottomPanel {
                background: white;
                border: 1px solid #ECEEEA;
                border-radius: 20px;
            }

            #reportPanel {
                background: #F1F8FD;
                border: 1px solid #D9ECF7;
                border-radius: 20px;
            }

            #filterLabel, #tableHeaderLabel, #miniPanelTitle {
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

            #personRow {
                background: white;
                border: none;
                border-bottom: 1px solid #ECEEEA;
            }

            #personName {
                font-size: 16px;
                font-weight: 900;
                color: #111827;
                background: transparent;
            }

            #personEmail {
                font-size: 13px;
                color: #475569;
                background: transparent;
            }

            #departmentName {
                font-size: 16px;
                font-weight: 800;
                color: #111827;
                background: transparent;
            }

            #roleName {
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

            #statusPassive {
                background: #E5E5E5;
                color: #374151;
                border-radius: 14px;
                padding: 6px 14px;
                font-size: 13px;
                font-weight: 800;
            }

            #lastLoginLabel {
                font-size: 14px;
                color: #1F2937;
                background: transparent;
            }

            #iconActionButton, #iconActionGreenButton {
                border: none;
                background: transparent;
                font-size: 18px;
                font-weight: 700;
            }

            #iconActionButton:hover, #iconActionGreenButton:hover {
                background: #F3F4F6;
                border-radius: 10px;
            }

            #iconActionGreenButton {
                color: #0B5B19;
            }

            #countLabel {
                font-size: 13px;
                color: #374151;
                background: transparent;
            }

            #pageActiveButton {
                background: #005E10;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 800;
            }

            #pageGhostButton {
                background: white;
                color: #374151;
                border: 1px solid #D9DED7;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 700;
            }

            #miniRowLabel, #miniRowCount {
                font-size: 15px;
                font-weight: 700;
                color: #111827;
                background: transparent;
            }

            #reportTitle {
                font-size: 18px;
                font-weight: 800;
                color: #48637A;
                background: transparent;
            }

            #reportSubtitle {
                font-size: 14px;
                color: #7A8EA3;
                background: transparent;
            }

            #reportLink {
                font-size: 14px;
                font-weight: 700;
                color: #48637A;
                text-decoration: underline;
                background: transparent;
            }

            #reportGhost {
                font-size: 52px;
                color: rgba(72, 99, 122, 0.18);
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