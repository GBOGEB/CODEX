// Read-only MissionControl diagnostic evidence viewer; no publisher, no authority transfer.
(function () {
  const state = document.getElementById('diagnosticCoverageState');
  const values = document.getElementById('diagnosticCoverageValues');
  if (!state || !values) return;
  fetch('data/diagnostic_coverage_receipt.json', {cache: 'no-store'})
    .then(response => { if (!response.ok) throw new Error('receipt not published'); return response.json(); })
    .then(receipt => {
      if (receipt.schema !== 'codex-diagnostic-coverage-rollup/v1' ||
          receipt.authority_transfer !== false ||
          receipt.formal_credit_delta !== 0 ||
          receipt.engineering_credit_delta !== 0 ||
          !/^[a-f0-9]{40}$/.test(receipt.source_sha || '')) {
        throw new Error('invalid or non-advisory receipt');
      }
      state.textContent = 'ADVISORY · source ' + receipt.source_sha;
      const surfaces = ['quality', 'runtime', 'ldab', 'crew'];
      const parts = surfaces.map(name => name + ': ' + (receipt.coverage?.[name]?.status || 'UNKNOWN'));
      parts.push('Queue wait: ' + (receipt.metrics?.mean_queue_wait_seconds ?? 'UNKNOWN'));
      parts.push('Worker handling: ' + (receipt.metrics?.mean_worker_handling_seconds ?? 'UNKNOWN'));
      values.textContent = parts.join(' | ');
    }).catch(error => {
      state.textContent = 'UNKNOWN — ' + error.message;
      values.textContent = 'No current authenticated and admitted evidence';
    });
}());
