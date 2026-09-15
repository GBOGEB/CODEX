from __future__ import annotations

import hashlib
import json
import os
import subprocess
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "release" / "W73_CODEX_UNKNOWN_DISPOSITION.json"
FEATURE = ROOT / "release" / "W73_FEATURE_ROW.json"

BINARY_EXTS = {".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".pdf", ".zip", ".gz", ".tar.gz"}
PACKAGE_MARKERS = {"__init__.py"}


def git(*args: str) -> str:
    p = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=True)
    return p.stdout


def ext(path: str) -> str:
    low = path.lower()
    return ".tar.gz" if low.endswith(".tar.gz") else (Path(path).suffix.lower() or "[none]")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def authority_zone(path: str) -> str | None:
    if path.startswith(".github/workflows/"):
        return "workflow_control"
    if path.startswith("release/"):
        return "release_control"
    if path.startswith("ssot/"):
        return "ssot_authority"
    if path.startswith("triage/requirements/"):
        return "requirement_authority"
    if path.startswith("codex/"):
        return "runtime_authority"
    if path.startswith("architecture/release/"):
        return "release_architecture"
    return None


def legacy_binary_disposition(path: str) -> tuple[str, str]:
    e = ext(path)
    if e not in BINARY_EXTS:
        return "NOT_BINARY", ""
    if path.startswith("07_ops/qps_roundtrip/") or path.startswith("qps/cost-master/"):
        return "POLICY_VIOLATION", "Controlled QPS paths are text-source only."
    if path == "VCR_Summary_master.pdf":
        return "MIGRATE_EXTERNAL_REFERENCE", "data/pdf/README.md identifies this PDF as an external-store reference master."
    name = Path(path).name
    wider_legacy = (
        path == "Addendum_book_master.docx"
        or name.startswith("Full_VCR_Handover")
        or (name.startswith("VCR_") and e in {".docx", ".pdf"})
        or path.startswith("Input/Addendum II -")
        or path == "Input/cryoplant_deck_handover_R1C2.zip"
    )
    if wider_legacy:
        return "REVIEW_KEEP_OR_MIGRATE", "qps/cost-master/docs/LEGACY_BINARY_CLASSIFICATION.md default for wider legacy binary estate."
    return "UNCLASSIFIED", "No governed binary disposition matched."


def parse_last_touch(tracked: set[str]) -> dict[str, dict[str, str]]:
    raw = git("log", "--format=@@%H%x1f%cI%x1f%an", "--name-only", "--no-renames", "--all")
    out: dict[str, dict[str, str]] = {}
    meta: dict[str, str] | None = None
    for line in raw.splitlines():
        if line.startswith("@@"):
            parts = line[2:].split("\x1f")
            if len(parts) >= 3:
                meta = {"sha": parts[0], "timestamp": parts[1], "author": parts[2]}
            continue
        p = line.strip()
        if meta and p in tracked and p not in out:
            out[p] = dict(meta)
            if len(out) == len(tracked):
                break
    return out


def temporal_clusters(rows: list[dict[str, object]], seconds: int = 300) -> tuple[int, int]:
    timed: list[tuple[datetime, str]] = []
    for r in rows:
        stamp = r.get("last_touch_utc")
        if not stamp:
            continue
        try:
            timed.append((datetime.fromisoformat(str(stamp).replace("Z", "+00:00")), str(r["path"])))
        except ValueError:
            pass
    timed.sort()
    groups: list[list[str]] = []
    current: list[str] = []
    prev: datetime | None = None
    for ts, p in timed:
        if prev is None or (ts - prev).total_seconds() <= seconds:
            current.append(p)
        else:
            groups.append(current)
            current = [p]
        prev = ts
    if current:
        groups.append(current)
    multi = [g for g in groups if len(g) >= 2]
    return len(multi), sum(len(g) for g in multi)


def explicit_generated_output(path: str) -> bool:
    # A name containing build/artifact is not enough. Count only binary authority
    # outputs or files that self-identify as generated/do-not-edit.
    zone = authority_zone(path)
    if not zone:
        return False
    if ext(path) in BINARY_EXTS:
        return True
    p = ROOT / path
    try:
        head = p.read_text(encoding="utf-8", errors="ignore")[:4096].lower()
    except OSError:
        return False
    return "generated file" in head or "do not edit" in head


