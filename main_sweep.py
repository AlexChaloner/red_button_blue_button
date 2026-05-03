"""Parameter sweeps: how robust is the 57% result across realistic parameter ranges?"""
import numpy as np

from simulation import run_many
from viz import plot_heatmap, plot_heatmap_grid, plot_sweep_1d
from main_weighted import TIERS

BASE = dict(
    n=1000,
    k=6,
    rewire_p=0.1,
    rescue_threshold=1.0,
    rescue_threshold_std=0.3,
    tiers=TIERS,
    initial_blue=0.15,
    stubborn_red=0.15,
)
SEEDS_PER_POINT = 20


def make_tiers(family_fraction):
    """Two-tier ties: a strong-tie share + a weak-tie remainder."""
    return [
        (family_fraction, 1.0),
        (1.0 - family_fraction, 0.5),
    ]


def _sweep_1d(xs, build_kwargs_fn, path, xlabel):
    means = np.zeros(len(xs))
    stds = np.zeros(len(xs))
    for i, x in enumerate(xs):
        finals, _ = run_many(SEEDS_PER_POINT, build_kwargs_fn(float(x)))
        means[i], stds[i] = finals.mean(), finals.std()
    plot_sweep_1d(xs, means, stds, path, xlabel=xlabel)
    return means


def sweep_committed():
    xs = np.linspace(0.05, 0.30, 11)
    return xs, _sweep_1d(
        xs,
        lambda c: dict(BASE, initial_blue=c, stubborn_red=c),
        "sweep_pics/sweep_committed.png",
        xlabel="initial_blue = stubborn_red",
    )


def sweep_threshold():
    xs = np.linspace(0.4, 2.0, 9)
    return xs, _sweep_1d(
        xs,
        lambda t: dict(BASE, rescue_threshold=t),
        "sweep_pics/sweep_threshold.png",
        xlabel="rescue_threshold",
    )


def sweep_family_fraction():
    xs = np.linspace(0.10, 0.40, 7)
    return xs, _sweep_1d(
        xs,
        lambda ff: dict(BASE, tiers=make_tiers(ff)),
        "sweep_pics/sweep_family_fraction.png",
        xlabel="fraction of ties that are family-tier",
    )


def _sweep_2d(xs, ys, build_kwargs_fn):
    grid = np.zeros((len(xs), len(ys)))
    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            finals, _ = run_many(SEEDS_PER_POINT, build_kwargs_fn(float(x), float(y)))
            grid[i, j] = finals.mean()
    return grid


THRESHOLD_AXIS = np.round(np.arange(0.4, 2.001, 0.1), 4)        # step 0.1, 17 points
STRONG_AXIS = np.round(np.arange(0.10, 0.7001, 0.05), 4)        # step 0.05, 13 points
COMMITTED_AXIS = np.round(np.arange(0.05, 0.3001, 0.025), 4)    # step 0.025, 11 points


def sweep_threshold_family():
    xs, ys = THRESHOLD_AXIS, STRONG_AXIS
    grid = _sweep_2d(xs, ys, lambda t, f: dict(BASE, rescue_threshold=t, tiers=make_tiers(f)))
    plot_heatmap(xs, ys, grid, "sweep_pics/sweep_threshold_family.png",
                 xlabel="rescue_threshold", ylabel="strong-tie fraction")
    return grid


def sweep_threshold_committed():
    xs, ys = THRESHOLD_AXIS, COMMITTED_AXIS
    grid = _sweep_2d(xs, ys, lambda t, c: dict(BASE, rescue_threshold=t, initial_blue=c, stubborn_red=c))
    plot_heatmap(xs, ys, grid, "sweep_pics/sweep_threshold_committed.png",
                 xlabel="rescue_threshold", ylabel="committed (each side)")
    return grid


def sweep_family_committed():
    xs, ys = STRONG_AXIS, COMMITTED_AXIS
    grid = _sweep_2d(xs, ys, lambda f, c: dict(BASE, tiers=make_tiers(f), initial_blue=c, stubborn_red=c))
    plot_heatmap(xs, ys, grid, "sweep_pics/sweep_family_committed.png",
                 xlabel="strong-tie fraction", ylabel="committed (each side)")
    return grid


def sweep_3d():
    """3D sweep (threshold × strong-tie × committed) shown as slices at fixed committed levels."""
    xs, ys = THRESHOLD_AXIS, STRONG_AXIS
    slices = np.array([0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45])
    grids = np.stack([
        _sweep_2d(xs, ys,
                  lambda t, f, c=c: dict(BASE, rescue_threshold=t, tiers=make_tiers(f), initial_blue=c, stubborn_red=c))
        for c in slices
    ])
    plot_heatmap_grid(xs, ys, grids, slices, "sweep_pics/sweep_3d.png",
                      xlabel="rescue_threshold", ylabel="strong-tie fraction",
                      slice_label="committed")
    return grids


def _print_sweep(name, xs, means):
    print(f"\nSweep: {name}")
    for x, m in zip(xs, means):
        print(f"  {x:.2f}  ->  final blue = {m:.1%}")


def _print_2d(name, grid):
    print(f"\nSweep 2D: {name}")
    print(f"  grid mean: {grid.mean():.1%}, range: {grid.min():.1%} to {grid.max():.1%}")


def main():
    _print_sweep("symmetric committed fraction", *sweep_committed())
    _print_sweep("rescue_threshold", *sweep_threshold())
    _print_sweep("family fraction", *sweep_family_fraction())

    _print_2d("threshold × strong-tie", sweep_threshold_family())
    _print_2d("threshold × committed", sweep_threshold_committed())
    _print_2d("strong-tie × committed", sweep_family_committed())

    grids = sweep_3d()
    print(f"\nSweep 3D (threshold × strong-tie × committed):")
    print(f"  cube mean: {grids.mean():.1%}, range: {grids.min():.1%} to {grids.max():.1%}")


if __name__ == "__main__":
    main()
