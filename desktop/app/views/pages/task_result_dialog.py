from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QComboBox,
    QTextEdit,
    QDialogButtonBox,
    QMessageBox,
)


class TaskResultDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Görev Sonuçlandır")
        self.setModal(True)
        self.resize(420, 260)
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout(self)

        form = QFormLayout()
        form.setSpacing(12)

        self.result_combo = QComboBox()
        self.result_combo.addItems([
            "Ulaşılamadı",
            "Yanlış İhbar",
            "Tekrar Kontrol Gerekli",
        ])

        self.note_input = QTextEdit()
        self.note_input.setPlaceholderText("İsteğe bağlı açıklama giriniz...")
        self.note_input.setFixedHeight(100)

        form.addRow("Sonuç:", self.result_combo)
        form.addRow("Açıklama:", self.note_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)

        layout.addLayout(form)
        layout.addWidget(buttons)

    def validate_and_accept(self):
        if not self.result_combo.currentText():
            QMessageBox.warning(self, "Uyarı", "Bir sonuç seçmelisiniz.")
            return
        self.accept()

    def get_data(self):
        return {
            "result_type": self.result_combo.currentText(),
            "note": self.note_input.toPlainText().strip(),
        }