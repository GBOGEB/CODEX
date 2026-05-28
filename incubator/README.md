# INCUBATOR Layer

This directory stores machine-readable chat/session tuple records for early-wave runtime governance scaffolding.

## Naming convention

Tuple files use:

`YY_Www_HH_MM__CATEGORY__THEME__TITLE__W###.yml`

Example:

`26_W22_12_35__INCUBATOR__RUNTIME_GOVERNANCE__CHAT_TUPLE_INGRESS_MAPPING__W000.yml`

## Contents

- `session_tuple_schema.yml` — field contract for tuple records.
- `*.yml` tuple records — one file per captured tuple.

## W000/W001 scope

- W000: naming convention and schema.
- W001: local parser and Markdown index generation (`scripts/parse_chat_tuple.py` and `scripts/build_incubator_index.py`).

No external APIs, tokens, or secrets are used.
