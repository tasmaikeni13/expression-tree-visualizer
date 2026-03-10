"""
Expression input panel — text field, buttons, and validation feedback.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Contains the input field with placeholder text, validation error display,
and action buttons (Build, Animate, Clear, Random Example).
"""

from __future__ import annotations
import random
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.config import COLORS, FONTS
from utils.expression_generator import generate_random_expression, EXAMPLE_EXPRESSIONS
from utils.validators import validate_expression


class ExpressionInput(QFrame):
    """Panel for entering and validating mathematical expressions.

    Signals:
        build_requested(str): Emitted when the user clicks **Build**.
        animate_requested(str): Emitted when the user clicks **Animate**.
        clear_requested(): Emitted when the user clicks **Clear**.
    """

    build_requested = Signal(str)
    animate_requested = Signal(str)
    clear_requested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("ExpressionInput")
        self._setup_ui()
        self._connect_signals()

    # ── UI Construction ────────────────────────────────────────────

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Title
        title = QLabel("Expression Input")
        title.setFont(QFont(FONTS["family"], FONTS["size_lg"], QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['accent_cyan']};")
        layout.addWidget(title)

        # Input field
        self._input = QLineEdit()
        self._input.setPlaceholderText("Enter expression: (3+4) or (A+B)")
        self._input.setFont(QFont(FONTS["mono"], FONTS["size_lg"]))
        self._input.setMinimumHeight(44)
        self._input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
                border: 2px solid {COLORS['text_muted']};
                border-radius: 10px;
                padding: 8px 14px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['accent_cyan']};
            }}
        """)
        layout.addWidget(self._input)

        # Validation label
        self._error_label = QLabel("")
        self._error_label.setFont(QFont(FONTS["family"], FONTS["size_sm"]))
        self._error_label.setStyleSheet(f"color: {COLORS['accent_red']}; padding-left: 4px;")
        self._error_label.setWordWrap(True)
        self._error_label.hide()
        layout.addWidget(self._error_label)

        # Preview label
        self._preview_label = QLabel("")
        self._preview_label.setFont(QFont(FONTS["mono"], FONTS["size_sm"]))
        self._preview_label.setStyleSheet(f"color: {COLORS['text_secondary']}; padding-left: 4px;")
        layout.addWidget(self._preview_label)

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        self._btn_build = self._make_button("⚡  Build Expression Tree", COLORS["btn_primary"])
        self._btn_animate = self._make_button("▶  Step-by-Step Animation", COLORS["accent_green"], text_color="#1a1b2e")
        self._btn_clear = self._make_button("✕  Clear", COLORS["btn_secondary"])
        self._btn_random = self._make_button("🎲  Random Example", COLORS["accent_orange"], text_color="#1a1b2e")

        btn_row.addWidget(self._btn_build)
        btn_row.addWidget(self._btn_animate)
        btn_row.addWidget(self._btn_clear)
        btn_row.addWidget(self._btn_random)
        layout.addLayout(btn_row)

    def _make_button(self, text: str, bg: str, text_color: str | None = None) -> QPushButton:
        btn = QPushButton(text)
        btn.setFont(QFont(FONTS["family"], FONTS["size_sm"], QFont.Weight.DemiBold))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setMinimumHeight(38)
        tc = text_color or COLORS["text_primary"]
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {tc};
                border: none;
                border-radius: 8px;
                padding: 6px 16px;
            }}
            QPushButton:hover {{
                background-color: {QColor(bg).lighter(120).name()};
            }}
            QPushButton:pressed {{
                background-color: {QColor(bg).darker(120).name()};
            }}
        """)
        return btn

    # ── Signal wiring ──────────────────────────────────────────────

    def _connect_signals(self) -> None:
        self._input.textChanged.connect(self._on_text_changed)
        self._btn_build.clicked.connect(self._on_build)
        self._btn_animate.clicked.connect(self._on_animate)
        self._btn_clear.clicked.connect(self._on_clear)
        self._btn_random.clicked.connect(self._on_random)

    # ── Slots ──────────────────────────────────────────────────────

    def _on_text_changed(self, text: str) -> None:
        """Real-time preview and validation as the user types."""
        if not text.strip():
            self._error_label.hide()
            self._preview_label.setText("")
            return

        err = validate_expression(text)
        if err:
            self._error_label.setText(f"⚠  {err}")
            self._error_label.show()
            self._preview_label.setText("")
        else:
            self._error_label.hide()
            self._preview_label.setText(f"Preview: {text.strip()}")

    def _on_build(self) -> None:
        text = self._input.text().strip()
        err = validate_expression(text)
        if err:
            self._error_label.setText(f"⚠  {err}")
            self._error_label.show()
            return
        self.build_requested.emit(text)

    def _on_animate(self) -> None:
        text = self._input.text().strip()
        err = validate_expression(text)
        if err:
            self._error_label.setText(f"⚠  {err}")
            self._error_label.show()
            return
        self.animate_requested.emit(text)

    def _on_clear(self) -> None:
        self._input.clear()
        self._error_label.hide()
        self._preview_label.setText("")
        self.clear_requested.emit()

    def _on_random(self) -> None:
        # Mix between curated and generated
        if random.random() < 0.5 and EXAMPLE_EXPRESSIONS:
            expr = random.choice(EXAMPLE_EXPRESSIONS)
        else:
            expr = generate_random_expression()
        self._input.setText(expr)

    # ── Public helpers ─────────────────────────────────────────────

    def get_expression(self) -> str:
        return self._input.text().strip()

    def set_expression(self, expr: str) -> None:
        self._input.setText(expr)
