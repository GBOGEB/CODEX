#!/usr/bin/env python3
"""CLI wrapper for MASTER Contract Workbench SSOT generation."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.contract_workbench.generator import main

if __name__ == "__main__":
    raise SystemExit(main())
