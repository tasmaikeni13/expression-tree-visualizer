"""
Application-wide configuration constants.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Centralises colours, font sizes, animation speeds, and layout
parameters so every module draws from a single source of truth.
"""

from __future__ import annotations

# ── Colour palette (dark-mode, glassmorphism-inspired) ─────────────
COLORS = {
    # Backgrounds
    "bg_primary":       "#1a1b2e",   # deep charcoal-indigo
    "bg_secondary":     "#232440",   # slightly lighter panel
    "bg_tertiary":      "#2c2d4a",   # card / input background
    "bg_glass":         "rgba(35, 36, 64, 0.85)",  # glassmorphism

    # Accents
    "accent_cyan":      "#00e5ff",
    "accent_violet":    "#b388ff",
    "accent_green":     "#69f0ae",
    "accent_orange":    "#ffab40",
    "accent_pink":      "#ff80ab",
    "accent_red":       "#ff5252",

    # Text
    "text_primary":     "#e8eaf6",
    "text_secondary":   "#9fa8da",
    "text_muted":       "#5c6bc0",

    # Node colours
    "node_operator":    "#7c4dff",   # violet for operators
    "node_operand":     "#00e5ff",   # cyan for numbers
    "node_highlight":   "#ffab40",   # orange highlight during traversal
    "node_eval":        "#69f0ae",   # green when evaluated
    "node_text":        "#ffffff",
    "edge_color":       "#5c6bc0",

    # Stack visualiser
    "stack_item":       "#3949ab",
    "stack_push":       "#69f0ae",
    "stack_pop":        "#ff5252",
    "output_item":      "#00897b",

    # Buttons
    "btn_primary":      "#7c4dff",
    "btn_hover":        "#651fff",
    "btn_secondary":    "#37474f",
    "btn_danger":       "#ff5252",
}

# ── Typography ─────────────────────────────────────────────────────
FONTS = {
    "family":           "Segoe UI, Roboto, Arial, sans-serif",
    "mono":             "Consolas, Fira Code, monospace",
    "size_sm":          11,
    "size_md":          13,
    "size_lg":          16,
    "size_xl":          20,
    "size_title":       24,
}

# ── Animation timing (milliseconds) ───────────────────────────────
ANIMATION = {
    "step_delay":       600,     # delay between algorithm steps
    "node_grow_ms":     350,     # node scale-up animation
    "highlight_ms":     400,     # traversal highlight duration
    "stack_slide_ms":   300,     # stack push / pop slide
    "fade_ms":          250,     # generic fade in/out
}

# ── Tree layout ────────────────────────────────────────────────────
TREE_LAYOUT = {
    "node_radius":      24,
    "h_spacing":        60,      # horizontal gap between siblings
    "v_spacing":        80,      # vertical gap between levels
    "margin":           40,
}

# ── Operator precedence (used by Shunting-Yard) ────────────────────
PRECEDENCE: dict[str, int] = {
    "+": 1,
    "-": 1,
    "*": 2,
    "/": 2,
    "^": 3,
}

RIGHT_ASSOCIATIVE: set[str] = {"^"}

OPERATORS: set[str] = set(PRECEDENCE.keys())
