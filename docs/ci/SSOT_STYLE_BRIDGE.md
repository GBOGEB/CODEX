# SSOT Style Bridge

`ssot/ssot_style_bridge.json` is the CODEX-side bridge contract for style, readability, rendering QA and CI grouping. It does not replace ABACUS as the user-facing artifact control surface. It proves that CODEX has reusable controls that ABACUS and controlled evidence lanes can consume.

## Role Split

| Repo lane | Role | Rule |
| --- | --- | --- |
| ABACUS | Artifact consumer and operational dashboard surface | Owns outward status, DOW/KEB probes and artifact readiness summaries. |
| CODEX | Reusable render/style/CI governance bridge | Owns semantic-card palette, contrast/render/federation test discovery and bridge scoring. |
| Controlled evidence lane | Non-public source evidence adapter | Emits hashes and render evidence without public disclosure. |

## Artifact Coverage

The bridge tracks five lanes: HTML, PDF, PPTX, Excel and graphs. Each lane has a short list of required controls so that future rendered outputs can be checked consistently without storing binary artifacts in Git.

## DMAIC Loop

| Phase | CODEX bridge action |
| --- | --- |
| Define | Treat CODEX as the reusable governance bridge, not the numeric or private evidence SSOT. |
| Measure | Score artifact lanes, awake probe presence and penetration depth separately. |
| Analyze | Use reversed PCA ordering from P5 to P1 so weak KEB/render lanes rise first. |
| Improve | Add a small validator before wiring heavier Playwright or screenshot checks into CI. |
| Control | Keep the contract code-only, testable and cheap to run in slim CI. |

## Current BT Priority

1. `keb_feedback_depth`: add explicit queue/runtime/feedback evidence.
2. `render_regression_depth`: replace placeholders with Playwright, screenshot and semantic HTML evidence.
3. `artifact_lane_binding`: bind HTML/PDF/PPTX/Excel/graph outputs to shared manifests and checksums.

## Validation

```bash
python scripts/validate_ssot_style_bridge.py --output reports/ssot_style_bridge_status.json
python -m unittest tests.test_validate_ssot_style_bridge -v
python -m py_compile scripts/validate_ssot_style_bridge.py tests/test_validate_ssot_style_bridge.py
```

The report is intentionally split into `artifact_lanes`, `awake` and `penetration` sections. A path can be awake while still scoring lower on penetration when the file exists but lacks runtime, feedback, checksum, Playwright or semantic-diff evidence.
