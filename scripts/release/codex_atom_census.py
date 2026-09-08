from __future__ import annotations

import hashlib
import json
import subprocess
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "release" / "W72_CODEX_ATOM_CENSUS.json"
FEATURE = ROOT / "release" / "W72_FEATURE_ROW.json"

TEXT_EXTS = {
    ".md", ".txt", ".py", ".yaml", ".yml", ".json", ".toml", ".ini",
    ".cfg", ".xml", ".html", ".htm", ".js", ".ts", ".tsx", ".jsx",
    ".sh", ".ps1", ".bat", ".csv", ".rst", ".sql", ".graphql",
}
BINARY_EXTS = {".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".pdf", ".zip", ".tar.gz", ".gz"}
SOURCE_EXTS = {".py", ".js", ".ts", ".tsx", ".jsx", ".sh", ".ps1", ".bat"}
CONFIG_EXTS = {".yaml", ".yml", ".json", ".toml", ".ini", ".cfg", ".xml"}
DOC_EXTS = {".md", ".rst", ".txt"}
GENERATED_WORDS = ("generated", "rendered", "artifact", "output", "build", "dist")
GENERATOR_CONTEXT = ("generated", "generator", "regenerate", "render", "build output", "produces", "output")
SOURCE_CONTEXT = ("source", "input", "upload", "offer", "origin", "evidence")


def git(*args: str) -> str:
    proc = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=True)
    return proc.stdout


def extension(path: Path) -> str:
    lower = path.name.lower()
    if lower.endswith(".tar.gz"):
        return ".tar.gz"
    return path.suffix.lower() or "[none]"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def authority_zone(rel: str) -> str | None:
    p = rel.replace("\\", "/")
    if p.startswith(".github/workflows/"):
        return "workflow_control"
    if p.startswith("release/"):
        return "release_control"
    if p.startswith("ssot/"):
        return "ssot_authority"
    if p.startswith("triage/requirements/"):
        return "requirement_authority"
    if p.startswith("codex/"):
        return "runtime_authority"
    if p.startswith("architecture/release/"):
        return "release_architecture"
    return None


def classify(rel: str, ext: str) -> str:
    p = rel.replace("\\", "/")
    zone = authority_zone(rel)
    if zone:
        return zone
    if p.startswith("tests/") or "/tests/" in p:
        return "test"
    if ext in BINARY_EXTS:
        return "binary_rendered"
    if ext in SOURCE_EXTS:
        return "source_script"
    if ext in CONFIG_EXTS or "schema" in p.lower():
        return "schema_config"
    if ext in DOC_EXTS or p.startswith("docs/"):
        return "documentation"
    return "other"


def parse_last_touch(tracked: set[str]) -> dict[str, dict[str, str]]:
    raw = git("log", "--format=@@%H%x1f%cI%x1f%an%x1f%ae", "--name-only", "--no-renames", "--all")
    result: dict[str, dict[str, str]] = {}
    meta: dict[str, str] | None = None
    for line in raw.splitlines():
        if line.startswith("@@"):
            parts = line[2:].split("\x1f")
            if len(parts) >= 4:
                meta = {"sha": parts[0], "timestamp": parts[1], "author": parts[2], "email": parts[3]}
            continue
        rel = line.strip()
        if meta and rel in tracked and rel not in result:
            result[rel] = dict(meta)
            if len(result) == len(tracked):
                break
    return result


def load_text_corpus(paths: list[str]) -> list[tuple[str, str]]:
    corpus: list[tuple[str, str]] = []
    for rel in paths:
        p = ROOT / rel
        if extension(p) not in TEXT_EXTS or not p.is_file():
            continue
        try:
            if p.stat().st_size > 1_000_000:
                continue
            corpus.append((rel, p.read_text(encoding="utf-8", errors="ignore")))
        except OSError:
            continue
    return corpus


def lineage_for(rel: str, corpus: list[tuple[str, str]]) -> dict[str, object]:
    name = Path(rel).name
    refs: list[dict[str, str]] = []
    generated = False
    source = False
    for source_path, text in corpus:
        if source_path == rel:
            continue
        if name not in text and rel not in text:
            continue
        for line in text.splitlines():
            if name in line or rel in line:
                low = line.lower()
                refs.append({"path": source_path, "context": line.strip()[:500]})
                generated = generated or any(k in low for k in GENERATOR_CONTEXT)
                source = source or any(k in low for k in SOURCE_CONTEXT)
                if len(refs) >= 12:
                    break
        if len(refs) >= 12:
            break
    if generated:
        state = "GENERATED_REFERENCED"
    elif source:
        state = "SOURCE_REFERENCED"
    elif refs:
        state = "REFERENCED_UNCLASSIFIED"
    else:
        state = "ORIGIN_UNDETERMINED"
    return {"origin_state": state, "reference_count": len(refs), "references": refs}


