# Incubator Runtime Map

This page describes W000/W001 tuple ingress flow for the INCUBATOR layer.

## Flow

1. Author tuple YAML records in `/incubator` using the naming convention.
2. Validate and parse tuples with `python scripts/parse_chat_tuple.py`.
3. Build the Markdown index with `python scripts/build_incubator_index.py`.
4. Extract simple theme counts with `python scripts/extract_themes.py`.

## Mapping sources

- Category map: `maps/category_map.yml`
- Theme map: `maps/theme_map.yml`
- Repo ingress map: `maps/repo_ingress_map.yml`

## W000/W001 status

- W000: complete (naming + schema + seeded tuple file)
- W001: complete (parser + markdown index generation)
