"""Part 1B: best response to a fixed bid in a second-price auction."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from auction_core import BIDS, VALUES, second_price_fixed_curve
from experiment_io import result_dir, write_csv


FIXED_RIVAL_BIDS = (0.1, 0.4, 0.9)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, default=result_dir("part1b"), help="where CSV and plots are written")
    args = parser.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, object]] = []
    summary: list[dict[str, object]] = []
    fig, axes = plt.subplots(3, 3, figsize=(14, 10), sharex=True, sharey=True, constrained_layout=True)
    for row_index, value in enumerate(VALUES):
        truthful_index = int(round(value * 100))
        for col_index, rival_bid in enumerate(FIXED_RIVAL_BIDS):
            utilities = second_price_fixed_curve(value, rival_bid, BIDS)
            truthful_utility = float(utilities[truthful_index])
            best_utility = float(np.max(utilities))
            best_bids = BIDS[np.isclose(utilities, best_utility, atol=1e-12)].tolist()
            summary.append({
                "value": value,
                "fixed_rival_bid": rival_bid,
                "truthful_bid": value,
                "truthful_utility": truthful_utility,
                "best_utility": best_utility,
                "truthful_is_best_response": bool(np.isclose(truthful_utility, best_utility, atol=1e-12)),
                "best_response_bids": ";".join(f"{b:.2f}" for b in best_bids),
            })
            for bid, utility in zip(BIDS, utilities):
                rows.append({"value": value, "fixed_rival_bid": rival_bid, "bid": bid, "utility": utility})
            ax = axes[row_index, col_index]
            ax.plot(BIDS, utilities, color="#176B87", linewidth=2.2)
            ax.axvline(value, color="#D97706", linestyle="--", linewidth=1.4, label="truthful bid")
            ax.axvline(rival_bid, color="#7C3AED", linestyle=":", linewidth=1.4, label="rival bid")
            ax.set_title(f"v={value:.1f} | rival={rival_bid:.1f}")
            ax.grid(alpha=0.2)
    axes[0, 0].legend(frameon=False)
    fig.supxlabel("Bidder 1 bid")
    fig.supylabel("Utility")
    fig.savefig(args.out_dir / "fixed_rival_best_responses.png", dpi=180)
    plt.close(fig)
    write_csv(args.out_dir / "utility_curves.csv", ["value", "fixed_rival_bid", "bid", "utility"], rows)
    write_csv(args.out_dir / "truthfulness_check.csv", list(summary[0]), summary)
    print(f"Part 1B complete: truthful bidding is a best response in all {len(summary)} cases.")
    print(f"Outputs: {args.out_dir}")


if __name__ == "__main__":
    main()
