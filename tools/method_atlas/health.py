"""Per-repository health for the Method Atlas: code, testing, DMAIC, MIP, bridge,
federation, Docker and SQL.

Every dimension is a list of sub-checks. A sub-check reports a completion
(num/den), a weight and evidence paths; the dimension score is the weighted
mean of its applicable sub-checks (0-100). A dimension whose artefacts do not
exist in a repo is N/A, never RED. All inputs are tracked files read from the
working tree; nothing is executed.
"""
from __future__ import annotations

import ast
import csv
import io
import json
import re
import warnings
from pathlib import Path

import yaml

TEST_RX = re.compile(r"(^|/)(tests?|testing)/.*\.py$|(^|/)test_[^/]*\.py$|_test\.py$")
WORD_RX = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
MARKER_RX = re.compile(r"#\s*(TODO|FIXME|XXX|HACK)\b")
DMAIC_PHASES = {"define": r"\bdefine\b", "measure": r"\bmeasure\b", "analyze": r"\banaly[sz]e\b",
                "improve": r"\bimprove\b", "control": r"\bcontrol\b"}
MIP_STAGES = {"modernize": r"\bmoderni[sz]e\b", "innovate": r"\binnovate\b", "perpetuate": r"\bperpetuate\b"}
DATA_EXT = {".json", ".jsonl", ".yaml", ".yml", ".csv"}
MAX_BYTES = 1_500_000
MAX_LINES_OK = 800
EVIDENCE = 8


def _read(path: Path) -> str | None:
    try:
        if path.stat().st_size > MAX_BYTES:
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def _parses(path: Path, text: str) -> bool:
    ext = path.suffix.lower()
    try:
        if ext == ".json":
            json.loads(text)
        elif ext == ".jsonl":
            for line in text.splitlines():
                if line.strip():
                    json.loads(line)
        elif ext in (".yaml", ".yml"):
            list(yaml.safe_load_all(text))
        elif ext == ".csv":
            list(csv.reader(io.StringIO(text)))
        return True
    except (ValueError, yaml.YAMLError, csv.Error):
        return False


def check(cid: str, label: str, num: float, den: float, weight: float = 1.0, evidence=(), note: str | None = None) -> dict:
    """One sub-check. den == 0 means not applicable (excluded from the score)."""
    return {"id": cid, "label": label, "num": num, "den": den, "weight": weight,
            "completion": round(num / den, 4) if den else None,
            "evidence": sorted(evidence)[:EVIDENCE], "note": note}


def score(checks: list[dict]) -> float | None:
    live = [c for c in checks if c["den"]]
    if not live:
        return None
    return round(100 * sum(c["completion"] * c["weight"] for c in live) / sum(c["weight"] for c in live), 1)


def status(value: float | None, thresholds: dict) -> str:
    if value is None:
        return "NA"
    return "GREEN" if value >= thresholds["green"] else "AMBER" if value >= thresholds["amber"] else "RED"


