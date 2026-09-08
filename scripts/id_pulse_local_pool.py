#!/usr/bin/env python3
"""Execute balanced CODEX ID-burndown packets as logical workers on one runner."""
from __future__ import annotations
import argparse, concurrent.futures, json, statistics, time
from pathlib import Path
ALLOWED={1,2,4,8,16,32,64}
def spread(v): return 0.0 if not v or max(v)==0 else round((max(v)-min(v))/max(v),4)
def percentile(values,p):
    if not values: return 0
    xs=sorted(values); i=min(len(xs)-1,max(0,round((len(xs)-1)*p))); return int(xs[i])
def consume(bucket,workers,out_dir,internal_enqueue_ns):
    started=time.perf_counter_ns(); wait_ns=max(0,started-internal_enqueue_ns)
    s=int(bucket['shard']); t=time.perf_counter_ns(); items=list(bucket['items']); elapsed=time.perf_counter_ns()-t
    r={'schema_version':'5.1','purpose':'CODEX_ID_BURNDOWN_DISCOVERY_RECEIPT','execution_transport':'LOCAL_LOGICAL_POOL','logical_workers':workers,'sue':workers*3,'shard':s,'assigned_count':len(items),'assigned_weight':bucket['weight'],'internal_enqueue_ns':internal_enqueue_ns,'worker_started_ns':started,'internal_queue_wait_ns':wait_ns,'elapsed_ns':elapsed,'candidates':items,'authority_mutation':'FORBIDDEN'}
    (out_dir/f'receipt-{s:02d}.json').write_text(json.dumps(r,indent=2)+'\n'); return r
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--plan',default='reports/id_burndown/work_plan.json'); ap.add_argument('--out-dir',default='reports/id_burndown/local-receipts'); ap.add_argument('--local-threads',type=int,default=0); a=ap.parse_args()
    plan=json.loads(Path(a.plan).read_text()); workers=int(plan['workers']); bins=list(plan['bins'])
    if workers not in ALLOWED or len(bins)!=workers: raise SystemExit('invalid logical worker plan')
    out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True); threads=max(1,min(a.local_threads or workers,workers))
    admitted_epoch_ns=time.time_ns(); plan_epoch_ns=int(plan.get('plan_created_epoch_ns',admitted_epoch_ns)); external_admission_wait_ns=max(0,admitted_epoch_ns-plan_epoch_ns)
    internal_enqueue_ns=time.perf_counter_ns(); start=internal_enqueue_ns
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as p: receipts=list(p.map(lambda b:consume(b,workers,out,internal_enqueue_ns),bins))
    wall=time.perf_counter_ns()-start; q=int(plan['queue'])
    for r in receipts: r['queue']=q; (out/f"receipt-{int(r['shard']):02d}.json").write_text(json.dumps(r,indent=2)+'\n')
    counts=[r['assigned_count'] for r in receipts]; weights=[r['assigned_weight'] for r in receipts]; elapsed=[r['elapsed_ns'] for r in receipts]; waits=[r['internal_queue_wait_ns'] for r in receipts]
    stats={'schema_version':'2.1','execution_transport':'LOCAL_LOGICAL_POOL','logical_workers':workers,'logical_worker_slots':workers,'physical_runner_slots':1,'local_threads':threads,'sue_depth':workers*3,'effective_sue_depth':len(receipts)*3,'queue':q,'queue_per_sue':round(q/(workers*3),4),'completed_workers':len(receipts),'count_skew':spread(counts),'weight_skew':spread(weights),'processing_time_skew':spread(elapsed),'processing_ns_p50':int(statistics.median(elapsed)) if elapsed else 0,'processing_ns_max':max(elapsed) if elapsed else 0,'external_runner_admission_wait_ns':external_admission_wait_ns,'external_runner_admission_wait_s':round(external_admission_wait_ns/1e9,6),'internal_queue_wait_ns_p50':percentile(waits,0.50),'internal_queue_wait_ns_p95':percentile(waits,0.95),'internal_queue_wait_ns_max':max(waits) if waits else 0,'internal_queue_wait_us_p50':round(percentile(waits,0.50)/1e3,3),'internal_queue_wait_us_p95':round(percentile(waits,0.95)/1e3,3),'internal_queue_wait_us_max':round((max(waits) if waits else 0)/1e3,3),'wall_ns':wall,'wall_ms':round(wall/1e6,4),'items_per_wall_second':round(q/(wall/1e9),4) if wall else None,'items_per_sue_second':round(q/((workers*3)*(wall/1e9)),6) if wall else None,'authority_mutation':'FORBIDDEN'}
    (out/'pool_stats.json').write_text(json.dumps(stats,indent=2)+'\n'); print('ID_LOCAL_POOL_PASS '+json.dumps(stats,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
