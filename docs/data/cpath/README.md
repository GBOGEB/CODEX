# C-PATH pilot data (2026-11-16)

`scripts/issue_critical_path.py` analyses an issue / PR / BD-queue graph. It reports:

- Kahn waves and any cycle (deadlock) Kahn cannot drain.
- The CPM critical path overall and per goal (`goals`), with slack per node.
- Downstream cone and Brandes betweenness (chokepoints).
- Reverse pressure. With `--mode and` (the default), every prerequisite inherits full pressure. With `--mode share`, pressure is split across blockers, PageRank style.
- Levers: multiplier and pairwise synergy, plus a greedy k-way **lever cover** per goal that shows how AND-joins need several levers together.
- Descriptive PCA and Bradley-Terry strengths.

| File | What |
|---|---|
| `cpath_graph_20261116.json` | Pilot graph: 40 open ABACUS + CODEX issues, open PRs, the #2752 main-red BD ledger (14 Nov) plus three live BD rows measured on ABACUS main (Black 275 files, isort 257, Bandit 24,823 raw), owner gates, and one time wait. Every edge carries `evidence` (`DECLARED` or `INFERRED`) and a `source` |
| `cpath_report_20261116.json` | `python scripts/issue_critical_path.py --graph cpath_graph_20261116.json --out cpath_report_20261116.json` |
| `cpath_graph_20261123.json` | The 2026-11-16 graph merged with a live PR census (`federation_pr_dag.py collect` then `export-cpath --base cpath_graph_20261116.json`): 98 nodes, 97 edges. Curated base nodes win; new nodes are open PRs (kind `pr`), held-run / owner-checklist gates and BD-queue rows. Census edges carry `DECLARED` (Depends-on, Fixes), `DERIVED` (kit pin, gates) or `INFERRED` (shared files) |
| `cpath_report_20261123.json` | `python scripts/issue_critical_path.py --graph cpath_graph_20261123.json --out cpath_report_20261123.json` |

Caveats, also written into the report:

- Durations are per-class defaults unless a node sets its own. The path orders the work; it does not forecast dates.
- `INFERRED` edges are reviewed judgements, not links declared on GitHub.
- PCA and Bradley-Terry over tens of nodes are descriptive only; they support no inference.
- The graph is a snapshot. Rebuild it before acting on any ranking.


## Advisory control boundary

Newly generated reports explicitly mark structural waves, ranking, lever unlocks
and cover as advisory only. They cannot authorize an operation or verify
completion. ABACUS #2470 is a protected negative canary: ordinary merge and
generic lever completion are prohibited. ABACUS #2471 requires separately
qualified effective policy, refusal evidence and authorized disposition. An
absent census node or a graph-local `done` flag is not that evidence. The guard
excludes both controls from generic lever completion and retains the refusal
prerequisite in lever-cover residuals, even if a census refresh removes #2470.
The original graph topology and dated graph/report snapshots are preserved;
historical reports predate this guard and must not be used for operational
dispatch. No new dispatcher or receipt verifier is introduced.
