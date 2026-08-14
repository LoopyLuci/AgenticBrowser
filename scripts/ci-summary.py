#!/usr/bin/env python
import json
import os
from pathlib import Path
from datetime import datetime

REPORT = Path("reports/results.jsonl")
if not REPORT.exists():
    print("No CI report found at reports/results.jsonl")
    raise SystemExit(1)

stages = []
for line in REPORT.read_text().splitlines():
    line = line.strip()
    if not line:
        continue
    try:
        obj = json.loads(line)
    except json.JSONDecodeError:
        continue
    if obj.get("stage"):
        stages.append(obj)

if not stages:
    print("No stage records found in report.")
    raise SystemExit(1)

passed = [s for s in stages if s.get("status") == "passed"]
failed = [s for s in stages if s.get("status") == "failed"]

print(f"Stages: {len(stages)} | Passed: {len(passed)} | Failed: {len(failed)}")
for stage in stages:
    status = stage.get("status", "unknown")
    label = "PASS" if status == "passed" else "FAIL" if status == "failed" else status.upper()
    ts = stage.get("timestamp", "")
    print(f"  [{label}] {stage.get('stage')}  {ts}")
if failed:
    raise SystemExit(1)

print("")
print("FINAL VERDICT: PASS")
