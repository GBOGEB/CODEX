#!/usr/bin/env python3
"""
MESSAGE 4 & 5: Gemini Bridge Sync Agent with Validation Patch.

Fixes the runtime ``NameError: name 'decision' is not defined`` by enclosing
validation and JSONL log append operations inside the artifact loop immediately
after agentic evaluation.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
from pathlib import Path, PureWindowsPath
from typing import Any

ALLOWED_STRATEGIES = {"PRUNE", "BRIDGE", "CHERRY-PICK", "PARALLEL", "DISCARD"}
SECRET_NAME_PATTERNS = (
    ".env",
    "secret",
    "secrets",
    "credential",
    "credentials",
    "token",
    "apikey",
    "api_key",
)
VOLATILE_NOTEBOOK_METADATA = {
    "widgets",
    "toc",
    "varInspector",
    "collapsed",
    "execution",
    "ExecuteTime",
}
DEFAULT_MODEL_ID = "gemini-3.1-pro-preview-customtools"


class DriveSyncAgent:
    """Review-first Drive sync agent for staged inbound artifacts."""

    def __init__(self, root: Path):
        self.root = root
        self.exchange_dir = root / "googledrive"
        self.staging_dir = self.exchange_dir / "inbound_staging"
        self.manifest_path = self.exchange_dir / ".codex-exchange.yaml"
        self.model_id = os.environ.get("GEMINI_MODEL", DEFAULT_MODEL_ID)

    def scrub_notebook(self, path: Path) -> str:
        """Remove execution outputs/counts and volatile metadata before analysis."""
        with open(path, "r", encoding="utf-8") as handle:
            notebook = json.load(handle)

        if "cells" in notebook:
            for cell in notebook["cells"]:
                if not isinstance(cell, dict):
                    continue
                cell["outputs"] = []
                cell["execution_count"] = None
                metadata = cell.get("metadata")
                if isinstance(metadata, dict):
                    for key in VOLATILE_NOTEBOOK_METADATA:
                        metadata.pop(key, None)

        metadata = notebook.get("metadata")
        if isinstance(metadata, dict):
            for key in VOLATILE_NOTEBOOK_METADATA:
                metadata.pop(key, None)

        return json.dumps(notebook, indent=2, sort_keys=True)

    def read_artifact_content(self, file_path: Path) -> str:
        if file_path.suffix.lower() == ".ipynb":
            return self.scrub_notebook(file_path)
        return file_path.read_text(encoding="utf-8", errors="ignore")

    def evaluate_artifact_agentically(self, name: str, content: str, manifest: str) -> dict[str, Any]:
        """Invoke Gemini when configured, otherwise return a conservative decision."""
        if not os.environ.get("GEMINI_API_KEY"):
            return self.evaluate_artifact_locally(name, content)
        if not google_genai_available():
            return {
                "strategy": "DISCARD",
                "target_path": "",
                "rationale": "GEMINI_API_KEY is set but google-genai is unavailable; failed closed.",
            }
        return self.evaluate_with_gemini(name, content, manifest)

    def evaluate_with_gemini(self, name: str, content: str, manifest: str) -> dict[str, Any]:
        """Invoke Gemini 3.1 Pro using structural JSON response protocols."""
        from google import genai
        from google.genai import types

        client = genai.Client()
        prompt = (
            f"Evaluate inbound asset '{name}' against the manifest:\n{manifest}\n\n"
            f"Content:\n{content[:20000]}"
        )
        response = client.models.generate_content(
            model=self.model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
                system_instruction=(
                    "Output JSON containing: 'strategy' "
                    "(PRUNE/BRIDGE/CHERRY-PICK/PARALLEL/DISCARD), "
                    "'target_path' (string), and 'rationale' (string)."
                ),
            ),
        )
        return self.parse_json_response(response.text)

    def parse_json_response(self, text: str) -> dict[str, Any]:
        stripped = text.strip()
        if stripped.startswith("```"):
            stripped = re.sub(r"^```(?:json)?\s*", "", stripped)
            stripped = re.sub(r"\s*```$", "", stripped)
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError as exc:
            return {
                "strategy": "DISCARD",
                "target_path": "",
                "rationale": f"Model response was invalid JSON; failed closed: {exc}",
            }
        if not isinstance(parsed, dict):
            return {
                "strategy": "DISCARD",
                "target_path": "",
                "rationale": "Model response was not a JSON object; failed closed.",
            }
        return parsed

    def evaluate_artifact_locally(self, name: str, content: str) -> dict[str, str]:
        """Offline fallback for environments without a Gemini API key."""
        lower_name = name.lower()
        if any(pattern in lower_name for pattern in SECRET_NAME_PATTERNS):
            return {
                "strategy": "DISCARD",
                "target_path": "",
                "rationale": "Secret-like filename is excluded from repository integration.",
            }
        if "\x00" in content:
            return {
                "strategy": "DISCARD",
                "target_path": "",
                "rationale": "Binary-looking content requires manual review outside this bridge.",
            }
        if lower_name.endswith(".ipynb"):
            return {
                "strategy": "PARALLEL",
                "target_path": f"googledrive/parallel_refs/{name}",
                "rationale": "Notebook was scrubbed and retained as a parallel reference.",
            }
        if lower_name.endswith((".patch", ".diff")):
            return {
                "strategy": "CHERRY-PICK",
                "target_path": f"googledrive/cherry_picks/{name}",
                "rationale": "Patch-like artifact should be reviewed as a cherry-pick candidate.",
            }
        return {
            "strategy": "BRIDGE",
            "target_path": f"googledrive/bridged/{name}",
            "rationale": "Text artifact is suitable for review-first bridge handling.",
        }

    def target_is_unsafe(self, target: Path) -> bool:
        windows_target = PureWindowsPath(str(target))
        return target.is_absolute() or windows_target.is_absolute() or ".." in target.parts

    def process_and_route(self) -> bool:
        if not self.staging_dir.exists():
            print("[-] No files found in staging folder.")
            return False

        inbound_files = sorted(
            file_path
            for file_path in self.staging_dir.iterdir()
            if file_path.is_file() and file_path.name != ".gitkeep"
        )
        if not inbound_files:
            print("[-] No files found in staging folder.")
            return False

        with open(self.manifest_path, "r", encoding="utf-8") as handle:
            manifest_content = handle.read()

        routed_any = False
        for file_path in inbound_files:
            print(f"\n[*] Processing artifact: {file_path.name}")

            content = self.read_artifact_content(file_path)
            decision = self.evaluate_artifact_agentically(file_path.name, content, manifest_content)

            # ==================== MESSAGE 5: VALIDATION PATCH ====================
            # Scoped strictly inside the loop context to eliminate the NameError trace.
            strategy = str(decision.get("strategy", "")).upper()
            allowed = {"PRUNE", "BRIDGE", "CHERRY-PICK", "PARALLEL", "DISCARD"}

            if strategy not in allowed:
                raise ValueError(f"Invalid strategy: {strategy}")

            target = Path(str(decision.get("target_path", "")))

            if self.target_is_unsafe(target):
                raise ValueError(f"Unsafe target path: {target}")

            decision["strategy"] = strategy
            decision["target_path"] = "" if str(target) == "." else str(target)

            log_path = self.exchange_dir / "decision_log.jsonl"

            with open(log_path, "a", encoding="utf-8") as log:
                log.write(json.dumps({
                    "file": file_path.name,
                    "strategy": decision["strategy"],
                    "target_path": decision["target_path"],
                    "rationale": decision.get("rationale", "")
                }) + "\n")
            # =====================================================================

            routed_any = True
            print(f" └── Verified Action: [{strategy}] -> {decision['target_path'] or '<none>'}")

        return routed_any


def google_genai_available() -> bool:
    google_spec = importlib.util.find_spec("google")
    if google_spec is None:
        return False
    return importlib.util.find_spec("google.genai") is not None


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Reserved for compatibility; logs stay JSONL.")
    parser.add_argument(
        "--check-google-genai",
        action="store_true",
        help="Report whether the optional google-genai package is importable.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.check_google_genai:
        print("google-genai available" if google_genai_available() else "google-genai missing")
        return 0 if google_genai_available() else 1

    workspace_root = Path(__file__).resolve().parents[2]
    agent = DriveSyncAgent(workspace_root)
    if agent.process_and_route():
        print("\n[+] Direct evaluation complete. Run Git sequencing hooks next.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
