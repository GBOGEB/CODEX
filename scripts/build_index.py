"""Command line helper for the zip packaging pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from src.zip_pipeline import ZipPipeline


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="Conversation source directory")
    parser.add_argument("--output", type=Path, required=True, help="Output directory for archives")
    parser.add_argument("--dataset-name", required=True, help="Name of the dataset to archive")
    parser.add_argument(
        "--manifest-name",
        default="conversations_manifest.json",
        help="Filename for the generated manifest",
    )
    parser.add_argument(
        "--index-path",
        type=Path,
        default=Path("GLOBAL_index.json"),
        help="Location of the aggregated index",
    )
    parser.add_argument(
        "--extra-manifest",
        type=Path,
        action="append",
        default=[],
        help="Additional manifest files to include in the global index",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv)

    pipeline = ZipPipeline(
        source_root=args.source,
        output_root=args.output,
        dataset_name=args.dataset_name,
        manifest_name=args.manifest_name,
    )
    manifest_path = pipeline.run()

    manifests = [manifest_path, *args.extra_manifest]
    ZipPipeline.build_global_index(manifests, args.index_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
