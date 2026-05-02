"""Unweighted edges + stubborn-red population: blue cascade meets firewalls."""
from simulation import build, run
from viz import animate, plot_timeline, visualize


def main():
    committed = 0.15
    graph, adj, presses, thresholds, stubborn = build(
        n=100,
        k=6,
        rewire_p=0.1,
        initial_blue=committed,
        rescue_threshold=1.5,
        rescue_threshold_std=0.3,
        stubborn_red=committed,
        seed=42,
    )
    history = run(adj, presses, thresholds)
    print(f"Initial blue:  {history[0].mean():.1%}")
    print(f"Stubborn red:  {stubborn.mean():.1%}")
    print(f"Final blue:    {history[-1].mean():.1%}")
    print(f"Iterations:    {len(history) - 1}")
    visualize(graph, history, "simulation_stubborn.png")
    plot_timeline(history, "timeline_stubborn.png")
    animate(graph, history, "simulation_stubborn.gif")


if __name__ == "__main__":
    main()
