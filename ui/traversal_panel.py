"""
Traversal panel — traversal buttons, evaluation display, export.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Provides Inorder / Preorder / Postorder buttons, the evaluation
step log, and export actions.
"""

from __future__ import annotations
from pathlib import Path
from typing import List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.config import COLORS, FONTS
from core.evaluator import EvalStep
from core.traversal import TRAVERSAL_DESCRIPTIONS


class TraversalPanel(QFrame):
    """Controls for traversal, evaluation display, and export."""

    # Signals carry the traversal name
    traversal_requested = Signal(str)   # "inorder" | "preorder" | "postorder"
    export_png_requested = Signal()
    export_log_requested = Signal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("TraversalPanel")
        self._log_lines: List[str] = []
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # ── Conversion display ─────────────────────────────────────
        conv_title = QLabel("Expression Conversions")
        conv_title.setFont(QFont(FONTS["family"], FONTS["size_lg"], QFont.Weight.Bold))
        conv_title.setStyleSheet(f"color: {COLORS['accent_cyan']};")
        layout.addWidget(conv_title)

        self._infix_label = self._notation_label("INFIX")
        self._prefix_label = self._notation_label("PREFIX")
        self._postfix_label = self._notation_label("POSTFIX")
        layout.addWidget(self._infix_label)
        layout.addWidget(self._prefix_label)
        layout.addWidget(self._postfix_label)

        # ── Traversal buttons ──────────────────────────────────────
        trav_title = QLabel("Tree Traversals")
        trav_title.setFont(QFont(FONTS["family"], FONTS["size_lg"], QFont.Weight.Bold))
        trav_title.setStyleSheet(f"color: {COLORS['accent_violet']};")
        layout.addWidget(trav_title)

        trav_row = QHBoxLayout()
        trav_row.setSpacing(8)
        self._btn_inorder = self._make_button("Inorder", COLORS["accent_cyan"], text_color="#1a1b2e")
        self._btn_preorder = self._make_button("Preorder", COLORS["accent_violet"])
        self._btn_postorder = self._make_button("Postorder", COLORS["accent_pink"])
        trav_row.addWidget(self._btn_inorder)
        trav_row.addWidget(self._btn_preorder)
        trav_row.addWidget(self._btn_postorder)
        layout.addLayout(trav_row)

        # Traversal description
        self._trav_desc = QLabel("")
        self._trav_desc.setFont(QFont(FONTS["family"], FONTS["size_sm"]))
        self._trav_desc.setStyleSheet(f"color: {COLORS['text_secondary']};")
        self._trav_desc.setWordWrap(True)
        layout.addWidget(self._trav_desc)

        # ── Evaluation / step log ──────────────────────────────────
        eval_title = QLabel("Evaluation & Steps")
        eval_title.setFont(QFont(FONTS["family"], FONTS["size_lg"], QFont.Weight.Bold))
        eval_title.setStyleSheet(f"color: {COLORS['accent_green']};")
        layout.addWidget(eval_title)

        self._log_area = QTextEdit()
        self._log_area.setReadOnly(True)
        self._log_area.setFont(QFont(FONTS["mono"], FONTS["size_sm"]))
        self._log_area.setStyleSheet(f"""
            QTextEdit {{
                background-color: {COLORS['bg_tertiary']};
                color: {COLORS['text_primary']};
                border: 1px solid {COLORS['text_muted']};
                border-radius: 8px;
                padding: 8px;
            }}
        """)
        self._log_area.setMinimumHeight(100)
        layout.addWidget(self._log_area, 1)

        # Result label
        self._result_label = QLabel("")
        self._result_label.setFont(QFont(FONTS["mono"], FONTS["size_xl"], QFont.Weight.Bold))
        self._result_label.setStyleSheet(f"color: {COLORS['accent_green']};")
        self._result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._result_label)

        # ── Export buttons ─────────────────────────────────────────
        export_row = QHBoxLayout()
        export_row.setSpacing(8)
        self._btn_png = self._make_button("📷  Export PNG", COLORS["btn_secondary"])
        self._btn_log = self._make_button("📝  Export Log", COLORS["btn_secondary"])
        export_row.addWidget(self._btn_png)
        export_row.addWidget(self._btn_log)
        layout.addLayout(export_row)

    # ── Helpers ────────────────────────────────────────────────────

    def _notation_label(self, prefix: str) -> QLabel:
        lbl = QLabel(f"{prefix}:  —")
        lbl.setFont(QFont(FONTS["mono"], FONTS["size_md"]))
        lbl.setStyleSheet(f"""
            color: {COLORS['text_primary']};
            background-color: {COLORS['bg_tertiary']};
            border-radius: 6px;
            padding: 6px 12px;
        """)
        lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        return lbl

    def _make_button(self, text: str, bg: str, text_color: str | None = None) -> QPushButton:
        btn = QPushButton(text)
        btn.setFont(QFont(FONTS["family"], FONTS["size_sm"], QFont.Weight.DemiBold))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setMinimumHeight(34)
        tc = text_color or COLORS["text_primary"]
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {tc};
                border: none;
                border-radius: 8px;
                padding: 6px 14px;
            }}
            QPushButton:hover {{ background-color: {QColor(bg).lighter(120).name()}; }}
            QPushButton:pressed {{ background-color: {QColor(bg).darker(120).name()}; }}
        """)
        return btn

    def _connect_signals(self) -> None:
        self._btn_inorder.clicked.connect(lambda: self._request_traversal("inorder"))
        self._btn_preorder.clicked.connect(lambda: self._request_traversal("preorder"))
        self._btn_postorder.clicked.connect(lambda: self._request_traversal("postorder"))
        self._btn_png.clicked.connect(self.export_png_requested.emit)
        self._btn_log.clicked.connect(self._export_log)

    def _request_traversal(self, name: str) -> None:
        desc = TRAVERSAL_DESCRIPTIONS.get(name, "")
        self._trav_desc.setText(desc)
        self.traversal_requested.emit(name)

    def _export_log(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Explanation Log", "expression_log.txt", "Text Files (*.txt)"
        )
        if path:
            Path(path).write_text("\n".join(self._log_lines), encoding="utf-8")

    # ── Public API ─────────────────────────────────────────────────

    def set_notations(self, infix: str, prefix: str, postfix: str) -> None:
        self._infix_label.setText(f"INFIX:     {infix}")
        self._prefix_label.setText(f"PREFIX:    {prefix}")
        self._postfix_label.setText(f"POSTFIX:  {postfix}")

    def show_eval_steps(
        self,
        steps: List[EvalStep],
        result: Optional[float],
        message: Optional[str] = None,
    ) -> None:
        lines = [s.description for s in steps]
        if message:
            lines = [message]
        self._log_lines = list(lines)
        self._log_area.setPlainText("\n".join(lines))
        if result is not None:
            r = int(result) if result == int(result) else f"{result:.4g}"
            self._result_label.setStyleSheet(f"color: {COLORS['accent_green']};")
            self._result_label.setText(f"RESULT = {r}")
        elif message:
            self._result_label.setStyleSheet(f"color: {COLORS['accent_orange']};")
            self._result_label.setText(message)
        else:
            self._result_label.setStyleSheet(f"color: {COLORS['accent_green']};")
            self._result_label.setText("")

    def append_log(self, text: str) -> None:
        self._log_lines.append(text)
        self._log_area.append(text)

    def clear_log(self) -> None:
        self._log_lines.clear()
        self._log_area.clear()
        self._result_label.setText("")
        self._trav_desc.setText("")

    def clear_all(self) -> None:
        self._infix_label.setText("INFIX:  —")
        self._prefix_label.setText("PREFIX:  —")
        self._postfix_label.setText("POSTFIX:  —")
        self.clear_log()
