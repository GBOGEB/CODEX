#!/usr/bin/env python3
"""Damped early-stage PID-like power-of-two controller for CODEX ID pulses.

This is deliberately not a tuned continuous PID: scale is discrete and samples are
small. P/I/D-style telemetry is recorded so gains can be learned before automation.
"""
from __future__ import annotations
import argparse,json
LEVELS=(1,2,4,8,16,32,64)
def decide(current,queue,active_workers,rework_rate,collisions,speed_per_sue=None,baseline_speed_per_sue=None,previous_queue=None,previous_wall_ms=None,wall_ms=None,sample_count=1):
    if current not in LEVELS: raise ValueError('current workers must be power-of-two 1..64')
    sue=current*3; effective=active_workers*3; qps=queue/max(effective,1); util=active_workers/current
    target=1.5; p_error=qps-target; d_queue=None if previous_queue is None else queue-previous_queue; wall_ratio=None if previous_wall_ms in (None,0) or wall_ms is None else wall_ms/previous_wall_ms
    degradation=None if speed_per_sue is None or baseline_speed_per_sue in (None,0) else 1-(speed_per_sue/baseline_speed_per_sue)
    idx=LEVELS.index(current); nxt=current; action='HOLD'; reasons=[]
    hard=collisions>0 or rework_rate>=.10 or (degradation is not None and degradation>.20)
    if hard: nxt=LEVELS[max(0,idx-1)]; action='RAMP_DOWN'; reasons=['correctness_or_efficiency_guard']
    elif util<.5: nxt=LEVELS[max(0,idx-1)]; action='RAMP_DOWN' if nxt<current else 'HOLD'; reasons=['capacity_starved']
    elif qps<1.0: nxt=LEVELS[max(0,idx-1)]; action='RAMP_DOWN'; reasons=['queue_shallow']
    elif qps>=target and util>=.8:
        # Early-stage damping: one step only; 64 requires >=2 comparable samples and no wall-time explosion.
        if current==32 and (sample_count<2 or (wall_ratio is not None and wall_ratio>1.8)): reasons=['hold_32_for_second_sample']
        else: nxt=LEVELS[min(len(LEVELS)-1,idx+1)]; action='RAMP_UP' if nxt>current else 'HOLD'; reasons=['promotion_gate_pass']
    else: reasons=['hold_band']
    return {'schema_version':'2.0','controller_mode':'DAMPED_EARLY_PID_LIKE','current_workers':current,'current_sue_depth':sue,'active_workers':active_workers,'effective_sue_depth':effective,'queue':queue,'queue_per_effective_sue':round(qps,4),'runner_utilization':round(util,4),'sample_count':sample_count,'p_queue_error':round(p_error,4),'i_term':'DEFERRED_UNTIL_SAMPLE_SERIES','d_queue':d_queue,'wall_ms':wall_ms,'previous_wall_ms':previous_wall_ms,'wall_ratio':None if wall_ratio is None else round(wall_ratio,4),'speed_per_sue':speed_per_sue,'baseline_speed_per_sue':baseline_speed_per_sue,'speed_degradation':None if degradation is None else round(degradation,4),'rework_rate':rework_rate,'collisions':collisions,'action':action,'next_workers':nxt,'next_sue_depth':nxt*3,'reasons':reasons,'authority_mutation':'SERIALIZED_OUTSIDE_DISCOVERY_WORKERS'}
def main():
    p=argparse.ArgumentParser(); p.add_argument('--current',type=int,required=True); p.add_argument('--queue',type=int,required=True); p.add_argument('--active-workers',type=int,required=True); p.add_argument('--rework-rate',type=float,default=0); p.add_argument('--collisions',type=int,default=0); p.add_argument('--speed-per-sue',type=float); p.add_argument('--baseline-speed-per-sue',type=float); p.add_argument('--previous-queue',type=int); p.add_argument('--previous-wall-ms',type=float); p.add_argument('--wall-ms',type=float); p.add_argument('--sample-count',type=int,default=1); a=p.parse_args(); print(json.dumps(decide(a.current,a.queue,a.active_workers,a.rework_rate,a.collisions,a.speed_per_sue,a.baseline_speed_per_sue,a.previous_queue,a.previous_wall_ms,a.wall_ms,a.sample_count),indent=2))
if __name__=='__main__': main()
