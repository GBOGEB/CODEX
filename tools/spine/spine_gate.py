"""SPINE-core extraction gate (ADR-0002).

Resolves spine/SPINE_MANIFEST.yaml against the working tree and, for every
admitted file, checks:

  1. deny_terms     — private organisation/project/system names
  2. secret_patterns — tokens, keys, credential assignments, e-mail addresses
  3. import closure — repo-local Python imports must resolve inside the
                       admitted set (a backbone that imports private code is
                       not a working backbone)

Emits receipts/spine/SPINE_GATE_RECEIPT.json (per-file sha256 + disposition)
and exits non-zero unless every admitted file is CLEAN. Stdlib + PyYAML only.
"""

from __future__ import annotations

import argparse
import ast
import fnmatch
import hashlib
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
TEXT_SUFFIXES = {
    ".py", ".ts", ".js", ".json", ".yaml", ".yml", ".md", ".txt", ".toml",
    ".cfg", ".ini", ".html", ".css", ".csv", ".template", ".sh", "",
}


def _match(rel: str, patterns: list[str]) -> bool:
    for pat in patterns:
        if fnmatch.fnmatch(rel, pat):
            return True
        # "dir/**" should also match files directly under dir
        if pat.endswith("/**") and rel.startswith(pat[:-3] + "/"):
            return True
    return False


SKIP_DIRS = {".git", "node_modules", "__pycache__"}


def _all_files(root: Path) -> list[str]:
    """Every file under root as a posix relative path.

    Matching is done with fnmatch on this list rather than Path.glob, because
    Path.glob("dir/**") returns only directories before Python 3.13 and files
    as well from 3.13 on; the gate must resolve identically on every runner.
    """
    out = []
    stack = [root]
    while stack:
        d = stack.pop()
        for p in d.iterdir():
            if p.is_dir():
                if p.name not in SKIP_DIRS:
                    stack.append(p)
            elif p.is_file():
                out.append(p.relative_to(root).as_posix())
    return out


def resolve(root: Path, manifest: dict) -> tuple[list[str], list[str]]:
    include = manifest.get("include", [])
    exclude = manifest.get("exclude", [])
    files = _all_files(root)
    admitted, missing = set(), []
    for pat in include:
        hits = [rel for rel in files if _match(rel, [pat])]
        if not hits:
            missing.append(pat)
        admitted.update(rel for rel in hits if not _match(rel, exclude))
    return sorted(admitted), missing


def _compile(groups: dict) -> list[tuple[str, re.Pattern]]:
    out = []
    for name, pats in (groups or {}).items():
        for pat in pats if isinstance(pats, list) else [pats]:
            out.append((name, re.compile(pat, re.IGNORECASE)))
    return out


def _allowed(rel: str, label: str, allowlist: list[dict]) -> bool:
    return any(
        fnmatch.fnmatch(rel, a.get("path", "")) and a.get("pattern") == label
        for a in allowlist
    )


def scan_text(rel: str, text: str, rules, allowlist, *, redact: bool = False) -> list[dict]:
    """Return findings; with redact=True the matched text never leaves this function.

    Secret findings are recorded only as a short digest and length, so the
    receipt (an uploaded CI artifact) and the log cannot republish a leaked
    credential that the gate has just caught.
    """
    findings = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for label, rx in rules:
            m = rx.search(line)
            if m and not _allowed(rel, label, allowlist):
                if redact:
                    digest = hashlib.sha256(m.group(0).encode()).hexdigest()[:12]
                    evidence = f"<redacted len={len(m.group(0))} sha256:{digest}>"
                else:
                    evidence = m.group(0)[:60]
                findings.append({"line": lineno, "rule": label, "match": evidence})
    return findings


def local_top_modules(root: Path) -> set[str]:
    names = set()
    for p in root.iterdir():
        if p.name.startswith("."):
            continue
        if p.is_dir() and any(p.glob("*.py")) or p.is_dir() and (p / "__init__.py").exists():
            names.add(p.name)
        elif p.suffix == ".py":
            names.add(p.stem)
    return names


