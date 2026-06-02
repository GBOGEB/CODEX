"""Runtime registry generation for federation runtime evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

FEDERATION_MEMBERS: tuple[str, ...] = ("ABACUS", "ARTSTYLE", "QPLANT", "CODEX")

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
REQUIRED_FIELDS: tuple[str, ...] = (
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
DEFAULT_RUNTIME_DIR = Path("federation") / "runtime_registry"
DEFAULT_REGISTRY_OUTPUT = Path("metrics") / "federation" / "runtime_registry.json"
DEFAULT_REPORT_OUTPUT = Path("reports") / "runtime_registry_report.json"
DEFAULT_ROLLUP_PATH = Path("metrics") / "federation" / "federation_rollup.json"
DEFAULT_SCREE_PATH = Path("metrics") / "federation" / "federation_scree.json"


class RuntimeRegistryError(Exception):
    """Raised when runtime registry generation fails."""


class RuntimeRegistry:
    """Build runtime evidence outputs from federation registry artifacts."""

class RuntimeRegistryError(Exception):
    """Raised when runtime registry generation fails."""


class RuntimeRegistry:
    """Build runtime evidence registry and report artifacts."""

    def __init__(self, members: tuple[str, ...] = FEDERATION_MEMBERS) -> None:
        self.members = members

    def _canonical_members(
        self,
        members: tuple[str, ...] | None = None,
        *,
        caller: str,
    ) -> tuple[str, ...]:
        candidate_members = members or self.members
        if set(candidate_members) != set(FEDERATION_MEMBERS) or len(candidate_members) != len(FEDERATION_MEMBERS):
            raise RuntimeRegistryError(
                f"{caller} requires exactly the canonical federation members "
                f"{sorted(FEDERATION_MEMBERS)} (in any order), got {sorted(candidate_members)}"
            )
        return FEDERATION_MEMBERS

    def _member_from_repo(self, repo: str, members: tuple[str, ...] | None = None) -> str:
        ordered_members = members or self.members
        repo_name = repo.split("/")[-1].upper()
        if repo_name not in ordered_members:
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

    def load_runtime_entries(
        self,
        runtime_dir: Path,
        members: tuple[str, ...] | None = None,
    ) -> dict[str, dict[str, Any]]:
        ordered_members = members or self.members
        entries: dict[str, dict[str, Any]] = {}
        for member in ordered_members:
            filename = DEFAULT_RUNTIME_FILENAMES.get(member)
            if filename is None:
                raise RuntimeRegistryError(f"No runtime evidence filename configured for member: {member}")
            path = runtime_dir / filename
            if not path.exists():
                raise RuntimeRegistryError(f"Runtime evidence file missing for {member}: {path}")
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise RuntimeRegistryError(
                    f"Invalid runtime evidence JSON for {member}: {path}: {exc.msg}"
                ) from exc
            if not isinstance(data, dict):
                raise RuntimeRegistryError(
                    f"Invalid runtime evidence payload for {member}: {path}: expected JSON object"
                )
            self._validate_entry(data, str(path))
            inferred = self._member_from_repo(str(data["repo"]), members=ordered_members)
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
        subwave: str = "W007.2A",
        members: tuple[str, ...] | None = None,
    ) -> dict[str, Any]:
        ordered_members = members or self.members
        ordered_entries = [entries[member] for member in ordered_members]
        return {
            "wave": wave,
            "subwave": subwave,
            "members": list(ordered_members),
            "runtime_registry": ordered_entries,
        }

    def _runtime_status(
        self,
        entries: dict[str, dict[str, Any]],
        members: tuple[str, ...] | None = None,
    ) -> dict[str, Any]:
        ordered_members = members or self.members
        total = float(len(ordered_members))
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
            for member in ordered_members
        }
        return {
            "members": member_status,
            "coverage": {
                "runtime_exists": round(sum(1 for m in ordered_members if bool(entries[m]["runtime_exists"])) / total, 6),
                "runtime_validated": round(
                    sum(1 for m in ordered_members if bool(entries[m]["runtime_validated"])) / total,
                    6,
                ),
                "deployment_exists": round(
                    sum(1 for m in ordered_members if bool(entries[m]["deployment_exists"])) / total,
                    6,
                ),
                "truth_score_average": round(sum(float(entries[m]["truth_score"]) for m in ordered_members) / total, 6),
            },
        }

    def build_truth_matrix(
        self,
        entries: dict[str, dict[str, Any]],
        members: tuple[str, ...] | None = None,
    ) -> dict[str, Any]:
        ordered_members = members or self.members
        matrix: list[dict[str, Any]] = []
        for member in ordered_members:
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

    def _load_repo_metrics(
        self,
        metrics_dir: Path,
        members: tuple[str, ...] | None = None,
    ) -> dict[str, dict[str, Any]]:
        ordered_members = members or self.members
        loaded: dict[str, dict[str, Any]] = {}
        for member in ordered_members:
            path = metrics_dir / f"{member.lower()}_metrics.json"
            if not path.exists():
                raise RuntimeRegistryError(f"Repository metrics file missing for {member}: {path}")
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise RuntimeRegistryError(
                    f"Invalid repository metrics JSON for {member}: {path}: {exc.msg}"
                ) from exc
            if not isinstance(payload, dict):
                raise RuntimeRegistryError(
                    f"Invalid repository metrics payload for {member}: {path}: expected JSON object"
                )
            loaded[member] = payload
        return loaded

    def build_runtime_report(
        self,
        entries: dict[str, dict[str, Any]],
        repo_metrics: dict[str, dict[str, Any]],
        wave: str = "W007",
        subwave: str = "W007.2A",
        members: tuple[str, ...] | None = None,
    ) -> dict[str, Any]:
        from .federation_rollup import FederationRollup
        from .federation_scree import FederationScree

        ordered_members = self._canonical_members(members, caller="build_runtime_report()")
        runtime_status = self._runtime_status(entries, members=ordered_members)
        rollup = FederationRollup().build_rollup_record(repo_metrics, wave=wave, subwave=subwave)
        scree = FederationScree().build_scree_record(repo_metrics, wave=wave, subwave=subwave)
        rollup["runtime_status"] = runtime_status
        scree["runtime_status"] = runtime_status
        return {
            "wave": wave,
            "subwave": subwave,
            "federation_rollup": rollup,
            "federation_scree": scree,
            "truth_matrix": self.build_truth_matrix(entries, members=ordered_members),
        }

    def write_outputs(
        self,
        runtime_dir: Path,
        metrics_dir: Path,
        registry_output: Path | None = None,
        report_output: Path | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        canonical_members = self._canonical_members(caller="write_outputs()")
        entries = self.load_runtime_entries(runtime_dir, members=canonical_members)
        repo_metrics = self._load_repo_metrics(metrics_dir, members=canonical_members)
        registry_record = self.build_registry_record(entries, members=canonical_members)
        report_record = self.build_runtime_report(entries, repo_metrics, members=canonical_members)
        registry_output = registry_output or (runtime_dir / "runtime_registry.json")
        report_output = report_output or (runtime_dir / "runtime_registry_report.json")
        registry_output.parent.mkdir(parents=True, exist_ok=True)
        report_output.parent.mkdir(parents=True, exist_ok=True)
        registry_output.write_text(json.dumps(registry_record, indent=2, sort_keys=True), encoding="utf-8")
        report_output.write_text(json.dumps(report_record, indent=2, sort_keys=True), encoding="utf-8")
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


def default_runtime_registry_dir() -> Path:
    """Return the repository default runtime registry directory."""
    return Path(__file__).resolve().parents[2] / "federation" / "runtime_registry"

    def _validate_weights(self) -> None:
        total = sum(self.weights.values())
        if abs(total - 1.0) > 1e-6:
            raise RuntimeRegistryError(f"Weights must sum to 1.0, got {total:.6f}")
        for member in MEMBERS:
            if member not in self.weights:
                raise RuntimeRegistryError(f"Missing weight for member: {member}")

def load_runtime_registry(runtime_registry_dir: Path | None = None) -> dict[str, dict[str, Any]]:
    """Load runtime registry evidence records from JSON files."""
    registry_dir = runtime_registry_dir or default_runtime_registry_dir()
    records: dict[str, dict[str, Any]] = {}
    for member, filename in DEFAULT_RUNTIME_FILENAMES.items():
        path = registry_dir / filename
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"Runtime registry file must contain a JSON object: {path}")
        missing = REQUIRED_RUNTIME_FIELDS - set(data.keys())
        if missing:
            raise RuntimeRegistryError(f"Missing runtime fields for {record.get('repo', 'unknown')}: {missing}")
        repo = record["repo"]
        if not isinstance(repo, str) or not repo:
            raise RuntimeRegistryError(
                f"Field repo must be a non-empty string, got {repo!r}"
            )
        for field in ("runtime_exists", "runtime_validated", "deployment_exists"):
            if not isinstance(record[field], bool):
                raise RuntimeRegistryError(f"Field {field} must be boolean for {record['repo']}")
        for field in ("last_execution", "last_validation", "last_deployment"):
            value = record[field]
            if value is not None and not isinstance(value, str):
                raise RuntimeRegistryError(
                    f"Field {field} must be a string or None for {record['repo']}, got {value!r}"
                )
        for field in ("truth_score", "forward_pca", "backward_pca", "geti", "pci"):
            try:
                float(record[field])
            except (TypeError, ValueError) as exc:
                raise RuntimeRegistryError(f"Field {field} must be numeric for {record['repo']}") from exc

    def load_runtime_records(
        self,
        runtime_dir: Path = DEFAULT_RUNTIME_DIR,
    ) -> dict[str, dict[str, Any]]:
        records: dict[str, dict[str, Any]] = {}
        for member, filename in RUNTIME_FILENAMES.items():
            record = self._load_json(runtime_dir / filename)
            self.validate_record(record)
            inferred_member = self._member_key(str(record["repo"]))
            if inferred_member != member:
                raise RuntimeRegistryError(
                    f"Runtime artifact {filename} repo mismatch: expected {member}, got {record['repo']}"
                )
            records[member] = record
        return records

    def build_truth_matrix(
        self,
        runtime_records: dict[str, dict[str, Any]],
    ) -> list[dict[str, Any]]:
        truth_matrix: list[dict[str, Any]] = []
        for member in MEMBERS:
            if member not in runtime_records:
                raise RuntimeRegistryError(f"Missing runtime record for member: {member}")
            record = runtime_records[member]
            # Validate per-member record to ensure consistent error contract
            self.validate_record(record)
            truth_matrix.append(
                {
                    "member": member,
                    "repo": record["repo"],
                    "runtime_exists": bool(record["runtime_exists"]),
                    "executed": bool(record["last_execution"]),
                    "runtime_validated": bool(record["runtime_validated"]),
                    "deployment_exists": bool(record["deployment_exists"]),
                    "truth_score": round(float(record["truth_score"]), 6),
                }
            )
        return truth_matrix

    def build_registry_record(
        self,
        runtime_records: dict[str, dict[str, Any]],
        rollup: dict[str, Any] | None = None,
        scree: dict[str, Any] | None = None,
        wave: str = "W007",
        subwave: str = "W007.2",
    ) -> dict[str, Any]:
        truth_matrix = self.build_truth_matrix(runtime_records)
        runtime_exists_count = sum(int(entry["runtime_exists"]) for entry in truth_matrix)
        execution_count = sum(int(entry["executed"]) for entry in truth_matrix)
        runtime_validated_count = sum(int(entry["runtime_validated"]) for entry in truth_matrix)
        deployment_exists_count = sum(int(entry["deployment_exists"]) for entry in truth_matrix)
        weighted_truth_score = round(
            sum(self.weights[member] * float(runtime_records[member]["truth_score"]) for member in MEMBERS),
            6,
        )
        return {
            "wave": wave,
            "subwave": subwave,
            "members": list(MEMBERS),
            "weights": self.weights,
            "summary": {
                "runtime_exists_count": runtime_exists_count,
                "execution_count": execution_count,
                "runtime_validated_count": runtime_validated_count,
                "deployment_exists_count": deployment_exists_count,
                "weighted_truth_score": weighted_truth_score,
            },
            "truth_matrix": truth_matrix,
            "per_repository": {member: runtime_records[member] for member in MEMBERS},
            "integrations": {
                "federation_rollup": (rollup or {}).get("aggregated", {}),
                "federation_scree": (scree or {}).get("federation_scree", {}),
            },
        }

    @staticmethod
    def build_report(registry_record: dict[str, Any]) -> dict[str, Any]:
        truth_matrix = registry_record["truth_matrix"]
        return {
            "wave": registry_record["wave"],
            "subwave": registry_record["subwave"],
            "repo_count": len(truth_matrix),
            "runtime_exists_count": registry_record["summary"]["runtime_exists_count"],
            "execution_count": registry_record["summary"]["execution_count"],
            "runtime_validated_count": registry_record["summary"]["runtime_validated_count"],
            "deployment_exists_count": registry_record["summary"]["deployment_exists_count"],
            "weighted_truth_score": registry_record["summary"]["weighted_truth_score"],
            "repos_missing_execution": [
                entry["member"] for entry in truth_matrix if not entry["executed"]
            ],
            "repos_missing_validation": [
                entry["member"] for entry in truth_matrix if not entry["runtime_validated"]
            ],
            "repos_missing_deployment": [
                entry["member"] for entry in truth_matrix if not entry["deployment_exists"]
            ],
        }

    def write_registry(
        self,
        runtime_records: dict[str, dict[str, Any]],
        output_path: Path,
        rollup: dict[str, Any] | None = None,
        scree: dict[str, Any] | None = None,
        wave: str = "W007",
        subwave: str = "W007.2",
    ) -> dict[str, Any]:
        record = self.build_registry_record(
            runtime_records,
            rollup=rollup,
            scree=scree,
            wave=wave,
            subwave=subwave,
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(record, indent=2), encoding="utf-8")
        return record

    def write_report(
        self,
        registry_record: dict[str, Any],
        output_path: Path,
    ) -> dict[str, Any]:
        report = self.build_report(registry_record)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        return report

    def generate(
        self,
        runtime_dir: Path = DEFAULT_RUNTIME_DIR,
        registry_output_path: Path = DEFAULT_REGISTRY_OUTPUT,
        report_output_path: Path = DEFAULT_REPORT_OUTPUT,
        rollup_path: Path = DEFAULT_ROLLUP_PATH,
        scree_path: Path = DEFAULT_SCREE_PATH,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        runtime_records = self.load_runtime_records(runtime_dir)
        rollup = self._load_json(rollup_path)
        scree = self._load_json(scree_path)
        registry_record = self.write_registry(
            runtime_records,
            registry_output_path,
            rollup=rollup,
            scree=scree,
        )
        report = self.write_report(registry_record, report_output_path)
        return registry_record, report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build federation runtime registry outputs.")
    parser.add_argument("--runtime-dir", type=Path, default=DEFAULT_RUNTIME_DIR)
    parser.add_argument("--registry-output", type=Path, default=DEFAULT_REGISTRY_OUTPUT)
    parser.add_argument("--report-output", type=Path, default=DEFAULT_REPORT_OUTPUT)
    parser.add_argument("--rollup-path", type=Path, default=DEFAULT_ROLLUP_PATH)
    parser.add_argument("--scree-path", type=Path, default=DEFAULT_SCREE_PATH)
    args = parser.parse_args(argv)

    registry = RuntimeRegistry()
    registry_record, report = registry.generate(
        runtime_dir=args.runtime_dir,
        registry_output_path=args.registry_output,
        report_output_path=args.report_output,
        rollup_path=args.rollup_path,
        scree_path=args.scree_path,
    )
    print(
        json.dumps(
            {
                "status": "generated",
                "registry_output": str(args.registry_output),
                "report_output": str(args.report_output),
                "repo_count": len(registry_record["truth_matrix"]),
                "weighted_truth_score": report["weighted_truth_score"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
