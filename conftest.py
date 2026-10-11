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

# GISTAU Ch15 is laid out as ``src/gistau_ch15`` but imports itself (and is
# imported by its tests) as the top-level package ``gistau_ch15``. Without
# ``src`` on the path every GISTAU test module fails at collection, which is
# why CI previously ``--ignore``d them. Append (not insert) so that ``src``
# has the lowest precedence and cannot shadow stdlib, site-packages or the
# repo-root ``src.<module>`` imports used elsewhere.
_SRC = str(Path(_ROOT) / "src")
if _SRC not in sys.path:
    sys.path.append(_SRC)
