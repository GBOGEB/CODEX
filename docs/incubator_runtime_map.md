# Incubator Runtime Map

This document defines the W000/W001 ingest flow:

1. Create tuple files in `incubator/` using the naming convention.
2. Parse tuple files locally with `scripts/parse_chat_tuple.py`.
3. Generate `docs/incubator_index.md` using `scripts/build_incubator_index.py`.

The current scope intentionally excludes DMAIC and advanced extraction until W002+.
