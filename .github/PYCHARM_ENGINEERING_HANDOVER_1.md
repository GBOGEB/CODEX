# PyCharm Engineering Handover — QPLANT_GitHub_Integration &harr; ABACUS &harr; CODEX &harr; cryoplant-project

Round 21, corrected and substantially extended in Round 22, corrected again in Round 23, extended
with a new finding in Round 24. Written for whoever (including future-you) opens this work in
PyCharm next.

> **Round 24 addendum, read this first.** &sect;4 below (Rounds 21-23) describes the ALAT
> Q3/Q4/Q5 clarification-bridge overlap as a two-way question -- "ABACUS has a package, this
> session's work covers the same ground." That framing is stale. **CODEX itself already has its
> own independent copy** of the same package at
> `rtm_integration/contract_followup/alat_clarification_bridge/` in this repo -- full `README.md`,
> `ssot/alat_questions_ssot_v0_1.yaml`, `RTM_LINKS.yaml`, `OFFER_REGISTER.yaml`, `tools/
> generate_bridge.py` + `tools/validate_ssot.py`, a review-gate doc, and a dedicated test file
> (`tests/test_alat_clarification_bridge.py`), with real git history of its own going back to
> `d7e2d80 "C017 add ALaT review merge gate"`. Nothing in that package's files or commit history
> references ABACUS's package of the same name and purpose. So this is not a two-way "ABACUS vs.
> this session" overlap any more -- it is a **three-way duplication** (ABACUS, CODEX, and the
> QPLANT_GitHub_Integration session work), and on the CODEX side it is not just awareness of a
> risk, it is a full, tested, independently-built implementation. Both CODEX guard scripts
> (`scripts/validate_master_contract_ssot.py`, `scripts/check_contract_workbench.py`) still exit 0
> with this package present, so nothing here is broken -- the duplication is a reconciliation
> question, not a defect. Full detail added inline in &sect;4 below; &sect;8 item 3 updated to
> reflect the three-way state. No file other than this handover has been changed to record this
> finding -- no SSOT was merged, and no code was moved between repos.

> **Round 23 correction, read this first.** Round 22's &sect;0 "RESOLVED" verdict overclaimed. It
> confirmed this session's `QINFRA = WPS + WSH` tree by citing
> `cryoplant-project:ocd-adr/architecture/knowledge_tree.yaml` -- but that file says of itself
> (line 2-3) that it is *"navigation and structure, not a substitute for governed source evidence
> or the generated OCD/ADR artefacts."* Working this round from CODEX's own local clone (this
> repo) which contains the actual Addendum II contract text ingested as `book_md/`, three
> contract-official abbreviation-table facts settle this independently of either prior tree:
> `book_md/I1_abbreviations.md:22` defines **CSS = QPLANT + QINFRA + QDIST** verbatim;
> `book_md/1_introduction.md:32` states **"QDIST comprises the QLM, the string of QVBs, and the
> QVE"**; `book_md/I1_abbreviations.md:101` defines **QCELL = QVB + QM**. The CSS formula is
> direct textual support for ABACUS's `QPLANT/QINFRA/QDIST` peer-branch tree, not for this
> session's `QINFRA = WPS + WSH` tree. Separately, `cryoplant-project`'s own canonical (not
> navigation-index) artifact, `ocd-adr/20_canonical/ocd/QPS_OCD_v0.8_CONSOLIDATED.md` --
> RTM-cited, `canonical_role: primary_engineering_output` in `knowledge_tree.yaml`'s own schema --
> draws WSH as a direct child of QPS (not nested under QINFRA) and places WPS, QDB, and
> "QCELLs / cryogenic users" *outside* the QPS boundary entirely as external interfaces; this is
> corroborated by `cryoplant-project`'s `ADR-QPS-006`, which states the WPS Contractor (not the
> QPS Contractor) owns site connection. So: **Round 22's "confirmed correct, ABACUS superseded"
> verdict does not hold.** ABACUS's `QPLANT/QINFRA/QDIST` peer structure has direct contract-text
> support; this session's `QINFRA = WPS + WSH` does not, on either contract-text or
> `cryoplant-project`'s own canonical-artifact grounds. Per `cryoplant-project`'s own
> `federation_model.yaml`, `contract_addendum_ii` is `precedence: 1, tie_rule: contract_wins` over
> both the RTM projection (precedence 2) and any navigation index -- so the contract abbreviation
> table outranks all three prior trees where they conflict with it. Full reconciled tree and
> reasoning: see the correction block inserted into &sect;0 below. No file outside this handover
> and `federation_bridge/bridge_manifest.yaml` (a read-only reference entry, no content copied) has
> been changed this round; `sbs_scope_of_supply.yaml` itself was not touched -- that edit is still
> a decision for you, now with better evidence to make it from.

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
> flagged explicitly rather than silently replaced. **Round 22's &sect;0 verdict itself was
> partly wrong -- see the Round 23 correction above, and inline in &sect;0 below.**

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

