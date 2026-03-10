#!/usr/bin/env python3
"""
Expression Tree Visualizer — Launcher
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Checks for required packages, installs any that are missing,
then launches the GUI application.

Usage:
    python run.py
"""

import importlib
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Required packages: mapping of import-name → pip-name
# ---------------------------------------------------------------------------
REQUIRED_PACKAGES = {
    "PySide6": "PySide6",
}


def _check_and_install() -> None:
    """Detect missing packages and install them via pip."""
    missing: list[str] = []
    for import_name, pip_name in REQUIRED_PACKAGES.items():
        try:
            importlib.import_module(import_name)
        except ImportError:
            missing.append(pip_name)

    if missing:
        print(f"[run] Installing missing packages: {', '.join(missing)}")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", *missing],
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        print("[run] Installation complete.\n")


def main() -> None:
    """Entry point: install deps then launch the app."""
    _check_and_install()

    # Add project root to sys.path so all sub-packages are importable
    project_root = str(Path(__file__).resolve().parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    from app.main import launch  # noqa: E402
    launch()


if __name__ == "__main__":
    main()
