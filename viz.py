"""Snapshot-grid and timeline plots for the rescue-contagion simulation."""
from pathlib import Path

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

DPI = 300

RED = "#ef4444"
BLUE = "#3b82f6"


def _graph_style(graph):
    if nx.is_weighted(graph):
        pos = nx.spring_layout(graph, weight="weight", iterations=200, seed=42)
        edge_widths = [graph[u][v]["weight"] * 1.8 for u, v in graph.edges()]
        edge_colors = [(0.25, 0.25, 0.25, graph[u][v]["weight"]) for u, v in graph.edges()]
    else:
        pos = nx.spring_layout(graph, iterations=200, seed=42)
        edge_widths = 0.5
        edge_colors = "#d1d5db"
    return pos, edge_widths, edge_colors


def visualize(graph, history, path, max_panels=6):
    n_total = len(history)
    if n_total <= max_panels:
        indices = list(range(n_total))
    else:
        indices = [round(i * (n_total - 1) / (max_panels - 1)) for i in range(max_panels)]
    n = len(indices)
    fig, axes = plt.subplots(1, n, figsize=(4.2 * n, 4.2), squeeze=False)
    axes = axes.flatten()
    pos, edge_widths, edge_colors = _graph_style(graph)
    for ax, idx in zip(axes, indices):
        presses = history[idx]
        colors = [BLUE if p else RED for p in presses]
        nx.draw(graph, pos=pos, node_color=colors, ax=ax,
                node_size=80, edge_color=edge_colors, width=edge_widths)
        ax.set_title(f"t={idx}   {presses.mean():.0%} blue")

    plt.tight_layout()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, dpi=DPI, bbox_inches="tight")
    print(f"Saved {path}")


def animate(graph, history, path, fps=2, hold_frames=2):
    """Render the cascade as an animated GIF, with a brief hold at start/end."""
    frames = [history[0]] * hold_frames + list(history) + [history[-1]] * (hold_frames + 1)
    n_orig = len(history)
    pos, edge_widths, edge_colors = _graph_style(graph)
    fig, ax = plt.subplots(figsize=(8, 8))

    def render(i):
        ax.clear()
        presses = frames[i]
        colors = [BLUE if p else RED for p in presses]
        nx.draw(graph, pos=pos, node_color=colors, ax=ax,
                node_size=140, edge_color=edge_colors, width=edge_widths)
        t = max(0, min(n_orig - 1, i - hold_frames))
        ax.set_title(f"t={t}   {presses.mean():.0%} blue", fontsize=16)

    anim = animation.FuncAnimation(fig, render, frames=len(frames), interval=1000 / fps)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    anim.save(path, writer="pillow", fps=fps, dpi=150)
    plt.close(fig)
    print(f"Saved {path}")


def plot_timeline(history, path):
    fractions = [h.mean() for h in history]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(fractions, marker="o", color=BLUE, linewidth=2)
    ax.axhline(0.5, linestyle="--", color="gray", alpha=0.5, label="50% saved threshold")
    ax.set_xlabel("iteration")
    ax.set_ylabel("fraction pressing blue")
    ax.set_ylim(0, 1.02)
    ax.set_xlim(left=0)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, dpi=DPI, bbox_inches="tight")
    print(f"Saved {path}")


def plot_band(timelines, path):
    """Mean ± std band of fraction-blue across many seeds."""
    mean = timelines.mean(axis=0)
    std = timelines.std(axis=0)
    iters = np.arange(len(mean))
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.fill_between(iters, mean - std, mean + std, color=BLUE, alpha=0.2, label="± 1 std")
    ax.plot(iters, mean, color=BLUE, linewidth=2, label="mean")
    ax.axhline(0.5, linestyle="--", color="gray", alpha=0.5, label="50% saved threshold")
    ax.set_xlabel("iteration")
    ax.set_ylabel("fraction pressing blue")
    ax.set_ylim(0, 1.02)
    ax.set_xlim(left=0)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, dpi=DPI, bbox_inches="tight")
    print(f"Saved {path}")


def plot_sweep_1d(x, mean, std, path, xlabel):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.fill_between(x, mean - std, mean + std, color=BLUE, alpha=0.2, label="± 1 std")
    ax.plot(x, mean, color=BLUE, linewidth=2, marker="o", label="mean")
    ax.axhline(0.5, linestyle="--", color="gray", alpha=0.5, label="50% saved threshold")
    ax.axhline(0.58, linestyle=":", color="black", alpha=0.6, label="empirical ~58%")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("final fraction blue")
    ax.set_ylim(0, 1.02)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, dpi=DPI, bbox_inches="tight")
    print(f"Saved {path}")


def plot_heatmap(xs, ys, grid, path, xlabel, ylabel):
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(
        grid.T, origin="lower", aspect="auto",
        extent=[xs[0], xs[-1], ys[0], ys[-1]],
        cmap="RdBu", vmin=0, vmax=1,
    )
    cb = plt.colorbar(im, ax=ax)
    cb.set_label("mean final fraction blue")
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    cs = ax.contour(X, Y, grid, levels=[0.5, 0.58], colors=["gray", "black"], linewidths=1.5)
    ax.clabel(cs, inline=True, fontsize=9, fmt="%.2f")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.tight_layout()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, dpi=DPI, bbox_inches="tight")
    print(f"Saved {path}")


def plot_distribution(finals, path):
    """Histogram of final blue fractions across seeds."""
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(finals, bins=20, color=BLUE, alpha=0.7, edgecolor="white")
    ax.axvline(finals.mean(), color="black", linestyle="--", label=f"mean = {finals.mean():.1%}")
    ax.axvline(0.5, color="gray", linestyle=":", alpha=0.5, label="50% saved threshold")
    ax.set_xlabel("final fraction blue")
    ax.set_ylabel("number of seeds")
    ax.set_xlim(0, 1)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, dpi=DPI, bbox_inches="tight")
    print(f"Saved {path}")
