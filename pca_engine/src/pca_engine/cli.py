"""Command-line interface for the generic PCA engine."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .pca_core import fit_pca
from .pca_loadings import loadings
from .pca_reconstruction import reconstruction_metrics
from .reporting import write_markdown_report


def run_csv(input_path: str, target_dir: str, n_components: int | None, scale: bool = True) -> dict:
    frame = pd.read_csv(input_path)
    result = fit_pca(frame, n_components=n_components, scale=scale)
    out = Path(target_dir); out.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(result.scores_, columns=[f"PC{i+1}" for i in range(result.n_components_)]).to_csv(out / "scores.csv", index=False)
    pd.DataFrame(result.components_, columns=result.feature_names_, index=[f"PC{i+1}" for i in range(result.n_components_)]).to_csv(out / "components.csv")
    pd.DataFrame(loadings(result), index=result.feature_names_, columns=[f"PC{i+1}" for i in range(result.n_components_)]).to_csv(out / "loadings.csv")
    metrics = reconstruction_metrics(result)
    summary = {
        "schema": "codex-generic-pca-engine/v1",
        "rows": int(result.input_matrix_.shape[0]),
        "features": result.feature_names_,
        "n_components": result.n_components_,
        "eigenvalues": result.eigenvalues_.tolist(),
        "explained_variance_ratio": result.explained_variance_ratio_.tolist(),
        "reconstruction": metrics,
        "domain": "GENERIC_NON_TRADING",
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    write_markdown_report(result, out / "report.md")
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pca-engine")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="run PCA on a generic CSV")
    run.add_argument("input_csv")
    run.add_argument("--target-dir", default="pca_out")
    run.add_argument("--n-components", type=int, default=None)
    run.add_argument("--no-scale", action="store_true")
    return parser


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "run":
        summary = run_csv(args.input_csv, args.target_dir, args.n_components, not args.no_scale)
        print(json.dumps(summary, indent=2))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
