"""
Validators — expression validation utilities.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Re-exports the core parser validation and adds a high-level
``validate_expression`` helper that returns a single error string
or ``None`` on success.
"""

from __future__ import annotations
from typing import Optional

from core.tokenizer import tokenize
from core.parser import validate_tokens


ALLOWED_CHARACTERS = set(
    "0123456789"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "+-*/^()."
)


def validate_expression(expression: str) -> Optional[str]:
    """Validate *expression* and return an error message or ``None``.

    This is the single entry-point for the UI to check user input.
    """
    expr = expression.strip()
    if not expr:
        return "Expression cannot be empty."

    invalid_char = next((ch for ch in expr if not ch.isspace() and ch not in ALLOWED_CHARACTERS), None)
    if invalid_char is not None:
        return f"Unrecognised character '{invalid_char}' in expression."

    tokens = tokenize(expr)
    errors = validate_tokens(tokens)
    if errors:
        return errors[0]  # return the first error for simplicity

    return None
