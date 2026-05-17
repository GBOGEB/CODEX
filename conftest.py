"""Root conftest: ensure the project root is on sys.path.

This makes the ``src`` package importable in all test modules without each
test file having to insert the path manually.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Insert the project root so ``from src.<module> import ...`` works when
# pytest is run without a prior ``pip install -e .`` (e.g. in bare CI runs).
_ROOT = str(Path(__file__).resolve().parent)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