> **SUPERSEDED, round 23.** The paragraph immediately above over-trusted
> `knowledge_tree.yaml` -- a file whose own header (line 2-3) calls it "navigation and structure,
> not a substitute for governed source evidence." Reconciled tree, built this round from (a) the
> Addendum II contract text as ingested into CODEX's `book_md/` (the highest-precedence source per
> `cryoplant-project`'s own `federation_model.yaml`: `contract_addendum_ii`,
> `precedence: 1, tie_rule: contract_wins`), and (b) `cryoplant-project`'s own canonical
> `QPS_OCD_v0.8_CONSOLIDATED.md` + `ADR-QPS-006`:
>
> ```text
> CSS (Cryogenic Supply System)  -- book_md/I1_abbreviations.md:22, verbatim contract definition
> ├── QPLANT                      -- main refrigeration plant
> │   ├── WCS                     -- Warm Compressor Station
> │   └── QRB                     -- "QPLANT Refrigeration Cold Box" (I1_abbreviations.md:111)
> ├── QINFRA                      -- interface/infrastructure branch; U/W/S warm lines into WCS.VLP
> └── QDIST                       -- "comprises the QLM, the string of QVBs, and the QVE"
>                                     (1_introduction.md:32)
>
> QCELL = QVB + QM (I1_abbreviations.md:101)  -- user cryomodules; per cryoplant-project's own
>   QPS_OCD_v0.8_CONSOLIDATED.md, explicitly OUTSIDE the QPS/CSS boundary, not a QPLANT/QINFRA child
> WSH (Warm Storage Helium) -- direct QPS-level sibling of QPLANT in QPS_OCD_v0.8_CONSOLIDATED.md,
>   NOT nested under QINFRA; functionally an intermediate reservoir tied to WCS
> WPS (Warm Piping System) -- per ADR-QPS-006, owned/site-connected by a separate "WPS Contractor",
>   external to QPS entirely; interfaces to QRB only via the QINFRA.U/W/S terminal points
> QDB -- appears in ADR-QPS-006 ("QRB-QDB/QLM interface") but is NOT in the contract's own
>   abbreviations table; given QLM is the core of QDIST and RTM-281..285 describe a
>   "QDB-Contractor"-led interface, QDB is most likely a contractor/round-specific label for the
>   QDIST-side boundary, not a fifth distinct system -- flagged as probable, not confirmed; worth
>   a direct question to GBO rather than further inference.
> ```
>
> **Net effect on the three-way dispute:** ABACUS's `QSYS → QPLANT/QINFRA/QCELL/QDIST` peer
> structure is directly supported by the contract's own CSS definition -- it was closer to right
> than Round 21/22 credited, not "superseded prior art." This session's round-19
> `QINFRA = WPS + WSH` tree is not supported by the contract text or by `cryoplant-project`'s own
> canonical OCD/ADR content -- WPS is external to QPS per `ADR-QPS-006`, and WSH sits directly
> under QPS per `QPS_OCD_v0.8_CONSOLIDATED.md`, not under QINFRA. Recommended action on
> `sbs_scope_of_supply.yaml`: correct it to the reconciled tree above (citing
> `book_md/I1_abbreviations.md`, `book_md/1_introduction.md`, and
> `cryoplant-project:ocd-adr/20_canonical/ocd/QPS_OCD_v0.8_CONSOLIDATED.md` as sources, at
> `CONTRACT_TEXT` / `CONFIRMED_CANONICAL_REPO` confidence respectively) rather than the
> `STATED_BY_GBO` -> `CONFIRMED_CANONICAL_REPO` upgrade Round 22 proposed. Not done yet -- still a
> YAML edit belonging to you, now with contract-grounded evidence to make it from. `QDB` remains
> open and should be asked about directly rather than assumed.

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

> **UPDATED, round 24 -- this is a three-way duplication, not two-way.** CODEX (this repo) has its
> own full copy of the same package, independently built, at
> `rtm_integration/contract_followup/alat_clarification_bridge/`:
> `README.md`, `ssot/alat_questions_ssot_v0_1.yaml`, `RTM_LINKS.yaml`, `OFFER_REGISTER.yaml`,
> `tools/generate_bridge.py`, `tools/validate_ssot.py`, `docs/review_checklist_merge_gate.md`,
> three response/summary templates, and a dedicated pytest file
> (`tests/test_alat_clarification_bridge.py`) that asserts the SSOT/RTM/OFFER trio validates
> clean. Its git history is real and CODEX-native --
> `d7e2d80 "C017 add ALaT review merge gate"`, `7b8a39d "Address ALaT bridge review gate gaps"`,
> `73fe6a4 "Clarify ALaT bridge pre-ready gates"`, `b45d5c3`/`d87c687` ("Potential fix for pull
> request finding") -- not a copy-paste of ABACUS's package: a `grep -rn "ABACUS"` across the whole
> directory returns nothing, so the two were built without cross-reference. CODEX's `README.md`
> states the same posture ABACUS's and this session's do: contractual origin locked to source
> documents, "does not replace the locked contract source." Practical effect: there are now three
> independent SSOT surfaces for the identical Q3 (Recovery System) / Q4 (Line S) / Q5 (Line W)
> clarification questions -- ABACUS's, CODEX's, and the QPLANT_GitHub_Integration session's
> `QPS_SBS_Scope_Boundary_and_Recovery_Navigator.html`. All three currently pass their own local
> checks in isolation, which is exactly the failure mode that lets three SSOTs quietly drift apart
> without anyone noticing until a bidder-facing answer disagrees with itself across repos. Not
> reconciled this round -- flagged so the &sect;8 decision is made with the real (three-way) shape
> of the problem, not the two-way shape Rounds 21-23 described.

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
2. **TODO, low priority (GBO, 2026-08-31).** Decide whether `QPLANT_GitHub_Integration` should
   formally take on the `supervisory_analysis` / "BigBrother" role named in `federation_model.yaml`,
   informally align with it without the formal label, or stay independent of that federation
   entirely. Explicitly deprioritized in favor of binary/document artifact output and
   OneDrive/Office365 editing integration -- see the new &sect;9.
3. Decide how to reconcile the &sect;4 ALAT clarification-bridge overlap -- now confirmed
   three-way (ABACUS's package, CODEX's own independently-built package at
   `rtm_integration/contract_followup/alat_clarification_bridge/`, and the QPLANT_GitHub_
   Integration session's Q3/Q4/Q5 = Recovery/Line S/Line W coverage): pick one as authoritative
   and retire or cross-link the other two, or keep all three and add explicit cross-references so
   they can't silently drift apart. Not something to guess at.
4. Decide whether to adopt cryoplant-project/CODEX's binaries-manifest + checksum-sidecar
   convention for this repo's own binaries (&sect;7).
5. **Partly settled (GBO, 2026-08-31).** &sect;1a's PyCharm-vs-VS-Code question isn't an either/or:
   GBO knows the VS Code environment well and will keep using it day to day, but finds PyCharm the
   better IDE specifically for working with Claude and repo navigation (still learning PyCharm and
   its GitHub-integration side). Both stay in use for different purposes -- no need to retire
   either or force a single-tool standardization.
6. **New (GBO, 2026-08-31).** Decide which OneDrive/Office365 editing-integration option in
   &sect;9 to invest in beyond what already exists: (A) keep the existing local-OneDrive-folder
   sync path as the only mechanism (zero new work, already governed), (B) add a Microsoft Graph
   API integration for direct programmatic read/write to OneDrive/SharePoint without depending on
   the desktop sync client being running, or (C) add local Office COM automation
   (`pywin32`/`win32com.client`, Windows-only) for precise Word/Excel/PowerPoint formatting Python
   libraries can't reach. Also decide whether to build the docx/pptx/pdf authoring capability
   `BUILDER_CONTRACT.md` specifies (currently deliberately unimplemented in CODEX -- see &sect;9).

## 9. Binary/document artifact inventory and OneDrive/Office365 editing options (round 24 addendum)

**What CODEX can create today, confirmed by reading the actual code (not inferred):**

| Format | Creatable? | Where |
|---|---|---|
| `.xlsx` | **Yes** | `codex/contract_governance/builder.py` (`openpyxl.Workbook`) -- Requirements / Traceability Matrix / Extraction Audit / Evaluation Notes sheets, tiered `internal`/`bidder` visibility. Also `rtm_integration/contract_followup/alat_clarification_bridge/tools/generate_bridge.py` (produces an xlsx + an html view). |
| `.html` | **Yes** | Same ALaT bridge tool; `analytics/qps_thermo_dashboard/*.html`; `src/tools/slide_preview_generator.py`'s `slide_preview.html`. |
| `.pptx` | **Read/ingest only, not authoring.** | `src/ingress/pptx_semantic_ingress_runtime_v1.py`, `src/ingress/pptx_geometry_semantic_runtime_v1.py`, `src/tools/slide_preview_generator.py` all open existing `.pptx` files (`python-pptx`'s `Presentation(path)`) to extract text/geometry/preview JSON+HTML. None of them write a new `.pptx`. |
| `.docx` | **No capability found.** | No `python-docx` import anywhere in this repo outside `.venv`. |
| `.pdf` | **No capability found in CODEX.** | Not produced by anything in this repo. |

**Specified but deliberately not implemented here**: `07_ops/qps_roundtrip/BUILDER_CONTRACT.md`
requires an external builder to produce exactly `QPS_COST_Master.xlsx`,
`QPS_Cost_Engineering_Handover.docx`, `QPS_Cost_Management_Deck.pptx`,
`QPS_Cost_Engineering_Handover.pdf`, `index.html`, `QA_REPORT.md`, `RELEASE_NOTES.md`,
`BUILD_META.json` -- but `07_ops/qps_roundtrip/README.md`'s own scope boundary states this
directory is "deliberately generic" and "must not contain QPS bidder values, confidential evidence
text or generated deliverables"; `Invoke-QpsControlledRoundtrip.ps1` "deliberately does not embed
the QPS cost-model builder. It orchestrates any approved builder that satisfies this interface."
The docx/pptx/pdf-producing builder itself lives outside CODEX (per the same file, canonical QPS
analytics remain in `GBOGEB/ABACUS`; project-specific confidential text in a private overlay).

**The OneDrive write/publish/review pipeline already exists and is already governed** -- this
directly answers "I want the write to local OneDrive which is also OneDrive in the cloud":

- `Initialize-QpsWorkspace.ps1` builds working trees **outside** OneDrive (so Git and the OneDrive
  sync client never fight over the same files while a build is in progress).
- `Publish-QpsRelease.ps1` then copies the *completed* release into
  `$env:QPS_RELEASE_ROOT` (an env var pointed at `<OneDriveRoot>\QPS\Cost Estimate\10_RELEASES` --
  never hardcoded in source, per README's explicit rule), verifying every file's SHA-256 at the
  destination before declaring success. Because that destination is inside the OneDrive-synced
  folder tree, the local write **is** the cloud write -- the OneDrive client picks it up and
  syncs it automatically; no separate cloud-upload step or API call exists or is needed for the
  basic publish path.
- `-CreateOfficeReviewCopy` on that same script additionally writes a second, mutable copy into
  `20_WORKING_REVIEW` (sibling of `10_RELEASES`) -- this is the actual **editing environment**:
  open that copy directly in desktop Word/Excel/PowerPoint (native OneDrive integration handles
  save/sync) or in Office 365 for the web (office.com opens the same synced file straight from
  OneDrive/SharePoint) -- either way, no custom integration code required for basic open/edit/save.
- `New-QpsReviewChange.ps1` is the governed loop *back*: every edit made in that Office review copy
  gets logged as a CSV ledger row (`QPS-CHG-#####`) with reviewer, change class
  (`DATA`/`CALCULATION_LOGIC`/`NARRATIVE`/`FORMATTING`), rationale, and a disposition state machine
  (`OPEN` -> `ACCEPTED`/`REJECTED`/`SUPERSEDED`/`IMPLEMENTED`) -- matching README's stated sequence
  "...create separate Office review copy -> register review changes -> assimilate approved changes
  into text source." Edits in Office never silently become the new source of truth; they're
  proposals until dispositioned.
- Confirmed real evidence root already in use: `C:\Users\gbonthuy\OneDrive - Studiecentrum voor
  Kernenergie\Master\_Input\OFFERS\_ITT` (`07_ops/qps_roundtrip/QPS_WCS_QRB_rev1_7_roundtrip.md`).

**What is not yet built, if more than the sync-folder path is wanted** (see &sect;8 item 6 for the
decision this needs):

- **Microsoft Graph API** integration (`/me/drive/root:/path:/content` etc.) -- lets a script push
  to OneDrive/SharePoint directly over HTTPS without depending on the desktop sync client being
  installed or running, and opens the door to real-time co-authoring session info, comment threads,
  and version history via API rather than filesystem inspection. Requires an Azure AD app
  registration and delegated/application permissions -- a real security/governance decision, not
  something to add unilaterally.
- **Local Office COM automation** (`pywin32` / `win32com.client`, Windows-only, requires desktop
  Office installed) -- for precise formatting operations `openpyxl`/`python-pptx`/`python-docx`
  can't reach (e.g. exact PowerPoint animation timing, Word field codes, Excel pivot-table
  refresh), or for driving an already-open document. Heavier and more fragile than the file-based
  approaches above; worth it only for specific formatting gaps, not as a general strategy.
- **`.docx`/`.pptx`/`.pdf` authoring in Python** (`python-docx`, `python-pptx` write mode, a
  PDF renderer) -- currently zero capability in CODEX for any of the three, versus full `.xlsx`
  authoring already in place. If CODEX is meant to produce (not just ingest) the docx/pptx/pdf
  outputs `BUILDER_CONTRACT.md` names, this is real, unstarted implementation work, separate from
  the OneDrive-write question above.
