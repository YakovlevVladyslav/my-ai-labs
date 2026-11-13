"""Matplotlib figures for input fuzzification and Mamdani output."""
import matplotlib.pyplot as plt
import numpy as np

from fuzzy_model import LABELS, MEMBERSHIPS, TERM_LABELS, UNIVERSES, RULES
from inference import InferenceResult

COLORS = {"low": "#2c7fb8", "medium": "#e6a23c", "high": "#c04461", "normal": "#2c7fb8", "overloaded": "#e6a23c", "critical": "#c04461"}


def plot_membership(variable: str, value: float | None = None):
    fig, ax = plt.subplots(figsize=(7, 3))
    x = UNIVERSES[variable]
    for term, y in MEMBERSHIPS[variable].items():
        ax.plot(x, y, label=TERM_LABELS[variable][term], color=COLORS[term], linewidth=2)
        if value is not None:
            degree = float(np.interp(value, x, y))
            ax.scatter([value], [degree], color=COLORS[term], s=35, zorder=3)
    if value is not None:
        ax.axvline(value, color="#555555", linestyle="--", alpha=0.7)
    name, unit = LABELS[variable]
    ax.set_title(name)
    ax.set_xlabel(f"{name}, {unit}")
    ax.set_ylabel("Принадлежность μ")
    ax.set_ylim(-0.03, 1.08)
    ax.set_xlim(x[0], x[-1])
    ax.legend(loc="upper right", ncol=3, fontsize=8)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    return fig


def plot_aggregation(result: InferenceResult):
    x = UNIVERSES["state"]
    fig, ax = plt.subplots(figsize=(8, 4))
    for term, curve in MEMBERSHIPS["state"].items():
        ax.plot(x, curve, color=COLORS[term], alpha=0.4, linestyle="--", label=f"{TERM_LABELS['state'][term]} (исходная)")
    for rule in RULES:
        if result.activations[rule.code] > 0:
            ax.plot(x, result.clipped[rule.code], color=COLORS[rule.output], alpha=0.14, linewidth=1)
    ax.fill_between(x, 0, result.aggregated, color="#36a98f", alpha=0.3, label="Агрегация (max)")
    ax.plot(x, result.aggregated, color="#168f79", linewidth=2)
    ax.axvline(result.score, color="#ad3d87", linewidth=2, label=f"Центроид: {result.score:.2f}")
    ax.set(xlim=(0, 100), ylim=(-0.03, 1.08), xlabel="Оценка состояния сети (0–100)", ylabel="Принадлежность μ", title="Обрезка → агрегация → центроид")
    ax.grid(alpha=0.2)
    ax.legend(fontsize=8)
    fig.tight_layout()
    return fig