class RepoView:
    """One pass over a repo's tracked files, keeping only what the checks need."""

    def __init__(self, root: Path, files: list[str]):
        self.root, self.files = root, files
        self.text: dict[str, str] = {}
        self.workflow_text: dict[str, str] = {}
        self.test_words: set[str] = set()
        for rel in files:
            ext = Path(rel).suffix.lower()
            if ext in (".py", ".sql", ".toml", ".cfg", ".ini") or ext in DATA_EXT or ext == ".md" or self.is_docker(rel):
                t = _read(root / rel)
                if t is None:
                    continue
                if rel.startswith(".github/workflows/"):
                    self.workflow_text[rel] = t
                if ext != ".md" or "dmaic" in rel.lower() or "mip" in rel.lower():
                    self.text[rel] = t
                if TEST_RX.search(rel):
                    self.test_words.update(WORD_RX.findall(t))
        self.py = [p for p in files if p.endswith(".py")]
        self.tests = [p for p in self.py if TEST_RX.search(p)]
        self.modules = [p for p in self.py if not TEST_RX.search(p) and Path(p).name != "__init__.py"]

    @staticmethod
    def is_docker(rel: str) -> bool:
        name = Path(rel).name.lower()
        return name.startswith("dockerfile") or name.endswith(".dockerfile")

    def tokens(self, rel: str) -> set[str]:
        return set(re.split(r"[^a-z0-9]+", rel.lower()))

    def tested(self, modules: list[str]) -> tuple[int, list[str]]:
        hit = [m for m in modules if Path(m).stem in self.test_words]
        return len(hit), [m for m in modules if m not in hit]

    def data_parse(self, paths: list[str]) -> tuple[int, list[str]]:
        data = [p for p in paths if Path(p).suffix.lower() in DATA_EXT and p in self.text]
        bad = [p for p in data if not _parses(self.root / p, self.text[p])]
        return len(data) - len(bad), bad

    def ci_mentions(self, rx: str) -> list[str]:
        r = re.compile(rx, re.I)
        return [w for w, t in self.workflow_text.items() if r.search(w) or r.search(t)]


# ---------------------------------------------------------------- dimensions

def code_health(v: RepoView) -> tuple[list, dict, bool]:
    if not v.py:
        return [], {}, False
    bad, warned, big, loc, markers = [], [], [], 0, 0
    for p in v.py:
        t = v.text.get(p)
        if t is None:
            continue
        n = t.count("\n") + 1
        loc += n
        markers += len(MARKER_RX.findall(t))
        if n > MAX_LINES_OK:
            big.append(p)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            try:
                ast.parse(t, filename=p)
            except (SyntaxError, ValueError):
                bad.append(p)
        if any(issubclass(w.category, SyntaxWarning) for w in caught):
            warned.append(p)
    pyproject = v.text.get("pyproject.toml", "")
    setup_cfg = v.text.get("setup.cfg", "")
    lint = [p for p in ("ruff.toml", ".ruff.toml", ".flake8") if p in v.files]
    if "[tool.ruff" in pyproject:
        lint.append("pyproject.toml [tool.ruff]")
    if "[flake8]" in setup_cfg:
        lint.append("setup.cfg [flake8]")
    lint += [f"CI: {w}" for w in v.ci_mentions(r"\bruff\b|\bflake8\b|\bpylint\b")]
    per_kloc = markers / max(loc / 1000, 1)
    checks = [
        check("syntax", "Python files parse (ast)", len(v.py) - len(bad), len(v.py), 3, bad),
        check("size", f"Files at most {MAX_LINES_OK} lines", len(v.py) - len(big), len(v.py), 1, big),
        check("warnings", "No SyntaxWarnings (e.g. invalid escape sequences)", len(v.py) - len(warned), len(v.py), 1, warned),
        check("lint", "Lint configured or run in CI (ruff/flake8/pylint)", 1 if lint else 0, 1, 1, lint),
        check("markers", "TODO/FIXME debt under 5 per kLOC", max(0.0, 1 - min(per_kloc / 5, 1)), 1, 1,
              note=f"{markers} markers, {per_kloc:.2f} per kLOC"),
    ]
    return checks, {"python_files": len(v.py), "loc": loc, "parse_failures": len(bad), "syntax_warnings": len(warned), "large_files": len(big),
                    "markers": markers}, True


