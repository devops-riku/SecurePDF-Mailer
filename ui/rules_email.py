import os
import csv
import json

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QFileDialog, QDialog, QLabel, QLineEdit, QDialogButtonBox,
    QMessageBox, QHeaderView
)

CONFIG_DIR = "config"
EMAIL_RULES_JSON = os.path.join(CONFIG_DIR, "email_rules.json")


# ------------------------------------------------------------
# ADD RULE DIALOG
# ------------------------------------------------------------
class AddEmailRuleDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add Email Rule")

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Substring Contains:"))
        self.contains_entry = QLineEdit()
        layout.addWidget(self.contains_entry)

        layout.addWidget(QLabel("Email Address:"))
        self.email_entry = QLineEdit()
        layout.addWidget(self.email_entry)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_values(self):
        return (
            self.contains_entry.text().strip(),
            self.email_entry.text().strip()
        )


# ------------------------------------------------------------
# EMAIL RULES EDITOR
# ------------------------------------------------------------
class EmailRulesEditor(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # BUTTON ROW
        btn_row = QHBoxLayout()

        btn_add = QPushButton("➕ Add Email Rule")
        btn_add.clicked.connect(self.add_rule_dialog)

        btn_import = QPushButton("📁 Import CSV")
        btn_import.clicked.connect(self.import_csv)

        btn_export = QPushButton("💾 Export CSV")
        btn_export.clicked.connect(self.export_csv)

        btn_row.addWidget(btn_add)
        btn_row.addWidget(btn_import)
        btn_row.addWidget(btn_export)
        btn_row.addStretch()

        layout.addLayout(btn_row)

        # TABLE
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Contains", "Email", "Delete"])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        layout.addWidget(self.table)

        self.load_rules()

    # --------------------------------------------------------
    # ADD RULE
    # --------------------------------------------------------
    def add_rule_dialog(self):
        dlg = AddEmailRuleDialog()
        if dlg.exec():
            contains, email = dlg.get_values()
            if contains and email:
                self.add_rule(contains, email)
                self.save_rules()

    def add_rule(self, contains, email):
        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row, 0, QTableWidgetItem(contains))
        self.table.setItem(row, 1, QTableWidgetItem(email))

        delete_btn = QPushButton("✕")
        delete_btn.setObjectName("deleteButton")
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.clicked.connect(self.handle_delete)
        self.table.setCellWidget(row, 2, delete_btn)

    # --------------------------------------------------------
    # DELETE RULE
    # --------------------------------------------------------
    def handle_delete(self):
        button = self.sender()
        for r in range(self.table.rowCount()):
            if self.table.cellWidget(r, 2) is button:
                self.table.removeRow(r)
                self.save_rules()
                return

    # --------------------------------------------------------
    # GET RULES
    # --------------------------------------------------------
    def get_rules(self):
        rules = []
        for r in range(self.table.rowCount()):
            c = self.table.item(r, 0).text().strip()
            e = self.table.item(r, 1).text().strip()
            if c and e:
                rules.append({"contains": c, "email": e})
        return rules

    # --------------------------------------------------------
    # SAVE RULES
    # --------------------------------------------------------
    def save_rules(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        rules = self.get_rules()
        with open(EMAIL_RULES_JSON, "w", encoding="utf-8") as f:
            json.dump(rules, f, indent=4)

    # --------------------------------------------------------
    # LOAD RULES
    # --------------------------------------------------------
    def load_rules(self):
        if not os.path.exists(EMAIL_RULES_JSON):
            return

        try:
            with open(EMAIL_RULES_JSON, "r", encoding="utf-8") as f:
                rules = json.load(f)

            for r in rules:
                self.add_rule(r["contains"], r["email"])

        except:
            pass

    # --------------------------------------------------------
    # IMPORT CSV
    # --------------------------------------------------------
    def import_csv(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Import Email Rules (CSV)", filter="CSV Files (*.csv)"
        )
        if not path:
            return

        try:
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.add_rule(row["contains"], row["email"])
            self.save_rules()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import CSV:\n{e}")

    # --------------------------------------------------------
    # EXPORT CSV
    # --------------------------------------------------------
    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Email Rules", "email_rules.csv", "CSV Files (*.csv)"
        )
        if not path:
            return

        rules = self.get_rules()

        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["contains", "email"])
                for r in rules:
                    writer.writerow([r["contains"], r["email"]])

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export CSV:\n{e}")
