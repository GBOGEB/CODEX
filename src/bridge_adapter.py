"""
ABACUS <-> CODEX bridge adapter contracts.

CODEX remains the lightweight platform layer. ABACUS remains the engineering
orchestration runtime. This module defines the boundary in code so downstream
work can depend on an explicit contract instead of duplicated implementations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple


GREEK_TRACE_SEQUENCE: Tuple[str, ...] = (
    "alpha", "beta", "gamma", "delta", "epsilon", "zeta",
    "eta", "theta", "iota", "kappa", "lambda",
)


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
    "RepoRole",
    "create_abacus_codex_contract",
    "default_trace_steps",
    "render_repo_ascii",
]
