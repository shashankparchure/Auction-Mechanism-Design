"""Shared simulation and mechanism code for Assignment 4.

All auction experiments use independent private values from U[0, 1].  The
random-number generator is passed in by each driver so that runs are
reproducible from a user-selected seed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np


RIVAL_STRATEGIES = ("truthful", "half-value", "random-bid")
VALUES = (0.2, 0.5, 0.8)
BIDS = np.round(np.linspace(0.0, 1.0, 101), 2)

# Figure 7.3, Multiagent Systems: Algorithmic, Game-Theoretic, and Logical
# Foundations. Edges are directed from A toward F; the costs are private costs.
VCG_EDGES: dict[str, tuple[str, str, float]] = {
    "AB": ("A", "B", 3.0),
    "AC": ("A", "C", 2.0),
    "BD": ("B", "D", 2.0),
    "BE": ("B", "E", 1.0),
    "CE": ("C", "E", 3.0),
    "CF": ("C", "F", 5.0),
    "DF": ("D", "F", 2.0),
    "EF": ("E", "F", 1.0),
}


def sample_rival_bids(
    rng: np.random.Generator,
    trials: int,
    rival_count: int,
    strategy: str,
) -> np.ndarray:
    """Draw rival bids with shape (trials, rival_count)."""
    if strategy not in RIVAL_STRATEGIES:
        raise ValueError(f"unknown rival strategy: {strategy}")
    values = rng.uniform(0.0, 1.0, size=(trials, rival_count))
    if strategy == "truthful":
        return values
    if strategy == "half-value":
        return 0.5 * values
    return rng.uniform(0.0, 1.0, size=(trials, rival_count))


def second_price_utility_curve(
    value: float,
    bids: Iterable[float],
    rival_bids: np.ndarray,
) -> np.ndarray:
    """Estimate bidder 1's average utility for each tested bid.

    The object passed in may contain one or several rival bids per auction;
    in a second-price auction, the price paid by bidder 1 is the largest rival
    bid whenever bidder 1 wins.
    """
    strongest_rival = np.max(rival_bids, axis=1)
    tested = np.asarray(tuple(bids), dtype=float)
    utilities = value - strongest_rival[:, None]
    won = tested[None, :] >= strongest_rival[:, None]
    return np.mean(np.where(won, utilities, 0.0), axis=0)


def second_price_fixed_curve(
    value: float,
    rival_bid: float,
    bids: Iterable[float],
    rival_count: int = 1,
) -> np.ndarray:
    """Expected utility against identical fixed rival bids.

    Ties are split uniformly among the tied highest bidders.  In the
    two-rival extension, both rivals use the specified fixed bid.
    """
    tested = np.asarray(tuple(bids), dtype=float)
    result = np.zeros_like(tested)
    result[tested > rival_bid] = value - rival_bid
    tied = np.isclose(tested, rival_bid, atol=1e-12, rtol=0.0)
    result[tied] = (value - rival_bid) / (rival_count + 1)
    return result


def first_price_theory(value: float, n: int, k: float) -> tuple[float, float]:
    """Return (expected utility, win probability) against equilibrium rivals.

    Each of the n-1 rival values is uniform on [0, 1] and its equilibrium bid
    is ((n-1)/n) times value. Bidder 1's bid is k * value.
    """
    if n < 2:
        raise ValueError("n must be at least 2")
    alpha = (n - 1) / n
    bid = k * value
    if bid <= 0.0:
        win_probability = 0.0
    elif bid >= alpha:
        win_probability = 1.0
    else:
        win_probability = (bid / alpha) ** (n - 1)
    return (value - bid) * win_probability, win_probability


@dataclass(frozen=True)
class VCGOutcome:
    path: tuple[str, ...]
    reported_path_cost: float
    payments: dict[str, float]


def enumerate_paths(costs: dict[str, float]) -> list[tuple[tuple[str, ...], float]]:
    """Enumerate all A-to-F paths and their reported costs."""
    adjacency: dict[str, list[tuple[str, str]]] = {}
    for edge, (start, end, _) in VCG_EDGES.items():
        adjacency.setdefault(start, []).append((end, edge))

    paths: list[tuple[tuple[str, ...], float]] = []

    def visit(node: str, used: tuple[str, ...], visited_nodes: frozenset[str]) -> None:
        if node == "F":
            paths.append((used, sum(costs[edge] for edge in used)))
            return
        for next_node, edge in adjacency.get(node, []):
            if next_node not in visited_nodes:
                visit(next_node, used + (edge,), visited_nodes | {next_node})

    visit("A", (), frozenset({"A"}))
    return sorted(paths, key=lambda item: (round(item[1], 12), "".join(item[0])))


def vcg_outcome(reported_costs: dict[str, float]) -> VCGOutcome:
    """Choose the cheapest path and compute pivot payments to its edges."""
    paths = enumerate_paths(reported_costs)
    if not paths:
        raise ValueError("the graph contains no A-to-F path")
    chosen_path, chosen_cost = paths[0]
    payments = {edge: 0.0 for edge in VCG_EDGES}
    for edge in chosen_path:
        alternative_costs = [cost for path, cost in paths if edge not in path]
        if not alternative_costs:
            raise ValueError(f"removing {edge} disconnects A from F")
        # Other agents' reported cost on the chosen path excludes this edge.
        payments[edge] = min(alternative_costs) - (chosen_cost - reported_costs[edge])
    return VCGOutcome(chosen_path, chosen_cost, payments)


def truthful_vcg_costs() -> dict[str, float]:
    return {edge: data[2] for edge, data in VCG_EDGES.items()}


def edge_utility(edge: str, outcome: VCGOutcome, true_cost: float) -> float:
    if edge not in outcome.path:
        return 0.0
    return outcome.payments[edge] - true_cost

