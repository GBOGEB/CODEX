#!/usr/bin/env python3
"""Source-bound read-only Ruff/Pyright/coverage collector. Missing files remain unknown."""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def load_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))

def coverage(path: Path):
    root = ET.parse(path).getroot()
    lines = root.attrib.get("lines-valid")
    hit = root.attrib.get("lines-covered")
    branches = root.attrib.get("branches-valid")
    covered = root.attrib.get("branches-covered")
    return {"statement": (hit, lines), "branch": (covered, branches)}

def collect(repo, sha, run_id, ruff=None, pyright=None, cov=None, eligible=None):
    populations = {}
    artifacts = {}
    if cov:
        p = Path(cov)
        vals = coverage(p)
        artifacts["coverage_xml_sha256"] = digest(p)
        for k, pair in vals.items():
            n, d = pair
            if n is not None and d is not None and int(d) > 0:
                populations[k] = {"status": "MEASURED", "numerator": int(n),
                    "denominator": int(d), "source_sha": sha, "run_id": run_id}
    if eligible:
        eligible_set = {line.strip() for line in Path(eligible).read_text().splitlines()
                        if line.strip() and not line.startswith("#")}
        artifacts["eligible_manifest_sha256"] = digest(Path(eligible))
    else:
        eligible_set = None
    for kind, name, key in ((ruff, "ruff", "ruff_files"), (pyright, "pyright", "pyright_files")):
        if not kind:
            continue
        path = Path(kind)
        doc = load_json(path)
        artifacts[name + "_sha256"] = digest(path)
        # Ruff is a list of diagnostics; Pyright uses generalDiagnostics.
        findings = doc if name == "ruff" else doc.get("generalDiagnostics", [])
        if not isinstance(findings, list):
            raise ValueError(name + " diagnostics must be an array")
        affected = {str(row.get("filename" if name == "ruff" else "file", ""))
                    for row in findings if isinstance(row, dict)}
        artifacts[name + "_findings"] = len(findings)
        artifacts[name + "_affected_files"] = len(affected - {""})
        # Diagnostics do not reveal all scanned files; require independent manifest.
        if eligible_set:
            populations[key] = {"status": "MEASURED", "numerator": len(eligible_set),
                "denominator": len(eligible_set), "source_sha": sha, "run_id": run_id}
        else:
            artifacts[name + "_coverage_status"] = "WITHHELD_NO_ELIGIBLE_MANIFEST"
    return {"repository": repo, "head_sha": sha, "populations": populations,
            "artifact_evidence": artifacts, "scope_warning": (
              "Eligible-file manifests must represent actual scanner inclusion; "
              "diagnostic-only records cannot establish scanned-file coverage.")}

def main():
    a=argparse.ArgumentParser()
    a.add_argument("--repo",required=True)
    a.add_argument("--sha",required=True)
    a.add_argument("--run-id",type=int,required=True)
    a.add_argument("--ruff")
    a.add_argument("--pyright")
    a.add_argument("--coverage")
    a.add_argument("--eligible")
    a.add_argument("--out",type=Path,required=True)
    z=a.parse_args()
    data=collect(z.repo,z.sha,z.run_id,z.ruff,z.pyright,z.coverage,z.eligible)
    z.out.parent.mkdir(parents=True,exist_ok=True)
    z.out.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"written":str(z.out),"sha256":digest(z.out),
        "populations":list(data["populations"])}))

if __name__=="__main__":
    main()
