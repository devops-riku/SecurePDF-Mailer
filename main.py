import sys
import os
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QLineEdit, QFileDialog,
    QProgressBar, QTabWidget, QComboBox
)
from PySide6.QtCore import QThread

# UI Modules
from ui.theme import apply_modern_theme
from ui.settings_tab import SettingsTab

# Workers
from core.worker_pdf import PDFEncryptWorker
from core.worker_email import EmailSendWorker   # UPDATED worker

import pythoncom
import win32com.client as win32


# =====================================================================
# MAIN APPLICATION WINDOW
# =====================================================================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SecurePDF Mailer - rikucat")
        self.resize(1000, 650)

        # Tabs
        self.tabs = QTabWidget()
        self.encrypt_tab = QWidget()
        self.email_tab = QWidget()
        self.settings_tab = SettingsTab()

        self.tabs.addTab(self.encrypt_tab, "Encrypt PDFs")
        self.tabs.addTab(self.email_tab, "Email Sender")
        self.tabs.addTab(self.settings_tab, "Settings")

        self.init_encrypt_tab()
        self.init_email_tab()

        self.setCentralWidget(self.tabs)

        # Apply theme last
        apply_modern_theme(self)

    # =================================================================
    # TAB 1 — PDF ENCRYPTOR
    # =================================================================
    def init_encrypt_tab(self):
        layout = QVBoxLayout(self.encrypt_tab)

        # Folder selectors
        folder_row = QHBoxLayout()

        self.input_entry = QLineEdit()
        self.input_entry.setPlaceholderText("Input folder...")
        btn_input = QPushButton("Browse")
        btn_input.clicked.connect(self.select_input)

        self.output_entry = QLineEdit()
        self.output_entry.setPlaceholderText("Output folder...")
        btn_output = QPushButton("Browse")
        btn_output.clicked.connect(self.select_output)

        folder_row.addWidget(self.input_entry)
        folder_row.addWidget(btn_input)
        folder_row.addWidget(self.output_entry)
        folder_row.addWidget(btn_output)

        # Start button
        self.start_pdf_btn = QPushButton("🚀 Encrypt PDFs")
        self.start_pdf_btn.setObjectName("startButton")
        self.start_pdf_btn.clicked.connect(self.start_encryption)

        # Progress & Log
        self.pdf_progress = QProgressBar()
        self.pdf_log = QTextEdit()
        self.pdf_log.setReadOnly(True)

        # Layout add
        layout.addLayout(folder_row)
        layout.addWidget(self.start_pdf_btn)
        layout.addWidget(self.pdf_progress)
        layout.addWidget(QLabel("Log"))
        layout.addWidget(self.pdf_log)

    def select_input(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Input Folder")
        if folder:
            self.input_entry.setText(folder)

    def select_output(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_entry.setText(folder)

    def start_encryption(self):
        input_folder = self.input_entry.text().strip()
        output_folder = self.output_entry.text().strip()
        pdf_rules = self.settings_tab.pdf_rules_tab.get_rules()

        if not pdf_rules:
            self.pdf_log.append("⚠ No PDF rules found.")
            return

        self.start_pdf_btn.setEnabled(False)

        # Thread
        self.thread = QThread()
        self.worker = PDFEncryptWorker(input_folder, output_folder, pdf_rules)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.log.connect(self.pdf_log.append)
        self.worker.progress.connect(self.pdf_progress.setValue)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(lambda: self.start_pdf_btn.setEnabled(True))

        self.thread.start()

    # =================================================================
    # TAB 2 — EMAIL SENDER
    # =================================================================
    def init_email_tab(self):
        layout = QVBoxLayout(self.email_tab)

        pythoncom.CoInitialize()
        self.outlook = win32.Dispatch("Outlook.Application")
        self.accounts = self.outlook.Session.Accounts

        # Account selector
        self.account_box = QComboBox()
        self.account_map = {}

        for acc in self.accounts:
            if acc.SmtpAddress:
                self.account_box.addItem(acc.SmtpAddress)
                self.account_map[acc.SmtpAddress] = acc

        # Subject / Body
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Email subject...")

        self.body_input = QTextEdit()
        self.body_input.setPlaceholderText("Email body...")

        # Folder selection
        self.email_folder_btn = QPushButton("Select Attachment Folder")
        self.email_folder_btn.clicked.connect(self.select_email_folder)
        self.email_folder = None

        # Send button
        self.send_email_btn = QPushButton("Send Emails")
        self.send_email_btn.clicked.connect(self.start_email_sending)

        # Progress + Log
        self.email_progress = QProgressBar()
        self.email_log = QTextEdit()
        self.email_log.setReadOnly(True)

        # Layout organization
        layout.addWidget(QLabel("Send From"))
        layout.addWidget(self.account_box)

        layout.addWidget(QLabel("Subject"))
        layout.addWidget(self.subject_input)

        layout.addWidget(QLabel("Body"))
        layout.addWidget(self.body_input)

        layout.addWidget(self.email_folder_btn)
        layout.addWidget(self.send_email_btn)
        layout.addWidget(self.email_progress)

        layout.addWidget(QLabel("Log"))
        layout.addWidget(self.email_log)

    def select_email_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Attachment Folder")
        if folder:
            self.email_folder = folder
            self.email_folder_btn.setText(folder)

    # ---------------- EMAIL THREAD START ----------------
    def start_email_sending(self):
        email_rules = self.settings_tab.email_rules_tab.get_rules()

        if not email_rules:
            self.email_log.append("⚠ No email rules found.")
            return

        if not self.email_folder:
            self.email_log.append("⚠ No folder selected.")
            return

        # Store for use in UI COM thread
        self.account = self.account_map[self.account_box.currentText()]
        self.subject = self.subject_input.text().strip()
        self.body = self.body_input.toPlainText()

        self.send_email_btn.setEnabled(False)

        # Worker + Thread
        self.email_thread = QThread()
        self.email_worker = EmailSendWorker(self.email_folder, email_rules, delay=1)
        self.email_worker.moveToThread(self.email_thread)

        # Worker emits send_next → UI sends email
        self.email_worker.send_next.connect(self.send_email_ui)
        self.email_worker.log.connect(self.email_log.append)
        self.email_worker.progress.connect(self.email_progress.setValue)

        self.email_worker.finished.connect(self.email_thread.quit)
        self.email_worker.finished.connect(lambda: self.send_email_btn.setEnabled(True))

        self.email_thread.started.connect(self.email_worker.run)
        self.email_thread.start()

    # ---------------------------------------------------------
    # This runs in UI thread → SAFE for Outlook COM
    # ---------------------------------------------------------
    def send_email_ui(self, filename, matched_email):
        if not matched_email:
            self.email_log.append(f"⏭ Skipped (no match): {filename}")
            return

        try:
            mail = self.outlook.CreateItem(0)
            mail.SendUsingAccount = self.account

            mail.To = matched_email
            mail.Subject = self.subject
            mail.Body = self.body
            mail.Attachments.Add(os.path.join(self.email_folder, filename))
            mail.Send()

            self.email_log.append(f"✔ Sent → {matched_email} ({filename})")

        except Exception as e:
            self.email_log.append(f"❌ Failed to send {filename}: {e}")


# =====================================================================
# RUN APPLICATION
# =====================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
