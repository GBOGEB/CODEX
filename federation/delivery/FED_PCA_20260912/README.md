# Federation delivery - FED-PCA-20260912-R1

Open `Federation_Delivery.html` after extracting the release archive. It links to the Excel register, five-page PDF, delivery SSOT, Zod receipt and release hashes. The HTML is a local release view, not a live hosted dashboard.

## Authority

`delivery_ssot.json` is the versioned action and lineage register. `Federation_Delivery.xlsx` contains the numerical summary formulas and the review list; HTML and PDF are read-only projections. Edit the input register and regenerate before issuing another release. No bidder numerical SSOT or engineering score was changed.

CODEX owns KEB terminology/contracts/provenance. ABACUS owns DOW consumption. cryoplant-project remains the child engineering/disposition authority. DOCX_RTM_Automation supplies document capability. Zod verifies identifiers, state vocabulary, source references and acyclic dependencies; it cannot establish engineering truth.

## Runtime

Install the pinned package dependency (`npm install`) and run `npm run validate`. The validator checks the real register and five negative controls. It emits `contract_receipt.json` bound to the exact input SHA256.

The CODEX/ABACUS/cryoplant repair PRs #636/#1132/#931 are merged. Merge-SHA verification found CODEX bridge PASS, CODEX semantic tests failing on GLOB YAML, ABACUS missing requests, and cryoplant runner_id=0 with zero steps. Current main GLOB quoting was checked; full new-head tests were not inferred from that correction. ABACUS follow-up #1148 replaces the partial dependency list with the existing requirements-test.txt.

## Rebuild

1. Refresh and inspect `runtime_sources.json`; update action dispositions only with scoped evidence.
2. Run `python build_register.py`, then `npm run validate`.
3. Run `build_excel.mjs` with `@oai/artifact-tool` in the Codex primary runtime and this directory as its argument. The Excel builder is an environment-dependent authoring adapter, not a standalone npm package.
4. Run `python build_views.py` with reportlab installed.
5. Run the retained browser checks, inspect PDF/Excel renders and run `finalize_release.py` to check parity and produce hashes and the handover archive.

## Next execution

N+1: relevant CODEX and ABACUS runtime PASS; cryoplant ordinary runner assignment. N+5: automate regenerating this pack under CI. N+10: three comparable telemetry pulses with queue and execution durations separately. N+50: repeated CONTROL and selective expansion based on residual blockers.

Stop each lane at missing source authority, unavailable runner, or review-dependent execution. Preserve first-red evidence and the next predicate. Do not widen test exclusions or promote a zero-step run. Global DoV remains WITHHELD.
