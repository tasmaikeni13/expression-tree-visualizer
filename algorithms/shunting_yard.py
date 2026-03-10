"""
Shunting-Yard algorithm — infix → postfix conversion.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Implements Edsger Dijkstra's algorithm and emits granular
``Step`` records that the UI can replay as an animation.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List

from algorithms.stack import Stack
from app.config import PRECEDENCE, RIGHT_ASSOCIATIVE, OPERATORS
from core.tokenizer import Token, TokenType


OPERAND_TOKENS = (TokenType.NUMBER, TokenType.VARIABLE)


# ── Step record for animation ─────────────────────────────────────

@dataclass
class ShuntingYardStep:
    """Snapshot of the algorithm state after processing one token."""
    token: str
    action: str                             # human-readable explanation
    stack_contents: List[str] = field(default_factory=list)
    output_contents: List[str] = field(default_factory=list)


# ── Algorithm ─────────────────────────────────────────────────────

def shunting_yard(tokens: List[Token]) -> tuple[List[str], List[ShuntingYardStep]]:
    """Convert an infix token list to postfix using Shunting-Yard.

    Parameters:
        tokens: Validated list of :class:`Token` objects in infix order.

    Returns:
        A tuple *(postfix_tokens, steps)* where *postfix_tokens* is the
        list of token-value strings in postfix order and *steps* records
        every intermediate state for animation.
    """
    output: List[str] = []
    op_stack: Stack[str] = Stack()
    steps: List[ShuntingYardStep] = []

    def _snapshot(token_val: str, action: str) -> None:
        steps.append(ShuntingYardStep(
            token=token_val,
            action=action,
            stack_contents=op_stack.items(),
            output_contents=list(output),
        ))

    for tok in tokens:
        val = tok.value

        # ── Operand → straight to output ──────────────────────────
        if tok.token_type in OPERAND_TOKENS:
            output.append(val)
            _snapshot(val, f"Operand '{val}' → push to output queue")

        # ── OPERATOR → apply precedence rules ─────────────────────
        elif tok.token_type == TokenType.OPERATOR:
            while (
                op_stack
                and op_stack.peek() != '('
                and op_stack.peek() in OPERATORS
                and (
                    PRECEDENCE[op_stack.peek()] > PRECEDENCE[val]
                    or (
                        PRECEDENCE[op_stack.peek()] == PRECEDENCE[val]
                        and val not in RIGHT_ASSOCIATIVE
                    )
                )
            ):
                popped = op_stack.pop()
                output.append(popped)
                _snapshot(val, f"Operator '{popped}' has ≥ precedence → pop to output")

            op_stack.push(val)
            _snapshot(val, f"Push operator '{val}' onto stack")

        # ── LEFT PAREN ─────────────────────────────────────────────
        elif tok.token_type == TokenType.LPAREN:
            op_stack.push(val)
            _snapshot(val, "Token '(' encountered → push to stack")

        # ── RIGHT PAREN ────────────────────────────────────────────
        elif tok.token_type == TokenType.RPAREN:
            while op_stack and op_stack.peek() != '(':
                popped = op_stack.pop()
                output.append(popped)
                _snapshot(val, f"Pop operator '{popped}' to output until '('")
            if op_stack:
                op_stack.pop()  # remove the '('
                _snapshot(val, "Matching '(' found → discard both parentheses")

    # ── Flush remaining operators ──────────────────────────────────
    while op_stack:
        popped = op_stack.pop()
        output.append(popped)
        _snapshot(popped, f"Flush remaining operator '{popped}' to output")

    return output, steps
