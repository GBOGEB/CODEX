(() => {
  'use strict';

  const $ = (s) => document.querySelector(s);
  let control = null;
  let stagedEnvelope = null;

  function esc(v) {
    return String(v ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  }

  async function loadControlPlane() {
    control = await fetch('data/missioncontrol_control_plane.json').then(r => {
      if (!r.ok) throw new Error('control-plane projection HTTP ' + r.status);
      return r.json();
    });
    renderAuthority();
    renderLanes();
    renderFederation();
    renderCheckpoint();
    bindCommandSurface();
    bindRecoveryControls();
    bindArtifactNavigator();
    document.documentElement.dataset.controlPlane = 'ready';
  }

  function renderAuthority() {
    const box = $('#authorityContext');
    if (!box || !control) return;
    const rows = Object.values(control.repositories || {}).map(r =>
      '<tr><td><b>' + esc(r.repo) + '</b><br><small>' + esc(r.role) + '</small></td>' +
      '<td><code>' + esc((r.refreshed_current_sha || '').slice(0,12)) + '</code></td>' +
      '<td>' + (r.handover_observed_sha === r.refreshed_current_sha ? '<span class="pill">unchanged</span>' : '<span class="pill warn">advanced</span>') + '</td></tr>'
    ).join('');
    box.innerHTML = '<table><thead><tr><th>Authority</th><th>Current SHA</th><th>Since handover</th></tr></thead><tbody>' + rows + '</tbody></table>';
  }

  function laneActions(lane) {
    const next = (lane.next_legal_transitions || [])[0] || 'WITHHELD';
    return '<button class="lane-resume" data-lane="' + esc(lane.id) + '" data-next="' + esc(next) + '">resume</button> ' +
           '<button class="lane-retry" data-lane="' + esc(lane.id) + '">retry read</button>';
  }

  function renderLanes() {
    const box = $('#laneRows');
    if (!box || !control) return;
    box.innerHTML = (control.lanes || []).map(lane =>
      '<tr><td><b>' + esc(lane.id) + '</b><br><small>' + esc(lane.repository) + '</small></td>' +
      '<td>' + esc(lane.state) + '<br><span class="pill">' + esc(lane.queue_state) + '</span></td>' +
      '<td>' + esc(lane.current_atom) + '</td>' +
      '<td>' + (lane.blocker ? '<span class="warn">' + esc(lane.blocker) + '</span>' : '<span class="ok">none</span>') + '</td>' +
      '<td>' + esc((lane.next_legal_transitions || []).join(' → ')) + '</td>' +
      '<td>' + laneActions(lane) + '</td></tr>'
    ).join('');
    document.querySelectorAll('.lane-resume').forEach(b => b.onclick = () => localRecoveryEvent('RESUME', b.dataset.lane, b.dataset.next));
    document.querySelectorAll('.lane-retry').forEach(b => b.onclick = () => localRecoveryEvent('RETRY_READ', b.dataset.lane, null));
  }

  function renderCheckpoint() {
    const box = $('#checkpoint');
    if (!box || !control) return;
    const codex = (control.lanes || []).find(x => x.id === 'CODEX_UI');
    box.innerHTML =
      '<b>Last durable predecessor:</b> PR #839 exact-head proof + merged-main Pages readback<br>' +
      '<b>Current lane:</b> ' + esc(codex?.id || 'WITHHELD') + ' · <b>atom:</b> ' + esc(codex?.current_atom || 'WITHHELD') + '<br>' +
      '<b>Continuation:</b> ' + esc((control.continuation || []).join(' → ')) + '<br>' +
      '<b>Replay completed atoms:</b> <span class="ok">' + esc(control.invariants?.replay_completed_atoms_on_reentry === false ? 'false' : 'UNKNOWN') + '</span>';
  }

  function renderFederation() {
    const box = $('#federationRows');
    if (!box || !control) return;
    const codex = control.repositories?.codex;
    box.innerHTML = Object.values(control.repositories || {}).map(r => {
      const remote = r.role !== 'UI_ORCHESTRATION_GRAPH_AUTHORITY';
      const mechanism = r.repo.includes('cryoplant') ? 'PROJECTED_OR_BRIDGED' : (r.repo.includes('ABACUS') ? 'REFERENCE / TYPED RETURN' : 'LOCAL');
      return '<tr><td><b>' + esc(r.repo) + '</b></td>' +
        '<td><code>' + esc((r.refreshed_current_sha || '').slice(0,12)) + '</code></td>' +
        '<td>' + esc(r.role) + '</td><td>' + esc(mechanism) + '</td>' +
        '<td>' + (remote ? '<span class="pill">preserved remote</span>' : '<span class="pill ok">local authority</span>') + '</td></tr>';
    }).join('');
    const qlm = $('#qlmContext');
    if (qlm) {
      const q = control.qlm_context || {};
      qlm.innerHTML = '<b>QLM:</b> ' + esc(q.functional_location) + ' / ' + esc(q.physical_boundary) +
        ' · <b>decision:</b> ' + esc(q.governing_decision_surface) +
        ' · <b>mode:</b> ' + esc(q.integration_mode) +
        ' · migrate authority: <b>' + esc(q.migrate_authority_into_CODEX) + '</b>';
    }
    const strategy = $('#federationStrategy');
    if (strategy) strategy.textContent = (control.federation?.strategy_order || []).join(' → ');
  }

  function parseCommand(text) {
    const trimmed = text.trim();
    if (!trimmed) return {ok:false, kind:'EMPTY', parsed:null, message:'No command/input supplied.'};
    if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
      try { return {ok:true, kind:'JSON', parsed:JSON.parse(trimmed), message:'JSON parsed.'}; }
      catch (e) { return {ok:false, kind:'JSON', parsed:null, message:'Invalid JSON: ' + e.message}; }
    }
    const yamlLike = trimmed.split(/\r?\n/).some(line => /^\s*[A-Za-z0-9_.-]+\s*:/.test(line));
    return {ok:true, kind:yamlLike ? 'YAML_TEXT' : 'TEXT', parsed:trimmed, message:yamlLike ? 'YAML-like text staged; canonical YAML parsing occurs in governed backend validation.' : 'Text command staged.'};
  }

  function buildEnvelope(requestedMode) {
    const input = $('#commandInput')?.value || '';
    const parsed = parseCommand(input);
    const repo = $('#commandAuthority')?.value || 'GBOGEB/CODEX';
    const lane = $('#commandLane')?.value || 'CODEX_UI';
    const event = {
      schema_version:'0.2.1',
      event_type:'USER_STEER',
      requested_mode:requestedMode,
      effective_mode: requestedMode === 'APPLY' ? 'STAGED_APPLY_WITHHELD_NO_AUTHENTICATED_GATEWAY' : 'DRY_RUN',
      repository:repo,
      lane,
      source_authority_sha:(Object.values(control?.repositories || {}).find(x => x.repo === repo)?.refreshed_current_sha || null),
      command_format:parsed.kind,
      command:parsed.parsed,
      parse_ok:parsed.ok,
      parse_message:parsed.message,
      invariants:{
        authority_transfer:false,
        formal_credit_delta:0,
        engineering_credit_delta:0,
        replay_completed_atoms:false
      },
      next_action: requestedMode === 'APPLY' ? 'SEND_TO_AUTHENTICATED_EXECUTION_GATEWAY_AND_BIND_PROOF' : 'REVIEW_STAGED_ENVELOPE'
    };
    return event;
  }

  function stage(mode) {
    stagedEnvelope = buildEnvelope(mode);
    const out = $('#commandReceipt');
    const status = stagedEnvelope.parse_ok ? (mode === 'APPLY' ? 'WITHHELD / staged only' : 'DRY RUN READY') : 'INPUT ERROR';
    if (out) out.innerHTML = '<b>' + esc(status) + '</b><pre>' + esc(JSON.stringify(stagedEnvelope,null,2)) + '</pre>';
    const dl = $('#commandDownload');
    if (dl) {
      const blob = new Blob([JSON.stringify(stagedEnvelope,null,2) + '\n'], {type:'application/json'});
      dl.href = URL.createObjectURL(blob);
      dl.download = 'missioncontrol-command-envelope.json';
      dl.hidden = false;
    }
  }

  function bindCommandSurface() {
    if (!control) return;
    const auth = $('#commandAuthority');
    if (auth) auth.innerHTML = Object.values(control.repositories || {}).map(r => '<option>' + esc(r.repo) + '</option>').join('');
    const lane = $('#commandLane');
    if (lane) lane.innerHTML = (control.lanes || []).map(x => '<option>' + esc(x.id) + '</option>').join('');
    const dry = $('#dryRunCommand'), apply = $('#applyCommand');
    if (dry) dry.onclick = () => stage('DRY_RUN');
    if (apply) apply.onclick = () => stage('APPLY');
    const upload = $('#configUpload');
    if (upload) upload.onchange = async () => {
      const file = upload.files?.[0];
      if (!file) return;
      $('#commandInput').value = await file.text();
      $('#commandReceipt').innerHTML = '<span class="ok">Loaded local config: ' + esc(file.name) + '</span>';
    };
  }

  function localRecoveryEvent(action, lane, next) {
    const box = $('#recoveryReceipt');
    const event = {
      event_type:'LOCAL_CONTROL_INTENT',
      action, lane, next,
      mutation_claim:false,
      message:'UI intent only; repository/runtime mutation requires authenticated gateway proof.'
    };
    if (box) box.innerHTML = '<pre>' + esc(JSON.stringify(event,null,2)) + '</pre>';
  }

  function bindRecoveryControls() {
    const continueBtn = $('#continueFromCheckpoint');
    if (continueBtn) continueBtn.onclick = () => localRecoveryEvent('CONTINUE_FROM_DURABLE_STATE','CODEX_UI','RESUME_FIRST_LEGAL_INCOMPLETE_ATOM');
  }

  function bindArtifactNavigator() {
    const filter = $('#artifactFilter');
    if (!filter) return;
    filter.oninput = () => {
      const q = filter.value.toLowerCase();
      document.querySelectorAll('#artifacts .artifact, #evidence tr[data-evidence-row]').forEach(el => {
        el.style.display = el.textContent.toLowerCase().includes(q) ? '' : 'none';
      });
    };
  }

  loadControlPlane().catch(err => {
    const box = $('#controlPlaneStatus');
    if (box) box.innerHTML = '<span class="bad">Control-plane projection unavailable: ' + esc(err.message) + '</span><br><span class="muted">Core graph renderer remains available by isolation contract.</span>';
  });
})();
