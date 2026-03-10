"""
Parser — validates a token stream for structural correctness.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Checks for balanced parentheses, consecutive operators, empty
sub-expressions, and unknown tokens.  Returns a list of human-
readable error messages (empty list ⇒ expression is valid).
"""

from __future__ import annotations
from typing import List

from core.tokenizer import Token, TokenType


OPERAND_TOKENS = (TokenType.NUMBER, TokenType.VARIABLE)


def validate_tokens(tokens: List[Token]) -> List[str]:
    """Validate *tokens* and return a list of error strings.

    An empty list means the expression is syntactically correct.
    """
    errors: List[str] = []
    if not tokens:
        errors.append("Expression is empty.")
        return errors

    # ── Check for unknown tokens ───────────────────────────────────
    for t in tokens:
        if t.token_type == TokenType.UNKNOWN:
            errors.append(f"Unrecognised character '{t.value}' at position {t.position}.")

    # ── Balanced parentheses ───────────────────────────────────────
    depth = 0
    for t in tokens:
        if t.token_type == TokenType.LPAREN:
            depth += 1
        elif t.token_type == TokenType.RPAREN:
            depth -= 1
        if depth < 0:
            errors.append(f"Unexpected ')' at position {t.position}.")
            break
    if depth > 0:
        errors.append("Unmatched '(' — missing closing parenthesis.")

    # ── Structural checks (consecutive operators, etc.) ────────────
    prev: Token | None = None
    for t in tokens:
        if prev is not None:
            # Two operators in a row
            if prev.token_type == TokenType.OPERATOR and t.token_type == TokenType.OPERATOR:
                errors.append(
                    f"Consecutive operators '{prev.value}' and '{t.value}' "
                    f"at positions {prev.position}–{t.position}."
                )
            # Operator immediately after '('
            if prev.token_type == TokenType.LPAREN and t.token_type == TokenType.OPERATOR:
                errors.append(
                    f"Operator '{t.value}' immediately after '(' at position {t.position}."
                )
            # Operand/RPAREN immediately followed by LPAREN/operand (implicit multiply not supported)
            if (prev.token_type in (*OPERAND_TOKENS, TokenType.RPAREN)
                    and t.token_type in (*OPERAND_TOKENS, TokenType.LPAREN)):
                errors.append(
                    f"Missing operator between '{prev.value}' and '{t.value}' "
                    f"at positions {prev.position}–{t.position}."
                )
            # Empty parens ()
            if prev.token_type == TokenType.LPAREN and t.token_type == TokenType.RPAREN:
                errors.append(f"Empty parentheses at position {prev.position}.")

        prev = t

    # Expression must not start/end with an operator (unless unary minus already consumed)
    first, last = tokens[0], tokens[-1]
    if first.token_type == TokenType.OPERATOR:
        errors.append(f"Expression starts with operator '{first.value}'.")
    if last.token_type == TokenType.OPERATOR:
        errors.append(f"Expression ends with operator '{last.value}'.")

    return errors
