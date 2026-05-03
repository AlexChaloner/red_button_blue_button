"""Unweighted edges + stubborn-red population: blue cascade meets firewalls."""
from simulation import build, run
from viz import animate, plot_timeline, visualize


def main():
    committed = 0.30
    graph, adj, state, thresholds, stubborn = build(
        n=100,
        k=6,
        rewire_p=0.1,
        initial_blue=committed,
        rescue_threshold=1.5,
        rescue_threshold_std=0.3,
        stubborn_red=committed,
        seed=42,
    )
    history = run(adj, state, thresholds)
    final = history[-1]
    print(f"Committed blue: {(history[0] == 1).mean():.1%}")
    print(f"Committed red:  {stubborn.mean():.1%}")
    print(f"Final blue:     {(final == 1).mean():.1%}")
    print(f"Final red:      {(final == -1).mean():.1%}")
    print(f"Iterations:     {len(history) - 1}")
    visualize(graph, history, "sim_pics/simulation_stubborn.png")
    plot_timeline(history, "sim_pics/timeline_stubborn.png")
    animate(graph, history, "sim_pics/simulation_stubborn.gif")


if __name__ == "__main__":
    main()
