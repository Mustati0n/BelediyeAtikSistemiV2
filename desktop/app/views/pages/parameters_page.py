from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QScrollArea,
    QFormLayout,
    QDoubleSpinBox,
    QSpinBox,
    QMessageBox,
)

from services.parameter_service import ParameterService


class ParametersPage(QWidget):
    def __init__(self):
        super().__init__()
        self.service = ParameterService()
        self.parameters = self.service.get_all()

        self.build_ui()
        self.apply_styles()
        self.load_values()

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

        header_row = QHBoxLayout()
        header_row.setSpacing(28)

        left_header = QVBoxLayout()
        left_header.setSpacing(8)

        title = QLabel("Sistem Parametreleri")
        title.setObjectName("pageTitle")

        subtitle = QLabel(
            "Kod değişikliği gerektirmeden yönetilebilen sistemsel eşikleri, maaş katsayılarını\n"
            "ve atık türlerine göre kilogram birim fiyatlarını buradan güncelleyebilirsiniz."
        )
        subtitle.setObjectName("pageSubtitle")
        subtitle.setWordWrap(True)

        left_header.addWidget(title)
        left_header.addWidget(subtitle)

        right_header = QVBoxLayout()
        right_header.setSpacing(14)

        save_btn = QPushButton("✓  Değişiklikleri Kaydet")
        save_btn.setObjectName("saveButton")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setFixedHeight(56)
        save_btn.clicked.connect(self.save_parameters)

        reset_btn = QPushButton("↺  Varsayılanlara Dön")
        reset_btn.setObjectName("resetButton")
        reset_btn.setCursor(Qt.PointingHandCursor)
        reset_btn.setFixedHeight(48)
        reset_btn.clicked.connect(self.reset_parameters)

        status_card = QFrame()
        status_card.setObjectName("statusCard")
        status_card.setFixedHeight(136)

        status_layout = QHBoxLayout(status_card)
        status_layout.setContentsMargins(28, 18, 28, 18)

        status_text_col = QVBoxLayout()
        status_text_col.setSpacing(0)

        status_value = QLabel("9")
        status_value.setObjectName("statusValue")

        status_label = QLabel("Aktif Parametre Alanı")
        status_label.setObjectName("statusLabel")

        status_text_col.addStretch()
        status_text_col.addWidget(status_value)
        status_text_col.addWidget(status_label)
        status_text_col.addStretch()

        ghost_icon = QLabel("⚙")
        ghost_icon.setObjectName("statusGhostIcon")
        ghost_icon.setAlignment(Qt.AlignCenter)

        status_layout.addLayout(status_text_col)
        status_layout.addStretch()
        status_layout.addWidget(ghost_icon)

        right_header.addWidget(save_btn)
        right_header.addWidget(reset_btn)
        right_header.addWidget(status_card)

        header_row.addLayout(left_header, 3)
        header_row.addLayout(right_header, 1.35)

        self.content_layout.addLayout(header_row)

        middle_row = QHBoxLayout()
        middle_row.setSpacing(24)

        left_col = QVBoxLayout()
        left_col.setSpacing(20)

        salary_panel = self.build_salary_panel()
        threshold_panel = self.build_threshold_panel()

        left_col.addWidget(salary_panel)
        left_col.addWidget(threshold_panel)

        right_col = QVBoxLayout()
        right_col.setSpacing(20)

        waste_price_panel = self.build_waste_price_panel()
        info_panel = self.build_info_panel()

        right_col.addWidget(waste_price_panel)
        right_col.addWidget(info_panel)

        middle_row.addLayout(left_col, 1)
        middle_row.addLayout(right_col, 1)

        self.content_layout.addLayout(middle_row)

        scroll.setWidget(content)
        root_layout.addWidget(scroll)

    def build_salary_panel(self):
        panel = QFrame()
        panel.setObjectName("paramPanel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)

        title = QLabel("Maaş Parametreleri")
        title.setObjectName("panelTitle")

        subtitle = QLabel("Personel maaş hesaplama sürecinde kullanılacak katsayılar.")
        subtitle.setObjectName("panelSubtitle")

        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignLeft)

        self.salary_base_multiplier = QDoubleSpinBox()
        self.salary_base_multiplier.setRange(0.10, 10.00)
        self.salary_base_multiplier.setDecimals(2)
        self.salary_base_multiplier.setSingleStep(0.05)
        self.salary_base_multiplier.setObjectName("spinInput")

        self.child_additional_payment = QDoubleSpinBox()
        self.child_additional_payment.setRange(0.00, 50000.00)
        self.child_additional_payment.setDecimals(2)
        self.child_additional_payment.setSingleStep(50.00)
        self.child_additional_payment.setSuffix(" ₺")
        self.child_additional_payment.setObjectName("spinInput")

        form.addRow("Taban Maaş Çarpanı", self.salary_base_multiplier)
        form.addRow("Çocuk Başına Ek Ödeme", self.child_additional_payment)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(form)

        return panel

    def build_threshold_panel(self):
        panel = QFrame()
        panel.setObjectName("paramPanel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)

        title = QLabel("Operasyon Eşikleri")
        title.setObjectName("panelTitle")

        subtitle = QLabel("Kritik konteyner ve görev üretiminde kullanılacak temel eşikler.")
        subtitle.setObjectName("panelSubtitle")

        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignLeft)

        self.critical_fill_threshold = QSpinBox()
        self.critical_fill_threshold.setRange(1, 100)
        self.critical_fill_threshold.setSuffix(" %")
        self.critical_fill_threshold.setObjectName("spinInput")

        form.addRow("Kritik Doluluk Eşiği", self.critical_fill_threshold)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(form)

        return panel

    def build_waste_price_panel(self):
        panel = QFrame()
        panel.setObjectName("paramPanel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(18)

        title = QLabel("Atık Türü Birim Fiyatları")
        title.setObjectName("panelTitle")

        subtitle = QLabel("Geri dönüşüm gelir süreçlerinde kullanılacak kilogram bazlı fiyatlar.")
        subtitle.setObjectName("panelSubtitle")

        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignLeft)

        self.plastic_unit_price = self.make_money_spin()
        self.glass_unit_price = self.make_money_spin()
        self.metal_unit_price = self.make_money_spin()
        self.paper_unit_price = self.make_money_spin()
        self.organic_unit_price = self.make_money_spin()
        self.other_unit_price = self.make_money_spin()

        form.addRow("Plastik", self.plastic_unit_price)
        form.addRow("Cam", self.glass_unit_price)
        form.addRow("Metal", self.metal_unit_price)
        form.addRow("Kağıt", self.paper_unit_price)
        form.addRow("Organik", self.organic_unit_price)
        form.addRow("Diğer", self.other_unit_price)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(form)

        return panel

    def build_info_panel(self):
        panel = QFrame()
        panel.setObjectName("infoPanel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(12)

        title = QLabel("Parametre Bilgilendirme")
        title.setObjectName("infoTitle")

        text1 = QLabel("• Buradaki değişiklikler yalnızca sistem parametre alanlarını temsil eden frontend yapısıdır.")
        text2 = QLabel("• Backend bağlantısı eklendiğinde bu alanlar API üzerinden okunup güncellenecektir.")
        text3 = QLabel("• Kaynak kapsamına göre bu ekran maaş katsayıları, kritik eşikler ve atık fiyatlarını yönetir.")

        for label in [text1, text2, text3]:
            label.setObjectName("infoText")
            label.setWordWrap(True)
            layout.addWidget(label)

        layout.addStretch()

        return panel

    def make_money_spin(self):
        spin = QDoubleSpinBox()
        spin.setRange(0.00, 1000.00)
        spin.setDecimals(2)
        spin.setSingleStep(0.10)
        spin.setSuffix(" ₺/kg")
        spin.setObjectName("spinInput")
        return spin

    def load_values(self):
        self.parameters = self.service.get_all()

        self.salary_base_multiplier.setValue(self.parameters["salary_base_multiplier"])
        self.child_additional_payment.setValue(self.parameters["child_additional_payment"])
        self.critical_fill_threshold.setValue(self.parameters["critical_fill_threshold"])
        self.plastic_unit_price.setValue(self.parameters["plastic_unit_price"])
        self.glass_unit_price.setValue(self.parameters["glass_unit_price"])
        self.metal_unit_price.setValue(self.parameters["metal_unit_price"])
        self.paper_unit_price.setValue(self.parameters["paper_unit_price"])
        self.organic_unit_price.setValue(self.parameters["organic_unit_price"])
        self.other_unit_price.setValue(self.parameters["other_unit_price"])

    def collect_values(self):
        return {
            "salary_base_multiplier": self.salary_base_multiplier.value(),
            "child_additional_payment": self.child_additional_payment.value(),
            "critical_fill_threshold": self.critical_fill_threshold.value(),
            "plastic_unit_price": self.plastic_unit_price.value(),
            "glass_unit_price": self.glass_unit_price.value(),
            "metal_unit_price": self.metal_unit_price.value(),
            "paper_unit_price": self.paper_unit_price.value(),
            "organic_unit_price": self.organic_unit_price.value(),
            "other_unit_price": self.other_unit_price.value(),
        }

    def save_parameters(self):
        values = self.collect_values()
        self.service.update_all(values)
        self.load_values()
        QMessageBox.information(self, "Başarılı", "Sistem parametreleri güncellendi.")

    def reset_parameters(self):
        answer = QMessageBox.question(
            self,
            "Varsayılanlara Dön",
            "Tüm sistem parametreleri varsayılan değerlere döndürülsün mü?"
        )
        if answer == QMessageBox.Yes:
            self.service.reset_defaults()
            self.load_values()
            QMessageBox.information(self, "Bilgi", "Varsayılan parametreler geri yüklendi.")

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

            #saveButton {
                background: #005E10;
                color: white;
                border: none;
                border-radius: 16px;
                font-size: 16px;
                font-weight: 800;
                padding: 0 24px;
            }

            #saveButton:hover {
                background: #004A0C;
            }

            #resetButton {
                background: white;
                color: #374151;
                border: 1px solid #D8DDD7;
                border-radius: 14px;
                font-size: 14px;
                font-weight: 700;
                padding: 0 18px;
            }

            #resetButton:hover {
                background: #F4F5F2;
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

            #paramPanel, #infoPanel {
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

            #panelSubtitle {
                font-size: 13px;
                color: #475569;
                background: transparent;
            }

            #infoTitle {
                font-size: 18px;
                font-weight: 800;
                color: #48637A;
                background: transparent;
            }

            #infoText {
                font-size: 14px;
                color: #5B7085;
                background: transparent;
            }

            QDoubleSpinBox, QSpinBox {
                background: #FAFBF9;
                border: 1px solid #E5E7EB;
                border-radius: 12px;
                padding: 10px 12px;
                font-size: 14px;
                min-height: 24px;
            }

            QLabel {
                background: transparent;
            }

            QDialog {
                background: white;
            }
        """)