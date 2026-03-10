"""
TreeNode — fundamental building block of the expression tree.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Each node holds a *value* (operator or operand) and optional
left / right children.  Layout coordinates (x, y) are set later
by the tree-renderer.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TreeNode:
    """A single node in a binary expression tree.

    Attributes:
        value:  The operator symbol (``+``, ``-``, …) or numeric string.
        left:   Left child (``None`` for leaf nodes).
        right:  Right child (``None`` for leaf nodes).
        x:      Horizontal position assigned by the layout engine.
        y:      Vertical position assigned by the layout engine.
        uid:    Unique identifier used by the visualisation layer.
    """

    value: str
    left: Optional["TreeNode"] = None
    right: Optional["TreeNode"] = None
    x: float = 0.0
    y: float = 0.0
    uid: int = field(default_factory=lambda: id(object()))

    # ── Convenience helpers ────────────────────────────────────────

    def is_leaf(self) -> bool:
        """Return ``True`` when the node has no children (i.e. operand)."""
        return self.left is None and self.right is None

    def is_operator(self) -> bool:
        """Return ``True`` when *value* is one of the supported operators."""
        from app.config import OPERATORS  # deferred to avoid circular import
        return self.value in OPERATORS

    def __repr__(self) -> str:
        return f"TreeNode({self.value!r})"
