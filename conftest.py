"""Root conftest: ensure the project root and src/ are on sys.path.

This makes both ``from src.<module> import ...`` and bare ``from <module>
import ...`` patterns work in all test modules without each test file having
to insert paths manually.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Insert the project root so ``from src.<module> import ...`` works when
# pytest is run without a prior ``pip install -e .`` (e.g. in bare CI runs).
_ROOT = str(Path(__file__).resolve().parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# Insert src/ so tests can import sub-packages directly, e.g.
# ``from gistau_ch15.calculations.compressor import ...``
_SRC = str(Path(__file__).resolve().parent / "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)
