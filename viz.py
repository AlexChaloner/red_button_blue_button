"""Snapshot-grid and timeline plots for the rescue-contagion simulation."""
import matplotlib.pyplot as plt
import networkx as nx

RED = "#ef4444"
BLUE = "#3b82f6"


def visualize(graph, history, path, max_panels=6):
    n_total = len(history)
    if n_total <= max_panels:
        indices = list(range(n_total))
    else:
        indices = [round(i * (n_total - 1) / (max_panels - 1)) for i in range(max_panels)]
    n = len(indices)
    fig, axes = plt.subplots(1, n, figsize=(4.2 * n, 4.2), squeeze=False)
    axes = axes.flatten()

    weighted = nx.is_weighted(graph)
    if weighted:
        pos = nx.spring_layout(graph, weight="weight", iterations=200, seed=42)
        edge_widths = [graph[u][v]["weight"] * 1.8 for u, v in graph.edges()]
        edge_colors = [(0.25, 0.25, 0.25, graph[u][v]["weight"]) for u, v in graph.edges()]
    else:
        pos = nx.spring_layout(graph, iterations=200, seed=42)
        edge_widths = 0.5
        edge_colors = "#d1d5db"

    for ax, idx in zip(axes, indices):
        presses = history[idx]
        colors = [BLUE if p else RED for p in presses]
        nx.draw(graph, pos=pos, node_color=colors, ax=ax,
                node_size=80, edge_color=edge_colors, width=edge_widths)
        ax.set_title(f"t={idx}   {presses.mean():.0%} blue")

    plt.tight_layout()
    plt.savefig(path, dpi=120, bbox_inches="tight")
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
    plt.savefig(path, dpi=120, bbox_inches="tight")
    print(f"Saved {path}")
