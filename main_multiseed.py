"""Multi-seed averaging for the weighted+stubborn variant."""
from simulation import run_many
from viz import plot_band, plot_distribution
from main_weighted import TIERS


def report(label, finals):
    print(f"--- {label} ---")
    print(f"Final blue:   {finals.mean():.1%} ± {finals.std():.1%}")
    print(f"Range:        {finals.min():.1%} to {finals.max():.1%}")
    print(f"Crossed 50%:  {(finals > 0.5).mean():.0%} of seeds")


def main():
    base = dict(
        k=6,
        rewire_p=0.1,
        initial_blue=0.15,
        rescue_threshold=1.0,
        rescue_threshold_std=0.3,
        tiers=TIERS,
        stubborn_red=0.15,
    )

    finals_small, timelines_small = run_many(n_seeds=100, build_kwargs=dict(n=100, **base))
    report("n=100, 100 seeds", finals_small)
    plot_band(timelines_small, "band_weighted.png")
    plot_distribution(finals_small, "histogram_weighted.png")

    print()
    finals_big, _ = run_many(n_seeds=50, build_kwargs=dict(n=10000, **base))
    report("n=10000, 50 seeds", finals_big)


if __name__ == "__main__":
    main()
