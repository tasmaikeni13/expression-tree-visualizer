"""
Infix → Prefix conversion.
~~~~~~~~~~~~~~~~~~~~~~~~~~~
Uses the *reverse-then-Shunting-Yard* approach:
1. Reverse the infix token list (swapping '(' ↔ ')').
2. Run a modified Shunting-Yard to get postfix of the reversed expression.
3. Reverse the result to obtain prefix notation.
"""

from __future__ import annotations
from typing import List

from algorithms.stack import Stack
from app.config import PRECEDENCE, RIGHT_ASSOCIATIVE, OPERATORS
from core.tokenizer import Token, TokenType, tokenize


OPERAND_TOKENS = (TokenType.NUMBER, TokenType.VARIABLE)


def infix_to_prefix_tokens(tokens: List[Token]) -> List[str]:
    """Convert validated infix *tokens* to prefix order.

    Returns:
        List of token-value strings in prefix notation.
    """
    # Step 1 — Reverse and swap parens
    reversed_tokens: List[Token] = []
    for tok in reversed(tokens):
        if tok.token_type == TokenType.LPAREN:
            reversed_tokens.append(Token(')', TokenType.RPAREN, tok.position))
        elif tok.token_type == TokenType.RPAREN:
            reversed_tokens.append(Token('(', TokenType.LPAREN, tok.position))
        else:
            reversed_tokens.append(tok)

    # Step 2 — Modified Shunting-Yard (right-to-left precedence)
    output: List[str] = []
    op_stack: Stack[str] = Stack()

    for tok in reversed_tokens:
        val = tok.value

        if tok.token_type in OPERAND_TOKENS:
            output.append(val)

        elif tok.token_type == TokenType.OPERATOR:
            # For prefix we flip the associativity comparison
            while (
                op_stack
                and op_stack.peek() != '('
                and op_stack.peek() in OPERATORS
                and (
                    PRECEDENCE[op_stack.peek()] > PRECEDENCE[val]
                    or (
                        PRECEDENCE[op_stack.peek()] == PRECEDENCE[val]
                        and val in RIGHT_ASSOCIATIVE
                    )
                )
            ):
                output.append(op_stack.pop())
            op_stack.push(val)

        elif tok.token_type == TokenType.LPAREN:
            op_stack.push(val)

        elif tok.token_type == TokenType.RPAREN:
            while op_stack and op_stack.peek() != '(':
                output.append(op_stack.pop())
            if op_stack:
                op_stack.pop()  # discard '('

    while op_stack:
        output.append(op_stack.pop())

    # Step 3 — Reverse to get prefix
    output.reverse()
    return output


def infix_to_prefix(expression: str) -> List[str]:
    """Convenience: tokenise *expression* then convert to prefix."""
    tokens = tokenize(expression)
    return infix_to_prefix_tokens(tokens)
