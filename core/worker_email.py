# worker_email.py
import os
import time
import pythoncom
import win32com.client as win32

from PySide6.QtCore import QObject, Signal
from core.rule_matcher import rule_matches


class EmailSendWorker(QObject):
    progress = Signal(int)
    log = Signal(str)
    finished = Signal()

    send_next = Signal(str, str)  # filename, matched_email

    def __init__(self, folder, rules, delay=1):
        super().__init__()
        self.folder = folder
        self.rules = rules
        self.delay = delay

        # Set externally by main UI thread:
        self.from_account = None
        self.delegate_address = None
        self.subject = ""
        self.body = ""

    # -----------------------------------------
    # Validate if user can SendAs / OnBehalfOf
    # -----------------------------------------
    def has_send_permission(self, outlook_session, delegate_email):
        try:
            # Lookup mailbox
            recip = outlook_session.CreateRecipient(delegate_email)
            recip.Resolve()

            if not recip.Resolved:
                return False  # mailbox not found

            exch = recip.AddressEntry.GetExchangeUser()
            if exch is None:
                return False

            # 1) SendOnBehalf (delegation)
            delegates = exch.GetDelegates()
            if delegates is not None:
                for d in delegates:
                    if d.Address.lower() == self.from_account.SmtpAddress.lower():
                        return True

            # 2) SendAs (Exchange permission)
            # Permission check: If user has SendAs, sending will succeed.
            # Best we can do programmatically is try to open mailbox.
            try:
                mailbox = outlook_session.GetSharedDefaultFolder(recip, 6)  # 6 = Inbox
                _ = mailbox.Items  # Try accessing mailbox
                return True
            except:
                pass

            return False

        except Exception:
            return False

    # -----------------------------------------
    # Worker main loop
    # -----------------------------------------
    def run(self):
        pythoncom.CoInitialize()

        outlook = win32.Dispatch("Outlook.Application")
        session = outlook.Session

        files = [f for f in os.listdir(self.folder)
                 if f.lower().endswith(".pdf")]

        if not files:
            self.log.emit("⚠ No PDF files found.")
            self.finished.emit()
            return

        total = len(files)

        # Validate permission BEFORE sending
        delegate = self.delegate_address
        if delegate:
            ok = self.has_send_permission(session, delegate)
            if not ok:
                self.log.emit(f"❌ You do NOT have permission to send as {delegate}.")
                self.log.emit("Email sending aborted to prevent Outlook errors.")
                self.finished.emit()
                return
            else:
                self.log.emit(f"✔ Permission confirmed: You can send as {delegate}")

        # Continue with normal loop
        for index, filename in enumerate(files, start=1):
            filepath = os.path.join(self.folder, filename)

            # match rule
            matched_email = None
            for r in self.rules:
                if rule_matches(r["contains"], filename):
                    matched_email = r["email"]
                    break

            # Send UI-controlled message
            self.send_next.emit(filename, matched_email)

            time.sleep(self.delay)
            self.progress.emit(int(index / total * 100))

        self.log.emit("🎉 Email batch completed!")
        self.finished.emit()
