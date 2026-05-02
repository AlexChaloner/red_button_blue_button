"""Watts-Strogatz rescue contagion: a person flips to blue when rescue_pressure from neighbors exceeds their rescue_threshold."""
import numpy as np
import networkx as nx


def build(n, k, rewire_p, initial_blue, rescue_threshold, rescue_threshold_std=0.0, tiers=None, stubborn_red=0.0, seed=None):
    """Build a population graph with optional weighted ties and stubborn-red subpopulation.

    rescue_threshold_std: per-person heterogeneity (Normal around rescue_threshold, clipped at 0).
    tiers: list of (fraction, weight). None = uniform weights.
    stubborn_red: fraction of people who never flip from red.
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

    p_switch = 1.0 - initial_blue - stubborn_red
    roles = rng.choice(3, size=n, p=[initial_blue, stubborn_red, p_switch])
    presses = (roles == 0).astype(np.int8)
    stubborn = roles == 1
    thresholds = rng.normal(rescue_threshold, rescue_threshold_std, size=n).astype(np.float32)
    np.maximum(thresholds, 0.0, out=thresholds)
    thresholds[stubborn] = np.inf
    return graph, adj, presses, thresholds, stubborn


def run(adj, presses, thresholds, max_iters=200):
    history = [presses.copy()]
    for _ in range(max_iters):
        rescue_pressure = adj @ presses.astype(np.float32)
        flipped = (rescue_pressure > thresholds) & (presses == 0)
        if not flipped.any():
            break
        presses = np.where(flipped, np.int8(1), presses)
        history.append(presses.copy())
    return history


def run_many(n_seeds, build_kwargs, max_iters=200):
    """Run the simulation across n_seeds different seeds. Returns (finals, timelines)."""
    finals = []
    timelines = []
    for seed in range(n_seeds):
        _, adj, presses, thresholds, _ = build(**{**build_kwargs, "seed": seed})
        history = run(adj, presses, thresholds, max_iters=max_iters)
        timeline = [float(h.mean()) for h in history]
        finals.append(timeline[-1])
        timelines.append(timeline)
    max_len = max(len(t) for t in timelines)
    padded = np.array([t + [t[-1]] * (max_len - len(t)) for t in timelines])
    return np.array(finals), padded
