"""Monotonic task-observation roll-up; no polling, background worker or dispatch."""
from __future__ import annotations
import hashlib
import json
from datetime import datetime

ORDER={"queued":0,"in_progress":1,"completed":2}

def _time(v):
    if not isinstance(v,str):
        raise ValueError("MISSING_EVENT_TIME")
    x=datetime.fromisoformat(v.replace("Z","+00:00"))
    if x.tzinfo is None or x.utcoffset() is None:
        raise ValueError("UNBOUND_EVENT_TIME")
    return x

def reconcile(events):
    if not isinstance(events,list) or not events:
        raise ValueError("EMPTY_EVENTS")
    current={}
    seen={}
    for event in events:
        if not isinstance(event,dict):
            raise ValueError("INVALID_EVENT")
        key=tuple(event.get(k) for k in ("repo","run_id","attempt","job_id"))
        if not isinstance(key[0],str) or not key[0] or any(type(x) is not int or x<1 for x in key[1:]):
            raise ValueError("INVALID_NATIVE_IDENTITY")
        head=event.get("head_sha")
        if not isinstance(head,str) or len(head)!=40 or any(c not in "0123456789abcdef" for c in head):
            raise ValueError("UNPINNED_HEAD")
        status=event.get("status")
        conclusion=event.get("conclusion")
        if status not in ORDER or ((status=="completed") != (conclusion is not None)):
            raise ValueError("INCONSISTENT_STATUS")
        if conclusion is not None and conclusion not in {"success","failure","cancelled","skipped","timed_out"}:
            raise ValueError("UNKNOWN_TERMINAL")
        _time(event.get("observed_at"))
        stamp=_time(event["observed_at"])
        identity=(key,head)
        if key in current and current[key]["head_sha"]!=head:
            raise ValueError("RUN_IDENTITY_HEAD_DRIFT")
        payload=json.dumps(event,sort_keys=True,separators=(",",":"))
        fingerprint=hashlib.sha256(payload.encode()).hexdigest()
        if (key,stamp) in seen:
            if seen[(key,stamp)]!=fingerprint:
                raise ValueError("SAME_TIME_CONFLICT")
            continue
        seen[(key,stamp)]=fingerprint
        older=current.get(key)
        if older:
            oldtime=_time(older["observed_at"])
            if stamp<oldtime:
                continue
            if ORDER[status]<ORDER[older["status"]]:
                raise ValueError("STATE_REGRESSION")
            if older["status"]=="completed" and (status!="completed" or conclusion!=older["conclusion"]):
                raise ValueError("TERMINAL_REWRITTEN")
        current[key]=dict(event)
    ordered=sorted(current.values(),key=lambda x:(x["repo"],x["run_id"],x["attempt"],x["job_id"]))
    return {"schema":"codepurple.mycelium.operational-event-rollup.v1",
            "events_ingested":len(events),
            "unique_event_observations":len(seen),
            "task_instances":len(ordered),
            "terminal":sum(x["status"]=="completed" for x in ordered),
            "reconciled":ordered,
            "source_digest":hashlib.sha256(json.dumps(ordered,sort_keys=True,separators=(",",":")).encode()).hexdigest(),
            "mutable_actions":0,"admission":"HOLD"}
