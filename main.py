"""Run the small (visualisable) red/blue button simulation."""
import matplotlib.pyplot as plt
import networkx as nx

from simulation import build, run

RED = "#ef4444"
BLUE = "#3b82f6"


def visualize(graph, history, path="simulation.png"):
    n = len(history)
    cols = min(n, 6)
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(4.2 * cols, 4.2 * rows), squeeze=False)
    axes = axes.flatten()
    pos = nx.spring_layout(graph, iterations=200, seed=42)
    for i, (ax, presses) in enumerate(zip(axes, history)):
        colors = [BLUE if p else RED for p in presses]
        nx.draw(graph, pos=pos, node_color=colors, ax=ax,
                node_size=80, edge_color="#d1d5db", width=0.5)
        ax.set_title(f"t={i}   {presses.mean():.0%} blue")
    for ax in axes[n:]:
        ax.axis("off")
    fig.suptitle("Red / Blue button - blue spreads via rescue contagion", y=1.02)
    plt.tight_layout()
    plt.savefig(path, dpi=120, bbox_inches="tight")
    print(f"Saved {path}")


def main():
    graph, adj, presses, thresholds = build(
        n=100,
        k=6,
        rewire_p=0.1,
        initial_blue=0.15,
        rescue_threshold=1.5,
        seed=42,
    )
    history = run(adj, presses, thresholds)
    print(f"Initial blue: {history[0].mean():.1%}")
    print(f"Final blue:   {history[-1].mean():.1%}")
    print(f"Iterations:   {len(history) - 1}")
    visualize(graph, history)


if __name__ == "__main__":
    main()
