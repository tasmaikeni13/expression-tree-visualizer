"""
Infix → Postfix conversion.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Thin wrapper around :func:`algorithms.shunting_yard.shunting_yard`
that also accepts raw expression strings.
"""

from __future__ import annotations
from typing import List, Tuple

from algorithms.shunting_yard import ShuntingYardStep, shunting_yard
from core.tokenizer import Token, tokenize


def infix_to_postfix_tokens(tokens: List[Token]) -> Tuple[List[str], List[ShuntingYardStep]]:
    """Convert validated *tokens* to postfix form.

    Returns:
        (postfix token strings, algorithm steps)
    """
    return shunting_yard(tokens)


def infix_to_postfix(expression: str) -> Tuple[List[str], List[ShuntingYardStep]]:
    """Convenience: tokenise *expression* then convert to postfix."""
    tokens = tokenize(expression)
    return infix_to_postfix_tokens(tokens)
