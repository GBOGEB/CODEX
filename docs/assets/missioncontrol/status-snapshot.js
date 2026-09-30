(() => {
  'use strict';
  const $ = s => document.querySelector(s);
  const esc = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const cls = state => /FAIL|ERROR|RED/.test(state) ? 'fail' : /WITHHELD|WAIT|OWNER_ACTION|HOLD/.test(state) ? 'warn' : /GREEN|MEASURED|MERGED|ACTIVE|REMOTE/.test(state) ? 'ok' : 'hold';
  const short = sha => sha ? sha.slice(0, 12) : 'unbound';
  const link = (href,label) => href ? '<a href="'+esc(href)+'" target="_blank" rel="noopener">'+esc(label)+'</a>' : esc(label);
  const themes=['system','light','dark']; let ti=0;
  function applyTheme(){const t=themes[ti]; if(t==='system') document.documentElement.removeAttribute('data-theme'); else document.documentElement.setAttribute('data-theme',t); $('#theme').textContent='Theme: '+t;}
  $('#theme').addEventListener('click',()=>{ti=(ti+1)%themes.length;applyTheme()}); applyTheme();

  fetch('data/missioncontrol_status_snapshot_v01.json',{cache:'no-store'})
    .then(r => { if(!r.ok) throw new Error('snapshot HTTP '+r.status); return r.json(); })
    .then(s => {
      document.title=s.title;
      $('#title').textContent=s.title;
      $('#subtitle').textContent='Frozen at '+s.snapshot_at+' · '+s.repository+' @ '+short(s.snapshot_sha);
      $('#meta').innerHTML='<b>snapshot</b><span>'+esc(short(s.snapshot_sha))+'</span><b>state</b><span>'+esc(s.snapshot_state)+'</span>';
      $('#state').innerHTML='<span class="chip '+cls(s.overall_state)+'">'+esc(s.overall_state)+'</span>'+
        '<span class="chip hold">authority_transfer=false</span><span class="chip hold">credit Δ=0</span>';

      $('#laneRows').innerHTML=s.lanes.map(x => '<tr>'+
        '<td><div class="lane">'+link(x.href,x.label)+'</div><div class="small mono">'+esc(x.repository)+' @ '+esc(short(x.declared_head_sha))+'</div></td>'+
        '<td><span class="chip '+cls(x.status)+'">'+esc(x.status)+'</span></td>'+
        '<td><div class="mono">'+esc(x.current_atom)+'</div><div class="small">'+esc(x.gate)+'</div></td>'+
        '<td class="mono">'+esc(x.next)+'</td></tr>').join('');

      $('#evidence').innerHTML=s.evidence_strip.map(x => '<div class="ev"><b>'+link(x.href,x.label)+'</b><span>'+esc(x.state)+'</span><span class="mono">'+esc(x.ref)+'</span></div>').join('');
      $('#interpretation').innerHTML=s.interpretation.map(x => '<li>'+esc(x)+'</li>').join('');
      $('#now').innerHTML='<span class="chip '+cls(s.continuation.now.state)+'">'+esc(s.continuation.now.state)+'</span><br><code>'+esc(s.continuation.now.id)+'</code>';
      $('#next').innerHTML=s.continuation.next.map(x => '<div><span class="chip '+cls(x.state)+'">'+esc(x.state)+'</span> <code>'+esc(x.id)+'</code></div>').join('');
      $('#hold').innerHTML=s.continuation.hold.map(x => '<div><span class="chip '+cls(x.state)+'">'+esc(x.state)+'</span> <code>'+esc(x.id)+'</code></div>').join('');

      const f=s.footer;
      $('#footer').innerHTML=[
        ['repo',f.repo],['snapshot_sha',f.snapshot_sha],['generated_from',f.generated_from],
        ['authority_transfer',String(f.authority_transfer)],['formal_credit_delta',String(f.formal_credit_delta)],
        ['engineering_credit_delta',String(f.engineering_credit_delta)],['snapshot_state',f.snapshot_state]
      ].map(([k,v])=>'<span>'+esc(k)+': <code>'+esc(v)+'</code></span>').join('');
    })
    .catch(err => {
      $('#subtitle').textContent='Snapshot renderer degraded: '+err.message;
      $('#state').innerHTML='<span class="chip fail">RENDER_WITHHELD</span>';
    });
})();
