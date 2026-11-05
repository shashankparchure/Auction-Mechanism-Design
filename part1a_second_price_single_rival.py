"""Part 1A: second-price auction payoff curves with one rival bidder."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from auction_core import BIDS, RIVAL_STRATEGIES, VALUES, sample_rival_bids, second_price_utility_curve
from experiment_io import result_dir, write_csv


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=100_000, help="auctions sampled for each value/strategy pair")
    parser.add_argument("--seed", type=int, default=7, help="random seed")
    parser.add_argument("--out-dir", type=Path, default=result_dir("part1a"), help="where CSV and plots are written")
    args = parser.parse_args()
    if args.trials < 1:
        parser.error("--trials must be positive")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    rows: list[dict[str, object]] = []
    curves: dict[tuple[float, str], np.ndarray] = {}
    for value in VALUES:
        for strategy in RIVAL_STRATEGIES:
            rival_bids = sample_rival_bids(rng, args.trials, 1, strategy)
            utilities = second_price_utility_curve(value, BIDS, rival_bids)
            curves[(value, strategy)] = utilities
            for bid, utility in zip(BIDS, utilities):
                rows.append({"value": value, "rival_strategy": strategy, "bid": bid, "mean_utility": utility})

            fig, ax = plt.subplots(figsize=(7.2, 4.5), constrained_layout=True)
            ax.plot(BIDS, utilities, color="#176B87", linewidth=2.5, label="estimated mean utility")
            ax.axvline(value, color="#D97706", linestyle="--", linewidth=1.8, label=f"truthful bid v={value:.1f}")
            ax.set(title=f"One rival: v={value:.1f}, rival bids {strategy}", xlabel="Bidder 1 bid", ylabel="Average utility")
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
    print(f"Part 1A complete: {args.trials:,} auctions per value/strategy; outputs: {args.out_dir}")


if __name__ == "__main__":
    main()
