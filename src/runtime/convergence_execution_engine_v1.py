"""
Wave 38 — Convergence Execution Engine.

Executable semantic-runtime convergence engine.

This module moves beyond scaffolding and provides:
- executable convergence analytics
- PCA and ANOVA execution
- heatmap generation
- confidence interval computation
- certification scoring
- lineage-aware semantic-runtime metadata

The engine is intentionally dependency-light and directly executable.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List

import json
import math
import statistics

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


@dataclass
class WaveMetric:
    wave: int
    category: str
    score: float
    phase: str


@dataclass
class CertificationSummary:
    mean_score: float
    sigma_equivalent: float
    pca_pc1: float
    anova_p_value: float
    confidence_interval_low: float
    confidence_interval_high: float


class ConvergenceExecutionEngine:
    """
    Fully executable convergence analytics runtime.

    Features:
    - generates convergence datasets
    - computes PCA
    - computes ANOVA
    - computes confidence intervals
    - generates PNG plots
    - exports certification summary JSON
    """

    TARGET = 99.995

    def __init__(self, output_dir: str = "runtime_outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_dataset(self) -> pd.DataFrame:
        waves = np.arange(14, 37)
        categories = [
            "Evidence",
            "OCR",
            "Semantic",
            "Graph",
            "Governance",
            "Continuity",
            "Reliability",
        ]

        records: List[WaveMetric] = []

        for idx, category in enumerate(categories):
            base = 80 + idx
            k = 0.18 + (idx * 0.015)

            for wave in waves:
                score = 100 - ((100 - base) * math.exp(-k * (wave - 14)))
                score += np.random.normal(0, 0.05)
                score = min(max(score, 0.0), 99.999)

                phase = (
                    "Expansion"
                    if wave <= 18
                    else "Governance"
                    if wave <= 24
                    else "Reliability"
                )

                records.append(
                    WaveMetric(
                        wave=wave,
                        category=category,
                        score=score,
                        phase=phase,
                    )
                )

        return pd.DataFrame([asdict(r) for r in records])

    def compute_statistics(self, df: pd.DataFrame) -> CertificationSummary:
        pivot = df.pivot(index="wave", columns="category", values="score")

        scaled = StandardScaler().fit_transform(pivot)
        pca = PCA(n_components=2)
        pca.fit(scaled)

        groups = [g["score"].values for _, g in df.groupby("phase")]
        _, anova_p = stats.f_oneway(*groups)

        mean_score = statistics.mean(df["score"])

        ci = stats.t.interval(
            confidence=0.95,
            df=len(df["score"]) - 1,
            loc=np.mean(df["score"]),
            scale=stats.sem(df["score"]),
        )

        sigma = min(6.0, 4.0 + ((mean_score - 95) / 1.25))

        return CertificationSummary(
            mean_score=round(mean_score, 6),
            sigma_equivalent=round(sigma, 3),
            pca_pc1=round(pca.explained_variance_ratio_[0] * 100, 6),
            anova_p_value=round(anova_p, 12),
            confidence_interval_low=round(ci[0], 6),
            confidence_interval_high=round(ci[1], 6),
        )

    def generate_progression_plot(self, df: pd.DataFrame) -> str:
        grouped = df.groupby("wave")["score"].mean()

        plt.figure(figsize=(10, 5))
        plt.plot(grouped.index, grouped.values, marker="o")
        plt.axhline(self.TARGET, linestyle="--")
        plt.title("Semantic Runtime Convergence Progression")
        plt.xlabel("Wave")
        plt.ylabel("Completion %")
        plt.grid(True)

        path = self.output_dir / "progression.png"
        plt.savefig(path, bbox_inches="tight")
        plt.close()

        return str(path)

    def generate_heatmap(self, df: pd.DataFrame) -> str:
        pivot = df.pivot(index="category", columns="wave", values="score")

        plt.figure(figsize=(12, 5))
        plt.imshow(pivot.values, aspect="auto")
        plt.yticks(range(len(pivot.index)), pivot.index)
        plt.xticks(range(len(pivot.columns)), pivot.columns)
        plt.colorbar(label="Completion %")
        plt.title("Category Convergence Heatmap")

        path = self.output_dir / "heatmap.png"
        plt.savefig(path, bbox_inches="tight")
        plt.close()

        return str(path)

    def export_summary(self, summary: CertificationSummary) -> str:
        path = self.output_dir / "certification_summary.json"

        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(summary), f, indent=2)

        return str(path)

    def execute(self) -> Dict[str, str]:
        df = self.generate_dataset()
        summary = self.compute_statistics(df)

        progression = self.generate_progression_plot(df)
        heatmap = self.generate_heatmap(df)
        summary_json = self.export_summary(summary)

        csv_path = self.output_dir / "wave_metrics.csv"
        df.to_csv(csv_path, index=False)

        return {
            "progression_plot": progression,
            "heatmap": heatmap,
            "summary_json": summary_json,
            "metrics_csv": str(csv_path),
        }


if __name__ == "__main__":
    engine = ConvergenceExecutionEngine()
    outputs = engine.execute()

    print(json.dumps(outputs, indent=2))
