from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from services.audit_log_service import AuditLogService
from services.container_service import ContainerService
from services.personnel_service import PersonnelService
from services.vehicle_service import VehicleService


class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.vehicle_service = VehicleService()
        self.container_service = ContainerService()
        self.personnel_service = PersonnelService()
        self.audit_service = AuditLogService()

        self.build_ui()
        self.apply_styles()
        self.refresh_dashboard()

    def build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        self.layout = QVBoxLayout(content)
        self.layout.setContentsMargins(42, 34, 42, 30)
        self.layout.setSpacing(26)

        self.page_title = QLabel("Yonetici Paneli")
        self.page_title.setObjectName("pageTitle")

        self.page_subtitle = QLabel("Operasyon, filo ve saha yogunlugunun anlik mock ozeti.")
        self.page_subtitle.setObjectName("pageSubtitle")

        self.layout.addWidget(self.page_title)
        self.layout.addWidget(self.page_subtitle)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(18)

        self.daily_waste_card = self.create_stat_card("GUNLUK TOPLANAN ATIK", "0", "kg", "ATIK")
        self.active_fleet_card = self.create_stat_card("AKTIF FILO", "0", "", "FILO")
        self.maintenance_card = self.create_stat_card("BAKIMDAKI ARAC", "0", "", "SERVIS")
        self.active_staff_card = self.create_stat_card("AKTIF PERSONEL", "0", "", "EKIP")
        self.critical_card = self.create_stat_card("KRITIK DOLULUK", "0", "", "UYARI", accent=True)

        stats_row.addWidget(self.daily_waste_card, 2)
        stats_row.addWidget(self.active_fleet_card, 1)
        stats_row.addWidget(self.maintenance_card, 1)
        stats_row.addWidget(self.active_staff_card, 1)
        stats_row.addWidget(self.critical_card, 1)
        self.layout.addLayout(stats_row)

        mid_row = QHBoxLayout()
        mid_row.setSpacing(22)
        self.monthly_panel = self.create_monthly_panel()
        self.approvals_panel = self.create_approvals_panel()
        mid_row.addWidget(self.monthly_panel, 3)
        mid_row.addWidget(self.approvals_panel, 1.25)
        self.layout.addLayout(mid_row)

        self.alerts_panel = self.create_alerts_panel()
        self.layout.addWidget(self.alerts_panel)

        footer = QLabel("© 2026 SUSTAINED CITY SYSTEMS  •  FRONTEND DEMO MODE")
        footer.setObjectName("footerLabel")
        footer.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(footer)

        scroll.setWidget(content)
        root_layout.addWidget(scroll)

    def refresh_dashboard(self):
        vehicles = self.vehicle_service.get_all()
        containers = self.container_service.get_all()
        personnel = self.personnel_service.get_all()
        logs = self.audit_service.get_all()

        active_vehicles = [vehicle for vehicle in vehicles if vehicle["status"] == "Aktif"]
        maintenance_vehicles = [vehicle for vehicle in vehicles if vehicle["status"] == "Bakimda"]
        active_personnel = [person for person in personnel if person["status"] == "Aktif"]
        critical_containers = [container for container in containers if container["fill_rate"] >= 85]

        total_capacity = sum(vehicle["capacity_kg"] for vehicle in active_vehicles)
        estimated_daily_collection = int(total_capacity * 0.62)

        self.update_stat_card(self.daily_waste_card, f"{estimated_daily_collection:,}".replace(",", "."), "kg")
        self.update_stat_card(self.active_fleet_card, str(len(active_vehicles)))
        self.update_stat_card(self.maintenance_card, str(len(maintenance_vehicles)))
        self.update_stat_card(self.active_staff_card, str(len(active_personnel)))
        self.update_stat_card(self.critical_card, str(len(critical_containers)))

        self.populate_monthly_panel(vehicles, containers, personnel)
        self.populate_approvals_panel(maintenance_vehicles, critical_containers, personnel)
        self.populate_alerts_panel(critical_containers, logs, vehicles)

    def create_stat_card(self, title, value, suffix, icon_text, accent=False):
        card = QFrame()
        card.setObjectName("criticalStatCard" if accent else "statCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(12)

        top_row = QHBoxLayout()
        icon_label = QLabel(icon_text)
        icon_label.setObjectName("statIconAccent" if accent else "statIcon")
        top_row.addWidget(icon_label)
        top_row.addStretch()

        title_label = QLabel(title)
        title_label.setObjectName("statTitle")
        value_label = QLabel(value)
        value_label.setObjectName("statValueAccent" if accent else "statValue")
        suffix_label = QLabel(suffix)
        suffix_label.setObjectName("statSuffix")

        value_row = QHBoxLayout()
        value_row.addWidget(value_label)
        if suffix:
            value_row.addWidget(suffix_label)
        value_row.addStretch()

        layout.addLayout(top_row)
        layout.addWidget(title_label)
        layout.addLayout(value_row)
        layout.addStretch()

        card.value_label = value_label
        card.suffix_label = suffix_label
        return card

    def update_stat_card(self, card, value, suffix=""):
        card.value_label.setText(value)
        card.suffix_label.setText(suffix)

    def create_monthly_panel(self):
        panel = QFrame()
        panel.setObjectName("whitePanel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(18)

        title = QLabel("Operasyon Yogunlugu")
        title.setObjectName("panelTitle")
        subtitle = QLabel("Mock veriden uretilen haftalik doluluk ve kapasite dengesi")
        subtitle.setObjectName("panelSubtitle")

        self.monthly_metrics_layout = QVBoxLayout()
        self.monthly_metrics_layout.setSpacing(12)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(self.monthly_metrics_layout)
        return panel

    def populate_monthly_panel(self, vehicles, containers, personnel):
        self.clear_layout(self.monthly_metrics_layout)

        metrics = [
            ("Aktif arac kullanimi", len([v for v in vehicles if v["status"] == "Aktif"]), len(vehicles), "#1F7A32"),
            ("Kritik konteyner yuklenmesi", len([c for c in containers if c["fill_rate"] >= 85]), len(containers), "#B42318"),
            ("Aktif personel kapsama", len([p for p in personnel if p["status"] == "Aktif"]), len(personnel), "#175CD3"),
        ]

        for title, current, total, color in metrics:
            self.monthly_metrics_layout.addWidget(self.create_progress_row(title, current, total, color))

        summary_box = QFrame()
        summary_box.setObjectName("summaryStrip")
        summary_layout = QHBoxLayout(summary_box)
        summary_layout.setContentsMargins(18, 14, 18, 14)

        summary_layout.addWidget(QLabel(f"Toplam arac: {len(vehicles)}"))
        summary_layout.addStretch()
        summary_layout.addWidget(QLabel(f"Konteyner: {len(containers)}"))
        summary_layout.addStretch()
        summary_layout.addWidget(QLabel(f"Personel: {len(personnel)}"))
        self.monthly_metrics_layout.addWidget(summary_box)

    def create_progress_row(self, title, current, total, color):
        row = QFrame()
        row.setObjectName("progressRow")
        layout = QVBoxLayout(row)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)

        top = QHBoxLayout()
        top.addWidget(QLabel(title))
        top.addStretch()
        percent = 0 if total == 0 else int((current / total) * 100)
        top.addWidget(QLabel(f"{current}/{total}  (%{percent})"))

        track = QFrame()
        track.setObjectName("progressTrack")
        track_layout = QHBoxLayout(track)
        track_layout.setContentsMargins(0, 0, 0, 0)
        track_layout.setSpacing(0)

        fill = QFrame()
        fill.setStyleSheet(
            f"background: {color}; border-radius: 9px;"
        )
        fill.setFixedHeight(18)
        fill.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        remainder = QFrame()
        remainder.setStyleSheet("background: transparent;")
        remainder.setFixedHeight(18)
        remainder.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        track_layout.addWidget(fill, max(percent, 1))
        track_layout.addWidget(remainder, max(100 - percent, 1))

        layout.addLayout(top)
        layout.addWidget(track)
        return row

    def create_approvals_panel(self):
        panel = QFrame()
        panel.setObjectName("whitePanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header = QHBoxLayout()
        title = QLabel("Oncelikli Isler")
        title.setObjectName("panelTitle")
        self.approval_badge = QLabel("0 Bekliyor")
        self.approval_badge.setObjectName("badgeLabel")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.approval_badge)

        self.approvals_list_layout = QVBoxLayout()
        self.approvals_list_layout.setSpacing(12)

        layout.addLayout(header)
        layout.addLayout(self.approvals_list_layout)
        layout.addStretch()
        return panel

    def populate_approvals_panel(self, maintenance_vehicles, critical_containers, personnel):
        self.clear_layout(self.approvals_list_layout)

        inactive_personnel = [person for person in personnel if person["status"] != "Aktif"]
        items = [
            (
                "Bakim planlamasi",
                f"{len(maintenance_vehicles)} arac serviste",
                "Bakim atolyeleri icin oncelikli planlama gerekli.",
            ),
            (
                "Kritik konteyner gorevi",
                f"{len(critical_containers)} nokta esik ustunde",
                "Sahaya yeni arac atamasi icin onay bekleniyor.",
            ),
            (
                "Personel vardiya dengeleme",
                f"{len(inactive_personnel)} pasif kayit",
                "Aktif ekip dagilimi yeniden gozden gecirilmeli.",
            ),
        ]

        self.approval_badge.setText(f"{len(items)} Bekliyor")
        for title, amount, desc in items:
            self.approvals_list_layout.addWidget(self.create_approval_item(title, amount, desc))

    def create_approval_item(self, title, amount, desc):
        item = QFrame()
        item.setObjectName("approvalItem")
        layout = QVBoxLayout(item)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        top_row = QHBoxLayout()
        top_row.addWidget(QLabel(title))
        top_row.addStretch()
        amount_label = QLabel(amount)
        amount_label.setObjectName("approvalAmount")
        top_row.addWidget(amount_label)

        desc_label = QLabel(desc)
        desc_label.setObjectName("approvalDesc")
        desc_label.setWordWrap(True)

        button_row = QHBoxLayout()
        approve_btn = QPushButton("Planla")
        approve_btn.setObjectName("approveButton")
        reject_btn = QPushButton("Ertele")
        reject_btn.setObjectName("rejectButton")
        button_row.addWidget(approve_btn)
        button_row.addWidget(reject_btn)

        layout.addLayout(top_row)
        layout.addWidget(desc_label)
        layout.addLayout(button_row)
        return item

    def create_alerts_panel(self):
        panel = QFrame()
        panel.setObjectName("whitePanel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(18)

        header_row = QHBoxLayout()
        title_col = QVBoxLayout()
        title = QLabel("Kritik Sistem Uyarilari")
        title.setObjectName("panelTitle")
        subtitle = QLabel("Saha ve sistem loglarindan derlenen son dikkat noktalar")
        subtitle.setObjectName("panelSubtitle")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)

        see_all = QPushButton("Tumunu Gor")
        see_all.setObjectName("seeAllButton")

        header_row.addLayout(title_col)
        header_row.addStretch()
        header_row.addWidget(see_all)
        layout.addLayout(header_row)

        self.alert_rows_layout = QVBoxLayout()
        self.alert_rows_layout.setSpacing(12)
        layout.addLayout(self.alert_rows_layout)
        return panel

    def populate_alerts_panel(self, critical_containers, logs, vehicles):
        self.clear_layout(self.alert_rows_layout)

        rows = []
        for container in critical_containers[:2]:
            rows.append(
                (
                    container["code"],
                    container["region"],
                    f"Doluluk %{container['fill_rate']}",
                    "Acil mudahale",
                    "Arac ata",
                )
            )

        for log in logs[:2]:
            rows.append(
                (
                    log["entity_type"],
                    log["user"],
                    log["action_type"],
                    log["date"],
                    "Incele",
                )
            )

        if not rows and vehicles:
            rows.append(
                (
                    vehicles[0]["plate"],
                    vehicles[0]["region"],
                    vehicles[0]["status"],
                    vehicles[0]["last_maintenance"],
                    "Durum ac",
                )
            )

        for asset_title, asset_subtitle, warning, time_text, action_text in rows:
            self.alert_rows_layout.addWidget(
                self.create_alert_row(asset_title, asset_subtitle, warning, time_text, action_text)
            )

    def create_alert_row(self, asset_title, asset_subtitle, warning, time_text, action_text):
        row = QFrame()
        row.setObjectName("alertRow")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(12)

        asset_col = QVBoxLayout()
        title = QLabel(asset_title)
        title.setObjectName("alertAssetTitle")
        subtitle = QLabel(asset_subtitle)
        subtitle.setObjectName("alertAssetSubtitle")
        asset_col.addWidget(title)
        asset_col.addWidget(subtitle)

        warning_label = QLabel(warning)
        warning_label.setObjectName("alertWarning")
        time_label = QLabel(time_text)
        time_label.setObjectName("alertTime")

        action_btn = QPushButton(action_text)
        action_btn.setObjectName("alertActionButton")
        action_btn.setCursor(Qt.PointingHandCursor)
        action_btn.setFixedHeight(36)
        action_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout.addLayout(asset_col, 3)
        layout.addWidget(warning_label, 2)
        layout.addWidget(time_label, 2)
        layout.addWidget(action_btn, 1)
        return row

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget is not None:
                widget.deleteLater()
            elif child_layout is not None:
                self.clear_layout(child_layout)

    def apply_styles(self):
        self.setStyleSheet(
            """
            QWidget {
                background: #F5F6F3;
                font-family: Segoe UI, Arial, sans-serif;
                color: #0F172A;
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

            #statCard, #criticalStatCard, #whitePanel, #alertRow, #approvalItem, #progressRow {
                background: white;
                border: 1px solid #E7EBE6;
                border-radius: 22px;
            }

            #criticalStatCard {
                border-color: #F3C8C1;
            }

            #statIcon, #statIconAccent {
                padding: 9px 12px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 800;
                background: #E5F4E9;
                color: #166534;
            }

            #statIconAccent {
                background: #FDE8E8;
                color: #B42318;
            }

            #statTitle {
                font-size: 14px;
                font-weight: 800;
                color: #263238;
                letter-spacing: 1px;
                background: transparent;
            }

            #statValue, #statValueAccent {
                font-size: 28px;
                font-weight: 800;
                color: #0F172A;
                background: transparent;
            }

            #statValueAccent {
                color: #C62828;
            }

            #statSuffix {
                font-size: 16px;
                color: #0F172A;
                background: transparent;
                margin-top: 10px;
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

            #progressTrack {
                background: #EEF2EF;
                border-radius: 9px;
                min-height: 18px;
            }

            #summaryStrip {
                background: #FAFBF9;
                border: 1px solid #ECEEEA;
                border-radius: 16px;
                color: #475569;
                font-size: 13px;
                font-weight: 700;
            }

            #badgeLabel {
                background: #D9ECFA;
                color: #567A95;
                border-radius: 14px;
                padding: 6px 12px;
                font-size: 11px;
                font-weight: 700;
            }

            #approvalItem {
                background: #FAFBF9;
                border-radius: 18px;
            }

            #approvalAmount {
                font-size: 14px;
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

            #rejectButton {
                background: #F3F4F6;
                color: #4B5563;
                border: none;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 800;
                padding: 8px 12px;
            }

            #seeAllButton {
                background: transparent;
                border: none;
                color: #0C5A17;
                font-size: 14px;
                font-weight: 800;
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

            #footerLabel {
                font-size: 11px;
                letter-spacing: 1px;
                color: #98A2B3;
                background: transparent;
                margin-top: 6px;
            }
            """
        )
