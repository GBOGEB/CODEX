# QPS BT Engine

Iteration 001 baseline for deterministic QPS tender requirement prioritization.

This module links the CODEX document-processing pipeline to a Bradley-Terry ranking engine and a separate Monte Carlo confidence engine.

Core rule:

- BT decides the official rank.
- Monte Carlo tests rank robustness.
- The bridge governs evidence exchange.
