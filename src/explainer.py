"""
SHAP Explainability — PhishGuard
==================================
Per-prediction feature attribution using SHAP TreeExplainer.

SHAP values are in log-odds space (XGBoost binary output):
  Positive SHAP  ->  feature pushes toward class 1 (Legitimate) — safe signal
  Negative SHAP  ->  feature pushes toward class 0 (Phishing)   — risk signal

Provides
--------
  ExplanationResult  : per-feature SHAP values + ranked contributors
  explain()          : compute SHAP values for one feature vector
  save_waterfall_plot() : horizontal bar chart of top contributors
  save_heatmap_plot()   : full-feature color heatmap
"""

import os
import warnings
from dataclasses import dataclass, field
from typing import List, Tuple

import matplotlib
matplotlib.use("Agg")   # headless — no GUI window needed
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import shap

warnings.filterwarnings("ignore", category=UserWarning, module="shap")


# ── Result dataclass ───────────────────────────────────────────────────────────

@dataclass
class ExplanationResult:
    """SHAP attribution for a single prediction."""
    base_value:         float                     # E[f(X)] — model expected log-odds
    prediction_value:   float                     # base + sum(shap) = final log-odds
    shap_values:        dict                      # feature_name -> shap_value
    top_risk_features:  List[Tuple[str, float]]   # push toward phishing (most negative)
    top_safe_features:  List[Tuple[str, float]]   # push toward legitimate (most positive)

    def as_dict(self) -> dict:
        """Serialisable representation for API responses."""
        return {
            "base_value":       round(self.base_value, 4),
            "prediction_value": round(self.prediction_value, 4),
            "top_risk_features": [
                {"feature": f, "shap": round(v, 4)}
                for f, v in self.top_risk_features
            ],
            "top_safe_features": [
                {"feature": f, "shap": round(v, 4)}
                for f, v in self.top_safe_features
            ],
        }


# ── Singleton TreeExplainer (expensive to build, reused across calls) ─────────

_tree_explainer: shap.TreeExplainer | None = None


def _get_explainer(model) -> shap.TreeExplainer:
    global _tree_explainer
    if _tree_explainer is None:
        _tree_explainer = shap.TreeExplainer(model)
    return _tree_explainer


# ── Core explain function ─────────────────────────────────────────────────────

def explain(
    model,
    feature_vector: np.ndarray,
    feature_names: list,
    top_n: int = 10,
) -> ExplanationResult:
    """
    Compute per-feature SHAP values for a single prediction.

    Parameters
    ----------
    model          : trained XGBoost binary classifier
    feature_vector : np.ndarray of shape (1, n_features)
    feature_names  : feature column names in same order as vector
    top_n          : number of top risk / safe features to surface

    Returns
    -------
    ExplanationResult

    Note
    ----
    SHAP values are in log-odds space.
    Positive  =>  feature pushes P(legitimate) up    (safe)
    Negative  =>  feature pushes P(legitimate) down  (phishing risk)
    """
    explainer = _get_explainer(model)

    # shap_values: ndarray (1, n_features) for binary XGBoost
    sv = explainer.shap_values(feature_vector)

    # Handle rare case where legacy SHAP returns a list [class0, class1]
    if isinstance(sv, list):
        shap_row = sv[1][0] if len(sv) > 1 else sv[0][0]
    else:
        shap_row = sv[0]                               # shape (n_features,)

    base_val = float(explainer.expected_value)
    pred_val = base_val + float(np.sum(shap_row))

    # Build feature -> value dict
    shap_dict = {
        feature_names[i]: float(shap_row[i])
        for i in range(len(feature_names))
    }

    # Sort ascending: most negative first (highest phishing risk)
    sorted_asc = sorted(shap_dict.items(), key=lambda x: x[1])

    # Top risk = most negative SHAP (push P(legitimate) down)
    top_risk = [(f, v) for f, v in sorted_asc      if v < 0][:top_n]
    # Top safe = most positive SHAP (push P(legitimate) up)
    top_safe = [(f, v) for f, v in reversed(sorted_asc) if v > 0][:top_n]

    return ExplanationResult(
        base_value        = base_val,
        prediction_value  = pred_val,
        shap_values       = shap_dict,
        top_risk_features = top_risk,
        top_safe_features = top_safe,
    )


