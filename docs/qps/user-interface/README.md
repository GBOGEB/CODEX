# QPS USER Interface Note Rendering

This directory contains the USER-facing QPS cold and warm piping interface note and its structured SSOT-derivative data.

> **IF IT CANNOT RENDER, IT CANNOT GOVERN.**

## Files

* `USER_INTERFACES_COLD_WARM_NOTE.md` — dominant Markdown source for rendered review.
* `USER_INTERFACES_COLD_WARM_NOTE.html` — checked-in HTML view of the Markdown note.
* `data/user_interface_lines.yaml` — structured line data for future calculations.
* `data/user_interface_lines.json` — structured line data for future calculations.
* `adr/ADR-USER-INTERFACE-SSOT-DERIVATIVE.md` — governance record for SSOT-derivative status.

## Governance Role

The CONTRACT remains the authoritative SSOT. The note in this directory is derivative, supplementary, descriptive, and user-facing. Treat it as an `SSOT_derivative` fixed/locked scientific configuration candidate once reviewed, with ADR traceability.

## Render Markdown to HTML

Placeholder Pandoc command for future rendering automation:

```sh
pandoc USER_INTERFACES_COLD_WARM_NOTE.md \
  --standalone \
  --metadata title="USER Interfaces — Cold and Warm Piping Descriptive Note" \
  --output USER_INTERFACES_COLD_WARM_NOTE.html
```

Placeholder static-site command for future documentation portals:

```sh
# Example only; replace with the repository's selected static-site generator.
static-site-render docs/qps/user-interface/USER_INTERFACES_COLD_WARM_NOTE.md \
  --out docs/qps/user-interface/USER_INTERFACES_COLD_WARM_NOTE.html
```

## Export PDF

Placeholder Pandoc PDF command for future release packages:

```sh
pandoc USER_INTERFACES_COLD_WARM_NOTE.md \
  --standalone \
  --pdf-engine=xelatex \
  --metadata title="USER Interfaces — Cold and Warm Piping Descriptive Note" \
  --output USER_INTERFACES_COLD_WARM_NOTE.pdf
```

Placeholder browser-based PDF export path from the checked-in HTML view:

```sh
# Example only; replace with the repository's selected browser automation tool.
html-to-pdf docs/qps/user-interface/USER_INTERFACES_COLD_WARM_NOTE.html \
  docs/qps/user-interface/USER_INTERFACES_COLD_WARM_NOTE.pdf
```
