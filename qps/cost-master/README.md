# QPS COST_Master - CODEX public bridge

This folder is the public, source-only execution contract for the private QPS
cost build. It does not contain current offer data or generated Office/PDF/image
artifacts.

CODEX responsibilities:

- define schemas and build interfaces;
- validate source/config shape;
- run public source-policy checks;
- record sanitized release pointers and semantic hashes;
- never receive the private Excel SSOT, offer files, generated PPTX/PDF/XLSX,
  or the local Git bundle.

The actual data-bearing build is cloned from the local-only private Git bundle
under `C:\Dev\QPS_COST_Master\private-control`.