def testing_health(v: RepoView) -> tuple[list, dict, bool]:
    if not v.py:
        return [], {}, False
    empty = [p for p in v.tests if Path(p).name.startswith("test_") and p in v.text and
             not re.search(r"^\s*(async\s+)?def test_|^\s*class Test|unittest\.TestCase", v.text[p], re.M)]
    test_fns = sum(len(re.findall(r"^\s*(?:async\s+)?def test_", v.text.get(p, ""), re.M)) for p in v.tests)
    runners = v.ci_mentions(r"\bpytest\b|\bunittest\b")
    cfg = [p for p in ("pytest.ini", "tox.ini", "conftest.py") if p in v.files]
    if "[tool.pytest" in v.text.get("pyproject.toml", ""):
        cfg.append("pyproject.toml [tool.pytest]")
    if "[tool:pytest]" in v.text.get("setup.cfg", ""):
        cfg.append("setup.cfg [tool:pytest]")
    ratio = len(v.tests) / max(len(v.modules), 1)
    named = [p for p in v.tests if Path(p).name.startswith("test_")]
    checks = [
        check("ratio", "Test files per module (target 0.5)", min(ratio / 0.5, 1), 1, 2,
              note=f"{len(v.tests)} test files / {len(v.modules)} modules = {ratio:.2f}"),
        check("non_empty", "Test files define tests", len(named) - len(empty), len(named), 2, empty),
        check("ci", "A workflow runs pytest/unittest", 1 if runners else 0, 1, 2, runners),
        check("config", "pytest configuration present", 1 if cfg else 0, 1, 1, cfg),
    ]
    return checks, {"test_files": len(v.tests), "test_functions": test_fns, "modules": len(v.modules),
                    "ci_workflows_running_tests": len(runners)}, True


def _family(v: RepoView, path_rx: str, text_rx: str) -> list[str]:
    pr, tr = re.compile(path_rx, re.I), re.compile(text_rx)
    return sorted(p for p in v.files if pr.search(p) or (p in v.text and tr.search(v.text[p])))


def _coverage(v: RepoView, family: list[str], terms: dict) -> tuple[list[str], list[str]]:
    found = []
    for term, rx in terms.items():
        r = re.compile(rx, re.I)
        if any(r.search(p) or (p in v.text and r.search(v.text[p])) for p in family):
            found.append(term)
    return found, [t for t in terms if t not in found]


def dmaic_health(v: RepoView) -> tuple[list, dict, bool]:
    fam = _family(v, r"dmaic", r"\bDMAIC\b")
    if not fam:
        return [], {}, False
    found, missing = _coverage(v, fam, DMAIC_PHASES)
    control = [p for p in fam if Path(p).suffix.lower() in DATA_EXT and re.search(r"control", p, re.I)]
    mods = [p for p in fam if p in v.modules]
    tested, untested = v.tested(mods)
    ok, bad = v.data_parse(fam)
    checks = [
        check("phases", "DMAIC phases referenced (D, M, A, I, C)", len(found), 5, 2, [f"missing: {m}" for m in missing]),
        check("control_artefacts", "Machine-readable Control artefacts exist", 1 if control else 0, 1, 1, control),
        check("tested", "DMAIC modules referenced by tests", tested, len(mods), 2, untested),
        check("data", "DMAIC data files parse", ok, ok + len(bad), 1, bad),
    ]
    return checks, {"files": len(fam), "modules": len(mods), "phases": found}, True


def mip_health(v: RepoView) -> tuple[list, dict, bool]:
    fam = _family(v, r"(^|[^a-z])mip([^a-z]|$)", r"\bMIP\b")
    if not fam:
        return [], {}, False
    found, missing = _coverage(v, fam, MIP_STAGES)
    mods = [p for p in fam if p in v.modules]
    tested, untested = v.tested(mods)
    ok, bad = v.data_parse(fam)
    ci = v.ci_mentions(r"(^|[^a-z])mip([^a-z]|$)")
    checks = [
        check("stages", "MIP stages referenced (Modernize, Innovate, Perpetuate)", len(found), 3, 2,
              [f"missing: {m}" for m in missing]),
        check("receipts", "MIP data/receipts parse", ok, ok + len(bad), 1, bad),
        check("tested", "MIP modules referenced by tests", tested, len(mods), 2, untested),
        check("ci", "A workflow covers MIP", 1 if ci else 0, 1, 1, ci),
    ]
    return checks, {"files": len(fam), "modules": len(mods), "stages": found, "ci_workflows": len(ci)}, True


