// Read-only disjoint crew review. All labels describe evidence, not execution authority.
(() => {
  const cards = document.getElementById('disjointPulseCards');
  const lanes = document.getElementById('disjointLaneCards');
  if (!cards || !lanes) return;
  const route = [
    ['A','Quality','9/9 populations classified; at least one measured test-coverage ratio','SOURCE EVIDENCE REQUIRED'],
    ['B','UBI 9 runtime','2/2 successful workflow jobs; hashed output production','HISTORICAL CI PASS'],
    ['C','LDAB / Docker','Real container, port, log, and debugger steps > 0','LIVE RECEIPT UNKNOWN'],
    ['D','Crew telemetry','Authenticated dispatch, queue depth, throughput and latency','CAPACITY UNKNOWN'],
    ['E','HTML / metrics','Comparable N to N+1 deltas and verified source readback','VIEW IMPLEMENTED'],
    ['G','Governance','Independent review and effective main protection','ADMISSION UNVERIFIED']
  ];
  function cell(parent, tag, value, className='') {
    const e = document.createElement(tag);
    e.textContent = value;
    if (className) e.className = className;
    parent.appendChild(e);
    return e;
  }
  function metric(title, value, note) {
    const box = document.createElement('div'); box.className='kpi';
    cell(box,'span',title,'muted compact');
    cell(box,'b',value);
    cell(box,'small',note,'muted');
    cards.appendChild(box);
    return box;
  }
  metric('Executable registration · historical','30 / 460 · 6.52%','Earlier 30/457 = 6.56%; Δ −0.04 pp, +3 eligible assets');
  metric('Code test coverage','UNKNOWN','Statement / branch / diff require valid exact-head receipt');
  const live = metric('LDAB / crew live proof','UNKNOWN','No session or authenticated dispatch receipt ingested');
  route.forEach(([id,name,target,status]) => {
    const d=document.createElement('details'); d.className='artifact';
    const summary=cell(d,'summary',id+' · '+name+' — '+status);
    summary.style.cursor='pointer';
    cell(d,'p','Next DOV: '+target,'compact');
    lanes.appendChild(d);
  });
  fetch('data/missioncontrol_disjoint_census.json',{cache:'no-store'})
   .then(r=>{if(!r.ok) throw Error('no admitted census file');return r.json()})
   .then(d=>{
      if(d.schema!=='code-purple.disjoint-census-validation.v1'||d.valid!==true||
         !/^[a-f0-9]{40}$/.test(d.head_sha||'')) throw Error('invalid census');
      const ps=d.populations||{};
      const available=['statement','branch','diff'].filter(k=>ps[k]?.status==='MEASURED' &&
         Number.isFinite(ps[k]?.percent));
      if(available.length) {
        const box=cards.children[1];
        box.querySelector('b').textContent=available.map(k=>k+': '+ps[k].percent+'%').join(' · ');
        box.querySelector('small').textContent='Source '+d.head_sha.slice(0,12)+' · verify currency against main';
      }
      const proven=ps.ldab_live_sessions?.status==='MEASURED' &&
       Number.isInteger(ps.ldab_live_sessions.numerator) && ps.ldab_live_sessions.numerator>0;
      if(proven) {
        live.querySelector('b').textContent=ps.ldab_live_sessions.numerator+' LDAB session(s)';
        live.querySelector('small').textContent='Census source '+d.head_sha.slice(0,12)+'; crew proof remains separate';
      }
   }).catch(()=>{ /* Preserve UNKNOWN without claiming failure or zero. */ });
})();
