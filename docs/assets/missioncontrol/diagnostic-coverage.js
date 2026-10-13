// Advisory-only MissionControl evidence leaves: never infer worker, gate, or coverage credit.
(function () {
  'use strict';
  const state = document.getElementById('diagnosticCoverageState');
  const values = document.getElementById('diagnosticCoverageValues');
  const cards = document.getElementById('diagnosticCoverageCards');
  if (!state || !values || !cards) return;
  const text = value => value === null || value === undefined ? 'UNKNOWN' : String(value);
  const addCard = (title, value, detail) => {
    const card = document.createElement('article');
    card.className = 'artifact';
    const heading = document.createElement('b');
    heading.textContent = title;
    const metric = document.createElement('div');
    metric.textContent = text(value);
    const note = document.createElement('small');
    note.className = 'muted';
    note.textContent = detail;
    card.append(heading, metric, note);
    cards.appendChild(card);
  };
  addCard('Ruff · historical', '182 → 175', '7 F401 resolved · 0 new · B2, not current main');
  addCard('Pyright · historical', '55 errors / 7 warnings', '120 files analyzed · fixed scan population');
  addCard('UBI 9 · historical', '3 entrypoints', '2 checks + 1 output-producing REX pipeline, verified testflight');
  addCard('LDAB / BD · current', 'UNKNOWN', 'Signature-to-task join not verified on current main');
  addCard('Crew / queue · current', 'UNKNOWN', 'Authenticated worker count and p50/p95 unavailable');
  addCard('RHEL / Docker / ports', 'UNKNOWN', 'Native hosts, listeners, debugger ports require runtime probes');
  fetch('data/diagnostic_coverage_receipt.json', {cache: 'no-store'})
    .then(response => { if (!response.ok) throw new Error('receipt not published'); return response.json(); })
    .then(receipt => {
      if (receipt.schema !== 'codex-diagnostic-coverage-rollup/v1' ||
          receipt.authority_transfer !== false || receipt.formal_credit_delta !== 0 ||
          receipt.engineering_credit_delta !== 0 ||
          !/^[a-f0-9]{40}$/.test(receipt.source_sha || '')) {
        throw new Error('invalid or non-advisory receipt');
      }
      state.textContent = 'ADVISORY SOURCE-BOUND · ' + receipt.source_sha;
      const surfaces = ['quality', 'runtime', 'ldab', 'crew'];
      values.textContent = surfaces.map(name => name + ': ' +
        (receipt.coverage?.[name]?.status || 'UNKNOWN')).join(' | ') +
        ' | Queue wait: ' + text(receipt.metrics?.mean_queue_wait_seconds) +
        ' | Worker handling: ' + text(receipt.metrics?.mean_worker_handling_seconds);
      addCard('Receipt identity', receipt.source_sha.slice(0, 12),
        'Advisory only · compare to checked-out main before calling CURRENT');
    }).catch(error => {
      state.textContent = 'CURRENT COVERAGE UNKNOWN — ' + error.message;
      values.textContent = 'No authenticated admitted current-head coverage receipt; historical cards are context only';
    });
}());