def import_closure(root: Path, admitted: list[str]) -> dict[str, list[str]]:
    local = local_top_modules(root)
    admitted_tops = {a.split("/")[0] for a in admitted}
    admitted_tops |= {Path(a).stem for a in admitted if a.endswith(".py")}
    # src-layout packages (pca_engine/src/pca_engine) are importable by package name
    for a in admitted:
        parts = a.split("/")
        if "src" in parts and parts.index("src") + 1 < len(parts):
            admitted_tops.add(parts[parts.index("src") + 1])
    broken: dict[str, list[str]] = {}
    for rel in admitted:
        if not rel.endswith(".py"):
            continue
        try:
            tree = ast.parse((root / rel).read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError) as exc:
            broken.setdefault(rel, []).append(f"unparseable: {exc}")
            continue
        for node in ast.walk(tree):
            mods = []
            if isinstance(node, ast.Import):
                mods = [n.name for n in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                mods = [node.module]
            for mod in mods:
                top = mod.split(".")[0]
                if top in local and top not in admitted_tops:
                    broken.setdefault(rel, []).append(mod)
    return broken


def run(root: Path, manifest_path: Path, receipt_path: Path) -> int:
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    admitted, missing = resolve(root, manifest)
    allowlist = manifest.get("allowlist") or []
    deny = _compile(manifest.get("deny_terms"))
    credential_rules = _compile(manifest.get("secret_patterns"))
    closure = import_closure(root, admitted)

    overlay = manifest.get("overlay") or {}
    for src in overlay.values():
        if not (root / src).is_file():
            missing.append(f"overlay source {src}")
    sources = [(rel, rel) for rel in admitted]
    sources += [(dest, src) for dest, src in overlay.items() if (root / src).is_file()]
    sources.sort()

    files, blocked = [], 0
    for rel, src in sources:
        data = (root / src).read_bytes()
        entry = {"path": rel, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
        if src != rel:
            entry["overlay_source"] = src
        findings = []
        if Path(rel).suffix in TEXT_SUFFIXES or Path(rel).name.startswith("."):
            text = data.decode("utf-8", errors="replace")
            findings = scan_text(rel, text, deny, allowlist)
            findings += scan_text(rel, text, credential_rules, allowlist, redact=True)
        if rel in closure:
            findings += [{"rule": "import_closure", "match": m} for m in closure[rel]]
        entry["status"] = "BLOCKED" if findings else "CLEAN"
        if findings:
            entry["findings"] = findings
            blocked += 1
        files.append(entry)

    verdict = "PASS" if admitted and not blocked and not missing else "FAIL"
    tree_digest = hashlib.sha256(
        "".join(f"{f['path']}\0{f['sha256']}\n" for f in files).encode()
    ).hexdigest()
    receipt = {
        "gate": "SPINE_GATE",
        "adr": "ADR-0002",
        "generated_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "verdict": verdict,
        "counts": {"admitted": len(files), "clean": len(files) - blocked, "blocked": blocked},
        "missing_include_patterns": missing,
        "admitted_tree_sha256": tree_digest,
        "files": files,
    }
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    print(f"SPINE_GATE {verdict}: admitted={len(files)} clean={len(files) - blocked} blocked={blocked}")
    for pat in missing:
        print(f"  MISSING include pattern matched nothing: {pat}")
    for f in files:
        if f["status"] == "BLOCKED":
            rules = sorted({x["rule"] for x in f["findings"]})
            print(f"  BLOCKED {f['path']}  [{', '.join(rules)}]")
    return 0 if verdict == "PASS" else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=REPO_ROOT)
    ap.add_argument("--manifest", type=Path, default=None)
    ap.add_argument("--receipt", type=Path, default=None)
    a = ap.parse_args(argv)
    root = a.root.resolve()
    manifest = a.manifest or root / "spine" / "SPINE_MANIFEST.yaml"
    receipt = a.receipt or root / "receipts" / "spine" / "SPINE_GATE_RECEIPT.json"
    return run(root, manifest, receipt)


if __name__ == "__main__":
    sys.exit(main())
