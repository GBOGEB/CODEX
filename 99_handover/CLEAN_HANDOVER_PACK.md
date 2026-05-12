# Clean Handover Pack Usage

Use the **clean handover pack** and avoid the rough tuple flow (that is, passing fragmented, loosely structured handover inputs instead of the packaged minimal copy-paste handover).

## Recommended operator flow

1. Start by pasting the **Minimal Copy-Paste Version** (see below) into CODEX.
2. Provide the full handover pack as supporting context only if more detail is needed.

## Minimal Copy-Paste Version

Copy and paste the version below verbatim at the start of every new CODEX interaction to give the agent essential project context before you supply any additional files.

```
## CODEX Minimal Context — HELIUM_VCR_UHP v1.3.0

Repo: GBOGEB/CODEX | Branch: main
Project: Helium UHP distribution system — VCR face-seal (/FS) policy and P&ID

Key rules:
  - Naming: QRB.A/.B/.D/.E; QINFRA.U/W/S; WCS.HP/LP/VLP (dots, not dashes)
  - All serviceable joints: metal gasket face-seal (/FS, VCR-compatible); new gasket at every remake
  - DBB purge: pull to ≤50 mbar(a), He backfill to 1.05 bar(a), analyser confirm
  - Leakage limit: per Table 6; verified by He MS test
  - Safety populations: 60+5 BD, 180+30 PSV; S-line PSV ≥200 g/s @ 300 K to WCS.LP

Outputs: HTML dashboard · Markdown handover · PDF · RTM · JSON/YAML · GitHub Pages
Source of truth: Markdown + YAML + JSON + Python calculation engine
Start here: OUTPUT_MANIFEST.json → 01_requirements/RTM.csv → 02_design/MASTER_FACE_SEAL_POLICY.md
```

## Pack contents checklist

The clean **CODEX Handover Manifest Glob Pack** should include:

> Note: the manifest and policy filenames below refer to artifacts bundled in the external clean handover pack. They are not expected to exist as tracked files in this repository unless they have been copied in as part of that bundle.

- master CODEX prompt
- repo target structure
- SAME vs SIMILAR branch rules
- root `MANIFEST.json` (handover-pack artifact)
- tool `MANIFEST.json` (handover-pack artifact)
- `GLOB_POLICY.md` (handover-pack artifact)
- `BACKBONE_POLICY.md` (handover-pack artifact)
- CI workflow
- GitHub Pages workflow
- acceptance checklist
- Minimal Copy-Paste Version (see above)

## Selection rule

**Best option:** paste the **Minimal Copy-Paste Version** into CODEX first, then add the full pack only as needed.
