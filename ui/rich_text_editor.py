# ui/rich_text_editor.py
from PySide6.QtWidgets import (
    QWidget, QTextEdit, QToolBar, QVBoxLayout, QComboBox, QColorDialog
)
from PySide6.QtGui import QTextCursor, QTextCharFormat, QFont, QColor, QAction
from PySide6.QtCore import Qt


class RichTextEditor(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # --------------------------
        # Toolbar
        # --------------------------
        self.toolbar = QToolBar()

        # Bold
        self.bold_action = QAction("B", self)
        self.bold_action.setCheckable(True)
        self.bold_action.triggered.connect(self.toggle_bold)
        self.toolbar.addAction(self.bold_action)

        # Italic
        self.italic_action = QAction("I", self)
        self.italic_action.setCheckable(True)
        self.italic_action.triggered.connect(self.toggle_italic)
        self.toolbar.addAction(self.italic_action)

        # Underline
        self.underline_action = QAction("U", self)
        self.underline_action.setCheckable(True)
        self.underline_action.triggered.connect(self.toggle_underline)
        self.toolbar.addAction(self.underline_action)

        # --------------------------
        # FONT SIZE DROPDOWN
        # --------------------------
        self.font_sizes = QComboBox()
        self.font_sizes.setFixedWidth(70)
        self.font_sizes.addItems(["8", "9", "10", "11", "12", "14", "16", "18", "20", "24"])
        self.font_sizes.setCurrentText("12")
        self.font_sizes.currentIndexChanged.connect(self.change_font_size)
        self.toolbar.addWidget(self.font_sizes)

        # --------------------------
        # FONT COLOR
        # --------------------------
        self.color_action = QAction("A▼", self)
        self.color_action.triggered.connect(self.change_text_color)
        self.toolbar.addAction(self.color_action)

        # --------------------------
        # HIGHLIGHT COLOR
        # --------------------------
        self.highlight_action = QAction("🖍", self)
        self.highlight_action.triggered.connect(self.change_highlight_color)
        self.toolbar.addAction(self.highlight_action)

        # --------------------------
        # Editor
        # --------------------------
        self.editor = QTextEdit()
        self.editor.setAcceptRichText(True)
        self.editor.selectionChanged.connect(self.sync_toolbar_state)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.editor)

    # =====================================================================
    # Formatting Helpers
    # =====================================================================
    def apply_format(self, callback):
        cursor = self.editor.textCursor()
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)

        fmt = QTextCharFormat()
        callback(fmt)
        cursor.mergeCharFormat(fmt)

    # =====================================================================
    # Basic Styles
    # =====================================================================
    def toggle_bold(self):
        def apply(fmt):
            fmt.setFontWeight(QFont.Bold if self.bold_action.isChecked() else QFont.Normal)
        self.apply_format(apply)

    def toggle_italic(self):
        def apply(fmt):
            fmt.setFontItalic(self.italic_action.isChecked())
        self.apply_format(apply)

    def toggle_underline(self):
        def apply(fmt):
            fmt.setFontUnderline(self.underline_action.isChecked())
        self.apply_format(apply)

    # =====================================================================
    # FONT SIZE
    # =====================================================================
    def change_font_size(self):
        size = int(self.font_sizes.currentText())

        def apply(fmt):
            fmt.setFontPointSize(size)

        self.apply_format(apply)

    # =====================================================================
    # TEXT COLOR PICKER
    # =====================================================================
    def change_text_color(self):
        color = QColorDialog.getColor(QColor("black"), self, "Select Text Color")
        if not color.isValid():
            return

        def apply(fmt):
            fmt.setForeground(color)

        self.apply_format(apply)

    # =====================================================================
    # HIGHLIGHT COLOR PICKER
    # =====================================================================
    def change_highlight_color(self):
        color = QColorDialog.getColor(QColor("yellow"), self, "Select Highlight Color")
        if not color.isValid():
            return

        def apply(fmt):
            fmt.setBackground(color)

        self.apply_format(apply)

    # =====================================================================
    # Sync toolbar state with selected text
    # =====================================================================
    def sync_toolbar_state(self):
        cursor = self.editor.textCursor()
        fmt = cursor.charFormat()

        self.bold_action.setChecked(fmt.fontWeight() == QFont.Bold)
        self.italic_action.setChecked(fmt.fontItalic())
        self.underline_action.setChecked(fmt.fontUnderline())

        if fmt.fontPointSize() > 0:
            self.font_sizes.setCurrentText(str(int(fmt.fontPointSize())))

    # =====================================================================
    # HTML Output (Outlook-friendly)
    # =====================================================================
    def get_raw_html(self):
        return self.editor.toHtml()

    def get_outlook_html(self):
        """Wrap HTML in Outlook-friendly Calibri template."""
        html = self.editor.toHtml()

        return f"""
        <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
            <style>
                body, p, span {{
                    font-family: Calibri, Arial, sans-serif !important;
                }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
