import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
SEMANTIC = ROOT / 'semantic_substrate'
PIPELINE_GLOSSARY = ROOT / 'PIPELINE' / 'GLOSSARY.yaml'

REQUIRED_FILES = [
    'overlay_ssot.yaml',
    'invariants.yaml',
    'branch_dag.yaml',
    'STATE_RECONSTRUCTION.md',
    'semantic_delta_ledger.yaml',
    'roe_log.yaml',
]

TOKEN_PATTERN = re.compile(r'\b(?:[a-z]+_){1,}[a-z0-9]+\b')
SCAN_DIRS = [
    ROOT,
]
SCAN_SUFFIXES = {'.py', '.yaml', '.yml', '.md', '.json'}
SKIP_FRAGMENTS = ('/.venv/', '/.git/', '/__pycache__/')

BASELINE_ALLOWED_UNDOCUMENTED = {
    'semantic_alignment', 'semantic_alignment_restored', 'semantic_cards', 'semantic_commit_hook',
    'semantic_confidence', 'semantic_conflict_priority', 'semantic_debt_score', 'semantic_delta_ledger',
    'semantic_distribution', 'semantic_event_intelligence', 'semantic_flow_edges', 'semantic_flow_summary',
    'semantic_flow_type', 'semantic_graph', 'semantic_graph_html', 'semantic_graph_renderer',
    'semantic_guardrail', 'semantic_index', 'semantic_memory', 'semantic_memory_gap',
    'semantic_memory_refs', 'semantic_mismatch', 'semantic_nodes', 'semantic_optimization',
    'semantic_planning_engine', 'semantic_query', 'semantic_region_reclassification', 'semantic_regions',
    'semantic_role', 'semantic_roles', 'semantic_runtime_pipeline_bridge_v1', 'semantic_search',
    'semantic_substrate', 'semantic_synchronization_loss', 'semantic_tags', 'semantic_text',
    'semantic_type', 'semantic_vector_confidence', 'semantic_weight',
    'semantic_ast', 'semantic_card_required', 'semantic_cards_and_ssot', 'semantic_cognition_alignment',
    'semantic_compliance_record', 'semantic_continuity_alignment', 'semantic_convergence_alignment',
    'semantic_decisions', 'semantic_delta', 'semantic_density', 'semantic_entropy',
    'semantic_execution', 'semantic_execution_confidence', 'semantic_execution_continuity',
    'semantic_execution_integrity', 'semantic_execution_lineage', 'semantic_execution_observability',
    'semantic_execution_stability', 'semantic_flows', 'semantic_governance_consistency',
    'semantic_governance_source', 'semantic_graph_runtime', 'semantic_ir', 'semantic_layer', 'semantic_links',
    'semantic_memory_alignment', 'semantic_normalization', 'semantic_operational_alignment',
    'semantic_operational_lineage', 'semantic_operational_mapping', 'semantic_operational_sovereignty',
    'semantic_operational_tracking', 'semantic_operational_visibility', 'semantic_orchestration',
    'semantic_prefixes', 'semantic_preservation', 'semantic_preservation_alignment',
    'semantic_proof_alignment', 'semantic_proof_balance', 'semantic_propagation_alignment',
    'semantic_provenance', 'semantic_recursion_alignment', 'semantic_release_alignment',
    'semantic_release_gate', 'semantic_runtime', 'semantic_runtime_alignment',
    'semantic_runtime_completion', 'semantic_runtime_confidence', 'semantic_runtime_visibility',
    'semantic_signal_alignment', 'semantic_signal_visibility', 'semantic_sovereignty_alignment',
    'semantic_telemetry_dashboard', 'semantic_tokens', 'semantic_traceability', 'semantic_traversal',
    'semantic_trust_propagation_engine', 'semantic_trust_visibility', 'semantic_validation_engine',
    'semantic_validator', 'semantic_verification_alignment'
}
BASELINE_ALLOWED_UNDOCUMENTED.update(
    {
        'semantic_ast', 'semantic_card_required', 'semantic_cards_and_ssot',
        'semantic_cognition_alignment', 'semantic_compliance_record',
        'semantic_continuity_alignment', 'semantic_convergence_alignment',
        'semantic_decisions', 'semantic_delta', 'semantic_density',
        'semantic_entropy', 'semantic_execution',
        'semantic_execution_confidence', 'semantic_execution_continuity',
        'semantic_execution_integrity', 'semantic_execution_lineage',
        'semantic_execution_observability', 'semantic_execution_stability',
        'semantic_flows', 'semantic_governance_consistency',
        'semantic_governance_source', 'semantic_graph_runtime', 'semantic_ir',
        'semantic_layer', 'semantic_links', 'semantic_memory_alignment',
        'semantic_normalization', 'semantic_operational_alignment',
        'semantic_operational_lineage', 'semantic_operational_mapping',
        'semantic_operational_sovereignty', 'semantic_operational_tracking',
        'semantic_operational_visibility', 'semantic_orchestration',
        'semantic_prefixes', 'semantic_preservation',
        'semantic_preservation_alignment', 'semantic_proof_alignment',
        'semantic_proof_balance', 'semantic_propagation_alignment',
        'semantic_provenance', 'semantic_recursion_alignment',
        'semantic_release_alignment', 'semantic_release_gate', 'semantic_runtime',
        'semantic_runtime_alignment', 'semantic_runtime_completion',
        'semantic_runtime_confidence', 'semantic_runtime_visibility',
        'semantic_signal_alignment', 'semantic_signal_visibility',
        'semantic_sovereignty_alignment', 'semantic_telemetry_dashboard',
        'semantic_tokens', 'semantic_traceability', 'semantic_traversal',
        'semantic_trust_propagation_engine', 'semantic_trust_visibility',
        'semantic_validation_engine', 'semantic_validator',
        'semantic_verification_alignment',
    }
)


