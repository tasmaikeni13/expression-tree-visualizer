"""
Tokenizer — splits a raw expression string into typed tokens.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Supports multi-digit integers, decimal numbers, single-character
operators (+, -, *, /, ^) and parentheses.
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto
from typing import List


class TokenType(Enum):
    """Categories a token can belong to."""
    NUMBER = auto()
    VARIABLE = auto()
    OPERATOR = auto()
    LPAREN = auto()
    RPAREN = auto()
    UNKNOWN = auto()


@dataclass
class Token:
    """A single lexical token with its type and position in the source."""
    value: str
    token_type: TokenType
    position: int          # index in the original string


# Characters recognised as operators
_OPERATORS = set("+-*/^")


def tokenize(expression: str) -> List[Token]:
    """Convert *expression* into a list of :class:`Token` objects.

    Parameters:
        expression: Raw infix expression string.

    Returns:
        Ordered list of tokens.

    Raises:
        ValueError: If an unrecognised character is encountered.
    """
    tokens: List[Token] = []
    i = 0
    n = len(expression)

    while i < n:
        ch = expression[i]

        # Skip whitespace
        if ch.isspace():
            i += 1
            continue

        # Numbers (integer or decimal)
        if ch.isdigit() or (ch == '.' and i + 1 < n and expression[i + 1].isdigit()):
            start = i
            while i < n and (expression[i].isdigit() or expression[i] == '.'):
                i += 1
            tokens.append(Token(expression[start:i], TokenType.NUMBER, start))
            continue

        # Single-letter symbolic variables
        if ch.isalpha():
            tokens.append(Token(ch, TokenType.VARIABLE, i))
            i += 1
            continue

        # Operators
        if ch in _OPERATORS:
            # Handle unary minus: treat leading '-' or '-' after '(' as part of number
            if ch == '-' and (not tokens or tokens[-1].token_type in (TokenType.LPAREN, TokenType.OPERATOR)):
                start = i
                i += 1
                if i < n and (expression[i].isdigit() or expression[i] == '.'):
                    while i < n and (expression[i].isdigit() or expression[i] == '.'):
                        i += 1
                    tokens.append(Token(expression[start:i], TokenType.NUMBER, start))
                    continue
                else:
                    # It's just a minus with nothing numeric after it — treat as operator
                    tokens.append(Token(ch, TokenType.OPERATOR, start))
                    continue
            tokens.append(Token(ch, TokenType.OPERATOR, i))
            i += 1
            continue

        # Parentheses
        if ch == '(':
            tokens.append(Token(ch, TokenType.LPAREN, i))
            i += 1
            continue
        if ch == ')':
            tokens.append(Token(ch, TokenType.RPAREN, i))
            i += 1
            continue

        # Unknown character
        tokens.append(Token(ch, TokenType.UNKNOWN, i))
        i += 1

    return tokens
