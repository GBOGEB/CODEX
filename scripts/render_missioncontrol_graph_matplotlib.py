from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "mission_control" / "mycelium" / "graph_analysis.json"
OUT = ROOT / "docs" / "assets" / "missioncontrol" / "missioncontrol_degree_distribution.png"


def main() -> None:
    import matplotlib.pyplot as plt

    analysis = json.loads(ANALYSIS.read_text(encoding="utf-8"))
    rows = analysis["degree_distribution"]
    degrees = [row["degree"] for row in rows]
    counts = [row["count"] for row in rows]

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.bar(degrees, counts)
    ax.set_title("MissionControl interaction graph — degree distribution")
    ax.set_xlabel("Total degree (in + out)")
    ax.set_ylabel("Node count")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        OUT,
        dpi=160,
        bbox_inches="tight",
        metadata={"Software": "CODEX MissionControl"},
    )
    plt.close(fig)
    print(f"Matplotlib graph evidence: {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
