"""Part 2: first-price deviations from the symmetric equilibrium bid."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from auction_core import first_price_theory
from experiment_io import result_dir, write_csv


K_GRID = np.round(np.arange(0.1, 2.0 + 1e-9, 0.1), 2)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=200_000, help="auctions sampled for each n")
    parser.add_argument("--value", type=float, default=0.5, help="fixed true value of bidder 1 in [0, 1]")
    parser.add_argument("--seed", type=int, default=31, help="random seed")
    parser.add_argument("--out-dir", type=Path, default=result_dir("part2"), help="where CSV and plots are written")
    parser.add_argument("--margin-tolerance", type=float, default=1e-12, help="numerical tie tolerance for the paid-less metric")
    parser.add_argument("--bid-increment", type=float, default=0.01,
                        help="smallest meaningful bid reduction for the could-pay-less metric")
    args = parser.parse_args()
    if args.trials < 1:
        parser.error("--trials must be positive")
    if not 0.0 <= args.value <= 1.0:
        parser.error("--value must be between 0 and 1")
    if args.margin_tolerance < 0.0:
        parser.error("--margin-tolerance cannot be negative")
    if args.bid_increment < 0.0:
        parser.error("--bid-increment cannot be negative")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    rows: list[dict[str, object]] = []
    results: dict[int, dict[str, list[float]]] = {}
    for n in (2, 3, 4):
        alpha = (n - 1) / n
        rival_values = rng.uniform(0.0, 1.0, size=(args.trials, n - 1))
        rival_bids = alpha * rival_values
        n_results = {"k": [], "empirical_utility": [], "theoretical_utility": [], "win_probability": [],
                     "fraction_winner_could_lower": [], "fraction_could_lower_by_increment": [],
                     "fraction_bidder1_could_lower_by_increment": [], "mean_winner_margin": []}
        # Add the exact equilibrium multiplier (2/3 and 0.75 are not on the 0.1 grid).
        k_grid = np.union1d(K_GRID, [alpha])
        for k in k_grid:
            focal_bid = float(k * args.value)
            bids = np.column_stack((np.full(args.trials, focal_bid), rival_bids))
            winner_indices = np.argmax(bids, axis=1)
            partitioned = np.partition(bids, -2, axis=1)
            winning_bid = partitioned[:, -1]
            runner_up_bid = partitioned[:, -2]
            margins = winning_bid - runner_up_bid
            focal_wins = winner_indices == 0
            utilities = np.where(focal_wins, args.value - focal_bid, 0.0)
            empirical_utility = float(np.mean(utilities))
            win_probability = float(np.mean(focal_wins))
            could_lower = margins > args.margin_tolerance
            fraction_could_lower = float(np.mean(could_lower))
            # The strict fraction is ~1 under continuous bids, so also require a full bid increment of slack.
            could_lower_tick = margins > args.bid_increment
            fraction_could_lower_tick = float(np.mean(could_lower_tick))
            fraction_bidder1_could_lower_tick = (
                float(np.mean(could_lower_tick[focal_wins])) if focal_wins.any() else float("nan"))
            mean_bidder1_overpayment = float(np.mean(margins[focal_wins])) if focal_wins.any() else float("nan")
            mean_margin = float(np.mean(margins))
            theory_utility, theory_win_probability = first_price_theory(args.value, n, float(k))
            row = {
                "n": n,
                "value": args.value,
                "k": float(k),
                "bid": focal_bid,
                "equilibrium_k": alpha,
                "equilibrium_bid": alpha * args.value,
                "empirical_expected_utility": empirical_utility,
                "theoretical_expected_utility": theory_utility,
                "empirical_win_probability": win_probability,
                "theoretical_win_probability": theory_win_probability,
                "fraction_auctions_winner_could_lower_bid": fraction_could_lower,
                "bid_increment": args.bid_increment,
                "fraction_winner_could_lower_by_increment": fraction_could_lower_tick,
                "fraction_bidder1_wins_could_lower_by_increment": fraction_bidder1_could_lower_tick,
                "mean_winner_bid_margin": mean_margin,
                "mean_bidder1_overpayment_when_winning": mean_bidder1_overpayment,
            }
            rows.append(row)
            n_results["k"].append(float(k))
            n_results["empirical_utility"].append(empirical_utility)
            n_results["theoretical_utility"].append(theory_utility)
            n_results["win_probability"].append(win_probability)
            n_results["fraction_winner_could_lower"].append(fraction_could_lower)
            n_results["fraction_could_lower_by_increment"].append(fraction_could_lower_tick)
            n_results["fraction_bidder1_could_lower_by_increment"].append(fraction_bidder1_could_lower_tick)
            n_results["mean_winner_margin"].append(mean_margin)
        results[n] = n_results

    fields = list(rows[0])
    write_csv(args.out_dir / "first_price_results.csv", fields, rows)

    palette = {2: "#176B87", 3: "#D97706", 4: "#7C3AED"}
    fig, axes = plt.subplots(2, 2, figsize=(13, 9), constrained_layout=True)
    for n, values in results.items():
        color = palette[n]
        alpha = (n - 1) / n
        axes[0, 0].plot(values["k"], values["empirical_utility"], marker="o", ms=3.4,
                        color=color, label=f"n={n} simulation")
        axes[0, 0].plot(values["k"], values["theoretical_utility"], linestyle="--", color=color, alpha=0.8)
        axes[0, 0].axvline(alpha, color=color, linestyle=":", alpha=0.55)
        axes[0, 1].plot(values["k"], values["win_probability"], marker="o", ms=3.4, color=color, label=f"n={n}")
        axes[1, 0].plot(values["k"], values["fraction_could_lower_by_increment"], marker="o", ms=3.4,
                        color=color, label=f"n={n} any winner")
        axes[1, 0].plot(values["k"], values["fraction_bidder1_could_lower_by_increment"], linestyle="--",
                        color=color, alpha=0.8, label=f"n={n} bidder 1 wins")
        axes[1, 1].plot(values["k"], values["mean_winner_margin"], marker="o", ms=3.4, color=color, label=f"n={n}")
    axes[0, 0].set_title("Bidder 1 expected utility")
    axes[0, 0].set_ylabel("Expected utility")
    axes[0, 0].legend(frameon=False, ncol=2)
    axes[0, 0].text(0.02, 0.02, "solid: Monte Carlo | dashed: exact expectation", transform=axes[0, 0].transAxes, fontsize=9)
    axes[0, 1].set_title("Bidder 1 win probability")
    axes[0, 1].set_ylabel("Win probability")
    axes[0, 1].legend(frameon=False)
    axes[1, 0].set_title(f"Winner could bid {args.bid_increment:g} less and still win")
    axes[1, 0].set_ylabel("Fraction of auctions")
    axes[1, 0].legend(frameon=False, ncol=2, fontsize=8)
    strict_min = min(min(values["fraction_winner_could_lower"]) for values in results.values())
    axes[1, 0].text(0.02, 0.02, f"strict (any positive margin): at least {strict_min:.3f} for every n, k",
                    transform=axes[1, 0].transAxes, fontsize=9)
    axes[1, 1].set_title("Average gap to runner-up bid")
    axes[1, 1].set_ylabel("Winning bid - runner-up bid")
    axes[1, 1].legend(frameon=False)
    for ax in axes.flat:
        ax.set_xlabel("Bid multiplier k (bid = k v)")
        ax.grid(alpha=0.2)
        ax.set_xlim(0.1, 2.0)
    fig.savefig(args.out_dir / "first_price_deviation_analysis.png", dpi=180)
    plt.close(fig)

    print(f"Part 2 complete: {args.trials:,} auctions for each n at bidder 1 value {args.value:.3f}.")
    print("The solid and dashed utility curves show Monte Carlo and exact expectations, respectively.")
    print(f"Outputs: {args.out_dir}")


if __name__ == "__main__":
    main()
