"""Snapshot-grid and timeline plots for the rescue-contagion simulation."""
from pathlib import Path

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

DPI = 300

plt.rcParams.update({
    "axes.labelsize": 14,
    "axes.titlesize": 14,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "legend.fontsize": 12,
})

RED = "#ef4444"
BLUE = "#3b82f6"
UNDECIDED = "#e5e7eb"


def _node_colors(state):
    return [BLUE if s == 1 else (RED if s == -1 else UNDECIDED) for s in state]


def _label(state):
    blue = (state == 1).mean()
    red = (state == -1).mean()
    return f"{blue:.0%} blue / {red:.0%} red"


def _layout(graph):
    weight = "weight" if nx.is_weighted(graph) else None
    return nx.spring_layout(graph, weight=weight, iterations=200, seed=42)


def _draw_edges(graph, pos, ax):
    """Draw weak ties first, strong ties on top — strong ones pop visually."""
    if nx.is_weighted(graph):
        edges = list(graph.edges())
        weights = np.array([graph[u][v]["weight"] for u, v in edges])
        for w in sorted(np.unique(weights)):
            sub = [e for e, ew in zip(edges, weights) if ew == w]
            shade = 1.0 - 0.45 * w
            color = (shade, shade, shade)
            width = 0.3 + 0.8 * w
            nx.draw_networkx_edges(graph, pos, edgelist=sub, ax=ax,
                                   edge_color=[color], width=width)
    else:
        nx.draw_networkx_edges(graph, pos, ax=ax, edge_color="#d1d5db", width=0.7)


def _draw(graph, pos, state, ax, node_size):
    _draw_edges(graph, pos, ax)
    nx.draw_networkx_nodes(graph, pos, node_color=_node_colors(state), ax=ax,
                           node_size=node_size, edgecolors="#6b7280", linewidths=0.5)
    ax.set_axis_off()


def visualize(graph, history, path, max_panels=6):
    n_total = len(history)
    if n_total <= max_panels:
        indices = list(range(n_total))
    else:
        indices = [round(i * (n_total - 1) / (max_panels - 1)) for i in range(max_panels)]
    n = len(indices)
    fig, axes = plt.subplots(1, n, figsize=(4.2 * n, 4.2), squeeze=False)
    axes = axes.flatten()
    pos = _layout(graph)
    for ax, idx in zip(axes, indices):
        state = history[idx]
        _draw(graph, pos, state, ax, node_size=80)
        ax.set_title(f"t={idx}   {_label(state)}")

    plt.tight_layout()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, dpi=DPI, bbox_inches="tight")
    print(f"Saved {path}")


def animate(graph, history, path, fps=2, hold_frames=2):
    """Render the cascade as an animated GIF, with a brief hold at start/end."""
    frames = [history[0]] * hold_frames + list(history) + [history[-1]] * (hold_frames + 1)
    n_orig = len(history)
    pos = _layout(graph)
    fig, ax = plt.subplots(figsize=(8, 8))

    def render(i):
        ax.clear()
        state = frames[i]
        _draw(graph, pos, state, ax, node_size=140)
        t = max(0, min(n_orig - 1, i - hold_frames))
        ax.set_title(f"t={t}   {_label(state)}", fontsize=16)

    anim = animation.FuncAnimation(fig, render, frames=len(frames), interval=1000 / fps)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    anim.save(path, writer="pillow", fps=fps, dpi=150)
    plt.close(fig)
    print(f"Saved {path}")


def plot_timeline(history, path):
    blue = [(h == 1).mean() for h in history]
    red = [(h == -1).mean() for h in history]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(blue, marker="o", color=BLUE, linewidth=2, label="blue")
    ax.plot(red, marker="o", color=RED, linewidth=2, label="red")
    ax.axhline(0.5, linestyle="--", color="gray", alpha=0.5)
    ax.set_xlabel("iteration")
    ax.set_ylabel("fraction of population")
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
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    pcm = ax.pcolormesh(X, Y, grid, cmap="RdBu", vmin=0, vmax=1, shading="nearest")
    cb = plt.colorbar(pcm, ax=ax)
    cb.set_label("mean final fraction blue", fontsize=13)
    cs = ax.contour(X, Y, grid, levels=[0.5, 0.58], colors=["gray", "black"], linewidths=1.5)
    ax.clabel(cs, inline=True, fontsize=11, fmt="%.2f")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.tight_layout()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, dpi=DPI, bbox_inches="tight")
    print(f"Saved {path}")


def plot_heatmap_grid(xs, ys, grids, slice_values, path, xlabel, ylabel, slice_label):
    """Render a 3D sweep as a 2x2 grid of 2D heatmaps, one per slice value, sharing one colorbar."""
    n = len(grids)
    nrows = (n + 1) // 2
    ncols = 2 if n > 1 else 1
    fig, axes = plt.subplots(nrows, ncols, figsize=(6 * ncols, 5 * nrows),
                             squeeze=False, constrained_layout=True)
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    pcm = None
    flat = axes.flatten()
    for i, (grid, sv) in enumerate(zip(grids, slice_values)):
        ax = flat[i]
        pcm = ax.pcolormesh(X, Y, grid, cmap="RdBu", vmin=0, vmax=1, shading="nearest")
        cs = ax.contour(X, Y, grid, levels=[0.5, 0.58], colors=["gray", "black"], linewidths=1.2)
        ax.clabel(cs, inline=True, fontsize=10, fmt="%.2f")
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(f"{slice_label} = {sv:.2f}")
    for j in range(n, len(flat)):
        flat[j].axis("off")
    cb = fig.colorbar(pcm, ax=axes.ravel().tolist(), shrink=0.85, pad=0.02)
    cb.set_label("mean final fraction blue", fontsize=13)
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
