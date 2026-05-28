"""
ABACUS <-> CODEX bridge adapter contracts.

CODEX remains the lightweight platform layer. ABACUS remains the engineering
orchestration runtime. This module defines the boundary in code so downstream
work can depend on an explicit contract instead of duplicated implementations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional, Sequence, Tuple

import yaml


GREEK_TRACE_SEQUENCE: Tuple[str, ...] = (
    "alpha", "beta", "gamma", "delta", "epsilon", "zeta",
    "eta", "theta", "iota", "kappa", "lambda",
)

BRIDGE_COMPONENT_PATHS: dict[str, Tuple[str, ...]] = {
    "codex": (
        "README.md",
        "src/github_interface.py",
        "docs/index.html",
        "telemetry/pca/drift_monitor.py",
    ),
    "abacus": (
        "abacus_runtime/README.md",
        "abacus_runtime/runtime_manifest.yaml",
        "docs/ALPHA_BRIDGE_ABACUS_CODEX.md",
    ),
    "mcp-bridge": (
        "src/bridge_adapter.py",
        "governance/contracts/delta-1-runtime-federation-contract.yaml",
        "governance/synchronization/abacus-codex-recursive-sync.yaml",
        ".github/workflows/full-stack-governance.yml",
    ),
    "keb": (
        "KEB/governance/GLOSSARY.yml",
        "KEB/governance/governance_rules.yml",
        "KEB/governance/metrics.yml",
        "src/keb/keb_client.py",
    ),
}

RUNTIME_MODULE_ALIGNMENT: dict[str, Tuple[str, ...]] = {
    "renderer": (
        "dashboards/telemetry_dashboard.py",
        "docs/dashboard.html",
    ),
    "topology": (
        "src/bridge_adapter.py",
        "docs/ALPHA_BRIDGE_ABACUS_CODEX.md",
    ),
    "validation": (
        "scripts/check_manifest.py",
        "scripts/check_bridge_health.py",
    ),
    "deployment": (
        "scripts/export_abacus_runtime.py",
        ".github/workflows/pages.yml",
    ),
    "telemetry": (
        "telemetry/pca/drift_monitor.py",
        "dashboards/telemetry_dashboard.py",
    ),
}


@dataclass(frozen=True)
class BridgeTraceStep:
    """A managed bridge step using Greek trace naming."""

    key: str
    title: str
    purpose: str
    status: str = "planned"

    def as_markdown_row(self) -> str:
        return f"| {self.key} | {self.title} | {self.purpose} | {self.status} |"


@dataclass(frozen=True)
class RepoRole:
    """Repository role in the CODEX/ABACUS bridge boundary."""

    repository: str
    primary_role: str
    owns: Tuple[str, ...]
    consumes: Tuple[str, ...] = ()

    def ownership_lines(self) -> List[str]:
        lines = [f"- {self.repository}: {self.primary_role}"]
        lines.extend(f"  - owns: {item}" for item in self.owns)
        lines.extend(f"  - consumes: {item}" for item in self.consumes)
        return lines


@dataclass(frozen=True)
class BridgeAdapterContract:
    """Reusable contract for bridge/adaptor integration work."""

    name: str
    source_repo: str
    target_repo: str
    boundary: str
    shared_resources: Tuple[str, ...]
    pruning_targets: Tuple[str, ...]
    validation_gates: Tuple[str, ...]
    trace_steps: Tuple[BridgeTraceStep, ...] = field(default_factory=tuple)

    def validate(self) -> List[str]:
        issues: List[str] = []
        for field_name in ("name", "source_repo", "target_repo", "boundary"):
            if not getattr(self, field_name).strip():
                issues.append(f"{field_name} is required")
        if self.source_repo == self.target_repo:
            issues.append("source_repo and target_repo must be different")
        if not self.shared_resources:
            issues.append("at least one shared resource must be identified")
        if not self.validation_gates:
            issues.append("at least one validation gate must be identified")
        seen = set()
        for step in self.trace_steps:
            if step.key in seen:
                issues.append(f"duplicate trace step: {step.key}")
            seen.add(step.key)
        return issues

    def render_markdown(self) -> str:
        state = "valid" if not self.validate() else "needs-review"
        lines = [
            f"# {self.name}",
            "",
            f"**Status:** {state}",
            f"**Source repo:** `{self.source_repo}`",
            f"**Target repo:** `{self.target_repo}`",
            "",
            "## Boundary",
            self.boundary,
            "",
            "## Shared Resources",
        ]
        lines.extend(f"- {item}" for item in self.shared_resources)
        lines.extend(["", "## Pruning Targets"])
        lines.extend(f"- {item}" for item in self.pruning_targets)
        lines.extend(["", "## Validation Gates"])
        lines.extend(f"- {item}" for item in self.validation_gates)
        if self.trace_steps:
            lines.extend(["", "## Managed Trace", "| Step | Title | Purpose | Status |", "|---|---|---|---|"])
            lines.extend(step.as_markdown_row() for step in self.trace_steps)
        return "\n".join(lines).strip() + "\n"


def default_trace_steps() -> Tuple[BridgeTraceStep, ...]:
    titles = {
        "alpha": "review baseline",
        "beta": "adapter implementation",
        "gamma": "shared resources",
        "delta": "pruning",
        "epsilon": "contract boundary",
        "zeta": "functional blocks",
        "eta": "ranking and validation",
        "theta": "CI/CD roundtrip",
        "iota": "next actions",
        "kappa": "ASCII structure",
        "lambda": "release conclusion",
    }
    return tuple(
        BridgeTraceStep(
            key=key,
            title=titles[key],
            purpose=f"Managed {titles[key]} step without repo-number coupling.",
            status="in-review" if key in {"alpha", "beta"} else "planned",
        )
        for key in GREEK_TRACE_SEQUENCE
    )


def create_abacus_codex_contract() -> BridgeAdapterContract:
    return BridgeAdapterContract(
        name="ABACUS <-> CODEX Bridge Adapter Contract",
        source_repo="GBOGEB/ABACUS",
        target_repo="GBOGEB/CODEX",
        boundary=(
            "CODEX owns reusable platform transport, enterprise adaptation, interface wiring, "
            "and lightweight launcher conventions. ABACUS consumes CODEX for platform integration "
            "while retaining DMAIC, DOW, KEB, GBOGEB, recursive agents, and engineering orchestration."
        ),
        shared_resources=("github_transport", "traceability_core", "dashboard_export", "ci_roundtrip_contracts"),
        pruning_targets=(
            "duplicated platform API handling in orchestration repos",
            "stale launcher and dashboard variants",
            "duplicated handover and DMAIC narrative fragments",
            "unclear ownership between transport and orchestration code",
        ),
        validation_gates=(
            "contract.validate() returns no issues",
            "CODEX interface tests pass",
            "ABACUS adapter consumes CODEX without copying platform logic",
            "CI/CD roundtrip produces reviewable trace output",
        ),
        trace_steps=default_trace_steps(),
    )


def bridge_alignment_matrix() -> dict[str, Tuple[str, ...]]:
    """Expose the stable module-to-path mapping used by bridge validation."""
    return RUNTIME_MODULE_ALIGNMENT


def _load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected YAML object in {path}")
    return payload


def build_bridge_report(component: str = "codex", repo_root: Path | None = None) -> dict[str, Any]:
    if component not in BRIDGE_COMPONENT_PATHS:
        available = ", ".join(sorted(BRIDGE_COMPONENT_PATHS))
        raise ValueError(f"Unknown component '{component}'. Choose from: {available}")

    root = (repo_root or Path(__file__).resolve().parents[1]).resolve()
    contract = create_abacus_codex_contract()
    runtime_manifest = _load_yaml(root / "abacus_runtime" / "runtime_manifest.yaml")
    sync_manifest = _load_yaml(
        root / "governance" / "synchronization" / "abacus-codex-recursive-sync.yaml"
    )
    federation_contract = _load_yaml(
        root / "governance" / "contracts" / "delta-1-runtime-federation-contract.yaml"
    )

    issues = contract.validate()
    component_paths = list(BRIDGE_COMPONENT_PATHS[component])
    missing_paths = [path for path in component_paths if not (root / path).exists()]
    if missing_paths:
        issues.append(f"{component} is missing required bridge paths: {', '.join(missing_paths)}")

    runtime = runtime_manifest.get("runtime", {})
    if not isinstance(runtime, dict):
        issues.append("abacus_runtime/runtime_manifest.yaml is missing a runtime mapping")
        runtime = {}

    runtime_modules = runtime.get("modules", runtime_manifest.get("modules", []))
    if not isinstance(runtime_modules, list):
        issues.append("abacus_runtime/runtime_manifest.yaml modules must be a list")
        runtime_modules = []

    module_alignment = {
        module: [path for path in RUNTIME_MODULE_ALIGNMENT.get(module, ()) if (root / path).exists()]
        for module in runtime_modules
    }
    missing_module_alignment = [
        module for module, paths in module_alignment.items() if not paths
    ]
    if missing_module_alignment:
        issues.append(
            "Runtime modules missing CODEX bridge coverage: "
            + ", ".join(sorted(missing_module_alignment))
        )

    missing_module_templates = [
        module for module in runtime_modules if module not in RUNTIME_MODULE_ALIGNMENT
    ]
    if missing_module_templates:
        issues.append(
            "Runtime modules missing bridge alignment templates: "
            + ", ".join(sorted(missing_module_templates))
        )

    sync_root = sync_manifest.get("abacus_codex_recursive_sync", {})
    if not isinstance(sync_root, dict):
        issues.append("governance synchronization manifest is missing abacus_codex_recursive_sync")
        sync_root = {}

    sync_domains = sync_root.get("synchronization_domains", [])
    if not isinstance(sync_domains, list) or not sync_domains:
        issues.append("synchronization_domains must list at least one bridge domain")
        sync_domains = []

    federation_root = federation_contract.get("delta_1_runtime_federation_contract", {})
    if not isinstance(federation_root, dict):
        issues.append("federation contract is missing delta_1_runtime_federation_contract")
        federation_root = {}
    repositories = federation_root.get("repositories", {})
    if not isinstance(repositories, dict):
        repositories = {}

    report = {
        "status": "pass" if not issues else "fail",
        "component": component,
        "boundary": contract.boundary,
        "shared_resources": list(contract.shared_resources),
        "component_paths": component_paths,
        "runtime": {
            "name": runtime.get("name"),
            "version": runtime.get("version"),
            "modules": runtime_modules,
        },
        "alignment": module_alignment,
        "synchronization_domains": sync_domains,
        "primary_execution_plane": repositories.get("primary_execution_plane"),
        "primary_governance_plane": repositories.get("primary_governance_plane"),
        "issues": issues,
    }
    return report


def render_repo_ascii(roles: Optional[Sequence[RepoRole]] = None) -> str:
    roles = roles or (
        RepoRole("CODEX", "platform substrate", ("GitHub interface", "Enterprise adapter", "transport", "launcher conventions")),
        RepoRole("ABACUS", "engineering orchestration runtime", ("DMAIC runtime", "12-cluster orchestrator", "DOW/KEB/GBOGEB", "CI/CD dashboards"), ("CODEX platform boundary",)),
    )
    lines = [
        "+----------------------------+",
        "| CODEX                      |",
        "| Platform / transport       |",
        "+-------------+--------------+",
        "              |",
        "              v",
        "+----------------------------+",
        "| ABACUS                     |",
        "| DMAIC / orchestration      |",
        "+----------------------------+",
        "",
        "Repository roles:",
    ]
    for role in roles:
        lines.extend(role.ownership_lines())
    return "\n".join(lines) + "\n"


__all__ = [
    "BridgeAdapterContract",
    "BridgeTraceStep",
    "BRIDGE_COMPONENT_PATHS",
    "RepoRole",
    "RUNTIME_MODULE_ALIGNMENT",
    "bridge_alignment_matrix",
    "build_bridge_report",
    "create_abacus_codex_contract",
    "default_trace_steps",
    "render_repo_ascii",
]
