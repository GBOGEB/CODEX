# CODE PURPLE REX — October ABACUS control candidate

**State:** source-bound candidate for independent CODEX acceptance.
Not a global REX ledger mutation, a worker launch or a QPS engineering acceptance.

## Source and normal execution

The originating issue is [ABACUS #1860](https://github.com/GBOGEB/ABACUS/issues/1860).
The supporting PRs are [#1858](https://github.com/GBOGEB/ABACUS/pull/1858)
and [#1876](https://github.com/GBOGEB/ABACUS/pull/1876).
Cross-iteration proof-reuse work remains in
[ABACUS #1877](https://github.com/GBOGEB/ABACUS/issues/1877).
MissionControl remote execution remains HOLD under
[CODEX #977](https://github.com/GBOGEB/CODEX/issues/977).

The return is in
`federation/rex/returns/ABACUS_CODE_PURPLE_20261012_REX_RETURN.yaml`.
The canonical global ledger and taxonomy stay unchanged until acceptance.

Run:

```sh
python -m pip install "PyYAML>=6,<7"
python -m unittest discover -s tests -p test_code_purple_rex_rollup.py -v
python scripts/code_purple_rex_rollup.py
python scripts/code_purple_rex_rollup.py --check
python -m http.server 8000 --directory docs
```

Open `http://localhost:8000/code_purple_rex_control.html` for
TOP7/14/21, source-specific REX details, provenance and KPI unknown states.
The targeted CI also publishes the generated JSON as a 30-day artifact.
The `pull_request` artifact name uses the **checked-out PR head SHA**, not the
synthetic `github.sha` merge-ref SHA. Consumers shall verify the artifact
content digest independently; an artifact name alone is not attestation.
The exporter accepts only the canonical governed return as `--source`.
Alternate-path and altered-in-memory records are refused rather than
misattributed to the canonical SHA-256 path.

**Post-merge follow-up:** CODEX #988 merged as
`cce9ce20c8ca8d3ea5d11ec077567c24e97e379e`. Three P2
findings arose in post-merge review. The required follow-up withholds
all independent verification credit when a REX source merely declares
`PASS` or `VERIFIED`: the projected effective state becomes
`VERIFICATION_PENDING` with source-declared evidence retained separately.
A source PASS string, GitHub-looking URL, syntactically valid SHA or
run ID is not authenticated terminal-job or named-security-reviewer proof.
Do not treat this candidate as admitted to the global REX ledger.

GitHub Pages requires a separate governed publication/content readback.

## DMAIC Control

The candidate records eight distinct signatures from the observed cohort.
Two material security P1s on #1858 remain open. Some repairs are committed
but not independently admitted. The #1876 documentation-lint job went
from [failed](https://github.com/GBOGEB/ABACUS/actions/runs/38253244397)
to [successful](https://github.com/GBOGEB/ABACUS/actions/runs/38254422522)
on a different exact head, without a validator waiver.

The rank score is **a transparent selection heuristic**, not observed PCA
or a safety-risk acceptance. TOP7, TOP14 and TOP21 are rank capacities
over the eight observed candidates, not 7/14/21-day time series.
Cross-unit frequencies are never totaled. The 25 Markdown errors belong
to one failed job and count as one REX signature.

Current main/PR/diff coverage, BD queue totals, true runner-minute savings,
authenticated CODEX worker runs and PCA remain `null` / UNKNOWN.
Historical coverage is explicitly separated from current measurements.

## Security, review and propagation

- CODEX owns the global REX/Control **lookup candidate**.
- ABACUS owns its code/test/runtime/security evidence.
- QPS TRIAGE owns independent read-only consumer acceptance and
  engineering/release authority. QPS rank 3–7 closures shall not reopen
  merely because an advisory REX candidate arrived.
- The 0 required GitHub review-approval count does not satisfy the
  repository-native exact-head Code/ Security Review contract.
- The strict required `PR Feedback Gate` on ABACUS main cannot be replaced
  by a GitHub Actions Matrix pass.
- Temporary break-glass is an owner-managed, independently assessed,
  time-bounded exception and is **not** performed by this exporter.
- No force-push, agent attestation, broad ruleset disable, ungoverned
  dispatch or false merge claim.

Accept this candidate only after independent CODEX review and terminal
exact-head CI. Then return a bound global REX acceptance/merge receipt,
not merely a link. Obtain QPS consumer QA in a separate follow-on.
