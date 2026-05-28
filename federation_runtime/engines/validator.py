#!/usr/bin/env python3
import json, sys
from pathlib import Path
r=Path(__file__).resolve().parents[1]
tele=json.load((r/'telemetry'/'telemetry_runtime.json').open())
if tele['semantic_density'] < 2.0:
    print('density below floor'); sys.exit(1)
if tele['semantic_entropy'] < 2.2:
    print('entropy below floor'); sys.exit(1)
print('validator checks passed')
