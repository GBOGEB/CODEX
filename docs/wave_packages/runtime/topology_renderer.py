from __future__ import annotations

import argparse
import json
from pathlib import Path


def render_mermaid(topology: dict) -> str:
    lines = ["graph TD"]

    forward = topology.get("forward_recursion", [])
    for index in range(len(forward) - 1):
        a = forward[index].replace(" ", "_")
        b = forward[index + 1].replace(" ", "_")
        lines.append(f"    {a} --> {b}")

    backward = topology.get("backward_recursion", [])
    for index in range(len(backward) - 1):
        a = backward[index].replace(" ", "_")
        b = backward[index + 1].replace(" ", "_")
        lines.append(f"    {a} --> {b}")

    return "\n".join(lines)


def load_topology(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description="Render topology graph")
    parser.add_argument(
        "--input",
        default="docs/wave_packages/topology/topology_runtime.json",
    )
    parser.add_argument(
        "--out",
        default="docs/wave_packages/runtime/out/topology_runtime.mmd",
    )
    args = parser.parse_args()

    mermaid = render_mermaid(load_topology(args.input))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(mermaid, encoding="utf-8")

    print(mermaid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
