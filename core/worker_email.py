# core/worker_email.py
import os
import time
import pythoncom
from PySide6.QtCore import QObject, Signal

from core.rule_matcher import rule_matches


class EmailSendWorker(QObject):
    send_next = Signal(str, str)   # filename, matched_email
    progress = Signal(int)
    log = Signal(str)
    finished = Signal()

    def __init__(self, folder, rules, delay=1):
        super().__init__()
        self.folder = folder
        self.rules = rules
        self.delay = delay

    def run(self):
        try:
            pythoncom.CoInitialize()

            files = [
                f for f in os.listdir(self.folder)
                if f.lower().endswith(".pdf")
            ]

            if not files:
                self.log.emit("⚠ No PDF files found.")
                self.finished.emit()
                return

            total = len(files)
            processed = 0

            for filename in files:
                matched_email = None

                # Match rule
                for r in self.rules:
                    if rule_matches(r["contains"], filename):
                        matched_email = r["email"]
                        break

                # Emit for UI thread to send email
                self.send_next.emit(filename, matched_email)

                processed += 1
                self.progress.emit(int(processed / total * 100))
                time.sleep(self.delay)

            self.log.emit("🎉 Email batch completed!")

        except Exception as e:
            self.log.emit(f"❌ CRITICAL ERROR: {e}")

        self.finished.emit()