# ── Plot helpers ──────────────────────────────────────────────────────────────

def _ensure_dir(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)


def save_waterfall_plot(
    explanation: ExplanationResult,
    url: str,
    output_path: str,
    top_n: int = 12,
) -> None:
    """
    Save a waterfall-style horizontal bar chart.

    Bars show the top contributors to the final log-odds prediction.
    Red  = phishing signal (negative SHAP, reduces P(legitimate)).
    Green = legitimate signal (positive SHAP, raises P(legitimate)).
    """
    # Take up to top_n/2 from each side so both directions are visible
    half = max(top_n // 2, 3)
    combined = explanation.top_risk_features[:half] + explanation.top_safe_features[:half]
    combined.sort(key=lambda x: x[1])   # ascending — most risky at top of plot

    if not combined:
        return

    names  = [f for f, _ in combined]
    values = [v for _, v in combined]
    colors = ["#e74c3c" if v < 0 else "#27ae60" for v in values]

    fig, ax = plt.subplots(figsize=(11, max(5, len(names) * 0.55 + 1.5)))
    ax.barh(names, values, color=colors, edgecolor="white", height=0.65)
    ax.axvline(0, color="#2c3e50", linewidth=0.9, linestyle="--", alpha=0.6)

    # Annotate bar ends with SHAP value
    for i, val in enumerate(values):
        ha     = "left"  if val >= 0 else "right"
        offset = 0.003   if val >= 0 else -0.003
        ax.text(val + offset, i, f"{val:+.4f}",
                va="center", ha=ha, fontsize=8, color="#2c3e50")

    # Reference lines: base and prediction
    ax.axvline(explanation.base_value,       color="#8e44ad", linewidth=1.2,
               linestyle=":", alpha=0.8, label=f"Base  {explanation.base_value:+.3f}")
    ax.axvline(explanation.prediction_value, color="#2980b9", linewidth=1.2,
               linestyle=":", alpha=0.8, label=f"Pred  {explanation.prediction_value:+.3f}")
    ax.legend(fontsize=8, loc="lower right")

    ax.set_xlabel(
        "SHAP value (log-odds)\n"
        "Negative = pushes toward Phishing  |  Positive = pushes toward Legitimate",
        fontsize=9,
    )
    ax.set_title(
        f"PhishGuard — Feature Attribution (SHAP Waterfall)\n{url[:90]}",
        fontsize=10, fontweight="bold", pad=10,
    )
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="y", labelsize=8)

    plt.tight_layout()
    _ensure_dir(output_path)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def save_heatmap_plot(
    explanation: ExplanationResult,
    url: str,
    output_path: str,
) -> None:
    """
    Save a single-row color heatmap of all 49 feature SHAP values.

    Red cells  = phishing signal.
    Green cells = legitimate signal.
    White/Yellow = neutral.
    Features are ordered left-to-right from most risky to most safe.
    """
    sorted_items = sorted(explanation.shap_values.items(), key=lambda x: x[1])
    names  = [k for k, _ in sorted_items]
    values = np.array([v for _, v in sorted_items])

    vmax = max(abs(values.min()), abs(values.max()), 0.05)
    norm = mcolors.TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)
    cmap = matplotlib.colormaps.get_cmap("RdYlGn")

    fig, ax = plt.subplots(figsize=(16, 2.8))
    img = ax.imshow(
        values.reshape(1, -1),
        aspect="auto",
        cmap=cmap,
        norm=norm,
    )

    ax.set_xticks(range(len(names)))
    ax.set_xticklabels(names, rotation=90, fontsize=6.5, ha="center")
    ax.set_yticks([])

    cbar = plt.colorbar(img, ax=ax, orientation="horizontal",
                        pad=0.55, fraction=0.04, aspect=50)
    cbar.set_label(
        "SHAP value   Red = Phishing signal  |  Green = Legitimate signal",
        fontsize=8,
    )

    ax.set_title(
        f"PhishGuard — Risk Heatmap (all {len(names)} features)\n{url[:90]}",
        fontsize=9, fontweight="bold",
    )

    plt.tight_layout()
    _ensure_dir(output_path)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
