from __future__ import annotations

import pathlib
import subprocess
import sys
from typing import Iterable
import datetime as dt

ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Repo-local import must happen after the sys.path bootstrap above so this
# module remains directly executable from the repository checkout.
from semantic_substrate.analytics.drift_engine import evaluate_semantic_drift
from semantic_substrate.engines.autonomous_correction_engine import (
    generate_correction_proposals,
)
from semantic_substrate.engines.delta_extractor import generate_delta_entry
from semantic_substrate.engines.replay_engine import ReplayEngine
from semantic_substrate.engines.semantic_planning_engine import build_semantic_plan
from semantic_substrate.memory.persistent_memory import persist_session
from semantic_substrate.viewers.semantic_graph_renderer import render_html_graph

VALIDATOR = ROOT / 'semantic_substrate' / 'validators' / 'validate_semantic_substrate.py'
STATE_SNAPSHOTS = ROOT / 'semantic_substrate' / 'state_snapshots.yaml'
BRANCH_DAG = ROOT / 'semantic_substrate' / 'branch_dag.yaml'
RECURSIVE_MERGE_POLICY = ROOT / 'semantic_substrate' / 'merge' / 'recursive_merge_policy.yaml'


def _decode_git_bytes(value: bytes) -> str:
    return value.decode('utf-8', errors='replace')


def _parse_porcelain_z(output: bytes) -> list[str]:
    """Parse `git status --porcelain=v1 -z` output into changed paths.

    Rename and copy records are encoded as two NUL-delimited paths after the
    two-character status and separating space. For semantic delta purposes the
    destination path is the actual current changed file.
    """
    parts = [part for part in output.split(b'\0') if part]
    files: list[str] = []
    index = 0

    while index < len(parts):
        entry = parts[index]
        status = entry[:2].decode('ascii', errors='replace')
        path = entry[3:]

        if status.startswith(('R', 'C')):
            # In --porcelain=v1 -z output, rename/copy records encode the
            # destination path in the current entry and the origin path in the
            # next NUL-delimited field.  We want the destination (current file).
            files.append(_decode_git_bytes(path))
            index += 1  # skip the origin path that follows
        else:
            files.append(_decode_git_bytes(path))

        index += 1

    return files


def _changed_files() -> list[str]:
    """Return tracked files changed in the git working tree."""
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain=v1', '-z'],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=False,
        )
    except OSError as exc:
        raise RuntimeError(f'Unable to run git status: {exc}') from exc

    if result.returncode != 0:
        stderr = result.stderr.decode('utf-8', errors='replace').strip()
        raise RuntimeError(f'git status failed with exit code {result.returncode}: {stderr}')

    return _parse_porcelain_z(result.stdout)


def _run_validator() -> dict:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return {
        'exit_code': result.returncode,
        'stdout': result.stdout,
        'stderr': result.stderr,
    }


def _load_yaml(path: pathlib.Path) -> dict:
    import yaml

    with open(path, 'r', encoding='utf-8') as handle:
        return yaml.safe_load(handle) or {}


def _current_state_id() -> str:
    snapshots = _load_yaml(STATE_SNAPSHOTS).get('snapshots', [])
    if not snapshots:
        return 'STATE-0000'
    return snapshots[-1].get('snapshot_id', 'STATE-0000')


def _next_state_id(previous: str) -> str:
    if not previous.startswith('STATE-'):
        return 'STATE-0001'
    suffix = previous.removeprefix('STATE-')
    if suffix.isdigit():
        return f'STATE-{(int(suffix) + 1):04d}'
    return 'STATE-0001'


def _update_snapshot(delta: dict) -> dict:
    replay = ReplayEngine().replay()
    state = replay.get('state') or {}
    previous = state.get('snapshot_id') or _current_state_id()
    return {
        'snapshot_id': _next_state_id(previous),
        'created_at': dt.date.today().isoformat(),
        'active_branches': state.get('active_branches', []),
        'active_invariants': state.get('active_invariants', []),
        'unresolved_semantic_debt': state.get('unresolved_semantic_debt', []),
        'next_actions': state.get('next_actions', []),
        'delta_id': delta.get('id'),
    }


def _update_lineage() -> dict:
    replay = ReplayEngine().replay()
    return {'tuple_lineage': (replay.get('state') or {}).get('tuple_lineage', {})}


