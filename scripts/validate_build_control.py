"""Measure/Control gate for the Recursive Build & DMAIC Control Plan.

Computes the repo-measurable KPIs named in ``99_handover/PROCESS_DMAIC.md`` and
``99_handover/BUILD_WORKFLOW.md`` for the HELIUM_VCR_UHP handover pack:

* diff_decisions     — every MASTER_DIFF change carries a ✅/❌/⏳ decision
* rtm_consistency    — RTM.csv and requirements.json carry the same requirements
* trace_references   — ITP references and requirement sources resolve
* glob_manifest      — every file listed in the .glob manifest exists
* baseline_meta      — requirements.json meta baseline matches the manifest version
* rename_pack        — no legacy RENAME_SBS names left in the handover pack
* rename_downstream  — legacy names in downstream book docs never exceed the
                       committed ratchet baseline (report-only until step 2 lands)

Usage:
    python scripts/validate_build_control.py [--root PATH] [--report-json PATH]

Exit codes:
    0 — all blocking checks passed
    1 — one or more blocking checks failed, or required files are missing
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

MASTER_DIFF = Path("99_handover/MASTER_DIFF.md")
RENAME_SBS = Path("99_handover/RENAME_SBS.csv")
RTM_CSV = Path("01_requirements/RTM.csv")
REQUIREMENTS_JSON = Path("01_requirements/requirements.json")
ITP_CSV = Path("04_quality/ITP_HE_VCR.csv")
GLOB_MANIFEST = Path("docs/artifacts/handover_master_applied.glob.yaml")
BASELINE = Path("99_handover/build_control_baseline.json")

# The MASTER document itself; RTM sources cite it as "Addendum ...".
EXTERNAL_ANCHORS = {"Addendum": Path("Input/Addendum_master.md")}

# Files that record the old names on purpose (diff ledger, rename map, rejected ADR option).
RENAME_LEDGER = {MASTER_DIFF, RENAME_SBS, Path("06_arch/ADR/ADR.md")}

DOWNSTREAM_GLOBS = ("Book_Master.md", "book_md/**/*.md")

VALID_DECISIONS = {"✅", "❌", "⏳"}
CHANGE_ROW = re.compile(r"^\|\s*(C\d+)\s*\|")


def _read(root: Path, rel: Path) -> str:
    return (root / rel).read_text(encoding="utf-8")


def _csv_rows(root: Path, rel: Path) -> list[dict[str, str]]:
    with (root / rel).open(encoding="utf-8", newline="") as fh:
        return [row for row in csv.DictReader(fh) if any(row.values())]


def _check(name: str, blocking: bool, errors: list[str], **kpis) -> dict:
    return {
        "name": name,
        "blocking": blocking,
        "status": "failed" if errors else "passed",
        "kpis": kpis,
        "errors": errors,
    }


def check_diff_decisions(root: Path) -> dict:
    errors: list[str] = []
    counts = {d: 0 for d in sorted(VALID_DECISIONS)}
    total = 0
    for line in _read(root, MASTER_DIFF).splitlines():
        match = CHANGE_ROW.match(line)
        if not match:
            continue
        total += 1
        decision = line.strip().strip("|").split("|")[-1].strip()
        if decision in counts:
            counts[decision] += 1
        else:
            errors.append(f"{match.group(1)}: missing or invalid decision {decision!r}")
    if total == 0:
        errors.append(f"{MASTER_DIFF.as_posix()}: no change rows found")
    approved = counts["✅"]
    return _check(
        "diff_decisions",
        True,
        errors,
        changes_total=total,
        approved=approved,
        rejected=counts["❌"],
        pending=counts["⏳"],
        approved_pct=round(approved / total * 100, 2) if total else 0.0,
    )


def _requirements(root: Path) -> dict:
    return json.loads(_read(root, REQUIREMENTS_JSON))


def check_rtm_consistency(root: Path) -> dict:
    errors: list[str] = []
    csv_rows = _csv_rows(root, RTM_CSV)
    json_rows = _requirements(root).get("requirements", [])
    csv_ids = [r["ReqID"].strip() for r in csv_rows]
    json_ids = [r.get("id", "") for r in json_rows]
    for label, ids in (("RTM.csv", csv_ids), ("requirements.json", json_ids)):
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        if dupes:
            errors.append(f"{label}: duplicate ids {dupes}")
    for missing in sorted(set(json_ids) - set(csv_ids)):
        errors.append(f"{missing}: in requirements.json but not RTM.csv")
    for missing in sorted(set(csv_ids) - set(json_ids)):
        errors.append(f"{missing}: in RTM.csv but not requirements.json")
    csv_shall = {r["ReqID"].strip(): r["Shall Statement"].strip() for r in csv_rows}
    for row in json_rows:
        rid = row.get("id", "")
        if rid in csv_shall and csv_shall[rid] != row.get("shall", "").strip():
            errors.append(f"{rid}: shall statement differs between RTM.csv and requirements.json")
    matched = len(set(csv_ids) & set(json_ids))
    union = len(set(csv_ids) | set(json_ids))
    return _check(
        "rtm_consistency",
        True,
        errors,
        requirements_total=union,
        matched=matched,
        coverage_pct=round(matched / union * 100, 2) if union else 0.0,
    )


def _manifest(root: Path) -> dict:
    return yaml.safe_load(_read(root, GLOB_MANIFEST)) or {}


def _pack_paths(manifest: dict) -> list[Path]:
    return [
        Path(entry["path"])
        for entry in (manifest.get("files") or {}).values()
        if isinstance(entry, dict) and "path" in entry
    ]


def _resolve_reference(ref: str, req_ids: set[str], stems: set[str], root: Path) -> bool:
    head = ref.split()[0] if ref.split() else ""
    if head in req_ids:
        return True
    if head in EXTERNAL_ANCHORS:
        return (root / EXTERNAL_ANCHORS[head]).exists()
    return Path(head).stem in stems


def check_trace_references(root: Path) -> dict:
    errors: list[str] = []
    req_ids = {r.get("id", "") for r in _requirements(root).get("requirements", [])}
    stems = {p.stem for p in _pack_paths(_manifest(root)) if (root / p).exists()}
    refs: list[tuple[str, str]] = []
    for row in _csv_rows(root, ITP_CSV):
        refs.append((f"ITP '{row['Step']}'", row["Reference"]))
    for row in _requirements(root).get("requirements", []):
        refs.append((f"{row.get('id', '?')} source", row.get("source", "")))
    resolved = 0
    for owner, value in refs:
        parts = [p.strip() for p in value.split(";") if p.strip()]
        bad = [p for p in parts if not _resolve_reference(p, req_ids, stems, root)]
        if not parts:
            errors.append(f"{owner}: empty reference")
        elif bad:
            errors.append(f"{owner}: unresolved reference(s) {bad}")
        else:
            resolved += 1
    return _check(
        "trace_references",
        True,
        errors,
        references_total=len(refs),
        resolved=resolved,
        resolved_pct=round(resolved / len(refs) * 100, 2) if refs else 0.0,
    )


def check_glob_manifest(root: Path) -> dict:
    paths = _pack_paths(_manifest(root))
    errors = [f"{p.as_posix()}: listed in manifest but missing" for p in paths if not (root / p).exists()]
    if not paths:
        errors.append(f"{GLOB_MANIFEST.as_posix()}: no file entries")
    return _check(
        "glob_manifest",
        True,
        errors,
        files_total=len(paths),
        present=len(paths) - len([p for p in paths if not (root / p).exists()]),
    )


def check_baseline_meta(root: Path) -> dict:
    errors: list[str] = []
    meta = _requirements(root).get("meta", {})
    version = str(_manifest(root).get("version", ""))
    for field in ("baseline", "date"):
        if not meta.get(field):
            errors.append(f"requirements.json meta: missing '{field}'")
    if meta.get("baseline") and str(meta["baseline"]) != version:
        errors.append(
            f"requirements.json meta baseline {meta['baseline']!r} != manifest version {version!r}"
        )
    return _check("baseline_meta", True, errors, baseline=str(meta.get("baseline", "")), manifest_version=version)


def _legacy_pattern(root: Path) -> re.Pattern[str]:
    with (root / RENAME_SBS).open(encoding="utf-8", newline="") as fh:
        legacy = [row[0] for row in csv.reader(fh) if row]
    return re.compile(r"(?<![\w.-])(" + "|".join(map(re.escape, legacy)) + r")(?!\w)")


def _count_legacy(root: Path, paths: list[Path], pattern: re.Pattern[str]) -> dict[str, int]:
    counts = {}
    for rel in paths:
        if (root / rel).exists():
            hits = len(pattern.findall(_read(root, rel)))
            if hits:
                counts[rel.as_posix()] = hits
    return counts


def check_rename_pack(root: Path) -> dict:
    pattern = _legacy_pattern(root)
    governed = [p for p in _pack_paths(_manifest(root)) if p not in RENAME_LEDGER]
    hits = _count_legacy(root, governed, pattern)
    errors = [f"{path}: {n} legacy name(s) from RENAME_SBS.csv" for path, n in sorted(hits.items())]
    return _check("rename_pack", True, errors, files_governed=len(governed), legacy_hits=sum(hits.values()))


def check_rename_downstream(root: Path) -> dict:
    pattern = _legacy_pattern(root)
    paths = sorted({p.relative_to(root) for g in DOWNSTREAM_GLOBS for p in root.glob(g)})
    hits = _count_legacy(root, paths, pattern)
    total = sum(hits.values())
    ceiling = json.loads(_read(root, BASELINE))["rename_downstream_max"] if (root / BASELINE).exists() else 0
    errors = []
    if total > ceiling:
        errors.append(f"legacy names in downstream docs rose to {total} (ratchet baseline {ceiling})")
    return _check(
        "rename_downstream",
        False,
        errors,
        files_scanned=len(paths),
        legacy_hits=total,
        ratchet_baseline=ceiling,
        by_file=dict(sorted(hits.items())),
    )


CHECKS = (
    check_diff_decisions,
    check_rtm_consistency,
    check_trace_references,
    check_glob_manifest,
    check_baseline_meta,
    check_rename_pack,
    check_rename_downstream,
)

REQUIRED = (MASTER_DIFF, RENAME_SBS, RTM_CSV, REQUIREMENTS_JSON, ITP_CSV, GLOB_MANIFEST)


def validate(root: Path = REPO_ROOT, report_json: Path | None = None) -> int:
    missing = [p.as_posix() for p in REQUIRED if not (root / p).exists()]
    if missing:
        for p in missing:
            print(f"FAIL: required file not found: {p}", file=sys.stderr)
        return 1

    results = [check(root) for check in CHECKS]
    blocking_failed = [r["name"] for r in results if r["blocking"] and r["status"] == "failed"]

    for r in results:
        tag = "OK  " if r["status"] == "passed" else ("FAIL" if r["blocking"] else "WARN")
        print(f"  {tag} {r['name']}: {json.dumps({k: v for k, v in r['kpis'].items() if k != 'by_file'})}")
        for e in r["errors"]:
            print(f"       - {e}", file=sys.stderr if r["blocking"] else sys.stdout)

    if report_json is not None:
        report_json.parent.mkdir(parents=True, exist_ok=True)
        report_json.write_text(
            json.dumps(
                {
                    "schema": "codex.build_control.report.v1",
                    "status": "failed" if blocking_failed else "passed",
                    "blocking_failed": blocking_failed,
                    "checks": results,
                },
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"Wrote build-control KPI report -> {report_json}")

    if blocking_failed:
        print(f"FAIL: blocking build-control checks failed: {blocking_failed}", file=sys.stderr)
        return 1
    print(f"PASS: {len(results)} build-control check(s) evaluated")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Measure/Control gate for the Recursive Build & DMAIC Control Plan."
    )
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help="Repository root to evaluate.")
    parser.add_argument("--report-json", type=Path, default=None, help="Write the KPI report here.")
    args = parser.parse_args(argv)
    return validate(args.root.resolve(), args.report_json)


if __name__ == "__main__":
    sys.exit(main())
