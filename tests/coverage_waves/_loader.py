"""Shared helpers for the L3 coverage-wave tests (not collected by pytest)."""
from __future__ import annotations

import importlib.util
import runpy
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[2]


def load(relpath: str) -> ModuleType:
    """Import a repo module by its path, even outside any package."""
    path = ROOT / relpath
    name = "l3cw_" + relpath.replace("/", "_").replace("-", "_").removesuffix(".py")
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run_main(relpath: str, argv: list[str] | None = None) -> dict:
    """Execute a module's ``__main__`` block with an optional argv."""
    old = sys.argv
    sys.argv = [str(ROOT / relpath), *(argv or [])]
    try:
        return runpy.run_path(str(ROOT / relpath), run_name="__main__")
    finally:
        sys.argv = old
