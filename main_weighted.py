"""Weighted-edge variant with stubborn-red population."""
from simulation import build, run
from viz import visualize, plot_timeline

TIERS = [
    (0.2, 1.0),   # family
    (0.3, 0.5),   # close friends
    (0.5, 0.25),  # acquaintances
]


def main():
    committed = 0.15
    graph, adj, presses, thresholds, stubborn = build(
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
    history = run(adj, presses, thresholds)
    print(f"Initial blue:  {history[0].mean():.1%}")
    print(f"Stubborn red:  {stubborn.mean():.1%}")
    print(f"Final blue:    {history[-1].mean():.1%}")
    print(f"Iterations:    {len(history) - 1}")
    visualize(graph, history, "readme_pics/simulation_weighted.png")
    plot_timeline(history, "timeline_weighted.png")


if __name__ == "__main__":
    main()