def _peers(v: RepoView, fam: list[str]) -> list[str]:
    peers = set()
    for p in fam:
        peers.update(re.findall(r"GBOGEB/([A-Za-z0-9_.-]+)", v.text.get(p, "")))
    clean = {}
    for x in sorted(peers):  # sorted: the kept spelling must not depend on set order
        x = re.sub(r"\.git$", "", x.rstrip("."))
        if x:
            clean.setdefault(x.lower(), x)
    return sorted(clean.values(), key=str.lower)


def bridge_health(v: RepoView) -> tuple[list, dict, bool]:
    fam = sorted(p for p in v.files if "bridge" in p.lower())
    if not fam:
        return [], {}, False
    mods = [p for p in fam if p in v.modules]
    tested, untested = v.tested(mods)
    ok, bad = v.data_parse(fam)
    ci = v.ci_mentions(r"bridge")
    checks = [
        check("tested", "Bridge modules referenced by tests", tested, len(mods), 2, untested),
        check("data", "Bridge data files parse", ok, ok + len(bad), 1, bad),
        check("ci", "A workflow covers bridges", 1 if ci else 0, 1, 1, ci),
    ]
    return checks, {"files": len(fam), "modules": len(mods), "peers_referenced": _peers(v, fam)}, True


def federation_health(v: RepoView, declared: set[str]) -> tuple[list, dict, bool]:
    fam = sorted(p for p in v.files if "federat" in p.lower())
    if not fam:
        return [], {}, False
    mods = [p for p in fam if p in v.modules]
    tested, untested = v.tested(mods)
    ok, bad = v.data_parse(fam)
    ci = v.ci_mentions(r"federat")
    peers = _peers(v, fam)
    checks = [
        check("data", "Federation data files parse", ok, ok + len(bad), 2, bad),
        check("tested", "Federation modules referenced by tests", tested, len(mods), 2, untested),
        check("ci", "A workflow covers federation", 1 if ci else 0, 1, 1, ci),
    ]
    return checks, {"files": len(fam), "modules": len(mods), "peers_referenced": len(peers),
                    "peers_outside_atlas": [p for p in peers if p.lower() not in declared and p.lower() != "gbogeb"]}, True


def docker_health(v: RepoView) -> tuple[list, dict, bool]:
    dockerfiles = sorted(p for p in v.files if v.is_docker(p))
    compose = sorted(p for p in v.files if re.search(r"(^|/)(docker-)?compose[^/]*\.ya?ml$", p, re.I))
    if not dockerfiles and not compose:
        return [], {}, False
    froms, pinned, unpinned = 0, 0, []
    no_user, no_health, no_ignore = [], [], []
    for p in dockerfiles:
        t = v.text.get(p, "")
        stage_names = set(re.findall(r"^\s*FROM\s+\S+\s+AS\s+(\S+)", t, re.I | re.M))
        for img in re.findall(r"^\s*FROM\s+(?:--\S+\s+)*(\S+)", t, re.I | re.M):
            if img.lower() in {s.lower() for s in stage_names} or img == "scratch":
                continue
            froms += 1
            if "@sha256:" in img or (":" in img.split("/")[-1] and not img.endswith(":latest")):
                pinned += 1
            else:
                unpinned.append(f"{p}: {img}")
        users = re.findall(r"^\s*USER\s+(\S+)", t, re.I | re.M)
        if not users or users[-1] in ("root", "0", "0:0"):
            no_user.append(p)
        if not re.search(r"^\s*HEALTHCHECK\s", t, re.I | re.M):
            no_health.append(p)
        folder = str(Path(p).parent).replace("\\", "/")
        local = ".dockerignore" if folder in ("", ".") else f"{folder}/.dockerignore"
        if local not in v.files and ".dockerignore" not in v.files:
            no_ignore.append(p)
    builds = v.ci_mentions(r"docker build|docker/build-push-action|buildx")
    c_ok, c_bad = v.data_parse(compose)
    n = len(dockerfiles)
    checks = [
        check("pinned", "Base images pinned (tag or digest, not latest)", pinned, froms, 2, unpinned),
        check("user", "Runs as a non-root USER", n - len(no_user), n, 2, no_user),
        check("healthcheck", "HEALTHCHECK declared", n - len(no_health), n, 1, no_health),
        check("dockerignore", ".dockerignore present", n - len(no_ignore), n, 1, no_ignore),
        check("ci_build", "A workflow builds an image", (1 if builds else 0) if n else 0, 1 if n else 0, 1, builds),
        check("compose", "Compose files parse", c_ok, c_ok + len(c_bad), 1, c_bad),
    ]
    return checks, {"dockerfiles": n, "compose_files": len(compose), "base_images": froms}, True