def temporal_clusters(atoms: list[dict[str, object]], seconds: int = 300) -> dict[str, int]:
    timed: list[tuple[datetime, str]] = []
    for atom in atoms:
        stamp = str(atom.get("last_touch_utc") or "")
        if not stamp:
            continue
        try:
            timed.append((datetime.fromisoformat(stamp.replace("Z", "+00:00")), str(atom["path"])))
        except ValueError:
            continue
    timed.sort()
    mapping: dict[str, int] = {}
    cluster_no = 0
    prev: datetime | None = None
    members: list[str] = []
    groups: list[list[str]] = []
    for ts, rel in timed:
        if prev is None or (ts - prev).total_seconds() <= seconds:
            members.append(rel)
        else:
            groups.append(members)
            members = [rel]
        prev = ts
    if members:
        groups.append(members)
    for group in groups:
        if len(group) < 2:
            continue
        cluster_no += 1
        for rel in group:
            mapping[rel] = cluster_no
    return mapping


def main() -> int:
    source_sha = git("rev-parse", "HEAD").strip()
    tracked = [p for p in git("ls-files", "-z").split("\0") if p]
    tracked_set = set(tracked)
    last_touch = parse_last_touch(tracked_set)
    corpus = load_text_corpus(tracked)

    atoms: list[dict[str, object]] = []
    class_counts: Counter[str] = Counter()
    ext_counts: Counter[str] = Counter()
    zone_counts: Counter[str] = Counter()
    binary_atoms: list[dict[str, object]] = []
    generated_candidates: list[dict[str, object]] = []

    for rel in sorted(tracked):
        p = ROOT / rel
        if not p.is_file():
            continue
        ext = extension(p)
        cls = classify(rel, ext)
        zone = authority_zone(rel)
        touch = last_touch.get(rel, {})
        atom: dict[str, object] = {
            "atom_id": "atom:" + hashlib.sha256(rel.encode("utf-8")).hexdigest()[:16],
            "repository": "GBOGEB/CODEX",
            "subrepo": rel.split("/", 1)[0] if "/" in rel else "[root]",
            "folder": str(Path(rel).parent),
            "path": rel,
            "filename": p.name,
            "extension": ext,
            "bytes": p.stat().st_size,
            "content_sha256": sha256_file(p),
            "last_commit_sha": touch.get("sha"),
            "last_touch_utc": touch.get("timestamp"),
            "last_touch_author": touch.get("author"),
            "provenance_plane": "GIT_TRACKED",
            "classification": cls,
            "authority_zone": zone,
            "release_critical": bool(zone),
        }
        class_counts[cls] += 1
        ext_counts[ext] += 1
        if zone:
            zone_counts[zone] += 1
        if ext in BINARY_EXTS:
            atom.update(lineage_for(rel, corpus))
            binary_atoms.append(atom)
        if zone and any(word in rel.lower() for word in GENERATED_WORDS):
            if "origin_state" not in atom:
                atom.update(lineage_for(rel, corpus))
            generated_candidates.append(atom)
        atoms.append(atom)

    cluster_map = temporal_clusters(atoms)
    for atom in atoms:
        atom["temporal_cluster_5m"] = cluster_map.get(str(atom["path"]))

    authority_by_name: dict[str, list[dict[str, object]]] = defaultdict(list)
    for atom in atoms:
        if atom["authority_zone"]:
            authority_by_name[str(atom["filename"]).lower()].append(atom)

    duplicate_families: list[dict[str, object]] = []
    competing_families: list[dict[str, object]] = []
    mirror_families: list[dict[str, object]] = []
    for key, members in sorted(authority_by_name.items()):
        if len(members) < 2:
            continue
        paths = sorted(str(m["path"]) for m in members)
        fingerprint = hashlib.sha256("\n".join(paths).encode("utf-8")).hexdigest()
        hashes = sorted(set(str(m["content_sha256"]) for m in members))
        family = {
            "exact_filename_key": key,
            "member_count": len(members),
            "paths": paths,
            "path_set_sha256": fingerprint,
            "distinct_content_hashes": len(hashes),
            "disposition": "SAME_CONTENT_MIRROR" if len(hashes) == 1 else "COMPETING_AUTHORITY_CANDIDATE",
        }
        duplicate_families.append(family)
        (mirror_families if len(hashes) == 1 else competing_families).append(family)

    binary_origin_undetermined = [a for a in binary_atoms if a.get("origin_state") == "ORIGIN_UNDETERMINED"]
    release_binary_origin_undetermined = [a for a in binary_origin_undetermined if a.get("release_critical")]
    generated_lineage_gaps = [a for a in generated_candidates if a.get("origin_state") not in {"GENERATED_REFERENCED", "SOURCE_REFERENCED"}]

    findings = {
        "competing_authority_families": len(competing_families),
        "competing_authority_assets": sum(int(f["member_count"]) for f in competing_families),
        "same_content_mirror_families": len(mirror_families),
        "binary_assets_total": len(binary_atoms),
        "binary_origin_undetermined_all_repo": len(binary_origin_undetermined),
        "binary_origin_undetermined_release_critical": len(release_binary_origin_undetermined),
        "generated_authority_lineage_gaps": len(generated_lineage_gaps),
        "provenance_plane_unknown": 0,
        "classification_unknown": sum(1 for a in atoms if a["classification"] == "other"),
    }
    critical_blocker_findings = (
        findings["competing_authority_families"]
        + findings["binary_origin_undetermined_release_critical"]
        + findings["generated_authority_lineage_gaps"]
    )

    payload = {
        "schema_version": "1.0",
        "gate": "CODEX_ATOM_UNKNOWN_BURNDOWN",
        "source_sha": source_sha,
        "rules": {
            "tracked_file_provenance": "Every git ls-files atom is GIT_TRACKED; source-vs-generated origin is tracked separately and never inferred from extension alone.",
            "duplicate_rule": "Exact filename within authority-bearing zones + exact sorted path-set SHA256. Stem-only grouping is prohibited.",
            "score_rule": "Classification/diagnostic improvement grants no terminal publish PASS by itself.",
        },
        "population": {
            "tracked_assets": len(atoms),
            "total_bytes": sum(int(a["bytes"]) for a in atoms),
            "release_critical_assets": sum(1 for a in atoms if a["release_critical"]),
            "classification_counts": dict(sorted(class_counts.items())),
            "extension_counts": dict(sorted(ext_counts.items(), key=lambda kv: (-kv[1], kv[0]))),
            "authority_zone_counts": dict(sorted(zone_counts.items())),
            "temporal_clustered_assets_5m": sum(1 for a in atoms if a.get("temporal_cluster_5m")),
            "temporal_clusters_5m": len(set(cluster_map.values())),
        },
        "unknown_burndown": {
            "pre_method_provenance_plane_undetermined": len(atoms),
            "post_method_provenance_plane_undetermined": 0,
            "provenance_plane_reduction": len(atoms),
            "origin_undetermined_retained": len(binary_origin_undetermined),
            "release_critical_origin_undetermined_retained": len(release_binary_origin_undetermined),
            "critical_blocker_findings": critical_blocker_findings,
            "findings": findings,
        },
        "duplicate_authority_families": duplicate_families,
        "binary_origin_undetermined": [
            {k: a.get(k) for k in ("atom_id", "path", "folder", "filename", "extension", "bytes", "content_sha256", "authority_zone", "origin_state", "reference_count")}
            for a in binary_origin_undetermined
        ],
        "generated_authority_lineage_gaps": [
            {k: a.get(k) for k in ("atom_id", "path", "folder", "filename", "bytes", "content_sha256", "authority_zone", "origin_state", "reference_count")}
            for a in generated_lineage_gaps
        ],
        "atoms": atoms,
    }

    feature = {
        "schema_version": "1.0",
        "source_sha": source_sha,
        "tracked_assets": len(atoms),
        "release_critical_assets": payload["population"]["release_critical_assets"],
        "critical_blocker_findings": critical_blocker_findings,
        "competing_authority_families": findings["competing_authority_families"],
        "binary_origin_undetermined": findings["binary_origin_undetermined_all_repo"],
        "release_binary_origin_undetermined": findings["binary_origin_undetermined_release_critical"],
        "generated_lineage_gap": findings["generated_authority_lineage_gaps"],
        "classification_unknown": findings["classification_unknown"],
        "provenance_plane_unknown": 0,
        "temporal_cluster_count_5m": payload["population"]["temporal_clusters_5m"],
        "temporal_clustered_assets_5m": payload["population"]["temporal_clustered_assets_5m"],
        "binary_assets_total": findings["binary_assets_total"],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    FEATURE.write_text(json.dumps(feature, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(feature, indent=2))
    print(f"atom_census={OUT.relative_to(ROOT)}")
    print(f"feature_row={FEATURE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
