"""
Tree canvas — QGraphicsView for interactive tree visualisation.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Supports zoom, pan, node highlighting, and animated tree growth.
"""

from __future__ import annotations
from typing import Dict, List, Optional

from PySide6.QtCore import (
    QPoint,
    QRectF,
    Qt,
    QTimer,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainter,
    QPen,
    QMouseEvent,
    QWheelEvent,
)
from PySide6.QtWidgets import (
    QFileDialog,
    QFrame,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from app.config import COLORS, FONTS, TREE_LAYOUT, ANIMATION
from core.tree_node import TreeNode
from visualization.tree_renderer import RenderedNode, render_tree


class _TreeGraphicsView(QGraphicsView):
    """Graphics view with explicit zoom and drag-to-pan controls."""

    def __init__(self, scene: QGraphicsScene, parent: QWidget | None = None):
        super().__init__(scene, parent)
        self._is_panning = False
        self._last_pan_pos = QPoint()
        self.setCursor(Qt.CursorShape.OpenHandCursor)

    def wheelEvent(self, event: QWheelEvent) -> None:
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(factor, factor)
        event.accept()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_panning = True
            self._last_pan_pos = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._is_panning:
            delta = event.position().toPoint() - self._last_pan_pos
            self._last_pan_pos = event.position().toPoint()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._is_panning:
            self._is_panning = False
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)


class TreeCanvas(QFrame):
    """Interactive tree-view area with zoom/pan support.

    The widget wraps a ``QGraphicsScene``/``QGraphicsView`` pair
    and exposes helpers for highlighting nodes during traversals
    and evaluations.
    """

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("TreeCanvas")
        self._node_map: Dict[int, RenderedNode] = {}
        self._root: Optional[TreeNode] = None
        self._setup_ui()

    # ── UI Construction ────────────────────────────────────────────

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Title bar
        title_bar = QHBoxLayout()
        title_bar.setContentsMargins(16, 12, 16, 8)
        title = QLabel("Expression Tree")
        title.setFont(QFont(FONTS["family"], FONTS["size_lg"], QFont.Weight.Bold))
        title.setStyleSheet(f"color: {COLORS['accent_cyan']};")
        title_bar.addWidget(title)
        title_bar.addStretch()

        # Zoom hint
        hint = QLabel("Scroll to zoom  •  Drag to pan")
        hint.setFont(QFont(FONTS["family"], FONTS["size_sm"]))
        hint.setStyleSheet(f"color: {COLORS['text_muted']};")
        title_bar.addWidget(hint)

        layout.addLayout(title_bar)

        # Graphics view
        self._scene = QGraphicsScene(self)
        self._view = _TreeGraphicsView(self._scene, self)
        self._view.setRenderHints(
            QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform
        )
        self._view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self._view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self._view.setStyleSheet(f"""
            QGraphicsView {{
                background-color: {COLORS['bg_primary']};
                border: none;
                border-radius: 12px;
            }}
        """)
        self._view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(self._view, 1)

    # ── Public API ─────────────────────────────────────────────────

    def display_tree(self, root: Optional[TreeNode]) -> None:
        """Render *root* onto the canvas."""
        self._root = root
        self._node_map = render_tree(self._scene, root)
        if root is not None:
            # Fit scene in view with some padding
            self._view.resetTransform()
            rect = self._scene.itemsBoundingRect()
            rect.adjust(-60, -60, 60, 60)
            self._scene.setSceneRect(rect)
            self._view.fitInView(rect, Qt.AspectRatioMode.KeepAspectRatio)

    def highlight_nodes(self, nodes: List[TreeNode], color: str = COLORS["node_highlight"]) -> None:
        """Sequentially highlight *nodes* with a timer-based animation."""
        self.reset_highlights()
        delay = ANIMATION["highlight_ms"]

        for i, node in enumerate(nodes):
            QTimer.singleShot(i * delay, lambda n=node, c=color: self._highlight_one(n, c))

        # Reset highlights after the last one
        QTimer.singleShot(len(nodes) * delay + 600, self.reset_highlights)

    def highlight_node_instant(self, node: TreeNode, color: str) -> None:
        """Immediately change the colour of a single node."""
        self._highlight_one(node, color)

    def reset_highlights(self) -> None:
        """Restore all nodes to their default colour."""
        for rn in self._node_map.values():
            default = (
                COLORS["node_operator"] if rn.tree_node.is_operator()
                else COLORS["node_operand"]
            )
            rn.circle.setBrush(QBrush(QColor(default)))
            pen = QPen(QColor(default).lighter(130), 2)
            rn.circle.setPen(pen)

    def clear(self) -> None:
        """Remove all items from the scene."""
        self._scene.clear()
        self._node_map.clear()
        self._root = None

    def export_png(self) -> None:
        """Export the current scene to a PNG file."""
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Tree as PNG", "expression_tree.png", "PNG Images (*.png)"
        )
        if not path:
            return

        from PySide6.QtGui import QImage, QPainter as _P

        rect = self._scene.itemsBoundingRect()
        rect.adjust(-30, -30, 30, 30)
        image = QImage(int(rect.width()), int(rect.height()), QImage.Format.Format_ARGB32)
        image.fill(QColor(COLORS["bg_primary"]))
        painter = _P(image)
        painter.setRenderHints(_P.RenderHint.Antialiasing | _P.RenderHint.SmoothPixmapTransform)
        self._scene.render(painter, QRectF(image.rect()), rect)
        painter.end()
        image.save(path)

    @property
    def node_map(self) -> Dict[int, RenderedNode]:
        return self._node_map

    @property
    def scene(self) -> QGraphicsScene:
        return self._scene

    # ── Internal ──────────────────────────────────────────────────

    def _highlight_one(self, node: TreeNode, color: str) -> None:
        rn = self._node_map.get(node.uid)
        if rn is None:
            return
        rn.circle.setBrush(QBrush(QColor(color)))
        pen = QPen(QColor(color).lighter(150), 3)
        rn.circle.setPen(pen)
