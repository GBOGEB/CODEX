# A7 — Executable Semantic Runtime

## Objective

Turn the semantic handover architecture into an executable reconstruction runtime.

The first slice implements four governed runtime responsibilities:

1. load semantic tuples;
2. reconstruct active state;
3. load invariants and semantic debt;
4. emit a deterministic validation summary suitable for CI.

## Runtime Contract

Input:
- tuple ledger
- reconstruction manifest
- invariant ledger
- semantic debt ledger

Output:
- reconstructed active branch state
- latest tuple
- invariant count
- open semantic debt count
- replay readiness result
- validation status

## Design Rules

- idempotent: repeated execution must not mutate source state;
- iterative: new tuples extend prior state;
- recursive: each runtime state can seed the next handover;
- evolutionary: competing branches remain explicit until evidence supports convergence.

## A7.1 — Evolutionary Branch Competition

`branch_evolution.py` enforces the evolutionary pillar (INV-005). The
governance ledger now holds a `branch_competition` list. Each record names a
`fork` tuple, two or more `alternatives` that are direct children of that
fork, a `status` (`open` or `converged`), a `winner` and `evidence`:

- an open competition names no winner;
- a converged competition names one winner from its alternatives and cites
  evidence tuples that descend from the fork;
- losing alternatives stay in the tuple ledger, so convergence never deletes
  lineage.

The runtime also reports fork points, the frontier (leaf tuples) and the
branches still competing. `first_red_gate.py` runs it as the
`branch_evolution` stage after the DAG stage. `COMP-001` records the open
competition between TUP-0002 (canonical convergence) and TUP-0003 (Option B
overlay-first).

## A7.3 — Append-Only Lineage Lock

`lineage_lock.py` enforces the iterative pillar. `data/lineage_lock.json`
holds an identity hash over `id`, `parent`, `branch`, `theme` and `intent`
for every locked tuple, in ledger order. The check fails when a locked tuple
is deleted, reordered or has an identity field rewritten. `progress`, `todo`
and `delta` may still change as work moves on.

After appending tuples to the ledger, lock them in the same PR:

```
python lineage_lock.py --extend
```

`--extend` only appends to the lock; it refuses to run if locked history was
rewritten. `first_red_gate.py` runs the check as the `lineage_append_only`
stage after `parentage`.

## A7.4 — Recursive Handover Seed

`handover_seed.py` enforces the recursive pillar. `data/handover_seed.json`
is the reconstructed state packaged to start the next handover: runtime
state, the frontier tuples to resume from (with their `todo`), open
competitions, open debt and invariant ids. It is bound to a SHA-256 digest of
the parsed ledgers, so checkout line endings do not change it.

Seeds form a chain. When the ledgers are unchanged, `--write` keeps the same
seed. When they change, it writes a new seed whose `parent_seed_sha256` is
the previous seed's hash.

Any PR that edits `semantic_tuple_ledger.json` or `governance_ledger.json`
must refresh the seed in the same PR:

```
python handover_seed.py --write
```

`first_red_gate.py` runs the check as the `handover_seed` stage after
`semantic_delta_replay`; a stale or edited seed turns it red.

## Immediate Next After This Slice

- tuple schema validation;
- branch DAG reconstruction;
- semantic delta replay;
- CI gating;
- renderer-governance integration;
- measurable completeness score.
