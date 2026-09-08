#!/usr/bin/env python3
"""Derive a 5-slot work-conserving scheduler sample from the current ID work plan."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from id_work_conserving_scheduler import Item, choose, summarize

CLASS_GAIN={
    'AUTHORITY_CANDIDATE': 5.0,
    'SCHEMA_CANDIDATE': 4.0,
    'CONSUMER_OR_CONTRACT_CANDIDATE': 3.0,
    'RECEIPT_CANDIDATE': 1.5,
}

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument('--plan',default='reports/id_burndown/work_plan.json')
    p.add_argument('--out',default='reports/id_burndown/scheduler_sample.json')
    p.add_argument('--pool-size',type=int,default=5)
    a=p.parse_args()
    plan=json.loads(Path(a.plan).read_text(encoding='utf-8'))
    items=[]
    ordinal=0
    for bucket in plan.get('bins',[]):
        for row in bucket.get('items',[]):
            cls=row.get('candidate_class','CONSUMER_OR_CONTRACT_CANDIDATE')
            weight=float(row.get('work_weight',2.0))
            size=max(1,int(row.get('bytes',1)))
            est=max(0.05, min(20.0, 0.05*weight + size/2_000_000.0))
            items.append(Item(
                id=row.get('logical_id') or row.get('path') or f'item-{ordinal}',
                est_remaining_s=round(est,4),
                convergence_gain=CLASS_GAIN.get(cls,2.0),
                stability_gain=1.0 if 'SCHEMA' in cls else 0.25,
                unblock_gain=1.5 if cls in {'AUTHORITY_CANDIDATE','SCHEMA_CANDIDATE'} else 0.25,
                age_s=float((ordinal % 11)*15),
                max_queue_s=300.0,
                resumable=True,
                setup_affinity=str(cls),
                checkpoint_cost_s=0.01,
            ))
            ordinal+=1
    execution_slots=max(0,a.pool_size-1)
    selected=choose(items,execution_slots)
    out=summarize(items,a.pool_size)
    out.update({
        'source_queue': len(items),
        'selected_count': len(selected),
        'dispatch_ids': [x.id for x in selected],
        'dispatch_value_density': [round(x.value_density(),6) for x in selected],
        'estimated_dispatch_work_s': round(sum(x.est_remaining_s for x in selected),4),
        'coordination_model': 'ONE_COORDINATOR_PRE_DISPATCH_POST_RECONCILE',
        'queue_policy': 'NON_FIFO_VALUE_DENSITY_WITH_AGING_DEADLINE',
    })
    path=Path(a.out); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print('ID_SCHEDULER_SAMPLE_PASS '+json.dumps(out,sort_keys=True))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
