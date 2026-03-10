"""
Stack ADT — a minimal, explicit stack implementation.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Used throughout the project for the Shunting-Yard algorithm
and expression-tree construction so that the data-structure
concept is taught clearly.
"""

from __future__ import annotations
from typing import Generic, List, TypeVar

T = TypeVar("T")


class Stack(Generic[T]):
    """Classic LIFO stack backed by a Python list.

    All operations are O(1) amortised.
    """

    def __init__(self) -> None:
        self._items: List[T] = []

    # ── Core operations ────────────────────────────────────────────

    def push(self, item: T) -> None:
        """Push *item* onto the top of the stack."""
        self._items.append(item)

    def pop(self) -> T:
        """Remove and return the top item.

        Raises:
            IndexError: If the stack is empty.
        """
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self) -> T:
        """Return the top item without removing it.

        Raises:
            IndexError: If the stack is empty.
        """
        if self.is_empty():
            raise IndexError("peek at empty stack")
        return self._items[-1]

    def is_empty(self) -> bool:
        """Return ``True`` when the stack contains no items."""
        return len(self._items) == 0

    def size(self) -> int:
        """Return the number of items on the stack."""
        return len(self._items)

    def items(self) -> List[T]:
        """Return a *copy* of the internal list (bottom → top)."""
        return list(self._items)

    def clear(self) -> None:
        """Remove all items from the stack."""
        self._items.clear()

    # ── Dunder helpers ─────────────────────────────────────────────

    def __len__(self) -> int:
        return self.size()

    def __repr__(self) -> str:
        return f"Stack({self._items!r})"

    def __bool__(self) -> bool:
        return not self.is_empty()
