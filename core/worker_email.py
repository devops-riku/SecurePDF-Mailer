# worker_email.py
import os
import time
from PySide6.QtCore import QObject, Signal
from core.worker_pdf import rule_matches


class EmailSendWorker(QObject):
    send_next = Signal(str, str)     # filename, matched_email
    progress = Signal(int)
    finished = Signal()
    log = Signal(str)

    def __init__(self, folder, rules, delay=2):
        super().__init__()
        self.folder = folder
        self.rules = rules
        self.delay = delay

    def run(self):
        files = [f for f in os.listdir(self.folder)
                 if f.lower().endswith(".pdf")]

        if not files:
            self.log.emit("⚠ No PDF files found.")
            self.finished.emit()
            return

        total = len(files)

        for idx, filename in enumerate(files, start=1):
            matched_email = None
            for r in self.rules:
                if rule_matches(r["contains"], filename):
                    matched_email = r["email"]
                    break

            # Emit to main UI — this sends the email safely on UI thread
            self.send_next.emit(filename, matched_email)

            # update progress
            self.progress.emit(int(idx / total * 100))

            time.sleep(self.delay)

        self.log.emit("🎉 Email batch completed!")
        self.finished.emit()