def sql_health(v: RepoView) -> tuple[list, dict, bool]:
    sql = sorted(p for p in v.files if p.lower().endswith(".sql"))
    dbs = sorted(p for p in v.files if re.search(r"\.(db|sqlite3?)$", p, re.I))
    users = sorted(p for p in v.py if re.search(r"^\s*(import|from)\s+(sqlite3|sqlalchemy|psycopg2?|pymysql|duckdb)\b",
                                                 v.text.get(p, ""), re.M))
    if not (sql or dbs or users):
        return [], {}, False
    unsafe_ddl = [p for p in sql if re.search(r"\bDROP\s+TABLE\s+(?!IF\s+EXISTS)", v.text.get(p, ""), re.I)]
    calls, unsafe = 0, []
    for p in users:
        for line in v.text.get(p, "").splitlines():
            if ".execute(" in line or ".executemany(" in line:
                calls += 1
                if re.search(r"\.execute(?:many)?\(\s*f[\"']|\.format\(|[\"']\s*%\s*[\w(]|\+\s*\w+\s*\+", line):
                    unsafe.append(p)
    corpus = " ".join(v.text.get(p, "") for p in v.py)
    referenced = [p for p in sql if Path(p).name in corpus]
    checks = [
        check("no_db_binaries", "No database binaries tracked", 0 if dbs else 1, 1, 2, dbs),
        check("guarded_ddl", "DROP TABLE guarded with IF EXISTS", len(sql) - len(unsafe_ddl), len(sql), 1, unsafe_ddl),
        check("parameterised", "Queries parameterised (no f-string/format/concat)", calls - len(unsafe), calls, 2, set(unsafe)),
        check("referenced", "SQL files referenced by code", len(referenced), len(sql), 1,
              [p for p in sql if p not in referenced]),
    ]
    return checks, {"sql_files": len(sql), "db_binaries": len(dbs), "modules_using_sql": len(users),
                    "execute_calls": calls}, True


def build_health(seed: dict, files: dict, roots: dict) -> dict:
    cfg = seed["health"]
    thresholds = cfg["thresholds"]
    declared = {s["id"].lower() for s in seed["repos"]} | {str(s.get("remote", "")).split("/")[-1].lower() for s in seed["repos"]}
    out = {}
    for rid in sorted(files):
        v = RepoView(roots[rid], files[rid])
        results = {
            "code": code_health(v), "testing": testing_health(v), "dmaic": dmaic_health(v), "mip": mip_health(v),
            "bridge": bridge_health(v), "federation": federation_health(v, declared),
            "docker": docker_health(v), "sql": sql_health(v),
        }
        dims = {}
        for d in cfg["dimensions"]:
            checks, metrics, applicable = results[d["id"]]
            s = score(checks) if applicable else None
            dims[d["id"]] = {"applicable": applicable, "score": s, "status": status(s, thresholds),
                             "checks": checks, "metrics": metrics}
        live = [x["score"] for x in dims.values() if x["score"] is not None]
        overall = round(sum(live) / len(live), 1) if live else None
        out[rid] = {"overall": overall, "status": status(overall, thresholds), "dimensions": dims}
    return {"thresholds": thresholds, "dimensions": cfg["dimensions"], "repos": out}
