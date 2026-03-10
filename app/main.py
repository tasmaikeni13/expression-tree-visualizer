"""
Application entry point — creates the QApplication, applies the
global dark stylesheet, and shows the main window.
"""

from __future__ import annotations
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from app.config import COLORS, FONTS


# ── Global stylesheet ─────────────────────────────────────────────

_GLOBAL_STYLESHEET = f"""
/* ── Base ────────────────────────────────────────────────── */
QWidget {{
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
    font-family: {FONTS['family']};
    font-size: {FONTS['size_md']}px;
}}

/* ── Scroll bars ─────────────────────────────────────────── */
QScrollBar:vertical {{
    background: {COLORS['bg_secondary']};
    width: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: {COLORS['text_muted']};
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
QScrollBar:horizontal {{
    background: {COLORS['bg_secondary']};
    height: 8px;
    border-radius: 4px;
}}
QScrollBar::handle:horizontal {{
    background: {COLORS['text_muted']};
    border-radius: 4px;
    min-width: 30px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* ── Tooltips ────────────────────────────────────────────── */
QToolTip {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['accent_cyan']};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: {FONTS['size_sm']}px;
}}

/* ── Splitter ────────────────────────────────────────────── */
QSplitter::handle {{
    background: {COLORS['text_muted']};
}}
"""


def launch() -> None:
    """Create the application, apply styling, and enter the event loop."""
    app = QApplication(sys.argv)

    # Apply global stylesheet
    app.setStyleSheet(_GLOBAL_STYLESHEET)

    # Set default font
    font = QFont(FONTS["family"], FONTS["size_md"])
    app.setFont(font)

    # Create and show main window
    from ui.main_window import MainWindow  # deferred to avoid circular imports

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