def _recommend_next_action(validation: dict, drift: dict) -> list[str]:
    if validation.get('exit_code') != 0:
        return ['Resolve semantic validator failures before merge.']
    if drift.get('finding_count', 0) > 0:
        return ['Review drift findings and append semantic delta ledger entry.']
    return ['Proceed with semantic merge orchestration and replay verification.']


def _recursive_merge_orchestration() -> dict:
    policy_data = _load_yaml(RECURSIVE_MERGE_POLICY)
    policy = policy_data.get('merge_semantics', {})
    return {
        'philosophy': policy.get('philosophy'),
        'priority': policy_data.get('conflict_resolution', {}).get(
            'semantic_conflict_priority', []
        ),
        'rules': policy.get('rules', []),
    }


def _semantic_event_intelligence(delta: dict, drift: dict, proposals: dict) -> dict:
    classifications: dict[str, int] = {}
    for item in delta.get('files', []):
        key = item.get('classification', 'unknown')
        classifications[key] = classifications.get(key, 0) + 1
    return {
        'event_count': len(delta.get('files', [])),
        'classification_counts': classifications,
        'drift_finding_count': drift.get('finding_count', 0),
        'correction_proposal_count': proposals.get('proposal_count', 0),
    }


def _cognition_summary(
    plan: dict,
    memory_entry: dict,
    events: dict,
) -> dict:
    top_priority = (plan.get('priorities') or [None])[0]
    return {
        'top_priority': top_priority,
        'memory_checkpoint': memory_entry.get('replay_checkpoint'),
        'event_intelligence': events,
    }


def run_orchestration(changed_files: Iterable[str] | None = None) -> dict:
    try:
        observed_files = list(changed_files) if changed_files is not None else _changed_files()
    except RuntimeError as exc:
        return {
            'validator_exit_code': None,
            'validator_stdout': '',
            'validator_stderr': '',
            'delta': None,
            'status': 'failed',
            'error': str(exc),
            'loop_trace': ['observe'],
        }

    try:
        validation = _run_validator()
    except OSError as exc:
        return {
            'validator_exit_code': None,
            'validator_stdout': '',
            'validator_stderr': '',
            'delta': None,
            'status': 'failed',
            'error': str(exc),
            'loop_trace': ['observe', 'classify', 'validate'],
        }

    from_state = _current_state_id()
    to_state = _next_state_id(from_state)
    delta = generate_delta_entry(
        observed_files,
        from_state=from_state,
        to_state=to_state,
    )
    drift = evaluate_semantic_drift(delta)
    snapshot = _update_snapshot(delta)
    lineage = _update_lineage()
    semantic_graph = render_html_graph(_load_yaml(BRANCH_DAG))
    next_actions = _recommend_next_action(validation, drift)
    merge_orchestration = _recursive_merge_orchestration()
    correction_proposals = generate_correction_proposals(drift)
    planning_report = build_semantic_plan(drift, snapshot, correction_proposals)
    events = _semantic_event_intelligence(delta, drift, correction_proposals)
    memory_entry = persist_session(snapshot, delta, drift, next_actions)
    cognition_summary = _cognition_summary(planning_report, memory_entry, events)

    validation_code = validation['exit_code']
    loop_trace = [
        'observe',
        'reconstruct',
        'reason',
        'prioritize',
        'recommend',
        'heal',
        'synchronize',
        'persist',
        'evolve',
        'validate',
        'generate_delta',
        'update_snapshot',
        'update_lineage',
        'update_debt',
        'adaptive_cognition',
    ]
    return {
        'validator_exit_code': validation_code,
        'validator_stdout': validation['stdout'],
        'validator_stderr': validation['stderr'],
        'delta': delta,
        'snapshot': snapshot,
        'lineage': lineage,
        'drift_report': drift,
        'semantic_graph_html': semantic_graph,
        'merge_orchestration': merge_orchestration,
        'recommended_next_actions': next_actions,
        'correction_proposals': correction_proposals,
        'planning_report': planning_report,
        'replay_checkpoint': memory_entry.get('replay_checkpoint'),
        'semantic_event_intelligence': events,
        'cognition_summary': cognition_summary,
        'loop_trace': loop_trace,
        'status': 'ok' if validation_code == 0 else 'failed',
        'error': None,
    }


if __name__ == '__main__':
    print(run_orchestration())
