"""Validate W000 governance YAML files."""

from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "governance" / "runtime_governance.yml",
    ROOT / "governance" / "agent_registry.yml",
    ROOT / "governance" / "federation_registry.yml",
]


class ValidationError(RuntimeError):
    """Raised when governance YAML validation fails."""


def _require(path: Path, condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(f"{path}: {message}")


def _load_yaml(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    _require(path, isinstance(data, dict), "document must parse to mapping")
    return data


def _validate_runtime(path: Path, data: dict) -> None:
    _require(path, data.get("framework") == "ABACUS-CODEX-FEDERATION", "framework must be ABACUS-CODEX-FEDERATION")
    machine = data.get("runtime_state_machine")
    _require(path, isinstance(machine, dict), "runtime_state_machine missing")
    states = machine.get("states")
    _require(path, isinstance(states, list) and states, "runtime_state_machine.states must be non-empty list")


def _validate_agent_registry(path: Path, data: dict) -> None:
    agents = data.get("agents")
    _require(path, isinstance(agents, list) and agents, "agents must be non-empty list")
    ids = {agent.get("id") for agent in agents if isinstance(agent, dict)}
    _require(path, "gpt_codex_chat" in ids, "gpt_codex_chat agent is required")


def _validate_federation(path: Path, data: dict) -> None:
    nodes = data.get("federation_nodes")
    _require(path, isinstance(nodes, list) and nodes, "federation_nodes must be non-empty list")


def main() -> int:
    validators = {
        "runtime_governance.yml": _validate_runtime,
        "agent_registry.yml": _validate_agent_registry,
        "federation_registry.yml": _validate_federation,
    }

    for path in TARGETS:
        if not path.exists():
            raise ValidationError(f"missing required file: {path}")
        data = _load_yaml(path)
        validators[path.name](path, data)

    print("governance YAML validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
