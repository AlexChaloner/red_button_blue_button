"""Parameter sweeps: how robust is the 57% result across realistic parameter ranges?"""
import numpy as np

from simulation import run_many
from viz import plot_sweep_1d, plot_heatmap
from main_weighted import TIERS

BASE = dict(
    n=1000,
    k=6,
    rewire_p=0.1,
    rescue_threshold=1.0,
    rescue_threshold_std=0.3,
    tiers=TIERS,
)
SEEDS_PER_POINT = 20


def sweep_committed():
    xs = np.linspace(0.05, 0.30, 11)
    means = np.zeros(len(xs))
    stds = np.zeros(len(xs))
    for i, c in enumerate(xs):
        finals, _ = run_many(SEEDS_PER_POINT, dict(BASE, initial_blue=float(c), stubborn_red=float(c)))
        means[i], stds[i] = finals.mean(), finals.std()
    plot_sweep_1d(xs, means, stds, "sweep_committed.png", xlabel="initial_blue = stubborn_red")
    return xs, means


def sweep_2d():
    xs = np.linspace(0.05, 0.30, 8)
    ys = np.linspace(0.05, 0.30, 8)
    grid = np.zeros((len(xs), len(ys)))
    for i, b in enumerate(xs):
        for j, s in enumerate(ys):
            finals, _ = run_many(SEEDS_PER_POINT, dict(BASE, initial_blue=float(b), stubborn_red=float(s)))
            grid[i, j] = finals.mean()
    plot_heatmap(xs, ys, grid, "sweep_heatmap.png", xlabel="initial_blue", ylabel="stubborn_red")
    return grid


def main():
    print("Sweep 1: symmetric committed fraction")
    xs, means = sweep_committed()
    for x, m in zip(xs, means):
        print(f"  committed={x:.2f}  ->  final blue = {m:.1%}")

    print("\nSweep 2: 2D (initial_blue, stubborn_red)")
    grid = sweep_2d()
    print(f"  grid mean: {grid.mean():.1%}, range: {grid.min():.1%} to {grid.max():.1%}")


if __name__ == "__main__":
    main()
