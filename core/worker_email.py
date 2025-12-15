import os
import time
import base64
import re
import requests
import msal

from PySide6.QtCore import QObject, Signal
from msal_extensions import FilePersistence, PersistedTokenCache
from core.rule_matcher import rule_matches


# ================= CONFIG =================
CLIENT_ID = "e7b6514d-ddb7-4168-8657-f494764717d1"
TENANT_ID = "8e3c1050-7050-4298-9bd3-fe83c3ad5673"
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["Mail.Send"]
CACHE_FILE = "msal_cache.bin"
GRAPH_SENDMAIL = "https://graph.microsoft.com/v1.0/me/sendMail"
# ==========================================


def normalize_html(html: str) -> str:
    """Prepare HTML for Outlook / Graph rendering"""
    if not html:
        return ""

    # Remove DOCTYPE
    html = re.sub(r'<!DOCTYPE.*?>', '', html, flags=re.I | re.S)

    # Extract body content
    match = re.search(r'<body[^>]*>(.*?)</body>', html, re.I | re.S)
    if match:
        html = match.group(1)

    # FORCE Outlook-safe font inline
    html = f"""
    <div style="
        font-family: Calibri, Arial, sans-serif;
        font-size: 11pt;
        color: #000000;
    ">
        {html}
    </div>
    """

    return html.strip()



class EmailSendWorker(QObject):
    progress = Signal(int)
    log = Signal(str)
    finished = Signal()

    def __init__(self, folder, rules, delay=1):
        super().__init__()
        self.folder = folder
        self.rules = rules
        self.delay = delay

        # Set by UI
        self.from_account = None     # delegated mailbox
        self.subject = ""
        self.body = ""

        # ---------- MSAL ----------
        cache = PersistedTokenCache(FilePersistence(CACHE_FILE))
        self.msal_app = msal.PublicClientApplication(
            client_id=CLIENT_ID,
            authority=AUTHORITY,
            token_cache=cache
        )

    # -----------------------------------------
    # MSAL Token
    # -----------------------------------------
    def get_access_token(self):
        accounts = self.msal_app.get_accounts()

        if accounts:
            result = self.msal_app.acquire_token_silent(
                SCOPES, account=accounts[0]
            )
        else:
            result = self.msal_app.acquire_token_interactive(
                SCOPES, prompt="select_account"
            )

        if "access_token" in result:
            return result["access_token"]

        raise Exception(result.get("error_description", "Authentication failed"))

    # -----------------------------------------
    # Send email via Microsoft Graph
    # -----------------------------------------
    def send_email(self, token, to_email, attachment_path):
        with open(attachment_path, "rb") as f:
            encoded_file = base64.b64encode(f.read()).decode("utf-8")

        payload = {
            "message": {
                "subject": self.subject,
                "body": {
                    "contentType": "HTML",
                    "content": normalize_html(self.body)
                },
                "toRecipients": [
                    {"emailAddress": {"address": to_email}}
                ],
                "attachments": [
                    {
                        "@odata.type": "#microsoft.graph.fileAttachment",
                        "name": os.path.basename(attachment_path),
                        "contentBytes": encoded_file
                    }
                ]
            }
        }

        # Send on behalf of (delegated mailbox)
        if self.from_account:
            payload["message"]["from"] = {
                "emailAddress": {"address": self.from_account}
            }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        r = requests.post(GRAPH_SENDMAIL, headers=headers, json=payload)

        if r.status_code != 202:
            raise Exception(r.text)

    # -----------------------------------------
    # Worker loop
    # -----------------------------------------
    def run(self):
        try:
            token = self.get_access_token()
        except Exception as e:
            self.log.emit(f"❌ Authentication failed: {e}")
            self.finished.emit()
            return

        files = [
            f for f in os.listdir(self.folder)
            if f.lower().endswith(".pdf")
        ]

        if not files:
            self.log.emit("⚠ No PDF files found.")
            self.finished.emit()
            return

        total = len(files)

        for index, filename in enumerate(files, start=1):
            filepath = os.path.join(self.folder, filename)

            matched_email = None
            for rule in self.rules:
                if rule_matches(rule["contains"], filename):
                    matched_email = rule["email"]
                    break

            if not matched_email:
                self.log.emit(f"⏭ Skipped: {filename}")
            else:
                try:
                    self.send_email(token, matched_email, filepath)
                    self.log.emit(
                        f"✔ Sent → {matched_email} ({filename})"
                    )
                except Exception as e:
                    self.log.emit(
                        f"❌ Failed: {filename}\n{e}"
                    )

            time.sleep(self.delay)
            self.progress.emit(int(index / total * 100))

        self.log.emit("🎉 Email batch completed!")
        self.finished.emit()
