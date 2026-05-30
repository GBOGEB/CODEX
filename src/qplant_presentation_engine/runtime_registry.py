"""Federation runtime evidence registry and truth-state reporting."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .federation_rollup import DEFAULT_WEIGHTS, MEMBERS

RUNTIME_FILENAMES: dict[str, str] = {
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

    def __init__(self, weights: dict[str, float] | None = None) -> None:
        self.weights: dict[str, float] = dict(weights) if weights is not None else dict(DEFAULT_WEIGHTS)
        self._validate_weights()

    def _validate_weights(self) -> None:
        total = sum(self.weights.values())
        if abs(total - 1.0) > 1e-6:
            raise RuntimeRegistryError(f"Weights must sum to 1.0, got {total:.6f}")
        for member in MEMBERS:
            if member not in self.weights:
                raise RuntimeRegistryError(f"Missing weight for member: {member}")

    @staticmethod
    def _member_key(repo: str) -> str:
        candidate = repo.split("/")[-1].upper()
        if candidate not in MEMBERS:
            raise RuntimeRegistryError(f"Unsupported runtime repo: {repo}")
        return candidate

    @staticmethod
    def _load_json(path: Path) -> dict[str, Any]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise RuntimeRegistryError(f"Missing runtime artifact: {path}") from exc
        except json.JSONDecodeError as exc:
            raise RuntimeRegistryError(f"Invalid JSON in {path}") from exc
        if not isinstance(data, dict):
            raise RuntimeRegistryError(f"Runtime artifact must be an object: {path}")
        return data

    def validate_record(self, record: dict[str, Any]) -> None:
        missing = [field for field in REQUIRED_FIELDS if field not in record]
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
