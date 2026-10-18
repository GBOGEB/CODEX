# QPLANT / SCK CEN PPTX builder — moved

The builder guide lives in one place: **[`slides/README.md`](../../../slides/README.md)**,
next to the module it documents (`python -m slides.qplant_sckcen_template build|batch`).

This file previously held a second copy of that guide. The copies had drifted:
this one described `src/`, `assets/`, `manifests/` and `output/` folders that do
not exist here, and CLI flags the builder does not have (`--include`,
`--fallback-font`, `--asset-root`, `--metadata`). Use `slides/README.md`.

Related:
- Corporate house style and the PPTX post-processing / QA gate: `tools/house_style/README.md`
- QPS slide system (YAML → HTML/Markdown decks): `docs/qps-slide-system/README.md`

`engine/qplant_sckcen_template.py` in this folder is an older copy of
`slides/qplant_sckcen_template.py`; the module that runs is the one under `slides/`.
