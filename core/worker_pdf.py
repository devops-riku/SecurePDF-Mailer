# worker_pdf.py
import os
import time
from PySide6.QtCore import QObject, Signal
from PyPDF2 import PdfReader, PdfWriter

# ------------------------------------------------------------
# SAFE RULE MATCH FUNCTION (no debug prints)
# ------------------------------------------------------------
def rule_matches(rule_text, filename):
    rule = rule_text.lower().strip()
    filename = filename.lower().strip()

    parts = rule.split()
    tail1 = parts[-1]
    tail2 = " ".join(parts[-2:]) if len(parts) >= 2 else tail1
    head_tokens = parts[:-2] if tail2 in rule else parts[:-1]

    initials = [p[0] for p in head_tokens]
    combined_initials = "".join(initials)

    block = filename.split(" - ")[-1] if " - " in filename else filename
    block = block.replace(".pdf", "").strip()
    block_tokens = block.split()

    if not (tail2 in block or tail1 in block):
        return False

    if not head_tokens:
        return True

    for token in head_tokens:
        if token in block_tokens:
            return True

    for token in block_tokens:
        if token.startswith(combined_initials):
            return True

    return all(
        any(init == t or t.startswith(init) for t in block_tokens)
        for init in initials
    )


# ============================================================
# PDF ENCRYPT WORKER — CLEAN, SAFE, LOGGING + PROGRESS SUPPORT
# ============================================================
class PDFEncryptWorker(QObject):
    progress = Signal(int)      # int only — FIXED
    log = Signal(str)
    finished = Signal()

    def __init__(self, input_folder, output_folder, rules):
        super().__init__()
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.rules = rules
        self.log_buffer = []    # store logs to export later

    def write_log(self, text):
        self.log.emit(text)
        self.log_buffer.append(text)

    def export_log(self):
        try:
            path = os.path.join(self.output_folder, "encrypt_log.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(self.log_buffer))
            return path
        except:
            return None

    def run(self):
        try:
            if not os.path.exists(self.input_folder):
                self.write_log("⚠ Input folder does not exist.")
                self.finished.emit()
                return

            os.makedirs(self.output_folder, exist_ok=True)

            pdfs = [f for f in os.listdir(self.input_folder) if f.lower().endswith(".pdf")]
            if not pdfs:
                self.write_log("⚠ No PDF files found.")
                self.finished.emit()
                return

            total = len(pdfs)

            for i, filename in enumerate(pdfs, start=1):
                self.write_log(f"\n⏳ Processing: {filename}")

                matched_rule = None
                for rule in self.rules:
                    if rule_matches(rule["contains"], filename):
                        matched_rule = rule
                        break

                if not matched_rule:
                    self.write_log(f"⏭ Skipped (no match): {filename}")
                else:
                    pw = matched_rule["password"]
                    self.write_log(f"🔐 Rule matched → Password: {pw}")

                    try:
                        reader = PdfReader(os.path.join(self.input_folder, filename))
                        writer = PdfWriter()
                        for p in reader.pages:
                            writer.add_page(p)
                        writer.encrypt(pw)

                        out_path = os.path.join(self.output_folder, filename)
                        with open(out_path, "wb") as f:
                            writer.write(f)

                        self.write_log("✔ Encrypted successfully")
                    except Exception as e:
                        self.write_log(f"❌ ERROR encrypting {filename}: {e}")

                percent = int((i / total) * 100)
                self.progress.emit(percent)

            # write final log to file
            log_path = self.export_log()
            if log_path:
                self.write_log(f"\n📄 Log saved to: {log_path}")

            self.write_log("\n🎉 ALL FILES PROCESSED!")
            self.finished.emit()

        except Exception as e:
            self.write_log(f"❌ CRITICAL ERROR: {e}")
            self.finished.emit()
