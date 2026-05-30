"""Runtime registry generation for federation runtime evidence."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .federation_rollup import FederationRollup, MEMBERS as FEDERATION_MEMBERS
from .federation_scree import FederationScree

RUNTIME_FIELDS: tuple[str, ...] = (
    "repo",
    "runtime_exists",
    "runtime_validated",
    "deployment_exists",
    "last_execution",
    "last_validation",
    "last_deployment",
    "truth_score",
    "forward_pca",
    "backward_pca",
    "geti",
    "pci",
)
DEFAULT_RUNTIME_FILENAMES: dict[str, str] = {
    "ABACUS": "abacus_runtime.json",
    "ARTSTYLE": "artstyle_runtime.json",
    "QPLANT": "qplant_runtime.json",
    "CODEX": "codex_runtime.json",
}


class RuntimeRegistryError(Exception):
    """Raised when runtime registry generation fails."""


class RuntimeRegistry:
    """Build runtime evidence registry and report artifacts."""

    def __init__(self, members: tuple[str, ...] = FEDERATION_MEMBERS) -> None:
        self.members = members

    def _member_from_repo(self, repo: str) -> str:
        repo_name = repo.split("/")[-1].upper()
        if repo_name not in self.members:
            raise RuntimeRegistryError(f"Unknown repository member in runtime entry: {repo}")
        return repo_name

    def _validate_entry(self, entry: dict[str, Any], source: str) -> None:
        missing = [field for field in RUNTIME_FIELDS if field not in entry]
        if missing:
            raise RuntimeRegistryError(f"Missing runtime fields in {source}: {', '.join(missing)}")
        if not isinstance(entry["repo"], str) or not entry["repo"].strip():
            raise RuntimeRegistryError(f"Invalid runtime field 'repo' in {source}: expected non-empty string")
        for field in ("runtime_exists", "runtime_validated", "deployment_exists"):
            if not isinstance(entry[field], bool):
                raise RuntimeRegistryError(f"Invalid runtime field '{field}' in {source}: expected boolean")
        for field in ("last_execution", "last_validation", "last_deployment"):
            value = entry[field]
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise RuntimeRegistryError(
                    f"Invalid runtime field '{field}' in {source}: expected non-empty string or null"
                )
        for field in ("truth_score", "geti", "pci"):
            if isinstance(entry[field], bool) or not isinstance(entry[field], (int, float)):
                raise RuntimeRegistryError(f"Invalid runtime field '{field}' in {source}: expected number")
            if not 0.0 <= float(entry[field]) <= 1.0:
                raise RuntimeRegistryError(
                    f"Invalid runtime field '{field}' in {source}: expected value in [0.0, 1.0]"
                )
        self._validate_pca_block(entry, "forward_pca", "convergence_score", source)
        self._validate_pca_block(entry, "backward_pca", "regression_score", source)

    def _validate_pca_block(
        self,
        entry: dict[str, Any],
        field_name: str,
        score_key: str,
        source: str,
    ) -> None:
        pca = entry.get(field_name)
        if not isinstance(pca, dict):
            raise RuntimeRegistryError(f"Invalid runtime field '{field_name}' in {source}: expected object")
        variance = pca.get("variance_explained")
        if (
            not isinstance(variance, list)
            or len(variance) != 5
            or not all(not isinstance(v, bool) and isinstance(v, (int, float)) for v in variance)
        ):
            raise RuntimeRegistryError(
                f"Invalid runtime field '{field_name}.variance_explained' in {source}: expected 5 numeric values"
            )
        # Validate variance ranges [0.0, 1.0]
        for i, v in enumerate(variance):
            if not 0.0 <= float(v) <= 1.0:
                raise RuntimeRegistryError(
                    f"Invalid runtime field '{field_name}.variance_explained[{i}]' in {source}: "
                    f"expected value in [0.0, 1.0], got {v}"
                )
        score = pca.get(score_key)
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise RuntimeRegistryError(
                f"Invalid runtime field '{field_name}.{score_key}' in {source}: expected number"
            )
        # Validate score range [0.0, 1.0]
        if not 0.0 <= float(score) <= 1.0:
            raise RuntimeRegistryError(
                f"Invalid runtime field '{field_name}.{score_key}' in {source}: "
                f"expected value in [0.0, 1.0], got {score}"
            )

    def load_runtime_entries(self, runtime_dir: Path) -> dict[str, dict[str, Any]]:
        entries: dict[str, dict[str, Any]] = {}
        for member in self.members:
            filename = DEFAULT_RUNTIME_FILENAMES.get(member)
            if filename is None:
                raise RuntimeRegistryError(f"No runtime evidence filename configured for member: {member}")
            path = runtime_dir / filename
            if not path.exists():
                raise RuntimeRegistryError(f"Runtime evidence file missing for {member}: {path}")
            data = json.loads(path.read_text(encoding="utf-8"))
            self._validate_entry(data, str(path))
            inferred = self._member_from_repo(str(data["repo"]))
            if inferred != member:
                raise RuntimeRegistryError(
                    f"Runtime evidence member mismatch for {path.name}: expected {member}, got {inferred}"
                )
            entries[member] = data
        return entries

    def build_registry_record(
        self,
        entries: dict[str, dict[str, Any]],
        wave: str = "W007",
        subwave: str = "W007.2",
    ) -> dict[str, Any]:
        ordered_entries = [entries[member] for member in self.members]
        return {
            "wave": wave,
            "subwave": subwave,
            "members": list(self.members),
            "runtime_registry": ordered_entries,
        }

    def _runtime_status(self, entries: dict[str, dict[str, Any]]) -> dict[str, Any]:
        total = float(len(self.members))
        if total == 0.0:
            return {
                "members": {},
                "coverage": {
                    "runtime_exists": 0.0,
                    "runtime_validated": 0.0,
                    "deployment_exists": 0.0,
                    "truth_score_average": 0.0,
                },
            }
        member_status = {
            member: {
                "runtime_exists": bool(entries[member]["runtime_exists"]),
                "runtime_validated": bool(entries[member]["runtime_validated"]),
                "deployment_exists": bool(entries[member]["deployment_exists"]),
                "truth_score": float(entries[member]["truth_score"]),
            }
            for member in self.members
        }
        return {
            "members": member_status,
            "coverage": {
                "runtime_exists": round(sum(1 for m in self.members if bool(entries[m]["runtime_exists"])) / total, 6),
                "runtime_validated": round(sum(1 for m in self.members if bool(entries[m]["runtime_validated"])) / total, 6),
                "deployment_exists": round(sum(1 for m in self.members if bool(entries[m]["deployment_exists"])) / total, 6),
                "truth_score_average": round(sum(float(entries[m]["truth_score"]) for m in self.members) / total, 6),
            },
        }

    def build_truth_matrix(self, entries: dict[str, dict[str, Any]]) -> dict[str, Any]:
        matrix: list[dict[str, Any]] = []
        for member in self.members:
            entry = entries[member]
            runtime_exists = bool(entry["runtime_exists"])
            runtime_validated = bool(entry["runtime_validated"])
            deployment_exists = bool(entry["deployment_exists"])
            if runtime_exists and runtime_validated and deployment_exists:
                state = "VALIDATED_DEPLOYED"
            elif runtime_exists and runtime_validated:
                state = "EXECUTED_VALIDATED"
            elif runtime_exists:
                state = "EXECUTED_ONLY"
            else:
                state = "REPO_ONLY"
            matrix.append(
                {
                    "member": member,
                    "repo": entry["repo"],
                    "runtime_exists": runtime_exists,
                    "runtime_validated": runtime_validated,
                    "deployment_exists": deployment_exists,
                    "truth_score": float(entry["truth_score"]),
                    "truth_state": state,
                }
            )
        return {
            "legend": ["REPO_ONLY", "EXECUTED_ONLY", "EXECUTED_VALIDATED", "VALIDATED_DEPLOYED"],
            "rows": matrix,
        }

    def _load_repo_metrics(self, metrics_dir: Path) -> dict[str, dict[str, Any]]:
        loaded: dict[str, dict[str, Any]] = {}
        for member in self.members:
            path = metrics_dir / f"{member.lower()}_metrics.json"
            if not path.exists():
                raise RuntimeRegistryError(f"Repository metrics file missing for {member}: {path}")
            loaded[member] = json.loads(path.read_text(encoding="utf-8"))
        return loaded

    def build_runtime_report(
        self,
        entries: dict[str, dict[str, Any]],
        repo_metrics: dict[str, dict[str, Any]],
        wave: str = "W007",
        subwave: str = "W007.2",
    ) -> dict[str, Any]:
        runtime_status = self._runtime_status(entries)
        rollup = FederationRollup().build_rollup_record(repo_metrics, wave=wave, subwave=subwave)
        scree = FederationScree().build_scree_record(repo_metrics, wave=wave, subwave=subwave)
        rollup["runtime_status"] = runtime_status
        scree["runtime_status"] = runtime_status
        return {
            "wave": wave,
            "subwave": subwave,
            "federation_rollup": rollup,
            "federation_scree": scree,
            "truth_matrix": self.build_truth_matrix(entries),
        }

    def write_outputs(
        self,
        runtime_dir: Path,
        metrics_dir: Path,
        registry_output: Path | None = None,
        report_output: Path | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        if sorted(self.members) != sorted(FEDERATION_MEMBERS):
            raise RuntimeRegistryError(
                f"write_outputs() requires exactly the canonical federation members "
                f"{sorted(FEDERATION_MEMBERS)} (in any order), got {sorted(self.members)}"
            )
        entries = self.load_runtime_entries(runtime_dir)
        repo_metrics = self._load_repo_metrics(metrics_dir)
        registry_record = self.build_registry_record(entries)
        report_record = self.build_runtime_report(entries, repo_metrics)
        registry_output = registry_output or (runtime_dir / "runtime_registry.json")
        report_output = report_output or (runtime_dir / "runtime_registry_report.json")
        registry_output.parent.mkdir(parents=True, exist_ok=True)
        report_output.parent.mkdir(parents=True, exist_ok=True)
        registry_output.write_text(json.dumps(registry_record, indent=2), encoding="utf-8")
        report_output.write_text(json.dumps(report_record, indent=2), encoding="utf-8")
        return registry_record, report_record


def generate_runtime_registry(
    runtime_dir: Path | None = None,
    metrics_dir: Path | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Generate runtime registry and runtime registry report artifacts."""
    root = Path(__file__).resolve().parents[2]
    resolved_runtime_dir = runtime_dir or (root / "federation" / "runtime_registry")
    resolved_metrics_dir = metrics_dir or (root / "metrics" / "repo")
    return RuntimeRegistry().write_outputs(
        runtime_dir=resolved_runtime_dir,
        metrics_dir=resolved_metrics_dir,
    )
