"""Simple unweighted demo: blue cascades to total takeover."""
from simulation import build, run
from viz import visualize, plot_timeline


def main():
    graph, adj, presses, thresholds, stubborn = build(
        n=100,
        k=6,
        rewire_p=0.1,
        initial_blue=0.15,
        rescue_threshold=1.5,
        rescue_threshold_std=0.3,
        seed=42,
    )
    history = run(adj, presses, thresholds)
    print(f"Initial blue: {history[0].mean():.1%}")
    print(f"Final blue:   {history[-1].mean():.1%}")
    print(f"Iterations:   {len(history) - 1}")
    visualize(graph, history, "simulation.png")
    plot_timeline(history, "timeline.png")


if __name__ == "__main__":
    main()
