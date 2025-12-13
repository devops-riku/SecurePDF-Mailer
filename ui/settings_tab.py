from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from ui.rules_pdf import PDFRulesEditor
from ui.rules_email import EmailRulesEditor


class SettingsTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # Create subtabs inside Settings
        self.subtabs = QTabWidget()

        # PDF Rules Tab
        self.pdf_rules_tab = PDFRulesEditor()
        self.subtabs.addTab(self.pdf_rules_tab, "PDF Rules")

        # Email Rules Tab
        self.email_rules_tab = EmailRulesEditor()
        self.subtabs.addTab(self.email_rules_tab, "Email Rules")

        layout.addWidget(self.subtabs)
