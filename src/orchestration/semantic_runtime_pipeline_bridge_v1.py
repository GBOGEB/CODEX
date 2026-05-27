"""
Wave 39 — Semantic Runtime Pipeline Bridge.

A complete, directly executable bridge/orchestration runtime for the narrowed
scope: convergence telemetry -> statistics -> certification -> artifacts.

This is intentionally self-contained so it can run even before the wider package
structure is fully normalized.

Run:
    python src/orchestration/semantic_runtime_pipeline_bridge_v1.py --out runtime_outputs/wave39

Outputs:
    telemetry.csv
    wave_stats.csv
    category_stats.csv
    weights_table.csv
    dmaic_stats.csv
    pca_components.csv
    pca_loadings.csv
    anova_one_way.csv
    anova_two_factor.csv
    claimed_vs_actual.csv
    certification_summary.json
    progression.png
    heatmap.png
    plotly_progression.html
    plotly_animation.html
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

try:
    import matplotlib.pyplot as plt
except Exception as exc:  # pragma: no cover
    raise RuntimeError("matplotlib is required for PNG artifact generation") from exc

try:
    import plotly.express as px
    import plotly.graph_objects as go
except Exception as exc:  # pragma: no cover
    raise RuntimeError("plotly is required for interactive artifact generation") from exc

try:
    from scipy import stats
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    import statsmodels.api as sm
    from statsmodels.formula.api import ols
except Exception as exc:  # pragma: no cover
    raise RuntimeError("scipy, scikit-learn and statsmodels are required for statistics") from exc


TARGET_ESRC = 99.995


@dataclass(frozen=True)
class RuntimeCategory:
    category: str
    weight: float
    factor: str
    description: str
    start_score: float
    convergence_rate: float


@dataclass
class CertificationSummary:
    target_esrc: float
    current_esrc: float
    wave_at_target: int | None
    sigma_band: str
    one_way_anova_p: float
    two_factor_phase_p: float
    pca_pc1_explained_percent: float
    pca_pc2_explained_percent: float
    status: str
    claimed_vs_actual_warning: str


class SemanticRuntimePipelineBridge:
    """Executable orchestration pipeline for convergence analytics."""

    def __init__(self, out_dir: Path):
        self.out_dir = out_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.categories = self._default_categories()

    @staticmethod
    def _default_categories() -> List[RuntimeCategory]:
        return [
            RuntimeCategory("Evidence Fidelity", 0.16, "F1", "Image/vector evidence remains primary and traceable", 82.0, 0.205),
            RuntimeCategory("OCR Governance", 0.10, "F2", "OCR remains sidecar and low-intrusion", 85.0, 0.230),
            RuntimeCategory("Semantic Reconstruction", 0.14, "F3", "Deck and diagram semantics converge structurally", 80.0, 0.200),
            RuntimeCategory("Topology Graph Runtime", 0.12, "F4", "Engineering relationships are represented as graph edges", 78.0, 0.185),
            RuntimeCategory("Governance Mesh", 0.12, "F5", "Policy gates and semantic trust checks are enforceable", 81.0, 0.215),
            RuntimeCategory("Automation Readiness", 0.12, "F6", "Pipeline can execute and export artifacts", 76.0, 0.190),
            RuntimeCategory("Continuity Fabric", 0.12, "F7", "Lineage, snapshots and replay are preserved", 74.0, 0.175),
            RuntimeCategory("Reliability Assurance", 0.12, "F8", "Chaos, certification and convergence checks are quantified", 72.0, 0.170),
        ]

    @staticmethod
    def _phase_for_wave(wave: int) -> str:
        if wave <= 18:
            return "Expansion"
        if wave <= 24:
            return "Governance"
        if wave <= 30:
            return "Reliability"
        return "Certification"

    @staticmethod
    def _sigma_band(esrc: float) -> str:
        if esrc >= 99.995:
            return "6sigma-target"
        if esrc >= 99.990:
            return "5.5sigma"
        if esrc >= 99.950:
            return "5sigma"
        if esrc >= 99.500:
            return "4.5sigma"
        return "below-4.5sigma"

    def generate_telemetry(self, start_wave: int = 14, end_wave: int = 40) -> pd.DataFrame:
        rows: List[Dict] = []
        rng = np.random.default_rng(39)
        for wave in range(start_wave, end_wave + 1):
            for cat in self.categories:
                deterministic = 100.0 - ((100.0 - cat.start_score) * math.exp(-cat.convergence_rate * (wave - start_wave)))
                small_noise = rng.normal(0.0, 0.025)
                score = float(np.clip(deterministic + small_noise, 0.0, 99.9995))
                rows.append({
                    "wave": wave,
                    "phase": self._phase_for_wave(wave),
                    "category": cat.category,
                    "factor": cat.factor,
                    "weight": cat.weight,
                    "score": score,
                    "normalized_score": score / 100.0,
                    "weighted_score": score * cat.weight,
                })
        return pd.DataFrame(rows)

    def compute_wave_stats(self, telemetry: pd.DataFrame) -> pd.DataFrame:
        grouped = telemetry.groupby("wave", as_index=False).agg(
            esrc=("weighted_score", "sum"),
            mean_score=("score", "mean"),
            min_score=("score", "min"),
            max_score=("score", "max"),
            std_score=("score", "std"),
        )
        grouped["gap_to_target"] = (TARGET_ESRC - grouped["esrc"]).clip(lower=0.0)
        grouped["incremental_gain"] = grouped["esrc"].diff().fillna(0.0)
        grouped["sigma_band"] = grouped["esrc"].apply(self._sigma_band)
        return grouped

    def compute_category_stats(self, telemetry: pd.DataFrame) -> pd.DataFrame:
        return telemetry.groupby(["category", "factor", "weight"], as_index=False).agg(
            first_wave=("wave", "min"),
            last_wave=("wave", "max"),
            start_score=("score", "first"),
            final_score=("score", "last"),
            mean_score=("score", "mean"),
            std_score=("score", "std"),
        )

    def compute_confidence_intervals(self, telemetry: pd.DataFrame) -> pd.DataFrame:
        rows = []
        for wave, group in telemetry.groupby("wave"):
            mean = group["score"].mean()
            sem = stats.sem(group["score"])
            low, high = stats.t.interval(0.95, len(group) - 1, loc=mean, scale=sem)
            rows.append({"wave": wave, "mean": mean, "ci95_low": low, "ci95_high": high})
        return pd.DataFrame(rows)

    def compute_pca(self, telemetry: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
        pivot = telemetry.pivot(index="wave", columns="category", values="score")
        scaled = StandardScaler().fit_transform(pivot)
        pca = PCA(n_components=2)
        pcs = pca.fit_transform(scaled)
        components = pd.DataFrame({
            "wave": pivot.index,
            "pc1": pcs[:, 0],
            "pc2": pcs[:, 1],
        })
        loadings = pd.DataFrame(
            pca.components_.T,
            columns=["pc1_loading", "pc2_loading"],
            index=pivot.columns,
        ).reset_index().rename(columns={"index": "category"})
        return components, loadings, pca.explained_variance_ratio_

    def compute_anova(self, telemetry: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        phase_groups = [g["score"].values for _, g in telemetry.groupby("phase")]
        f_stat, p_value = stats.f_oneway(*phase_groups)
        one_way = pd.DataFrame([{"effect": "phase", "f_statistic": f_stat, "p_value": p_value}])
        model = ols("score ~ C(category) + C(phase) + C(category):C(phase)", data=telemetry).fit()
        two_factor = sm.stats.anova_lm(model, typ=2).reset_index().rename(columns={"index": "effect"})
        return one_way, two_factor

    def compute_dmaic(self, wave_stats: pd.DataFrame) -> pd.DataFrame:
        latest = wave_stats.iloc[-1]
        previous = wave_stats.iloc[-2]
        return pd.DataFrame([
            {"dmaic": "Define", "metric": "target_esrc", "value": TARGET_ESRC, "interpretation": "Six-sigma-inspired semantic-runtime convergence target"},
            {"dmaic": "Measure", "metric": "current_esrc", "value": latest["esrc"], "interpretation": "Weighted telemetry-derived current convergence"},
            {"dmaic": "Analyze", "metric": "incremental_gain", "value": latest["incremental_gain"], "interpretation": "Diminishing-return signal for latest wave"},
            {"dmaic": "Improve", "metric": "gap_closed_from_previous", "value": previous["gap_to_target"] - latest["gap_to_target"], "interpretation": "Latest wave contribution to closing target gap"},
            {"dmaic": "Control", "metric": "gap_to_target", "value": latest["gap_to_target"], "interpretation": "Residual instability still requiring certification maintenance"},
        ])

    def claimed_vs_actual(self) -> pd.DataFrame:
        rows = [
            ("Pipeline bridge exists", "actual", "Implemented as this executable orchestrator"),
            ("Telemetry generation", "actual", "Deterministic modeled telemetry generated to CSV"),
            ("Weighted ESRC", "actual", "Computed from category weights and exported"),
            ("PCA", "actual", "Executed with scikit-learn and exported components/loadings"),
            ("One-way ANOVA", "actual", "Executed with scipy"),
            ("Two-factor ANOVA", "actual", "Executed with statsmodels formula API"),
            ("Confidence intervals", "actual", "95% CI computed per wave"),
            ("Plotly animation", "actual", "Generated to HTML artifact"),
            ("Real uploaded deck parsing", "todo", "Bridge currently uses modeled telemetry; connect to PPTX/SVG inventory extractor next"),
            ("CI/CD execution", "todo", "No GitHub Actions workflow added yet"),
            ("Package imports", "partial", "Bridge is self-contained; wider package normalization remains TODO"),
            ("Civilization semantics lineage", "partial", "Glossary exists; lineage should be linked into runtime outputs next"),
        ]
        return pd.DataFrame(rows, columns=["claim", "actual_status", "notes"])

    def render_artifacts(self, telemetry: pd.DataFrame, wave_stats: pd.DataFrame, pca_components: pd.DataFrame) -> Dict[str, str]:
        paths: Dict[str, str] = {}
        pivot = telemetry.pivot(index="category", columns="wave", values="score")

        plt.figure(figsize=(10, 5))
        plt.plot(wave_stats["wave"], wave_stats["esrc"], marker="o")
        plt.axhline(TARGET_ESRC, linestyle="--")
        plt.xlabel("Wave")
        plt.ylabel("Weighted ESRC %")
        plt.title("Wave Progression — Weighted ESRC")
        plt.grid(True)
        progression_png = self.out_dir / "progression_esrc.png"
        plt.savefig(progression_png, bbox_inches="tight")
        plt.close()
        paths["progression_png"] = str(progression_png)

        plt.figure(figsize=(12, 5))
        plt.imshow(pivot.values, aspect="auto")
        plt.yticks(range(len(pivot.index)), pivot.index)
        plt.xticks(range(len(pivot.columns)), pivot.columns)
        plt.colorbar(label="Score %")
        plt.title("Category Completion Heatmap")
        heatmap_png = self.out_dir / "completion_heatmap.png"
        plt.savefig(heatmap_png, bbox_inches="tight")
        plt.close()
        paths["heatmap_png"] = str(heatmap_png)

        fig = go.Figure()
        for category, group in telemetry.groupby("category"):
            fig.add_trace(go.Scatter(x=group["wave"], y=group["score"], mode="lines", name=category))
        fig.add_hline(y=TARGET_ESRC, line_dash="dash")
        fig.update_layout(title="Plotly Category Progression", xaxis_title="Wave", yaxis_title="Score %")
        plotly_progression = self.out_dir / "plotly_progression.html"
        fig.write_html(plotly_progression)
        paths["plotly_progression"] = str(plotly_progression)

        anim = px.scatter(
            telemetry,
            x="category",
            y="score",
            animation_frame="wave",
            color="phase",
            size="weight",
            range_y=[70, 100.2],
            title="Animated Wave Progression by Category",
        )
        plotly_animation = self.out_dir / "plotly_wave_animation.html"
        anim.write_html(plotly_animation)
        paths["plotly_animation"] = str(plotly_animation)

        pca_fig = px.scatter(
            pca_components,
            x="pc1",
            y="pc2",
            text="wave",
            title="PCA Wave Trajectory",
        )
        plotly_pca = self.out_dir / "plotly_pca.html"
        pca_fig.write_html(plotly_pca)
        paths["plotly_pca"] = str(plotly_pca)

        return paths

    def execute(self) -> Dict[str, object]:
        telemetry = self.generate_telemetry()
        wave_stats = self.compute_wave_stats(telemetry)
        category_stats = self.compute_category_stats(telemetry)
        ci = self.compute_confidence_intervals(telemetry)
        pca_components, pca_loadings, pca_explained = self.compute_pca(telemetry)
        one_way, two_factor = self.compute_anova(telemetry)
        dmaic = self.compute_dmaic(wave_stats)
        claimed = self.claimed_vs_actual()
        artifacts = self.render_artifacts(telemetry, wave_stats, pca_components)

        weights = pd.DataFrame([asdict(c) for c in self.categories])
        latest = wave_stats.iloc[-1]
        target_rows = wave_stats[wave_stats["esrc"] >= TARGET_ESRC]
        wave_at_target = int(target_rows.iloc[0]["wave"]) if not target_rows.empty else None

        summary = CertificationSummary(
            target_esrc=TARGET_ESRC,
            current_esrc=round(float(latest["esrc"]), 6),
            wave_at_target=wave_at_target,
            sigma_band=str(latest["sigma_band"]),
            one_way_anova_p=round(float(one_way.iloc[0]["p_value"]), 12),
            two_factor_phase_p=round(float(two_factor.loc[two_factor["effect"] == "C(phase)", "PR(>F)"].iloc[0]), 12),
            pca_pc1_explained_percent=round(float(pca_explained[0] * 100.0), 6),
            pca_pc2_explained_percent=round(float(pca_explained[1] * 100.0), 6),
            status="PASS" if latest["esrc"] >= TARGET_ESRC else "HOLD",
            claimed_vs_actual_warning="Modeled telemetry is executable; real deck telemetry ingestion remains TODO.",
        )

        outputs = {
            "telemetry_csv": self.out_dir / "telemetry.csv",
            "wave_stats_csv": self.out_dir / "wave_stats.csv",
            "category_stats_csv": self.out_dir / "category_stats.csv",
            "weights_csv": self.out_dir / "weights_table.csv",
            "ci_csv": self.out_dir / "confidence_intervals.csv",
            "pca_components_csv": self.out_dir / "pca_components.csv",
            "pca_loadings_csv": self.out_dir / "pca_loadings.csv",
            "anova_one_way_csv": self.out_dir / "anova_one_way.csv",
            "anova_two_factor_csv": self.out_dir / "anova_two_factor.csv",
            "dmaic_csv": self.out_dir / "dmaic_stats.csv",
            "claimed_vs_actual_csv": self.out_dir / "claimed_vs_actual.csv",
            "summary_json": self.out_dir / "certification_summary.json",
        }

        telemetry.to_csv(outputs["telemetry_csv"], index=False)
        wave_stats.to_csv(outputs["wave_stats_csv"], index=False)
        category_stats.to_csv(outputs["category_stats_csv"], index=False)
        weights.to_csv(outputs["weights_csv"], index=False)
        ci.to_csv(outputs["ci_csv"], index=False)
        pca_components.to_csv(outputs["pca_components_csv"], index=False)
        pca_loadings.to_csv(outputs["pca_loadings_csv"], index=False)
        one_way.to_csv(outputs["anova_one_way_csv"], index=False)
        two_factor.to_csv(outputs["anova_two_factor_csv"], index=False)
        dmaic.to_csv(outputs["dmaic_csv"], index=False)
        claimed.to_csv(outputs["claimed_vs_actual_csv"], index=False)
        outputs["summary_json"].write_text(json.dumps(asdict(summary), indent=2), encoding="utf-8")

        return {
            "summary": asdict(summary),
            "artifact_paths": {k: str(v) for k, v in outputs.items()} | artifacts,
        }


def main() -> None:
    parser = argparse.ArgumentParser(description="Wave 39 semantic runtime pipeline bridge")
    parser.add_argument("--out", default="runtime_outputs/wave39", help="Output directory")
    args = parser.parse_args()

    bridge = SemanticRuntimePipelineBridge(Path(args.out))
    result = bridge.execute()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
