#!/usr/bin/env python3
"""Generate Phase 0 orchestration task links and cross-repository signals."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

import yaml


def generate(output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).isoformat()
    task_links = {
        "phase": "Phase 0",
        "generated_at": generated_at,
        "principle": "Federation, not duplication",
        "task_links": [
            {
                "source_content_id": "confluence:ACR:page:1023934467",
                "source_title": "DSBT Task 3 - Technical Support",
                "github_issue": "TBD: create/attach issue after repository owner confirms issue tracker target",
                "engineering_task": "CD_Item1 Confluence target read and artifact generation",
                "repository_modules": ["federation_runtime/engines/confluence_artifact_pipeline.py", "outputs/confluence/page_1023934467"],
                "future_jobs": ["ABACUS semantic-section enrichment", "CODEX knowledge-graph construction"],
                "trace_reference": "outputs/confluence/page_1023934467/metadata.yaml",
            },
            {
                "source_content_id": "qplant:contractual-baseline:locked",
                "source_title": "QPLANT locked contractual baseline",
                "github_issue": "TBD: create/attach issue after baseline governance owner confirms tracker target",
                "engineering_task": "CD_Item2 QPLANT contractual baseline ingestion",
                "repository_modules": ["federation_runtime/engines/qplant_contractual_ingestion.py", "docs/qplant/baseline", "docs/qplant/rtm"],
                "future_jobs": ["RTM validation", "Contractual delta review", "ABACUS compliance roll-up"],
                "trace_reference": "docs/qplant/baseline/contractual_baseline_manifest.yaml",
            },
        ],
    }
    signals = {
        "phase": "Phase 0",
        "generated_at": generated_at,
        "cross_repo_signals": [
            {
                "source_content_id": "confluence:ACR:page:1023934467",
                "target_repository": "CODEX",
                "requested_action": "archive_confluence_artifacts_and_seed_semantic_tasks",
                "payload_status": "artifact_generation_initialized",
                "trace_reference": "outputs/confluence/page_1023934467",
            },
            {
                "source_content_id": "qplant:contractual-baseline:locked",
                "target_repository": "QPLANT",
                "requested_action": "review_locked_baseline_manifest_and_contractual_delta_policy",
                "payload_status": "baseline_ingestion_initialized",
                "trace_reference": "outputs/qplant/contractual_ingestion/change_deltas.yaml",
            },
            {
                "source_content_id": "phase0:dmaic:wave-anthology",
                "target_repository": "ABACUS",
                "requested_action": "prepare_future_semantic_enrichment_job_contract",
                "payload_status": "rudimentary_signal_ready",
                "trace_reference": "docs/governance/WAVE_ANTHOLOGY.md",
            },
        ],
    }
    task_path = output_dir / "task_links.yaml"
    signal_path = output_dir / "cross_repo_signals.yaml"
    task_path.write_text(yaml.safe_dump(task_links, sort_keys=False), encoding="utf-8")
    signal_path.write_text(yaml.safe_dump(signals, sort_keys=False), encoding="utf-8")
    return task_path, signal_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate Phase 0 orchestration artifacts")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/orchestration"))
    args = parser.parse_args(argv)
    task_path, signal_path = generate(args.output_dir)
    print(f"wrote {task_path} and {signal_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
