"""
Evaluator — postorder evaluation of an expression tree.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Walks the tree in postorder, computes intermediate results,
and records each computation step for animated display.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Tuple

from core.tree_node import TreeNode


@dataclass
class EvalStep:
    """One computation performed during evaluation."""
    left_val: float
    right_val: float
    operator: str
    result: float
    description: str           # e.g. "3 + 4 = 7"
    node: Optional[TreeNode] = None


def _contains_symbolic_operand(node: TreeNode | None) -> bool:
    if node is None:
        return False
    if node.is_leaf():
        return node.value.isalpha()
    return _contains_symbolic_operand(node.left) or _contains_symbolic_operand(node.right)


def evaluate_tree(root: TreeNode | None) -> Tuple[Optional[float], List[EvalStep], Optional[str]]:
    """Evaluate the expression tree rooted at *root*.

    Returns:
        *(final_result, eval_steps, message)* — the numeric result, an ordered
        list of :class:`EvalStep` objects for step-by-step display, and an
        optional explanatory message when evaluation is not available.
    """
    if root is None:
        return None, [], None

    if _contains_symbolic_operand(root):
        return None, [], "Evaluation not available for symbolic expressions"

    steps: List[EvalStep] = []

    def _eval(node: TreeNode) -> float:
        # Leaf → return numeric value
        if node.is_leaf():
            return float(node.value)

        left_val = _eval(node.left)   # type: ignore[arg-type]
        right_val = _eval(node.right)  # type: ignore[arg-type]

        op = node.value
        if op == '+':
            result = left_val + right_val
        elif op == '-':
            result = left_val - right_val
        elif op == '*':
            result = left_val * right_val
        elif op == '/':
            result = left_val / right_val if right_val != 0 else float('inf')
        elif op == '^':
            result = left_val ** right_val
        else:
            result = 0.0

        # Format nicely
        def _fmt(v: float) -> str:
            return str(int(v)) if v == int(v) else f"{v:.4g}"

        desc = f"{_fmt(left_val)} {op} {_fmt(right_val)} = {_fmt(result)}"
        steps.append(EvalStep(
            left_val=left_val,
            right_val=right_val,
            operator=op,
            result=result,
            description=desc,
            node=node,
        ))
        return result

    final = _eval(root)
    return final, steps, None
