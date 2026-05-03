"""Watts-Strogatz contagion: undecided people pick up red or blue from neighbors via the same threshold rule.

State values: -1 = red, 0 = undecided, 1 = blue. Committed reds and blues never change.
"""
import numpy as np
import networkx as nx

RED, UNDECIDED, BLUE = -1, 0, 1


def build(n, k, rewire_p, initial_blue, rescue_threshold, rescue_threshold_std=0.0, tiers=None, stubborn_red=0.0, seed=None):
    """Build a population graph.

    initial_blue: fraction of committed blues (start blue, never flip).
    stubborn_red: fraction of committed reds (start red, never flip).
    Everyone else starts undecided and may flip to either colour once enough weighted neighbours agree.
    rescue_threshold_std: per-person heterogeneity (Normal, clipped at 0).
    tiers: list of (fraction, weight). None = uniform weights.
    """
    rng = np.random.default_rng(seed)
    graph = nx.watts_strogatz_graph(n, k, rewire_p, seed=seed)

    if tiers is None:
        adj = nx.to_scipy_sparse_array(graph, format="csr", dtype=np.float32)
    else:
        fractions = np.array([t[0] for t in tiers])
        weights = np.array([t[1] for t in tiers])
        edges = list(graph.edges())
        chosen = rng.choice(len(tiers), size=len(edges), p=fractions)
        for (u, v), idx in zip(edges, chosen):
            graph[u][v]["weight"] = float(weights[idx])
        adj = nx.to_scipy_sparse_array(graph, format="csr", dtype=np.float32, weight="weight")

    n_blue = round(initial_blue * n)
    n_red = round(stubborn_red * n)
    roles = np.full(n, 2, dtype=np.int8)
    chosen = rng.choice(n, size=n_blue + n_red, replace=False)
    roles[chosen[:n_blue]] = 0
    roles[chosen[n_blue:]] = 1
    state = np.zeros(n, dtype=np.int8)
    state[roles == 0] = BLUE
    state[roles == 1] = RED
    thresholds = rng.normal(rescue_threshold, rescue_threshold_std, size=n).astype(np.float32)
    np.maximum(thresholds, 0.0, out=thresholds)
    stubborn = roles == 1
    return graph, adj, state, thresholds, stubborn


def run(adj, state, thresholds, max_iters=200):
    """Asymmetric rule: a single blue tie vetoes any flip to red — captures the rescue intuition.

    Anyone still undecided at the end defaults to red (red is the no-action baseline).
    """
    history = [state.copy()]
    for _ in range(max_iters):
        blue_pressure = adj @ (state == BLUE).astype(np.float32)
        undecided = state == UNDECIDED
        flip_blue = undecided & (blue_pressure > thresholds)
        flip_red = undecided & (blue_pressure == 0)
        if not (flip_blue.any() or flip_red.any()):
            break
        state = state.copy()
        state[flip_blue] = BLUE
        state[flip_red] = RED
        history.append(state.copy())
    if (state == UNDECIDED).any():
        state = state.copy()
        state[state == UNDECIDED] = RED
        history.append(state)
    return history


def run_many(n_seeds, build_kwargs, max_iters=200):
    """Run across n_seeds seeds. Returns (final_blue_fraction, blue_timelines)."""
    finals = []
    timelines = []
    for seed in range(n_seeds):
        _, adj, state, thresholds, _ = build(**{**build_kwargs, "seed": seed})
        history = run(adj, state, thresholds, max_iters=max_iters)
        timeline = [float((h == BLUE).mean()) for h in history]
        finals.append(timeline[-1])
        timelines.append(timeline)
    max_len = max(len(t) for t in timelines)
    padded = np.array([t + [t[-1]] * (max_len - len(t)) for t in timelines])
    return np.array(finals), padded
