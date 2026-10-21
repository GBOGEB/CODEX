"""Measure the Mycelium / MIP KPIs declared in MANIFEST/MYCELIUM_KPI_MANIFEST.yaml.

Every value is computed from a bound receipt; a KPI that cannot be computed
is reported WITHHELD with a reason instead of a default number. The output is
deterministic (no wall-clock timestamps), so it can be committed and checked:

    python scripts/measure_mycelium_kpis.py          # write the report
    python scripts/measure_mycelium_kpis.py --check  # exit 1 if the committed report is stale
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "MANIFEST" / "MYCELIUM_KPI_MANIFEST.yaml"
OUTPUT = ROOT / "docs" / "data" / "mycelium_kpi_measurement.json"

MISSING = object()


class Withheld(Exception):
    """A KPI input is not available yet."""


class BindingError(Exception):
    """A present source does not contain the bound path."""


def _load_file(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        return yaml.safe_load(text)
    return json.loads(text)


def _run_generator(spec: str) -> Any:
    module_path, func_name = spec.split(":")
    module_file = ROOT / module_path
    module_spec = importlib.util.spec_from_file_location(module_file.stem, module_file)
    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return getattr(module, func_name)()


def _fingerprint(path: Path) -> str:
    # Normalise CRLF so a Windows working copy fingerprints like CI.
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def load_sources(manifest: dict, root: Path = ROOT) -> tuple[dict[str, Any], list[dict]]:
    data: dict[str, Any] = {}
    meta: list[dict] = []
    for alias, spec in manifest["sources"].items():
        path = root / spec["path"]
        origin = "file"
        if spec.get("generator"):
            # Always recompute: the file is an untracked byproduct whose presence
            # (and OS-specific path labels) would make the report non-deterministic.
            payload = _run_generator(spec["generator"])
            origin = "generator"
        elif path.exists():
            payload = _load_file(path)
        else:
            payload = MISSING
            origin = "missing"
        data[alias] = payload
        stamp = None
        if payload is not MISSING and spec.get("stamp") and isinstance(payload, dict):
            stamp = payload.get(spec["stamp"])
        meta.append(
            {
                "alias": alias,
                "path": spec["path"],
                "origin": origin,
                "sha256": _fingerprint(path) if origin == "file" else None,
                "stamp": stamp,
            }
        )
    return data, meta


def _walk(node: Any, segments: list[str], trail: str) -> list[Any]:
    if not segments:
        return [node]
    head, rest = segments[0], segments[1:]
    if head == "*":
        if isinstance(node, dict):
            children = list(node.values())
        elif isinstance(node, list):
            children = node
        else:
            raise BindingError(f"cannot expand '*' at '{trail}'")
        out: list[Any] = []
        for child in children:
            out.extend(_walk(child, rest, f"{trail}/*"))
        return out
    if isinstance(node, dict):
        if head not in node:
            # Under a wildcard, a node without the key simply does not contribute.
            if "*" in trail:
                return []
            raise BindingError(f"missing key '{head}' at '{trail or '/'}'")
        return _walk(node[head], rest, f"{trail}/{head}")
    if isinstance(node, list) and head.isdigit() and int(head) < len(node):
        return _walk(node[int(head)], rest, f"{trail}/{head}")
    raise BindingError(f"cannot read '{head}' at '{trail or '/'}'")


def _matches(value: Any, where: dict) -> bool:
    op = where["op"]
    target = where.get("value")
    if op == "eq":
        return value == target
    if op == "ne":
        return value != target
    if op == "in":
        return value in target
    if op == "contains":
        return isinstance(value, str) and target in value
    if op == "file_exists":
        return isinstance(value, str) and (ROOT / value.split("#", 1)[0]).is_file()
    raise ValueError(f"unknown where op: {op}")


def select(sources: dict[str, Any], selector: dict) -> Any:
    payload = sources.get(selector["source"], MISSING)
    if payload is MISSING:
        raise Withheld(f"source '{selector['source']}' is not available")
    path = selector.get("path", "")
    segments = [s for s in path.split("/") if s]
    values = _walk(payload, segments, "")
    agg = selector.get("agg", "value")
    if agg == "value":
        if "*" in segments:
            raise BindingError(f"'{path}' expands to many values; choose an aggregate")
        return values[0]
    if agg == "len":
        return len(values[0])
    if agg == "not_null":
        return 0 if values[0] is None else 1
    if agg == "sum":
        return sum(v for v in values if isinstance(v, (int, float)) and not isinstance(v, bool))
    if agg == "sum_keys":
        mapping = values[0]
        return sum(mapping.get(key, 0) for key in selector["keys"])
    if agg == "count_where":
        return sum(1 for v in values if _matches(v, selector["where"]))
    if agg == "distribution":
        return dict(sorted(Counter(str(v) for v in values if v is not None).items()))
    raise ValueError(f"unknown aggregate: {agg}")


def _number(value: Any, label: str) -> float:
    if isinstance(value, dict) and value.get("status") == "WITHHELD":
        raise Withheld(f"{label} is WITHHELD upstream")
    if value is None:
        raise Withheld(f"{label} is null upstream")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise BindingError(f"{label} is not numeric: {value!r}")
    return value


def band(value: Any, kpi: dict) -> str:
    direction = kpi.get("direction", "info")
    bands = kpi.get("bands")
    if direction == "info" or not bands or not isinstance(value, (int, float)):
        return "INFO"
    green, amber = bands["green"], bands["amber"]
    if direction == "higher_is_better":
        return "GREEN" if value >= green else "AMBER" if value >= amber else "RED"
    return "GREEN" if value <= green else "AMBER" if value <= amber else "RED"


def evaluate_kpi(kpi: dict, sources: dict[str, Any], unlock: dict[str, str]) -> dict:
    row = {
        "id": kpi["id"],
        "dimension": kpi["dimension"],
        "name": kpi["name"],
        "unit": kpi["unit"],
        "direction": kpi.get("direction", "info"),
        "target": kpi.get("target"),
        "dmaic_phase": kpi.get("dmaic_phase"),
    }
    try:
        if "status_from" in kpi:
            upstream = select(sources, kpi["status_from"])
            if upstream == "WITHHELD":
                raise Withheld("upstream status is WITHHELD")
        kind = kpi["formula"]["kind"]
        numerator = select(sources, kpi["numerator"])
        inputs: dict[str, Any] = {"numerator": numerator}
        if kind == "value":
            if kpi["unit"] == "distribution":
                if not isinstance(numerator, dict):
                    raise BindingError("distribution KPI did not resolve to a mapping")
                value: Any = numerator
            else:
                value = _number(numerator, "numerator")
        elif kind in {"ratio", "ratio_pct"}:
            denominator = select(sources, kpi["denominator"])
            inputs["denominator"] = denominator
            num = _number(numerator, "numerator")
            den = _number(denominator, "denominator")
            if den == 0:
                raise Withheld("denominator is zero")
            value = round(num / den * (100 if kind == "ratio_pct" else 1), 2)
        else:
            raise ValueError(f"unknown formula kind: {kind}")
        row.update(status="MEASURED", value=value, band=band(value, kpi), inputs=inputs)
    except Withheld as exc:
        row.update(status="WITHHELD", value=None, band=None, reason=str(exc))
    except BindingError as exc:
        row.update(status="BINDING_ERROR", value=None, band=None, reason=str(exc))
    if kpi["id"] in unlock:
        row["unlock"] = unlock[kpi["id"]]
    return row


def evaluate_check(check: dict, sources: dict[str, Any]) -> dict:
    row = {"id": check["id"], "name": check["name"]}
    try:
        left = select(sources, check["left"])
        right = select(sources, check["right"])
        row.update(status="PASS" if left == right else "FAIL", left=left, right=right)
    except Withheld as exc:
        row.update(status="WITHHELD", reason=str(exc))
    except BindingError as exc:
        row.update(status="BINDING_ERROR", reason=str(exc))
    if check.get("note"):
        row["note"] = check["note"]
    return row


def _summarize(rows: list[dict]) -> dict:
    status = Counter(r["status"] for r in rows)
    bands = Counter(r["band"] for r in rows if r.get("band"))
    defined = len(rows)
    return {
        "defined": defined,
        "measured": status.get("MEASURED", 0),
        "withheld": status.get("WITHHELD", 0),
        "binding_errors": status.get("BINDING_ERROR", 0),
        "measurement_coverage_pct": round(status.get("MEASURED", 0) / defined * 100, 2) if defined else None,
        "bands": {name: bands.get(name, 0) for name in ("GREEN", "AMBER", "RED", "INFO")},
    }


def measure(manifest: dict | None = None, root: Path = ROOT) -> dict:
    manifest = manifest or yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    sources, source_meta = load_sources(manifest, root)
    unlock = manifest.get("unlock", {})
    kpis = [evaluate_kpi(k, sources, unlock) for k in manifest["kpis"]]
    checks = [evaluate_check(c, sources) for c in manifest.get("checks", [])]
    by_dimension = {
        dim: _summarize([r for r in kpis if r["dimension"] == dim]) for dim in manifest["dimensions"]
    }
    check_status = Counter(c["status"] for c in checks)
    return {
        "schema_version": "0.1",
        "manifest_id": manifest["manifest_id"],
        "authority_class": manifest["authority_class"],
        "authority_transfer": False,
        "formal_credit_delta": 0,
        "engineering_credit_delta": 0,
        "evidence_policy": manifest["principles"]["evidence_policy"],
        "composite_score": None,
        "composite_score_reason": "no_composite_score: KPIs are control signals, not a ranking",
        "sources": source_meta,
        "summary": {
            "overall": _summarize(kpis),
            "by_dimension": by_dimension,
            "checks": {name: check_status.get(name, 0) for name in ("PASS", "FAIL", "WITHHELD", "BINDING_ERROR")},
        },
        "kpis": kpis,
        "checks": checks,
        "red_kpis": [
            {"id": r["id"], "name": r["name"], "value": r["value"], "target": r["target"], "unlock": r.get("unlock")}
            for r in kpis
            if r.get("band") == "RED"
        ],
        "withheld_kpis": [
            {"id": r["id"], "reason": r["reason"], "unlock": r.get("unlock")} for r in kpis if r["status"] == "WITHHELD"
        ],
        "unbound_declared_metrics": manifest.get("unbound_declared_metrics", []),
    }


def render(report: dict) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="exit 1 if the committed report is stale")
    args = parser.parse_args(argv)
    report = measure()
    text = render(report)
    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != text:
            print(f"STALE: run `python scripts/measure_mycelium_kpis.py` and commit {OUTPUT.name}.", file=sys.stderr)
            return 1
    else:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(text, encoding="utf-8", newline="\n")
    overall = report["summary"]["overall"]
    print(
        f"Mycelium KPIs: {overall['measured']}/{overall['defined']} measured, "
        f"{overall['withheld']} withheld, {overall['binding_errors']} binding errors; "
        f"bands {overall['bands']}; checks {report['summary']['checks']}"
    )
    return 1 if overall["binding_errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
