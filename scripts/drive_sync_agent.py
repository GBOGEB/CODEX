#!/usr/bin/env python3
"""Compatibility shim for googledrive/scripts/drive_sync_agent.py."""

from __future__ import annotations

import runpy
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "googledrive" / "scripts" / "drive_sync_agent.py"
runpy.run_path(str(SCRIPT), run_name="__main__")
