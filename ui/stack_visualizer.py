"""
Stack visualizer panel — animated stack + output queue display.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Shows the Shunting-Yard algorithm state: current token,
operator stack contents, and output queue.
"""

from __future__ import annotations
from typing import List

from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.config import COLORS, FONTS
from algorithms.shunting_yard import ShuntingYardStep


class _StackItem(QFrame):
    """A single item in the visual stack."""

    def __init__(self, text: str, color: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.setFixedHeight(36)
        self.setMinimumWidth(48)
        self.setStyleSheet(f"""
            background-color: {color};
            border-radius: 6px;
            margin: 2px;
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        lbl = QLabel(text)
        lbl.setFont(QFont(FONTS["mono"], FONTS["size_md"], QFont.Weight.Bold))
        lbl.setStyleSheet(f"color: {COLORS['text_primary']}; background: transparent;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl)


class StackVisualizer(QFrame):
    """Interactive panel showing the Shunting-Yard stack state."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("StackVisualizer")
        self._setup_ui()

    def _setup_ui(self) -> None:
        main = QVBoxLayout(self)
        main.setContentsMargins(16, 16, 16, 16)
        main.setSpacing(12)

        # Title
        title = QLabel("Stack Visualization")
        title.setFont(QFont(FONTS["family"], FONTS["size_lg"], QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['accent_violet']};")
        main.addWidget(title)

        # Current token
        self._token_label = QLabel("TOKEN: —")
        self._token_label.setFont(QFont(FONTS["mono"], FONTS["size_md"]))
        self._token_label.setStyleSheet(f"color: {COLORS['accent_cyan']};")
        main.addWidget(self._token_label)

        # Action description
        self._action_label = QLabel("")
        self._action_label.setFont(QFont(FONTS["family"], FONTS["size_sm"]))
        self._action_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        self._action_label.setWordWrap(True)
        main.addWidget(self._action_label)

        # Stack + Output side-by-side
        columns = QHBoxLayout()
        columns.setSpacing(16)

        # --- Stack column ---
        stack_col = QVBoxLayout()
        stack_title = QLabel("STACK")
        stack_title.setFont(QFont(FONTS["family"], FONTS["size_sm"], QFont.Weight.Bold))
        stack_title.setStyleSheet(f"color: {COLORS['accent_pink']};")
        stack_col.addWidget(stack_title)

        self._stack_container = QVBoxLayout()
        self._stack_container.setSpacing(2)
        self._stack_container.setAlignment(Qt.AlignmentFlag.AlignBottom)
        stack_frame = QFrame()
        stack_frame.setMinimumHeight(120)
        stack_frame.setStyleSheet(f"""
            background-color: {COLORS['bg_tertiary']};
            border-radius: 8px;
            border: 1px solid {COLORS['text_muted']};
        """)
        stack_frame.setLayout(self._stack_container)
        stack_col.addWidget(stack_frame, 1)
        columns.addLayout(stack_col)

        # --- Output column ---
        out_col = QVBoxLayout()
        out_title = QLabel("OUTPUT")
        out_title.setFont(QFont(FONTS["family"], FONTS["size_sm"], QFont.Weight.Bold))
        out_title.setStyleSheet(f"color: {COLORS['accent_green']};")
        out_col.addWidget(out_title)

        self._output_container = QVBoxLayout()
        self._output_container.setSpacing(2)
        self._output_container.setAlignment(Qt.AlignmentFlag.AlignTop)
        out_frame = QFrame()
        out_frame.setMinimumHeight(120)
        out_frame.setStyleSheet(f"""
            background-color: {COLORS['bg_tertiary']};
            border-radius: 8px;
            border: 1px solid {COLORS['text_muted']};
        """)
        out_frame.setLayout(self._output_container)
        out_col.addWidget(out_frame, 1)
        columns.addLayout(out_col)

        main.addLayout(columns, 1)

    # ── Public API ─────────────────────────────────────────────────

    def show_step(self, step: ShuntingYardStep) -> None:
        """Update the display to reflect *step*."""
        self._token_label.setText(f"TOKEN: {step.token}")
        self._action_label.setText(step.action)

        # Rebuild stack items (bottom → top, displayed top-down)
        self._clear_layout(self._stack_container)
        for val in reversed(step.stack_contents):
            self._stack_container.addWidget(_StackItem(val, COLORS["stack_item"]))

        # Rebuild output items
        self._clear_layout(self._output_container)
        for val in step.output_contents:
            self._output_container.addWidget(_StackItem(val, COLORS["output_item"]))

    def clear(self) -> None:
        """Reset the panel to its initial state."""
        self._token_label.setText("TOKEN: —")
        self._action_label.setText("")
        self._clear_layout(self._stack_container)
        self._clear_layout(self._output_container)

    # ── Helpers ────────────────────────────────────────────────────

    @staticmethod
    def _clear_layout(layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
