"""
Tree renderer — computes layout coordinates and draws onto QGraphicsScene.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Uses a simple recursive algorithm to assign (x, y) positions to each
node, then creates circle items, text labels, and edge lines.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QPen, QPainterPath
from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsDropShadowEffect,
    QGraphicsItem,
    QGraphicsPathItem,
)

from app.config import COLORS, FONTS, TREE_LAYOUT
from core.tree_node import TreeNode


# ── Layout computation ─────────────────────────────────────────────

def compute_layout(
    root: Optional[TreeNode],
    x: float = 0,
    y: float = 0,
    h_gap: float | None = None,
    depth: int = 0,
) -> None:
    """Assign *x* / *y* coordinates to every node in the tree.

    Uses a simple recursive approach: each child is offset by
    ``h_gap / 2^depth`` horizontally and ``v_spacing`` vertically.
    """
    if root is None:
        return

    if h_gap is None:
        # Calculate initial gap based on tree height
        height = _tree_height(root)
        h_gap = TREE_LAYOUT["h_spacing"] * (2 ** (height - 1))

    root.x = x
    root.y = y

    v_gap = TREE_LAYOUT["v_spacing"]
    child_h_gap = h_gap / 2

    if root.left:
        compute_layout(root.left, x - child_h_gap, y + v_gap, child_h_gap, depth + 1)
    if root.right:
        compute_layout(root.right, x + child_h_gap, y + v_gap, child_h_gap, depth + 1)


def _tree_height(node: Optional[TreeNode]) -> int:
    """Return the height of the sub-tree rooted at *node*."""
    if node is None:
        return 0
    return 1 + max(_tree_height(node.left), _tree_height(node.right))


# ── Scene drawing ──────────────────────────────────────────────────

class RenderedNode:
    """Groups the QGraphicsItems that belong to one tree node."""
    __slots__ = ("tree_node", "circle", "label", "edge_to_parent")

    def __init__(
        self,
        tree_node: TreeNode,
        circle: QGraphicsEllipseItem,
        label: QGraphicsSimpleTextItem,
        edge_to_parent: Optional[QGraphicsLineItem] = None,
    ):
        self.tree_node = tree_node
        self.circle = circle
        self.label = label
        self.edge_to_parent = edge_to_parent


def render_tree(
    scene: QGraphicsScene,
    root: Optional[TreeNode],
) -> Dict[int, RenderedNode]:
    """Draw the expression tree onto *scene*.

    Returns:
        A mapping from ``TreeNode.uid`` → :class:`RenderedNode` so
        that the animation controller can manipulate individual nodes.
    """
    scene.clear()
    if root is None:
        return {}

    compute_layout(root)
    node_map: Dict[int, RenderedNode] = {}
    _draw_subtree(scene, root, None, node_map)
    return node_map


def _draw_subtree(
    scene: QGraphicsScene,
    node: TreeNode,
    parent: Optional[TreeNode],
    node_map: Dict[int, RenderedNode],
) -> None:
    """Recursively draw *node* and its children."""
    r = TREE_LAYOUT["node_radius"]

    # ── Edge to parent ─────────────────────────────────────────────
    edge: Optional[QGraphicsLineItem] = None
    if parent is not None:
        pen = QPen(QColor(COLORS["edge_color"]), 2.5)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        edge = scene.addLine(parent.x, parent.y, node.x, node.y, pen)
        edge.setZValue(0)

    # ── Circle node ────────────────────────────────────────────────
    color = COLORS["node_operator"] if node.is_operator() else COLORS["node_operand"]
    brush = QBrush(QColor(color))
    pen = QPen(QColor(color).lighter(130), 2)
    circle = scene.addEllipse(node.x - r, node.y - r, 2 * r, 2 * r, pen, brush)
    circle.setZValue(1)

    # Drop-shadow
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(18)
    shadow.setOffset(0, 4)
    shadow.setColor(QColor(0, 0, 0, 120))
    circle.setGraphicsEffect(shadow)

    # ── Label ──────────────────────────────────────────────────────
    font = QFont(FONTS["family"], FONTS["size_md"])
    font.setBold(True)
    label = scene.addSimpleText(node.value, font)
    label.setBrush(QBrush(QColor(COLORS["node_text"])))

    # Centre the label inside the circle
    br = label.boundingRect()
    label.setPos(node.x - br.width() / 2, node.y - br.height() / 2)
    label.setZValue(2)

    # Tooltip
    tip = f"{'Operator' if node.is_operator() else 'Operand'}: {node.value}"
    circle.setToolTip(tip)
    label.setToolTip(tip)

    node_map[node.uid] = RenderedNode(node, circle, label, edge)

    # ── Recurse ────────────────────────────────────────────────────
    if node.left:
        _draw_subtree(scene, node.left, node, node_map)
    if node.right:
        _draw_subtree(scene, node.right, node, node_map)
