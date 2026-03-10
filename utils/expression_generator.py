"""
Expression generator — random valid expression strings.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Produces well-formed, fully-parenthesised expressions of
configurable depth for the "Random Example" button.
"""

from __future__ import annotations
import random
from typing import List


_OPERATORS = ['+', '-', '*', '/']
_DIGITS = list(range(1, 10))  # 1-9 to keep expressions readable


def _random_expr(depth: int) -> str:
    """Recursively build a random expression up to *depth* levels."""
    if depth <= 0 or random.random() < 0.35:
        return str(random.choice(_DIGITS))

    left = _random_expr(depth - 1)
    right = _random_expr(depth - 1)
    op = random.choice(_OPERATORS)
    return f"({left}{op}{right})"


def generate_random_expression(max_depth: int = 3) -> str:
    """Return a random valid infix expression string.

    Parameters:
        max_depth: Maximum nesting depth (default 3).

    Returns:
        A fully-parenthesised expression such as ``((2+7)*(8-3))``.
    """
    # Ensure at least one operator
    expr = _random_expr(max_depth)
    # If we got a bare number, wrap it
    if expr.isdigit():
        right = str(random.choice(_DIGITS))
        op = random.choice(_OPERATORS)
        expr = f"({expr}{op}{right})"
    return expr


# ── Curated examples ──────────────────────────────────────────────

EXAMPLE_EXPRESSIONS: List[str] = [
    "((3+4)/(9-2))",
    "(A+B)",
    "x*(y+z)",
    "((a+4)/(b-2))",
    "(7+(3*(5-2)))",
    "((8/2)+(3*4))",
    "((2+7)*(8-3))",
    "(4*(6+(3-1)))",
    "((5^2)-(3*4))",
    "((1+2)*(3+4))",
    "(9/(3*(2-1)))",
]
