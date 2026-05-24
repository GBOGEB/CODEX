from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

REQUIRED_KEYS = ["source", "wave", "timestamp", "signals"]


class FeedValidationError(RuntimeError):
    pass


def validate_feed(feed: dict) -> dict:
    missing = [key for key in REQUIRED_KEYS if key not in feed]
    if missing:
        raise FeedValidationError(f"Missing required feed keys: {', '.join(missing)}")

    if not isinstance(feed["signals"], dict):
        raise FeedValidationError("signals must be an object")

    normalized = {str(k): float(v) for k, v in feed["signals"].items()}

    return {
        "source": feed["source"],
        "wave": feed["wave"],
        "timestamp": feed["timestamp"],
        "signal_count": len(normalized),
        "signals": normalized,
        "status": "validated",
    }


def load_feed(path: str | None) -> dict:
    if path is None:
        return {
            "source": "ABACUS",
            "wave": "A67",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "signals": {
                "temperature_K": 4.5,
                "pressure_bar": 1.2,
                "mass_flow_g_s": 42.0
            }
        }

    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate ABACUS feeds")
    parser.add_argument("--input")
    parser.add_argument("--out", default="docs/wave_packages/runtime/abacus_feed_report.json")
    args = parser.parse_args()

    report = validate_feed(load_feed(args.input))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
