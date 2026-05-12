# Clean Handover Pack Usage

Use the **clean handover pack** and avoid the rough tuple flow (that is, passing fragmented, loosely structured handover inputs instead of the packaged minimal copy-paste handover).

## Recommended operator flow

1. Start by pasting the **Minimal Copy-Paste Version** into CODEX.
2. Provide the full handover pack as supporting context only if more detail is needed.

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
- minimal copy-paste CODEX block

## Selection rule

**Best option:** paste the **Minimal Copy-Paste Version** section into CODEX first, then add the full pack only as needed.
