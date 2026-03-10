"""
Expression-tree construction from postfix tokens.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Walks the postfix list, pushing operand nodes and combining
operator nodes, producing an animated step list for the UI.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from algorithms.stack import Stack
from app.config import OPERATORS
from core.tree_node import TreeNode


# ── Build-step record for animation ──────────────────────────────

@dataclass
class TreeBuildStep:
    """Snapshot of tree-building state after processing one postfix token."""
    token: str
    action: str
    node: Optional[TreeNode] = None
    stack_size: int = 0


def build_expression_tree(postfix: List[str]) -> Tuple[Optional[TreeNode], List[TreeBuildStep]]:
    """Build a binary expression tree from *postfix* tokens.

    Parameters:
        postfix: List of token strings in postfix order.

    Returns:
        *(root_node, build_steps)* — the root of the tree and a list
        of :class:`TreeBuildStep` objects for animation.
    """
    node_stack: Stack[TreeNode] = Stack()
    steps: List[TreeBuildStep] = []

    for token in postfix:
        if token in OPERATORS:
            # ── Operator: pop two children, create internal node ──
            right = node_stack.pop() if node_stack else TreeNode("?")
            left = node_stack.pop() if node_stack else TreeNode("?")
            node = TreeNode(value=token, left=left, right=right)
            node_stack.push(node)
            steps.append(TreeBuildStep(
                token=token,
                action=f"Create node '{token}' with left={left.value} and right={right.value}",
                node=node,
                stack_size=node_stack.size(),
            ))
        else:
            # ── Operand: push leaf node ───────────────────────────
            node = TreeNode(value=token)
            node_stack.push(node)
            steps.append(TreeBuildStep(
                token=token,
                action=f"Push operand node '{token}' onto stack",
                node=node,
                stack_size=node_stack.size(),
            ))

    root = node_stack.pop() if node_stack else None
    return root, steps
