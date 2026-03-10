"""
Animation controller — QTimer-based sequencer.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Drives step-by-step animations for tree building, traversals,
and evaluation, calling back the UI at each tick.
"""

from __future__ import annotations
from typing import Any, Callable, List, Optional

from PySide6.QtCore import QTimer, Signal, QObject

from app.config import ANIMATION


class AnimationController(QObject):
    """Plays a sequence of *steps* one-by-one on a timer.

    Signals:
        step_played(int, object): Emitted with (index, step_data)
            every time the timer fires.
        finished(): Emitted when the last step has been played.
    """

    step_played = Signal(int, object)   # (step_index, step_data)
    finished = Signal()

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._steps: List[Any] = []
        self._index: int = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._delay: int = ANIMATION["step_delay"]
        self._running: bool = False

    # ── Public API ─────────────────────────────────────────────────

    def load(self, steps: List[Any], delay_ms: int | None = None) -> None:
        """Load a new step sequence and reset the cursor."""
        self.stop()
        self._steps = list(steps)
        self._index = 0
        if delay_ms is not None:
            self._delay = delay_ms

    def play(self) -> None:
        """Start or resume playback."""
        if not self._steps:
            return
        self._running = True
        self._timer.start(self._delay)

    def pause(self) -> None:
        """Pause playback (can be resumed)."""
        self._timer.stop()
        self._running = False

    def stop(self) -> None:
        """Stop playback and reset to the beginning."""
        self._timer.stop()
        self._index = 0
        self._running = False

    def step_forward(self) -> None:
        """Advance one step manually (without the timer)."""
        if self._index < len(self._steps):
            self._emit_step()

    def set_speed(self, delay_ms: int) -> None:
        """Change the inter-step delay while running or paused."""
        self._delay = max(50, delay_ms)
        if self._running:
            self._timer.setInterval(self._delay)

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def total_steps(self) -> int:
        return len(self._steps)

    @property
    def current_index(self) -> int:
        return self._index

    # ── Internal ──────────────────────────────────────────────────

    def _tick(self) -> None:
        """Timer callback — play the next step or finish."""
        if self._index >= len(self._steps):
            self._timer.stop()
            self._running = False
            self.finished.emit()
            return
        self._emit_step()

    def _emit_step(self) -> None:
        step_data = self._steps[self._index]
        self.step_played.emit(self._index, step_data)
        self._index += 1
        if self._index >= len(self._steps):
            self._timer.stop()
            self._running = False
            self.finished.emit()
