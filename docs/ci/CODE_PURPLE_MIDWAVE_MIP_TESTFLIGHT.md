# CODE PURPLE — mid-wave pulse / MIP testflight (candidate v1)

Status: DRAFT, diagnostic only. No CI result or bot comment confers security approval, merge authority, local runner evidence, or QPS engineering acceptance. Primary recovery: CODEX #1037; ABACUS #1860/#1929.

## 1. Execution modes and schedule

| Mode | Trigger | Identity and effect |
|---|---|---|
| Stage 0 preflight | local developer, `pull_request` (path-filtered) | exact checkout SHA, unit negatives, branch-aware focused line coverage >=80%; no write token |
| Stage 1 mid-wave | manual `workflow_dispatch` | same source checkout, bounded org/read-only census; comments only to CODEX issue #1037 if new bot findings |
| Stage 2 pulse | six-hour cron (`17 */6 * * *`) **after reviewed merge to main** | sample 12 priority repositories, compare latest comment fingerprints against issue receipt, only new observations trigger comments |
| Stage 3 completion | independent existing CI/security/reviewer/branch-protection gates | DoV remains HOLD until separately established; never self-merge |

`concurrency.cancel-in-progress=false`: queue another run rather than terminating a nearly completed wave. Do not increase cadence while the ABACUS PR Feedback Gate is noisy. Scheduled workflow runs on the default branch only once deployed; PR testing exercises the unit-test job, not a cross-repo scan or issue write.

Resume identity is `root_id + source_sha + comment_fingerprint`. The canonical CODEX #1037 issue stores the latest idempotent comment fingerprint ledger **only when new bot findings appear**. Prior source-SHA evidence is preserved as history but cannot count as new-head passing coverage/security. Work continuity and verification admission are distinct.

## 2. Bot coding/security review intake

Sources: PR discussion comments, inline review comments, and submitted reviews for active CODEX/ABACUS PRs, bounded to five open PRs per sampled repo. Bot identities include `*[bot]`, `chatgpt-codex-connector`, `github-actions`, and `dependabot`. Each receipt includes repository, PR, observed PR SHA, comment URL, identity, timestamp, semantic class and a SHA-256 comment fingerprint.

Security, coverage, code and other review findings are **not approvals**. Human reviewer and current policy checks remain separate. No unsanitized bot text is executed, replayed, or posted. New-finding comments use links/IDs; unchanged observations do not create another issue comment. Failure to read a comments endpoint is not proof of zero findings.

## 3. Preconfigured tooling and real execution boundaries

| Surface | Observed configuration | What would verify execution |
|---|---|---|
| Local developer fast pre-commit | ABACUS `.pre-commit-config.yaml`: pre-commit-hooks v5.0.0 (merge/json/yaml/toml, EOF, whitespace) and `python scripts/testpilot_preflight.py --mode fast` | local hook output + machine receipt; repo-wide historical EOF/Ruff debt must not be silently normalized |
| ABACUS tests/coverage | `.github/workflows/mip-coverage-evidence.yml`, `.github/workflows/testpilot-preflight.yml` | matching full checkout SHA, canonical pytest JUnit and coverage context JSON; distinguish measured executed/eligible lines/branches from configured thresholds |
| Lint/security | ABACUS `bandit.yml`, `bandit-disjoint-census.yml`, `security-scan.yml`; CODEX `bandit.yml`, `security-scan.yml`, CodeQL/OSV | scan config fingerprint + findings + exact SHA/run/job/artifact, no unsafe default auto-fix |
| RHEL | CODEX `quality-ubi-testflight.yml` executes Docker UBI9 by image digest; ABACUS DOW RHEL 8/9 workflow jobs exist | actual container digest/OS, executed steps, nonempty receipts and matching SHA; skipped != passed |
| LLDB/DAP | CODEX `lldb-dap-swift-docker-runner-mcp.yml` supports macOS Swift LLDB and Docker probes | specific job/session ID, image digest/port lease, process execution proof and teardown; old localhost port is not currently listening |
| LDAB/DAB | ABACUS `tools/everred_v3/src/ldab_adapter.py`, MIP B0 and DAB producer | producer checksum, source files/test/line identities and accepted-repair proof; census count != active session |
| Runner capacity | hosted `ubuntu-24.04`, `ubuntu-latest`, `macos-latest`, Windows on documented workflows | effective queue/time and owner/admin runner census; self-hosted registrations and online/idle status UNKNOWN without runner permissions |

Suggested local preflight (run *in the cloned repository*, not in the browser):
```bash
python -m pip install pre-commit pytest pytest-cov coverage ruff bandit
pre-commit run --files scripts/testpilot_preflight.py
python scripts/testpilot_preflight.py --mode fast --parity
python -m pytest -q tests/test_code_purple_midwave_testflight.py
python -m coverage run --branch -m unittest discover -s tests -p test_code_purple_midwave_testflight.py
python -m coverage report -m --include=scripts/code_purple_midwave_testflight.py
ruff check scripts/code_purple_midwave_testflight.py tests/test_code_purple_midwave_testflight.py
bandit -q scripts/code_purple_midwave_testflight.py
```

The TestPilot commands belong to ABACUS; the mid-wave test commands belong to CODEX. They are shown together for operator planning, not as a single executable directory context. Avoid `pre-commit run --all-files` on ABACUS until the inherited repo-wide normalization scope is approved and owned.

On Linux, inspect actual debugger/container listeners with `docker ps --no-trunc` and `ss -ltnp`; on Windows use `Get-NetTCPConnection -State Listen` and process correlation. These queries establish only *current host* state when actually run; no local machine probe was executed in this implementation.

## 4. Portfolio expansion and evidence units

Owner listing: 90 repositories visible to connected GitHub account at initial measurement. Native workflow token may see a different public/private scope; never compare censuses until scope and permissions agree. Deep probe first 12 priority repositories; next cohorts in non-overlapping increments of at most 25 per dispatch. No automatic writes to non-CODEX repositories. Forks and archives retain flags and should not receive remediation PRs without explicit repository authority.

Reports keep distinct: repository counts, configured workflows, executed check jobs, bot comments, reviewed findings, completed patch receipts, line/branch coverage, active workers, debugger sessions, Docker port leases and governed admissions. No composite success score. Mark unmeasured values UNKNOWN.

## 5. MIP / DMAIC / reverse-pressure checkpoints

MIP P0: source SHA, ownership/permissions, scope fingerprint, stage testflight. P1: classify root-specific first red; perform bounded repair. P2: rerun focused/negative tests then canonical CI/security and native OS-specific tests. P3: independent review, protected admission, comparable N -> N+1 before/after debt. At each intermediate pulse preserve the same root ID and already completed scope receipts. A new SHA invalidates stale validation credit, **not** the engineering progress ledger.

DoV: a tested, independently reviewed PR on its final head with effective branch protection; a scheduled census or GitHub/Codex bot comment alone never meets DoV.
