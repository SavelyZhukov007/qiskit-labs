"""Plotting helpers for qiskit-labs notebooks and reports."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit.visualization import plot_histogram


def plot_counts(
    counts: dict[str, int], title: str = "Measurement counts"
) -> plt.Figure:
    """Draw a histogram from a counts dictionary."""
    fig = plot_histogram(counts, title=title)
    if isinstance(fig, plt.Figure):
        return fig
    # plot_histogram may return a Figure or pyplot state depending on backend
    plt.title(title)
    return plt.gcf()


def save_circuit_image(
    circuit: QuantumCircuit,
    filename: str | Path,
    *,
    output: str = "mpl",
) -> Path:
    """Save a circuit diagram to ``images/`` or an explicit path."""
    path = Path(filename)
    if path.parent == Path("."):
        path = Path("images") / path
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = circuit.draw(output=output)
    if hasattr(fig, "savefig"):
        fig.savefig(path, bbox_inches="tight", dpi=150)
        plt.close(fig)
    else:
        raise TypeError("Circuit draw did not return a matplotlib figure")
    return path


def plot_qber(
    interception_rates: list[float],
    qber_values: list[float],
    *,
    title: str = "QBER vs interception rate",
) -> plt.Figure:
    """Plot QBER curve (for future Eve simulations)."""
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(interception_rates, qber_values, marker="o")
    ax.set_xlabel("Interception rate")
    ax.set_ylabel("QBER")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig
