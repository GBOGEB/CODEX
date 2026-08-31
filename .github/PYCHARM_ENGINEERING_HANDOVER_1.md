# PyCharm Engineering Handover — QPLANT_GitHub_Integration &harr; ABACUS &harr; CODEX &harr; cryoplant-project

Round 21, corrected and substantially extended in Round 22. Written for whoever (including
future-you) opens this work in PyCharm next.

> **Round 22 update, read this first.** Round 21 (below, mostly kept intact for traceability)
> could not locate `cryoplant-project` on GitHub and left &sect;0's SBS discrepancy and &sect;4's
> "what does the parent pipeline do" question open. Your desktop was linked this round, which let
> this session request read access to the actual local folders
> (`C:\Users\gbonthuy\cryoplant-project`, `C:\Users\gbonthuy\codex`,
> `C:\Users\gbonthuy\Clone_FrOM_GITHUB`) and read the real, authoritative architecture files
> straight from disk. Both open questions are now resolved with real evidence, not inference --
> see the new &sect;7 and the correction notes inline in &sect;0 and &sect;1 below. This is a
> materially better answer than Round 20/21's guesses, and it disagrees with part of what Round 20
> concluded (specifically, the "what does the parent pipeline do with this information" answer) --
> flagged explicitly rather than silently replaced.

## 0. Read this first: a real SBS-hierarchy discrepancy between this session and ABACUS

This session's own round-19 `sbs_scope_of_supply.yaml` (built from your typed architecture
statement + bidder offer-text) says:

> QSYS = QPLANT (WCS + QRB) + QINFRA (WPS + WSH)

