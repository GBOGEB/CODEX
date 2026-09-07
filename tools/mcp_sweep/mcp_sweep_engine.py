#!/usr/bin/env python3
"""Compatibility entrypoint for the canonical CODEX MCP sweep runtime.

The historical tools implementation used a second hard-coded MCPSweepEngine.
W04 removes that competing implementation. New runtime code must import from
``src.federation.mcp_sweep_engine`` or invoke ``scripts/run_mcp_sweep.py``.

This module remains temporarily import-compatible while downstream consumers
are censused. It intentionally defines no independent runtime behavior.
"""
from __future__ import annotations

from src.federation.mcp_sweep_engine import MCPSweepEngine, SweepItem

__all__ = ["MCPSweepEngine", "SweepItem"]
