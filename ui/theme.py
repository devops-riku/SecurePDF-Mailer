# ui/theme.py

def apply_modern_theme(window):
    window.setStyleSheet("""
        QWidget {
            background: #0F1015;
            color: #E8EAED;
            font-family: 'Segoe UI', sans-serif;
            font-size: 13px;
        }

        /* QLineEdit */
        QLineEdit {
            background: #15171C;
            border: 1px solid #2A2D35;
            border-radius: 6px;
            padding: 8px 12px;
        }
        QLineEdit:focus {
            border: 1px solid #3B82F6;
        }

        /* QTextEdit */
        QTextEdit {
            background: #15171C;
            border: 1px solid #2A2D35;
            border-radius: 6px;
            padding: 10px;
            font-family: Consolas, monospace;
            font-size: 12px;
        }

        /* Buttons */
        QPushButton {
            background: #25272F;
            border: 1px solid #2F3138;
            padding: 8px 14px;
            border-radius: 6px;
        }
        QPushButton:hover {
            background: #2E3038;
        }

        /* Blue CTA Button */
        #startButton {
            background: #3B82F6;
            border: none;
            color: white;
            font-weight: 600;
            font-size: 14px;
            padding: 10px 20px;
        }
        #startButton:hover {
            background: #4C8CFF;
        }

        /* Delete buttons in tables */
        #deleteButton {
            background: transparent;
            border: none;
            padding: 0px;
            margin: 0px;
            color: #FF5F80;
            font-size: 16px;
            font-weight: bold;
        }
        #deleteButton:hover {
            color: #FF80A0;
            background: transparent;
        }

        /* Table cell editor */
        QTableWidget QLineEdit {
            background: #1A1C22;
            border: 1px solid #2A2D35;
            border-radius: 0px;
            padding: 4px 6px;
            color: #E8EAED;
        }
        QTableWidget QLineEdit:focus {
            border: 1px solid #3A3D45;
        }

        /* Tabs */
        QTabWidget::pane {
            border: 1px solid #2A2D35;
            background: #1A1C23;
            border-radius: 6px;
        }
        QTabBar::tab {
            background: #1A1C23;
            padding: 8px 16px;
            border: 1px solid #2A2D35;
        }
        QTabBar::tab:selected {
            background: #25272F;
        }
        QTabBar::tab:hover {
            background: #2E3038;
        }
    """)
