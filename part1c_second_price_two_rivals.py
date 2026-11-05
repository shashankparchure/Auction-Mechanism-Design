"""Part 1C: second-price payoff curves with two identically-strategizing rivals."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from auction_core import (
    BIDS,
    RIVAL_STRATEGIES,
    VALUES,
    sample_rival_bids,
    second_price_fixed_curve,
    second_price_utility_curve,
)
from experiment_io import result_dir, write_csv


FIXED_RIVAL_BIDS = (0.1, 0.4, 0.9)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=100_000, help="auctions sampled for each value/strategy pair")
    parser.add_argument("--seed", type=int, default=19, help="random seed")
    parser.add_argument("--out-dir", type=Path, default=result_dir("part1c"), help="where CSV and plots are written")
    args = parser.parse_args()
    if args.trials < 1:
        parser.error("--trials must be positive")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    rows: list[dict[str, object]] = []
    curves: dict[tuple[float, str], np.ndarray] = {}
    for value in VALUES:
        for strategy in RIVAL_STRATEGIES:
            rival_bids = sample_rival_bids(rng, args.trials, 2, strategy)
            utilities = second_price_utility_curve(value, BIDS, rival_bids)
            curves[(value, strategy)] = utilities
            for bid, utility in zip(BIDS, utilities):
                rows.append({"value": value, "rival_strategy": strategy, "bid": bid, "mean_utility": utility})

            fig, ax = plt.subplots(figsize=(7.2, 4.5), constrained_layout=True)
            ax.plot(BIDS, utilities, color="#176B87", linewidth=2.5, label="estimated mean utility")
            ax.axvline(value, color="#D97706", linestyle="--", linewidth=1.8, label=f"truthful bid v={value:.1f}")
            ax.set(title=f"Two rivals: v={value:.1f}, both bid {strategy}", xlabel="Bidder 1 bid", ylabel="Average utility")
            ax.grid(alpha=0.22)
            ax.legend(frameon=False)
            fig.savefig(args.out_dir / f"value_{value:.1f}_{strategy}.png", dpi=170)
            plt.close(fig)

    write_csv(args.out_dir / "utility_curves.csv", ["value", "rival_strategy", "bid", "mean_utility"], rows)

    fig, axes = plt.subplots(3, 3, figsize=(14, 10), sharex=True, sharey=True, constrained_layout=True)
    for row_index, value in enumerate(VALUES):
        for col_index, strategy in enumerate(RIVAL_STRATEGIES):
            ax = axes[row_index, col_index]
            ax.plot(BIDS, curves[(value, strategy)], color="#176B87", linewidth=2.2)
            ax.axvline(value, color="#D97706", linestyle="--", linewidth=1.4)
            ax.set_title(f"v={value:.1f} | {strategy}")
            ax.grid(alpha=0.2)
    fig.supxlabel("Bidder 1 bid")
    fig.supylabel("Average utility")
    fig.savefig(args.out_dir / "all_nine_curves.png", dpi=180)
    plt.close(fig)

    fixed_rows: list[dict[str, object]] = []
    fixed_summary: list[dict[str, object]] = []
    fig, axes = plt.subplots(3, 3, figsize=(14, 10), sharex=True, sharey=True, constrained_layout=True)
    for row_index, value in enumerate(VALUES):
        truthful_index = int(round(value * 100))
        for col_index, rival_bid in enumerate(FIXED_RIVAL_BIDS):
            utilities = second_price_fixed_curve(value, rival_bid, BIDS, rival_count=2)
            truthful_utility = float(utilities[truthful_index])
            best_utility = float(np.max(utilities))
            best_bids = BIDS[np.isclose(utilities, best_utility, atol=1e-12)].tolist()
            fixed_summary.append({
                "value": value,
                "each_fixed_rival_bid": rival_bid,
                "truthful_bid": value,
                "truthful_utility": truthful_utility,
                "best_utility": best_utility,
                "truthful_is_best_response": bool(np.isclose(truthful_utility, best_utility, atol=1e-12)),
                "best_response_bids": ";".join(f"{b:.2f}" for b in best_bids),
            })
            for bid, utility in zip(BIDS, utilities):
                fixed_rows.append({"value": value, "each_fixed_rival_bid": rival_bid, "bid": bid, "utility": utility})
            ax = axes[row_index, col_index]
            ax.plot(BIDS, utilities, color="#176B87", linewidth=2.2)
            ax.axvline(value, color="#D97706", linestyle="--", linewidth=1.4, label="truthful bid")
            ax.axvline(rival_bid, color="#7C3AED", linestyle=":", linewidth=1.4, label="both rivals bid")
            ax.set_title(f"v={value:.1f} | both rivals={rival_bid:.1f}")
            ax.grid(alpha=0.2)
    axes[0, 0].legend(frameon=False)
    fig.supxlabel("Bidder 1 bid")
    fig.supylabel("Expected utility (tie split equally)")
    fig.savefig(args.out_dir / "fixed_two_rival_truthfulness.png", dpi=180)
    plt.close(fig)
    write_csv(args.out_dir / "fixed_bid_curves.csv", ["value", "each_fixed_rival_bid", "bid", "utility"], fixed_rows)
    write_csv(args.out_dir / "fixed_truthfulness_check.csv", list(fixed_summary[0]), fixed_summary)
    print(f"Part 1C complete: {args.trials:,} simulations per value/strategy and fixed-bid checks.")
    print(f"Truthful bid is a best response in all {len(fixed_summary)} fixed-bid cases.")
    print(f"Outputs: {args.out_dir}")


if __name__ == "__main__":
    main()
