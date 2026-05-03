"""Weighted-edge variant with stubborn-red population."""
from simulation import build, run
from viz import animate, plot_timeline, visualize

TIERS = [
    (0.4, 1.0),   # strong ties (family / close friends)
    (0.6, 0.5),   # weaker ties (friends / acquaintances)
]


def main():
    committed = 0.30
    graph, adj, state, thresholds, stubborn = build(
        n=100,
        k=6,
        rewire_p=0.1,
        initial_blue=committed,
        rescue_threshold=1.0,
        rescue_threshold_std=0.3,
        tiers=TIERS,
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
    visualize(graph, history, "sim_pics/simulation_weighted.png")
    plot_timeline(history, "sim_pics/timeline_weighted.png")
    animate(graph, history, "sim_pics/simulation_weighted.gif")


if __name__ == "__main__":
    main()