A **pre-existing, already-committed document inside GBOGEB/ABACUS**,
`rtm_integration/docs/QPLANT_RTM_Engineering_Handover.md` (generated 2025-09-24, *"generated
automatically from the QPLANT technical requirements specification"* — i.e. machine-extracted
straight from Addendum II's own contractual Technical Requirements text, the same source this
whole project's 722-item RTM tracker is built from), says something structurally different:

> **Level 0:** QSYS (Complete Cryogenic System), sibling QSYS-PR (Project Requirements)
> **Level 1:** QPLANT (main refrigeration plant), QINFRA (CSS cryogenic supply system
> infrastructure), QCELL (CSS cryogenic USER — individual cryomodule/valve-box), QDIST (CSS
> cryogenic USER — distribution lines/headers)
> **Level 2:** WCS, QRB (both under QPLANT)
> **Level 3:** PVPS, HP (under WCS); CC, TURBINES, BATH-4K, BATH-2K (under QRB)

Cross-checked against a second ABACUS document, `ssot_artifacts_catalog.md`, which independently
states the same tree (`QSYS -> QSYS-PR -> QPLANT/QINFRA/QCELL/QDIST -> WCS/QRB`) while cataloguing
`rtm_integration/automation/docs/rtm/QPLANT_RTM.xlsx` (16-17 formal requirements, an SBS sheet, a
Navigation sheet) as its own SSOT artifact — so this is not a one-off typo in a single markdown
file, it is a document + a spreadsheet agreeing with each other.

**The disagreement that matters:** in this session's tree, QINFRA = WPS + WSH (an
infrastructure/interface branch under QPLANT's sibling). In ABACUS's pre-existing RTM extraction,
QINFRA is its own top-level branch alongside QPLANT, and the "user side" you asked me to include
("both the supply system and the user side") is actually **QCELL + QDIST**, not WSH. WCS and QRB
sit under QPLANT in both versions — that part is not in dispute. WPS and WSH do not appear
anywhere in ABACUS's RTM-01..016 extraction at all.

**What this is not**: neither version is being asserted here as simply "right." ABACUS's version
has a stronger provenance claim (machine-extracted from the actual contract technical-requirements
text, not from typed chat or bidder-offer prose), but it only covers 16 requirements — a small
slice of the 722-item RTM this project tracks — so it may simply not have reached the WPS/WSH
material yet, rather than having ruled it out. **This needs your call, not mine**: do you want
`sbs_scope_of_supply.yaml` corrected to match ABACUS's QSYS/QPLANT/QINFRA/QCELL/QDIST tree, kept
as-is with the discrepancy flagged, or reconciled by treating QCELL/QDIST and WPS/WSH as two
different, both-real cuts of the same system (contract-requirements view vs. bidder-offer-scope
view)? No change has been made to `sbs_scope_of_supply.yaml` this round — this section only
surfaces the finding.

> **RESOLVED, round 22.** `cryoplant-project`'s own canonical architecture file,
> `ocd-adr/architecture/knowledge_tree.yaml`, states the tree verbatim:
> `QSYS(alias QPS) -> {QPLANT{WCS,QRB}, QINFRA{WPS,WSH}}` -- an exact, byte-for-byte match to this
> session's round-19 tree, not an approximation. `cryoplant-project` is explicitly the repository
> whose job is to own the QPS knowledge hierarchy (`federation_model.yaml`'s
> `qps_domain_product.responsibilities` lists `qps_knowledge_hierarchy` by name), and its files
> are dated 2026-08 (this project's own timeframe), versus ABACUS's `QPLANT_RTM_Engineering_
> Handover.md` which is dated 2025-09-24 -- nine months older, and pulled from only a 16-requirement
> partial extraction, not the maintained canonical tree. **This session's round-19
> `sbs_scope_of_supply.yaml` tree is therefore confirmed correct**, and its tags should be upgraded
> from `STATED_BY_GBO` to a new `CONFIRMED_CANONICAL_REPO` confidence level citing
> `GBOGEB/cryoplant-project:ocd-adr/architecture/knowledge_tree.yaml` directly -- not done yet in
> this file (a YAML edit, not a markdown one), flagged here so it isn't lost. ABACUS's older
> QCELL/QDIST-based document should be treated as superseded prior art, not a live discrepancy.

## 1. Repo triage — what was actually confirmed, and what was not

| Repo | Access | Confirmed identity | Notes |
|---|---|---|---|
| `GBOGEB/CODEX` | Public, cloned (`git ls-remote` succeeds) | "CODEX space for MCB (Blocks via MCP)", Python `>=3.11`, `pyproject.toml` present (`name="codex"`, deps: `PyYAML`, `requests`; dev: `pytest`) | Contains its own `EMBEDDED_REPOS.md` — CODEX has already audited ABACUS for "ghost" local-only folders (`rich_padding`, `CODESPACES_jyperter`, `codex_project`, `integration_DOW_KEB_MASTER`) that don't appear on ABACUS's public GitHub surface. Federation between these two repos already exists at the document level; this handover formalizes it further, it doesn't originate it. |
| `GBOGEB/ABACUS` | Public, cloned (`git ls-remote` succeeds) | "CodeLLM and Deep Agent place to view and drop all files", v4.4.0, 561 Python files, MIT | Contains `rtm_integration/` -- a QPLANT-specific subtree with its own RTM extraction, its own `EMBEDDED_REPOS.md`-flagged ghost folders, and (see &sect;3) an existing ALAT-clarification bridge directly overlapping this session's own recovery-system/Line-S/Line-W work. |
| `cryoplant-project` | **RESOLVED, round 22** -- confirmed private on GitHub (per your own answer), and read directly off your linked desktop at `C:\Users\gbonthuy\cryoplant-project` (a real, structured local git repo -- `.git`, `.github`, `.devcontainer` all present) | "QPS domain product repository" -- owns the QPS OCD (Operational Concept Description) + ADR (Architecture Decision Record) content model, the AS-IS Contract/RTM/OFFER-request baseline, and the canonical QPS knowledge hierarchy. Explicitly **not** meant to duplicate ABACUS/CODEX's runtime or governance responsibilities. | Round 21's six `git ls-remote` name-variant attempts all failed because the repo is genuinely private -- that failure mode was correctly read as "private or nonexistent," and it was private. See &sect;7 for the full architecture this repo defines. |

No commits, branches, or pushes were made to CODEX or ABACUS's real history this round beyond
what was already disclosed in `FEDERATION_BRIDGE_ROUND20.md` (the local-only, unpushed
`local/qps-qplant-knowledge-seed` branch).

## 1a. Real local paths (round 22, confirmed from your linked desktop)

Your desktop's OneDrive-synced `Master_Input` folder already contains
`04_GITHUB_INTEGRATION`, which is almost certainly the Windows-side counterpart of this very
project (`QPLANT_GitHub_Integration`) -- worth confirming and treating as the same thing rather
than a fifth parallel copy. The other three repos live outside OneDrive, matching
`BINARIES_MANIFEST.md`'s own stated convention ("working copies/models live in the non-OneDrive
local clones"):

| Repo | Real local path |
|---|---|
| `cryoplant-project` | `C:\Users\gbonthuy\cryoplant-project` |
| `CODEX` (full local clone, richer than this session's shallow read-only clone -- verified same content, not a divergent fork) | `C:\Users\gbonthuy\codex` |
| `ABACUS` (full local clone) | `C:\Users\gbonthuy\Clone_FrOM_GITHUB\gg_ABACUS` |
| `CODEX` (second local clone, same repo) | `C:\Users\gbonthuy\Clone_FrOM_GITHUB\gg_CODEX` |
| `QPLANT_GitHub_Integration` (this repo, probable match) | `C:\Users\gbonthuy\OneDrive - Studiecentrum voor Kernenergie\Master_Input\04_GITHUB_INTEGRATION` |

You already have two separate local CODEX checkouts (`~/codex` and
`~/Clone_FrOM_GITHUB/gg_CODEX`) -- worth confirming which one you actually work in day to day so
the PyCharm project points at the live one, not a stale second copy.

**Existing prior art, don't skip this**: `C:\Users\gbonthuy\Clone_FrOM_GITHUB\
Master_Input_ggA_ggC.code-workspace` is a real, already-configured **VS Code** multi-root workspace
joining OneDrive `Master_Input` + `gg_CODEX` + `gg_ABACUS` (GitHub Copilot enabled, squash-merge
default, GitHub Actions YAML schema validation wired up, PowerShell default terminal). You asked
for a PyCharm handover specifically, so &sect;2 below gives you the PyCharm equivalent, but it's
worth deciding whether you want PyCharm as a second, parallel setup for this work, or want the
existing VS Code workspace extended with `cryoplant-project` as its fourth folder instead of
standing up PyCharm from scratch. Not decided here -- your call.

## 2. Recommended PyCharm project layout

Four codebases, three different dependency profiles, one contractual subject. Recommended setup:
**one PyCharm project per repo**, not a single mega-project, linked via PyCharm's "Attach
directory as content root" only where you actually cross-reference files day to day (e.g.
attaching `ABACUS/rtm_integration` as a secondary content root inside the
`QPLANT_GitHub_Integration` project, so both SBS trees are visible side by side while you resolve
&sect;0). Reasons: (a) each repo already has its own Python version / dependency set (below), and
PyCharm interpreters are per-project; (b) ABACUS alone is large enough (1,730 commits, hundreds of
top-level files) that indexing it inside a shared project would slow down completion/search across
all four; (c) it keeps VCS operations unambiguous — one project window, one `.git`, no risk of
committing into the wrong repo's history.

| Repo | Python | Dependency file | Suggested venv name |
|---|---|---|---|
| `QPLANT_GitHub_Integration` (this project) | 3.x (uses `openpyxl`, `PyYAML`, `python-pptx`, `pdfplumber`, `playwright`) | none checked in yet — worth adding a `requirements.txt` this round if you want PyCharm's "Sync Python Requirements" to work | `.venv-qplant` |
| `CODEX` | `>=3.11` per `pyproject.toml` | `pyproject.toml` (`PyYAML`, `requests`; dev extra: `pytest`, `pytest-json-report`) also a plain `requirements.txt` at root | `.venv-codex` |
| `ABACUS` (root) | not pinned at root; `rtm_integration/automation/requirements.txt` pins `pandas`, `openpyxl`, `pyyaml`, `pytest`, `python-docx`, `jsonschema`, `pytest-cov` | multiple `requirements*.txt` scattered by subproject (root-level dependency story is not unified — a real finding, not a PyCharm-setup mistake) | `.venv-abacus` |
| `ABACUS/MINERVA_PID` (own subproject) | `3.8+` per its `pyproject.toml`; developed/validated on 3.11 | `requirements.txt` (`openpyxl`, `PyYAML`, `cairosvg` core; `Pillow`, `python-pptx` optional) + needs native `libcairo2` (`SYSTEM_DEPENDENCIES.md`) | `.venv-minerva-pid` (separate from the ABACUS-root venv, since it has its own `pyproject.toml`) |
| `cryoplant-project` | unknown | unknown | pending &sect;1 |

For each: **Settings &rarr; Project &rarr; Python Interpreter &rarr; Add Interpreter &rarr; Virtualenv
&rarr; New**, pointed at that repo's own dependency file. Do not reuse one shared interpreter across
all four — `MINERVA_PID`'s native `cairosvg`/Cairo dependency in particular is easy to silently
break if it shares an environment with ABACUS-root's much larger, less-pinned dependency set.

## 3. Real entry points worth wiring up as PyCharm Run Configurations

All of these were run for real this round (not just located) except where noted:

- **CODEX** &mdash; `scripts/validate_master_contract_ssot.py` (validates `ssot/master_contract_ssot_v0_2.yaml` against its schema; exit 0 confirmed) and `scripts/check_contract_workbench.py` (deterministic manifest drift guard; exit 0 confirmed). Both are also wired into `.github/workflows/master-contract-ssot-validation.yml` / `contract-workbench.yml` — a PyCharm Run Configuration mirroring these gives you the same check locally before pushing.
- **ABACUS** &mdash; `clone_based_validator.py` (CLI: `python3 clone_based_validator.py --repo-url <url> --branch main --workspace <path>`; confirmed this round: 561/561 files checksum-match, 0 circular imports, 505 orphaned). `DMAIC_V3/core/twelve_cluster_orchestrator.py` (the 12-cluster DMAIC entry point) and `DMAIC_V3/orchestrators/dmaic_postdeploy.py`'s `PostDeployOrchestrator.ingest_workspace()` (the workspace-ingestion entry point named in `FEDERATION_BRIDGE_ROUND20.md`) are both worth a Run Configuration if you intend to actually execute an ingestion rather than just read the code, though note the DOW/KEB engine imports fall back to a mock without the full ABACUS runtime present in a shallow clone.
- **ABACUS/MINERVA_PID** &mdash; `./make.sh` (regenerates all derived P&ID outputs; its own README states 31/31 tests pass fresh) plus the four `PYTHONPATH=src python3 tests/test_*.py` invocations listed in its README. Needs `libcairo2` installed system-side first (`SYSTEM_DEPENDENCIES.md`).
- **ABACUS/rtm_integration/contract_followup/alat_clarification_bridge** &mdash; `tools/generate_bridge.py --ssot ssot/alat_questions_ssot_v0_1.yaml --out dist` (produces an xlsx + html view of the Q3/Q4/Q5 clarification tracker described in &sect;4). Not run this round — flagged for awareness, not executed, since it touches a live bidder-clarification workflow that should not be regenerated without your say-so.
- **QPLANT_GitHub_Integration** (this repo) &mdash; every `02_SCRIPTS/build_*.py` script is already its own natural Run Configuration; `status_legend.py` should never appear as a target itself (it's the imported taxonomy module every builder depends on, per the standing "no duplicated SSOT" rule).

## 4. Overlap found this round that needs reconciling, not duplicating

**`ABACUS/rtm_integration/contract_followup/alat_clarification_bridge/`** is a small (38 lines of
YAML total across its 3 SSOT files), already-scaffolded package tracking **ALAT bidder
clarification questions under exactly three heads: Q3 = Recovery System, Q4 = Line S, Q5 = Line
W** — the identical subject matter this session's own round-18/20
`QPS_SBS_Scope_Boundary_and_Recovery_Navigator.html` covers in depth (the recovery-system
deep-dive, and the U/S/W line-code glossary from LKT's Distribution Panel). Its `README.md` states
its contractual origin is locked to `MASTER.docx` + `QPS_Contract_mirror_DOCX(1).pdf`, and that
"the YAML SSOT is the working clarification model only. It does not replace the locked contract
source" -- the exact same posture this project's own SSOT files already take relative to the two
bookmarked offer PDFs. Its `OFFER_REGISTER.yaml` (12 lines) currently shows `bidder: ALaT,
status: Open`, with `review_state` for `dsbt`/`dbe`/`qcell`/`ped` all `Open`.

This is a real, disclosed overlap risk: two independent workstreams (this session's, and this
pre-existing ABACUS package) are tracking the same three clarification topics without referencing
each other. Nothing was merged or generated from either side this round -- surfacing this is as far
as this handover goes, since actually reconciling them (deciding which SSOT is authoritative for
the Q3/Q4/Q5 clarification questions specifically, separate from the broader RTM/OFFER compliance
tracking this project owns) is a decision for you, not something to guess at.

## 5. Git/VCS handling across four repos in one PyCharm window layout

- `QPLANT_GitHub_Integration` is a local-only git repo (`main` branch) with no remote configured —
  PyCharm's VCS menu will show it as a plain local repo; there is nothing to accidentally push
  here yet.
- `CODEX` and `ABACUS` clones under `/tmp/repo_audit/` are shallow (`--depth 60`), read-only-intent
  clones of the real public repos. ABACUS additionally has one extra local branch,
  `local/qps-qplant-knowledge-seed` (one commit, disclosed in full in
  `FEDERATION_BRIDGE_ROUND20.md`), not merged and not pushed. If you open these clones in
  PyCharm, the VCS log will show real GBOGEB history plus that one local commit — do not push
  either clone's `main` or the local branch to `origin` without deciding to first; per this
  session's standing git-safety rule, nothing here does that automatically.
- If/when `cryoplant-project`'s real location is confirmed, treat it the same way: read-only clone
  or local folder first, no push until you say so.

## 7. The real federation model (round 22 -- supersedes Round 20's guess on this point)

Round 20's `FEDERATION_BRIDGE_ROUND20.md` answered "what does the parent pipeline do with this
information" using ABACUS's generic `dmaic_postdeploy.py` (DOW classification + KEB metrics +
GBOGEB knowledge update + dashboard link), because that was the best evidence available without
access to `cryoplant-project`. Now that `cryoplant-project/ocd-adr/architecture/federation_model.yaml`
(schema `ocd-adr-federation-model/v2`) is readable, that answer is superseded by something far more
specific and precise, already fully designed:

**Four planes, one still unresolved:**

| Plane | Repository | Responsibilities |
|---|---|---|
| `qps_domain_product` | `GBOGEB/cryoplant-project` | governed QPS source bundle, AS-IS Contract/RTM/OFFER-request baseline, QPS knowledge hierarchy, OCD content, ADR content, QPS release assembly |
| `runtime_analysis` | `GBOGEB/ABACUS` | orchestration, runtime validation, engineering/scientific kernels, binary-processing feedback, provenance-aware analysis, federation execution |
| `governance_automation` | `GBOGEB/CODEX` | governance, certification, audit, operational policy, automation, CI/portal surfaces |
| `supervisory_analysis` | **`UNRESOLVED_BIGBROTHER_REPOSITORY`** -- `status: provisional_until_exact_repo_identity_is_confirmed`, per the file's own text | cross-repository observation, drift/anomaly analysis, coverage/freshness analysis, trend/risk feedback, **recommendation only** -- explicitly barred from mutating QPS SSOT, promoting authority, approving ADRs, or overwriting controlled source content |

That fourth plane is a real, disclosed gap in your own architecture, not something this session
is inventing: the spec names the role and its authority limits precisely, but has no repository
assigned to it yet. **Worth naming directly**: this session's own `QPLANT_GitHub_Integration`
work -- comparing ALAT vs LKT, tracking compliance drift, flagging coverage gaps across 722 RTM +
50 OFFER items, producing recommendation-only findings that never silently overwrite either
bidder's SSOT -- matches the `supervisory_analysis` responsibility list closely enough to be worth
your consideration as a candidate for that slot, or at least a close cousin of it. Not asserted as
settled; your architecture, your call.

**"Trickle down," precisely defined** (this is the real mechanism, not the round-20 guess): six
named interaction types govern all cross-repo data flow -- `INIT-BASELINE` (once per new baseline
family, cryoplant-project pushes its hierarchy/receipts/hashes outward to the other three planes),
`SOURCE-CHANGE` (event-driven, fires on a governed source hash/semantic delta), `ANALYSIS-REQUEST`
(on-demand, cryoplant-project asks ABACUS for a specific engineering analysis),
`SUPERVISORY-FEEDBACK` (the BigBrother plane's only sanctioned channel back into cryoplant-project
-- explicitly "proposed/derived evidence or an open item," promotion into canonical content
requires normal QPS governance), `PRE-RELEASE-GATE`, and `POST-RELEASE-ROLLUP`. Every one of these
carries a **minimum bridge tuple** (source id, source SHA-256, semantic SHA-256, authority,
lifecycle status, hierarchy node, trace links, producer repo+commit, parser/builder version,
artifact hashes, freshness state, supersedes) -- this is what "roll up to the federated body of
knowledge" concretely means: propagate the tuple, never mutate source authority.

This exact design pattern is already live, not just specified: `QPS_FED_W04_EXECUTABLE_PARENT_
RETURN_JOIN_v0.1.yaml` (also read from `cryoplant-project` this round) shows real, merged PRs
implementing one wave of it -- cryoplant-project PR #143/#146 (child-owned disposition scaffolding
and return-artifact bindings), ABACUS PR #725 and CODEX PR #270 (parent-side receipt validators,
`tools/validate_qps_w04_dow_receipt.py` and `tools/validate_qps_w04_keb_receipt.py`), gated by an
explicit rule that "no returned finding changes QPS SSOT ... until the child explicitly
dispositions it" (ACCEPT/REJECT/DEFER, each requiring a rationale and an evidence reference). At
the time these files were read, the wave was sitting at stage A1 (`ACTIVE`, both parent validators
merged but their runtime receipts still `PENDING_EXECUTION_OR_BINDING`), with stages A2-A5
(child disposition, SSOT assimilation, reverse feedback, gate/metric refresh) all `BLOCKED_BY`
the stage before it -- a real, current, in-progress state, not a finished pipeline.

**One directly actionable convention worth adopting here**: `cryoplant-project/BINARIES_MANIFEST.md`
documents a binary-segregation convention (canonical binaries live in OneDrive `Master_Input`;
working/model copies live in the non-OneDrive local clones; a `BINARIES_MANIFEST.md` +
`checksums.sha256` sidecar records what belongs where without git ever tracking the binary itself)
that it says is "same convention already used in the sibling `CODEX` repo under
`GISTAU/sources/master/`." `QPLANT_GitHub_Integration` currently just gitignores binaries outright
with no manifest/checksum sidecar at all -- adopting the same convention here (rather than
inventing a fourth variant) would make this repo's binary handling consistent with its two
siblings. Not done this round -- flagged for your decision.

## 8. Next steps, in order

1. Decide how to resolve &sect;0's now-resolved-with-evidence SBS discrepancy in practice: update
   `sbs_scope_of_supply.yaml`'s confidence tags from `STATED_BY_GBO` to cite
   `cryoplant-project:ocd-adr/architecture/knowledge_tree.yaml` directly (a small, mechanical
   change, not done yet).
2. Decide whether `QPLANT_GitHub_Integration` should formally take on the `supervisory_analysis` /
   "BigBrother" role named in `federation_model.yaml`, informally align with it without the formal
   label, or stay independent of that federation entirely.
3. Decide whether the &sect;4 ALAT clarification-bridge overlap (Q3/Q4/Q5 = Recovery/Line
   S/Line W) should be merged into this session's SSOT, left as ABACUS's separate ownership, or
   explicitly cross-linked.
4. Decide whether to adopt cryoplant-project/CODEX's binaries-manifest + checksum-sidecar
   convention for this repo's own binaries (&sect;7).
5. Decide on the PyCharm-vs-existing-VS-Code-workspace question in &sect;1a.