def main() -> int:
    head = git("rev-parse", "HEAD").strip()
    expected = os.environ.get("EXPECTED_SOURCE_SHA", "").strip()
    if expected and head != expected:
        raise SystemExit(f"exact-head binding FAIL: git={head} expected={expected}")

    tracked = [p for p in git("ls-files", "-z").split("\0") if p]
    touch = parse_last_touch(set(tracked))
    rows: list[dict[str, object]] = []
    authority_by_name: dict[str, list[dict[str, object]]] = defaultdict(list)
    binary_dispositions: Counter[str] = Counter()
    binary_rows: list[dict[str, object]] = []
    other_noncritical = 0

    known_suffixes = {
        ".py", ".md", ".yaml", ".yml", ".json", ".html", ".htm", ".csv", ".svg", ".sh",
        ".ps1", ".ts", ".tsx", ".js", ".txt", ".toml", ".css", ".j2", ".jsonl", ".swift",
        ".mmd", ".sha256", ".template", ".vba", ".xml", ".ini", ".cfg", ".sql", ".graphql",
    }

    for path in sorted(tracked):
        p = ROOT / path
        if not p.is_file():
            continue
        e = ext(path)
        zone = authority_zone(path)
        t = touch.get(path, {})
        row: dict[str, object] = {
            "path": path,
            "folder": str(Path(path).parent),
            "filename": p.name,
            "extension": e,
            "bytes": p.stat().st_size,
            "sha256": sha256(p),
            "provenance_plane": "GIT_TRACKED",
            "authority_zone": zone,
            "last_commit_sha": t.get("sha"),
            "last_touch_utc": t.get("timestamp"),
            "last_touch_author": t.get("author"),
        }
        if e in BINARY_EXTS:
            disp, basis = legacy_binary_disposition(path)
            row["binary_disposition"] = disp
            row["disposition_basis"] = basis
            binary_dispositions[disp] += 1
            binary_rows.append(row)
        elif e not in known_suffixes and e != "[none]" and not zone:
            other_noncritical += 1
        if zone and p.name not in PACKAGE_MARKERS:
            authority_by_name[p.name.lower()].append(row)
        rows.append(row)

    competing: list[dict[str, object]] = []
    mirrors: list[dict[str, object]] = []
    for name, members in sorted(authority_by_name.items()):
        if len(members) < 2:
            continue
        paths = sorted(str(x["path"]) for x in members)
        hashes = {str(x["sha256"]) for x in members}
        family = {
            "filename": name,
            "member_count": len(members),
            "paths": paths,
            "path_set_sha256": hashlib.sha256("\n".join(paths).encode()).hexdigest(),
            "distinct_content_hashes": len(hashes),
        }
        if len(hashes) == 1:
            family["disposition"] = "SAME_CONTENT_MIRROR"
            mirrors.append(family)
        else:
            family["disposition"] = "COMPETING_AUTHORITY_CANDIDATE"
            competing.append(family)

    generated_collisions = [r for r in rows if explicit_generated_output(str(r["path"]))]
    unclassified_binary = [r for r in binary_rows if r.get("binary_disposition") == "UNCLASSIFIED"]
    policy_violations = [r for r in binary_rows if r.get("binary_disposition") == "POLICY_VIOLATION"]
    controlled_review = [r for r in binary_rows if r.get("binary_disposition") == "REVIEW_KEEP_OR_MIGRATE"]
    external_refs = [r for r in binary_rows if r.get("binary_disposition") == "MIGRATE_EXTERNAL_REFERENCE"]
    release_binary_unknown = [r for r in unclassified_binary if r.get("authority_zone")]
    critical_unknown = len(competing) + len(policy_violations) + len(release_binary_unknown) + len(generated_collisions)
    clusters, clustered_assets = temporal_clusters(rows)

    payload = {
        "schema_version": "2.0",
        "gate": "CODEX_UNKNOWN_DISPOSITION",
        "source_sha": head,
        "population": {
            "tracked_assets": len(rows),
            "tracked_bytes": sum(int(r["bytes"]) for r in rows),
            "authority_assets": sum(1 for r in rows if r.get("authority_zone")),
            "binary_assets": len(binary_rows),
            "binary_bytes": sum(int(r["bytes"]) for r in binary_rows),
            "binary_by_extension": dict(Counter(str(r["extension"]) for r in binary_rows)),
            "temporal_clusters_5m": clusters,
            "temporal_clustered_assets_5m": clustered_assets,
        },
        "burndown": {
            "w72_diagnostic_critical_findings": 5,
            "w73_critical_unknown_findings": critical_unknown,
            "critical_finding_reduction": 5 - critical_unknown,
            "provenance_plane_unknown": 0,
            "unclassified_binary_assets": len(unclassified_binary),
            "controlled_review_binary_assets": len(controlled_review),
            "external_reference_binary_assets": len(external_refs),
            "policy_violation_binary_assets": len(policy_violations),
            "competing_authority_families": len(competing),
            "same_content_mirror_families": len(mirrors),
            "generated_authority_collisions": len(generated_collisions),
            "noncritical_other_extension_assets": other_noncritical,
            "boundary": "REVIEW_KEEP_OR_MIGRATE is a governed disposition, not proof of source-vs-generated lineage or permission to delete/migrate.",
        },
        "binary_disposition_counts": dict(binary_dispositions),
        "binary_assets": binary_rows,
        "competing_authority_families": competing,
        "same_content_mirror_families": mirrors,
        "generated_authority_collisions": generated_collisions,
    }

    feature = {
        "schema_version": "2.0",
        "source_sha": head,
        "tracked_assets": len(rows),
        "authority_assets": payload["population"]["authority_assets"],
        "binary_assets": len(binary_rows),
        "binary_bytes": payload["population"]["binary_bytes"],
        "critical_unknown_findings": critical_unknown,
        "unclassified_binary_assets": len(unclassified_binary),
        "controlled_review_binary_assets": len(controlled_review),
        "external_reference_binary_assets": len(external_refs),
        "policy_violation_binary_assets": len(policy_violations),
        "competing_authority_families": len(competing),
        "generated_authority_collisions": len(generated_collisions),
        "provenance_plane_unknown": 0,
        "temporal_clusters_5m": clusters,
        "temporal_clustered_assets_5m": clustered_assets,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    FEATURE.write_text(json.dumps(feature, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(feature, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
