# MIP Rollout

MIP means Modernize, Innovate, Perpetuate.

This repo uses MIP as a repeatable self-improvement loop:

| Lane | Purpose | First executable evidence |
| --- | --- | --- |
| `repo_self_index` | Census the repo and expose real denominators. | `MIP/receipts/repo_self_index.json` |
| `repo_self_assess_debug_ldab` | Find debug, logging, diagnostics, and LDAB-style breakpoints/observability gaps. | Assessment section in the same receipt |
| `repo_self_assess_runners_mcp` | Classify Docker, runners, CI, MCP, and orchestration surfaces. | Assessment section in the same receipt |
| `repo_self_assess_codz_health_selfheal` | Identify code-health and self-heal candidates without silently changing behavior. | Assessment section in the same receipt |
| `repo_self_produce` | Promote reusable repo functionality into an implantable skill, agent, manager, or orchestrator. | Candidate list in the same receipt |

## DoD

1. The self-index runs locally with only the Python standard library.
2. The receipt records repo SHA, branch, dirty-state summary, file census, runtime surfaces, and candidate MIP lanes.
3. The next repair target is selected from the first red or missing evidence class, not from a widened backlog.
4. Produce candidates are separated from claims: a reusable skill/agent is a candidate until packaged, tested, and documented.

## DoV

MIP DoV is withheld until at least three distinct repo SHAs have receipts and one self-heal or produce candidate is proven by an executable check.



## Shareable kit (canonical in CODEX)

CODEX hosts the canonical MIP kit. ABACUS, cryoplant-project and other consumers copy it unchanged.

| Part | Path | Shared? |
| --- | --- | --- |
| Skill package | `.codex/skills/mip-repo-self-index/` | yes |
| Self-index emitter and verifier | `scripts/mip_repo_self_index.py`, `scripts/mip_verify_self_index.py` | yes |
| Debug/LDAB diagnostic | `scripts/mip_debug_diagnostic.py` | yes |
| Manifest writer and drift check | `scripts/mip_kit_manifest.py` | yes |
| Kit manifest (file list and sha256) | `MIP/kit/KIT_MANIFEST.json` | copied from CODEX |
| Surface config | `MIP/mip_surface.json` | no, one per repo |

`MIP/mip_surface.json` holds the only repo-specific settings:

- `health_probe`: repo-relative path of the health/self-heal probe. `null` means no probe. If the key is absent, the default is `scripts/mip_health_selfheal_probe.py`.
- `debug_diagnostic`: repo-relative path of the debug/LDAB diagnostic. `null` means none. If the key is absent, the default is the kit's `scripts/mip_debug_diagnostic.py`. The debug lane is GREEN only when this diagnostic runs on the exact SHA and every check passes; debug-like file names alone give AMBER.
- `nested_surfaces`: list of `{path, emitter, diagnostic?}` nested self-index surfaces. Use an empty list when there are none.
- `shareable_skill`: skill package the verifier validates.
- `required_green`: lanes that must be GREEN, or the verifier fails.
- `repository`, `role`, `next_victory_condition`: labels copied into the receipt and summary.

After you change a kit file in CODEX, run `python scripts/mip_kit_manifest.py write` and commit the refreshed manifest in the same PR. A consumer checks its copy with `python scripts/mip_kit_manifest.py check --canonical <copy of CODEX's KIT_MANIFEST.json>`.
