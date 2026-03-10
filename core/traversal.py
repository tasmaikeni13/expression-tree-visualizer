"""
Tree traversal algorithms — inorder, preorder, postorder.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Each function returns the ordered list of visited
:class:`TreeNode` objects (for highlighting in the UI).
"""

from __future__ import annotations
from typing import List

from core.tree_node import TreeNode


def inorder(root: TreeNode | None) -> List[TreeNode]:
    """Left → Root → Right (produces infix expression)."""
    result: List[TreeNode] = []

    def _walk(node: TreeNode | None) -> None:
        if node is None:
            return
        _walk(node.left)
        result.append(node)
        _walk(node.right)

    _walk(root)
    return result


def preorder(root: TreeNode | None) -> List[TreeNode]:
    """Root → Left → Right (produces prefix expression)."""
    result: List[TreeNode] = []

    def _walk(node: TreeNode | None) -> None:
        if node is None:
            return
        result.append(node)
        _walk(node.left)
        _walk(node.right)

    _walk(root)
    return result


def postorder(root: TreeNode | None) -> List[TreeNode]:
    """Left → Right → Root (produces postfix expression)."""
    result: List[TreeNode] = []

    def _walk(node: TreeNode | None) -> None:
        if node is None:
            return
        _walk(node.left)
        _walk(node.right)
        result.append(node)

    _walk(root)
    return result


# ── Traversal descriptions (for the educational panel) ────────────

TRAVERSAL_DESCRIPTIONS = {
    "inorder": (
        "In Inorder traversal we visit:\n"
        "  left subtree → root → right subtree.\n"
        "This produces the original infix expression (with implicit parentheses)."
    ),
    "preorder": (
        "In Preorder traversal we visit:\n"
        "  root → left subtree → right subtree.\n"
        "This produces the prefix (Polish) notation."
    ),
    "postorder": (
        "In Postorder traversal we visit:\n"
        "  left subtree → right subtree → root.\n"
        "This produces the postfix (Reverse-Polish) notation."
    ),
}