def validate_required_files():
    missing = []
    for item in REQUIRED_FILES:
        path = SEMANTIC / item
        if not path.exists():
            missing.append(str(path))
    return missing


def validate_basic_ids():
    content = (SEMANTIC / 'invariants.yaml').read_text(encoding='utf-8')
    required = ['INV-001', 'INV-002', 'INV-003']
    missing = [rid for rid in required if rid not in content]
    return missing


def load_declared_terms() -> set[str]:
    if not PIPELINE_GLOSSARY.exists():
        return set()

    declared: set[str] = set()
    in_glossary = False
    for line in PIPELINE_GLOSSARY.read_text(encoding='utf-8').splitlines():
        if line.startswith('glossary:'):
            in_glossary = True
            continue
        if in_glossary and re.match(r'^[^\s].*:', line):
            break
        if in_glossary:
            match = re.match(r'^\s{2}([a-z][a-z0-9_]*)\s*:\s*$', line)
            if match:
                declared.add(match.group(1))

    declared.update({'ssot', 'yaml', 'json', 'runtime', 'render', 'lineage'})
    return declared


def collect_snake_case_tokens() -> set[str]:
    discovered: set[str] = set()
    for directory in SCAN_DIRS:
        if not directory.exists():
            continue
        for path in directory.rglob('*'):
            if not path.is_file() or path.suffix not in SCAN_SUFFIXES:
                continue
            path_text = path.as_posix()
            if any(fragment in path_text for fragment in SKIP_FRAGMENTS):
                continue
            text = path.read_text(encoding='utf-8', errors='ignore')
            discovered.update(TOKEN_PATTERN.findall(text))
    return discovered


def find_undocumented_terms(declared_terms: set[str], scanned_terms: set[str]) -> list[str]:
    undocumented = [
        term
        for term in scanned_terms
        if term.startswith('semantic_')
        and term not in declared_terms
        and term not in BASELINE_ALLOWED_UNDOCUMENTED
    ]
    return sorted(set(undocumented))


def main():
    failures = []

    missing_files = validate_required_files()
    if missing_files:
        failures.append(f'Missing files: {missing_files}')

    missing_ids = validate_basic_ids()
    if missing_ids:
        failures.append(f'Missing invariant IDs: {missing_ids}')

    declared_terms = load_declared_terms()
    scanned_terms = collect_snake_case_tokens()
    undocumented_terms = find_undocumented_terms(declared_terms, scanned_terms)
    if undocumented_terms:
        failures.append(f'Undocumented semantic terms: {undocumented_terms}')

    if failures:
        print('SEMANTIC VALIDATION FAILED')
        for failure in failures:
            print(f'- {failure}')
        sys.exit(1)

    print('SEMANTIC VALIDATION PASSED')
    sys.exit(0)


if __name__ == '__main__':
    main()
