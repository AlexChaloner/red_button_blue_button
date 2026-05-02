"""Weighted-edge variant: family/friend/acquaintance ties contribute differently to the rescue sum."""
import matplotlib.pyplot as plt
import networkx as nx

from simulation import build_weighted, run

RED = "#ef4444"
DARK_RED = "#7f1d1d"
BLUE = "#3b82f6"

TIERS = [
    (0.2, 1.0),   # family
    (0.3, 0.5),   # close friends
    (0.5, 0.25),  # acquaintances
]


def visualize(graph, history, stubborn, path="simulation_weighted.png", max_panels=6):
    n_total = len(history)
    if n_total <= max_panels:
        indices = list(range(n_total))
    else:
        indices = [round(i * (n_total - 1) / (max_panels - 1)) for i in range(max_panels)]
    n = len(indices)
    fig, axes = plt.subplots(1, n, figsize=(4.2 * n, 4.2), squeeze=False)
    axes = axes.flatten()
    pos = nx.kamada_kawai_layout(graph)
    edge_widths = [graph[u][v]["weight"] * 1.8 for u, v in graph.edges()]
    edge_colors = [(0.25, 0.25, 0.25, graph[u][v]["weight"]) for u, v in graph.edges()]
    for ax, idx in zip(axes, indices):
        presses = history[idx]
        colors = [BLUE if p else (DARK_RED if s else RED) for p, s in zip(presses, stubborn)]
        nx.draw(graph, pos=pos, node_color=colors, ax=ax,
                node_size=80, edge_color=edge_colors, width=edge_widths)
        ax.set_title(f"t={idx}   {presses.mean():.0%} blue")
    fig.suptitle("Dark red = stubborn (never flips). Edge thickness = tie strength.", y=1.02)
    plt.tight_layout()
    plt.savefig(path, dpi=120, bbox_inches="tight")
    print(f"Saved {path}")


def plot_timeline(history, path="timeline_weighted.png"):
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


def main():
    committed = 0.15
    graph, adj, presses, thresholds, stubborn = build_weighted(
        n=100,
        k=6,
        rewire_p=0.1,
        initial_blue=committed,
        rescue_threshold=1.0,
        tiers=TIERS,
        stubborn_red=committed,
        seed=42,
    )
    history = run(adj, presses, thresholds)
    print(f"Initial blue:  {history[0].mean():.1%}")
    print(f"Stubborn red:  {stubborn.mean():.1%}")
    print(f"Final blue:    {history[-1].mean():.1%}")
    print(f"Iterations:    {len(history) - 1}")
    visualize(graph, history, stubborn)
    plot_timeline(history)


if __name__ == "__main__":
    main()
