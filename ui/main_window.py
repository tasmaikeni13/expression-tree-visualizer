"""
Main window — top-level QMainWindow composing all panels.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Wires together ExpressionInput, TreeCanvas, StackVisualizer,
TraversalPanel, and the AnimationController.
"""

from __future__ import annotations
from typing import Dict, List, Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from app.config import COLORS, FONTS, ANIMATION
from algorithms.shunting_yard import ShuntingYardStep
from core.evaluator import EvalStep, evaluate_tree
from core.expression_tree import TreeBuildStep, build_expression_tree
from core.infix_to_postfix import infix_to_postfix
from core.infix_to_prefix import infix_to_prefix
from core.traversal import inorder, preorder, postorder, TRAVERSAL_DESCRIPTIONS
from core.tree_node import TreeNode
from ui.expression_input import ExpressionInput
from ui.stack_visualizer import StackVisualizer
from ui.tree_canvas import TreeCanvas
from ui.traversal_panel import TraversalPanel
from visualization.animation_controller import AnimationController


class MainWindow(QMainWindow):
    """The application's primary window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Expression Tree Visualizer")
        self.setMinimumSize(1200, 750)
        self.resize(1440, 880)

        # State
        self._root: Optional[TreeNode] = None
        self._postfix: List[str] = []
        self._shunting_steps: List[ShuntingYardStep] = []
        self._build_steps: List[TreeBuildStep] = []
        self._eval_steps: List[EvalStep] = []
        self._eval_result: Optional[float] = None
        self._eval_message: Optional[str] = None

        # Animation controllers
        self._stack_anim = AnimationController(self)
        self._build_anim = AnimationController(self)
        self._trav_anim = AnimationController(self)

        self._setup_ui()
        self._connect_signals()

    # ── UI Construction ────────────────────────────────────────────

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── Header ─────────────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(56)
        header.setStyleSheet(f"""
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 {COLORS['bg_secondary']},
                stop:1 {COLORS['bg_primary']}
            );
        """)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(24, 0, 24, 0)

        logo = QLabel("🌳  Expression Tree Visualizer")
        logo.setFont(QFont(FONTS["family"], FONTS["size_title"], QFont.Weight.Bold))
        logo.setStyleSheet(f"color: {COLORS['accent_cyan']};")
        h_layout.addWidget(logo)

        h_layout.addStretch()

        subtitle = QLabel("Interactive Data Structures Learning Tool")
        subtitle.setFont(QFont(FONTS["family"], FONTS["size_sm"]))
        subtitle.setStyleSheet(f"color: {COLORS['text_muted']};")
        h_layout.addWidget(subtitle)

        root_layout.addWidget(header)

        # ── Splitter: left panel | right panel ─────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(2)
        splitter.setChildrenCollapsible(False)
        splitter.setStyleSheet(self._splitter_style())

        # ── Left panel (scrollable) ───────────────────────────────
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(12, 12, 4, 12)
        left_layout.setSpacing(12)

        self._input_panel = ExpressionInput()
        self._input_panel.setStyleSheet(self._panel_style())
        left_layout.addWidget(self._input_panel)

        self._traversal_panel = TraversalPanel()
        self._traversal_panel.setStyleSheet(self._panel_style())
        left_layout.addWidget(self._traversal_panel, 1)

        left_scroll = QScrollArea()
        left_scroll.setWidgetResettable = True
        left_scroll.setWidget(left_widget)
        left_scroll.setWidgetResizable(True)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        left_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        splitter.addWidget(left_scroll)

        # ── Right panel ────────────────────────────────────────────
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        right_splitter.setHandleWidth(2)
        right_splitter.setChildrenCollapsible(False)
        right_splitter.setStyleSheet(self._splitter_style())

        self._tree_canvas = TreeCanvas()
        self._tree_canvas.setStyleSheet(self._panel_style())
        right_splitter.addWidget(self._tree_canvas)

        self._stack_viz = StackVisualizer()
        self._stack_viz.setStyleSheet(self._panel_style())
        right_splitter.addWidget(self._stack_viz)

        right_splitter.setStretchFactor(0, 3)
        right_splitter.setStretchFactor(1, 1)
        right_splitter.setSizes([520, 220])

        splitter.addWidget(right_splitter)

        # Default split ratio (40 / 60)
        splitter.setSizes([520, 780])
        root_layout.addWidget(splitter, 1)

    def _panel_style(self) -> str:
        return f"""
            QFrame {{
                background-color: {COLORS['bg_secondary']};
                border-radius: 14px;
                border: 1px solid rgba(92, 107, 192, 0.25);
            }}
        """

    def _splitter_style(self) -> str:
        return f"""
            QSplitter::handle {{
                background-color: {COLORS['text_muted']};
            }}
        """

    # ── Signal wiring ──────────────────────────────────────────────

    def _connect_signals(self) -> None:
        # Input panel
        self._input_panel.build_requested.connect(self._on_build)
        self._input_panel.animate_requested.connect(self._on_animate)
        self._input_panel.clear_requested.connect(self._on_clear)

        # Traversal
        self._traversal_panel.traversal_requested.connect(self._on_traversal)
        self._traversal_panel.export_png_requested.connect(self._tree_canvas.export_png)

        # Animation controllers
        self._stack_anim.step_played.connect(self._on_stack_step)
        self._stack_anim.finished.connect(self._on_stack_anim_done)
        self._build_anim.step_played.connect(self._on_build_step)
        self._build_anim.finished.connect(self._on_build_anim_done)
        self._trav_anim.step_played.connect(self._on_trav_step)

    # ── Handlers ───────────────────────────────────────────────────

    def _on_build(self, expression: str) -> None:
        """Instant build (no animation)."""
        self._stop_all_animations()
        self._process_expression(expression)
        self._tree_canvas.display_tree(self._root)
        self._traversal_panel.show_eval_steps(self._eval_steps, self._eval_result, self._eval_message)

    def _on_animate(self, expression: str) -> None:
        """Animated step-by-step build."""
        self._stop_all_animations()
        self._process_expression(expression)

        # Clear tree canvas — will build progressively
        self._tree_canvas.clear()
        self._traversal_panel.clear_log()
        self._stack_viz.clear()

        # Stage 1: animate Shunting-Yard
        self._stack_anim.load(self._shunting_steps, ANIMATION["step_delay"])
        self._stack_anim.play()

    def _on_clear(self) -> None:
        self._stop_all_animations()
        self._tree_canvas.clear()
        self._stack_viz.clear()
        self._traversal_panel.clear_all()
        self._root = None

    def _on_traversal(self, name: str) -> None:
        """Highlight nodes in traversal order."""
        if self._root is None:
            return

        self._stop_all_animations()

        if name == "inorder":
            nodes = inorder(self._root)
        elif name == "preorder":
            nodes = preorder(self._root)
        else:
            nodes = postorder(self._root)

        # Show traversal result in log
        values = [n.value for n in nodes]
        self._traversal_panel.append_log(f"{name.capitalize()} traversal: {' '.join(values)}")

        # Animate highlighting
        self._tree_canvas.highlight_nodes(nodes)

    # ── Animation callbacks ────────────────────────────────────────

    def _on_stack_step(self, index: int, step: ShuntingYardStep) -> None:
        self._stack_viz.show_step(step)
        self._traversal_panel.append_log(f"[Shunting-Yard] {step.action}")

    def _on_stack_anim_done(self) -> None:
        """After Shunting-Yard, animate tree building."""
        if self._build_steps:
            self._build_anim.load(self._build_steps, ANIMATION["step_delay"])
            self._build_anim.play()

    def _on_build_step(self, index: int, step: TreeBuildStep) -> None:
        self._traversal_panel.append_log(f"[Tree Build] {step.action}")
        # Progressively display tree up to root
        if index == len(self._build_steps) - 1:
            # Last step — show the complete tree
            self._tree_canvas.display_tree(self._root)

    def _on_build_anim_done(self) -> None:
        """After tree is built, show the final tree and evaluation."""
        self._tree_canvas.display_tree(self._root)
        self._traversal_panel.show_eval_steps(self._eval_steps, self._eval_result, self._eval_message)
        self._traversal_panel.append_log("✅ Tree construction complete!")

    def _on_trav_step(self, index: int, node: TreeNode) -> None:
        self._tree_canvas.highlight_node_instant(node, COLORS["node_highlight"])

    # ── Core logic ─────────────────────────────────────────────────

    def _process_expression(self, expression: str) -> None:
        """Parse, convert, build, and evaluate."""
        # Postfix + animation steps
        self._postfix, self._shunting_steps = infix_to_postfix(expression)
        prefix = infix_to_prefix(expression)

        # Build tree
        self._root, self._build_steps = build_expression_tree(self._postfix)

        # Evaluate
        self._eval_result, self._eval_steps, self._eval_message = evaluate_tree(self._root)

        # Update notation display
        self._traversal_panel.set_notations(
            infix=expression,
            prefix=" ".join(prefix),
            postfix=" ".join(self._postfix),
        )

    def _stop_all_animations(self) -> None:
        self._stack_anim.stop()
        self._build_anim.stop()
        self._trav_anim.stop()
        self._tree_canvas.reset_highlights()
