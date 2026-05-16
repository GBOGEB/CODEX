# Handoff Packaging Notes

This repository keeps handoff contents in text/source form to remain PR-reviewable on platforms that do not support binary diff rendering.

## Included (tracked)
- `handoff/v0_6_2/` package directory (HTML, SVG, YAML)

## Excluded (generated locally)
- `handoff/v0_6_2_handover_bundle.zip`
- `handoff/v0_6_2_handover_bundle.tar.gz`

## Rebuild bundles
From repository root:

```bash
(cd handoff && zip -r v0_6_2_handover_bundle.zip v0_6_2)
(cd handoff && tar -czf v0_6_2_handover_bundle.tar.gz v0_6_2)
```

These commands are deterministic for package contents and should be used only for distribution artifacts, not for source control.
