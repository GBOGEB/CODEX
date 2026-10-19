"""Turn OSV-Scanner SARIF into readable findings: GitHub annotations plus a job-summary table.

The OSV push/schedule scan runs Google's reusable workflow, which uploads its
findings only to the Security tab and as a SARIF artifact. This script makes
the same findings visible in the run itself (annotations are readable through
the check-runs API and in the Actions UI). Report-only: always exits 0 unless
the input is unreadable.

    python scripts/osv_sarif_summary.py PATH [PATH ...]   # files or directories
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

MAX_ANNOTATIONS = 40


def _files(paths: list[str]) -> list[Path]:
    out: list[Path] = []
    for p in map(Path, paths):
        if p.is_dir():
            out.extend(sorted(q for q in p.rglob("*") if q.suffix in (".sarif", ".json")))
        elif p.is_file():
            out.append(p)
    return out


def findings(sarif: dict[str, Any]) -> list[dict[str, str]]:
    rows = []
    for run in sarif.get("runs", []):
        rules = {r.get("id"): r for r in run.get("tool", {}).get("driver", {}).get("rules", [])}
        for res in run.get("results", []):
            rule_id = res.get("ruleId", "?")
            rule = rules.get(rule_id, {})
            loc = (res.get("locations") or [{}])[0].get("physicalLocation", {})
            rows.append({
                "id": rule_id,
                "level": res.get("level", "warning"),
                "file": loc.get("artifactLocation", {}).get("uri", ""),
                "line": str(loc.get("region", {}).get("startLine", "")),
                "summary": (rule.get("shortDescription", {}) or {}).get("text", ""),
                "message": " ".join(str(res.get("message", {}).get("text", "")).split()),
            })
    return rows


def _esc(text: str) -> str:
    return text.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")


def main(argv: list[str]) -> int:
    files = _files(argv)
    if not files:
        print("::warning::OSV findings: no SARIF file found (artifact missing or scan did not run)")
        return 0
    rows: list[dict[str, str]] = []
    for f in files:
        try:
            rows.extend(findings(json.loads(f.read_text(encoding="utf-8"))))
        except (json.JSONDecodeError, OSError) as exc:
            print(f"::error::OSV findings: cannot read {f}: {exc}")
            return 1
    print(f"::notice title=OSV findings::{len(rows)} finding(s) in {len(files)} SARIF file(s)")
    for r in rows[:MAX_ANNOTATIONS]:
        params = [f"file={r['file']}"] if r["file"] else []
        if r["file"] and r["line"]:
            params.append(f"line={r['line']}")
        params.append(f"title=OSV {r['id']}")
        text = r["summary"] or r["message"]
        print(f"::warning {','.join(params)}::{_esc(text[:900])}")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        lines = ["## OSV-Scanner findings", "", f"{len(rows)} finding(s).", "", "| Advisory | File | Summary |", "|---|---|---|"]
        lines += [f"| {r['id']} | `{r['file']}` | {(r['summary'] or r['message'])[:200].replace('|', '/')} |" for r in rows]
        with open(summary, "a", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
