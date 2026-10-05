from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "mission_control" / "mycelium" / "executable_value_report.json"
OBSERVATION = ROOT / "mission_control" / "mycelium" / "executable_value_control_observation.json"


def consume(report_path: Path = REPORT, output_path: Path = OBSERVATION) -> dict[str, object]:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    inventory = report["inventory"]
    observation = {
        "schema_version": "0.1",
        "authority_class": "DERIVED_CONTROL_OBSERVATION",
        "authority_transfer": False,
        "registration_debt_queue_required": bool(
            report["control"]["registration_debt_queue_required"]
        ),
        "tested_orphan_queue_required": bool(
            report["control"]["tested_orphan_queue_required"]
        ),
        "unregistered_asset_count": int(inventory["unregistered_asset_count"]),
        "tested_orphan_count": len(report["tested_orphans"]),
        "global_integration_complete": bool(inventory["global_integration_complete"]),
        "next_control_action": (
            "CLASSIFY_EXECUTABLE_REGISTRATION_DEBT"
            if inventory["unregistered_asset_count"]
            else "CLASSIFY_TESTED_ORPHANS"
            if report["tested_orphans"]
            else "PRESERVE_CONTROL"
        ),
    }
    output_path.write_text(
        json.dumps(observation, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return observation


def main() -> int:
    observation = consume()
    print(
        "Executable value control: "
        f"{observation['next_control_action']} / "
        f"{observation['unregistered_asset_count']} unregistered / "
        f"{observation['tested_orphan_count']} tested orphans"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
