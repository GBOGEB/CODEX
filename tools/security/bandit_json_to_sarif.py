#!/usr/bin/env python3
"""Convert Bandit JSON output to a minimal deterministic SARIF 2.1.0 document."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


LEVELS = {"HIGH": "error", "MEDIUM": "warning", "LOW": "note"}


def convert(payload: dict[str, Any]) -> dict[str, Any]:
    rules: dict[str, dict[str, Any]] = {}
    results: list[dict[str, Any]] = []

    for finding in payload.get("results", []):
        rule_id = str(finding.get("test_id") or "BANDIT")
        test_name = str(finding.get("test_name") or rule_id)
        text = str(finding.get("issue_text") or test_name)
        severity = str(finding.get("issue_severity") or "LOW").upper()
        confidence = str(finding.get("issue_confidence") or "UNDEFINED").upper()
        more_info = finding.get("more_info")

        rule = rules.setdefault(
            rule_id,
            {
                "id": rule_id,
                "name": test_name,
                "shortDescription": {"text": test_name},
                "help": {"text": f"Bandit {rule_id}: {test_name}"},
                "properties": {"tags": ["security", "bandit"]},
            },
        )
        if more_info:
            rule["helpUri"] = str(more_info)

        result: dict[str, Any] = {
            "ruleId": rule_id,
            "level": LEVELS.get(severity, "warning"),
            "message": {"text": f"{text} (confidence: {confidence})"},
        }
        filename = finding.get("filename")
        if filename:
            try:
                start_line = max(1, int(finding.get("line_number") or 1))
            except (TypeError, ValueError):
                start_line = 1
            result["locations"] = [
                {
                    "physicalLocation": {
                        "artifactLocation": {"uri": str(filename).replace("\\", "/")},
                        "region": {"startLine": start_line},
                    }
                }
            ]
        results.append(result)

    ordered_rules = [rules[key] for key in sorted(rules)]
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Bandit",
                        "informationUri": "https://bandit.readthedocs.io/",
                        "rules": ordered_rules,
                    }
                },
                "results": results,
            }
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    sarif = convert(payload)
    args.output.write_text(json.dumps(sarif, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"Converted {len(payload.get('results', []))} Bandit finding(s) "
        f"to {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
