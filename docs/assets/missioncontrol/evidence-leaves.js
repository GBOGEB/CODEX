// Display only SHA-bound advisory diagnostic evidence; never mutate governance state.
(async function () {
  const set = (id, value) => { const el = document.getElementById(id); if (el) el.textContent = String(value); };
  try {
    const response = await fetch('data/diagnostic_coverage_receipt.json', {cache: 'no-store'});
    if (!response.ok) throw Error('No published current-source receipt');
    const r = await response.json();
    if (r.schema !== 'codex-diagnostic-coverage-rollup/v1' ||
        !/^[a-f0-9]{40}$/.test(r.source_sha || '') ||
        r.authority_transfer !== false ||
        r.formal_credit_delta !== 0 || r.engineering_credit_delta !== 0) {
      throw Error('Evidence authority or provenance invalid');
    }
    const q = r.coverage?.quality;
    const rt = r.coverage?.runtime;
    const ld = r.coverage?.ldab;
    const cr = r.coverage?.crew;
    set('leafQuality', q?.status === 'MEASURED' && Number.isInteger(q.ruff_findings) ? q.ruff_findings + ' findings' : 'UNKNOWN');
    set('leafRuntime', rt?.status === 'MEASURED' && Number.isInteger(rt.passed_entrypoints) ? rt.passed_entrypoints + ' PASS' : 'UNKNOWN');
    set('leafLdab', ld?.status === 'MEASURED' && ld.handshake_verified === true ? 'VERIFIED' : 'UNKNOWN');
    set('leafCrew', cr?.status === 'MEASURED' && typeof r.metrics?.mean_queue_wait_seconds === 'number'
      ? r.metrics.mean_queue_wait_seconds + ' s' : 'UNKNOWN');
    // Security and cross-repo figures require separate governed evidence; do not infer from CODEX receipt.
    set('leafSecurity', 'UNKNOWN');
    set('leafCrossRepo', 'UNKNOWN');
    set('leafEvidenceSource', 'Advisory evidence source: ' + r.source_sha + ' · Publication identity must be validated separately');
  } catch (error) {
    set('leafEvidenceSource', 'Current-source evidence UNKNOWN: ' + error.message);
  }
}());
