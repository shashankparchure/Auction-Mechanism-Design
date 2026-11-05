"""Part 3: VCG procurement on the Figure 7.3 transportation network."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from auction_core import VCG_EDGES, edge_utility, truthful_vcg_costs, vcg_outcome
from experiment_io import result_dir, write_csv


MISREPORTS = np.round(np.arange(0.0, 10.0 + 1e-9, 0.5), 2)


def path_label(edges: tuple[str, ...]) -> str:
    """Format a sequence of edge IDs as its node path, e.g. AB, BE, EF -> ABEF."""
    if not edges:
        return ""
    return edges[0][0] + "".join(VCG_EDGES[edge][1] for edge in edges)


def run_misreport_sweep(edge: str, true_cost: float) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    truthful_costs = truthful_vcg_costs()
    baseline = vcg_outcome(truthful_costs)
    baseline_utility = edge_utility(edge, baseline, true_cost)
    for report in MISREPORTS:
        reported = dict(truthful_costs)
        reported[edge] = float(report)
        outcome = vcg_outcome(reported)
        rows.append({
            "edge": edge,
            "true_cost": true_cost,
            "reported_cost": float(report),
            "selected_path": path_label(outcome.path),
            "selected": edge in outcome.path,
            "payment": outcome.payments[edge],
            "utility": edge_utility(edge, outcome, true_cost),
            "truthful_utility": baseline_utility,
        })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--on-path-edge", default="BE", help="edge whose truthful path includes it (default: BE)")
    parser.add_argument("--off-path-edge", default="AC", help="edge outside the truthful path (default: AC)")
    parser.add_argument("--out-dir", type=Path, default=result_dir("part3"), help="where CSV, JSON, and plots are written")
    args = parser.parse_args()
    for edge in (args.on_path_edge, args.off_path_edge):
        if edge not in VCG_EDGES:
            parser.error(f"unknown edge {edge!r}; choose from {', '.join(VCG_EDGES)}")
    if args.on_path_edge == args.off_path_edge:
        parser.error("choose different on-path and off-path edges")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    true_costs = truthful_vcg_costs()
    baseline = vcg_outcome(true_costs)
    rows = run_misreport_sweep(args.on_path_edge, true_costs[args.on_path_edge])
    rows += run_misreport_sweep(args.off_path_edge, true_costs[args.off_path_edge])
    fields = list(rows[0])
    write_csv(args.out_dir / "vcg_misreport_sweeps.csv", fields, rows)

    summary = {
        "true_costs": true_costs,
        "selected_path": path_label(baseline.path),
        "path_cost": baseline.reported_path_cost,
        "payments_to_edges": baseline.payments,
        "on_path_edge": args.on_path_edge,
        "off_path_edge": args.off_path_edge,
        "on_path_truthful_utility": edge_utility(args.on_path_edge, baseline, true_costs[args.on_path_edge]),
        "off_path_truthful_utility": edge_utility(args.off_path_edge, baseline, true_costs[args.off_path_edge]),
    }
    (args.out_dir / "vcg_truthful_outcome.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8), sharey=True, constrained_layout=True)
    for ax, edge, label in zip(axes, (args.on_path_edge, args.off_path_edge), ("On selected path", "Off selected path")):
        edge_rows = [row for row in rows if row["edge"] == edge]
        reports = [float(row["reported_cost"]) for row in edge_rows]
        utilities = [float(row["utility"]) for row in edge_rows]
        true_cost = true_costs[edge]
        truthful_utility = edge_utility(edge, baseline, true_cost)
        ax.plot(reports, utilities, marker="o", markersize=4, color="#176B87", linewidth=2.2)
        ax.axvline(true_cost, color="#D97706", linestyle="--", linewidth=1.6, label=f"true cost {true_cost:g}")
        ax.axhline(truthful_utility, color="#7C3AED", linestyle=":", linewidth=1.5, label="truthful utility")
        ax.set(title=f"{label}: {edge}", xlabel="Reported cost", ylabel="Edge agent utility")
        ax.set_xticks(MISREPORTS[::2])
        ax.grid(alpha=0.2)
        ax.legend(frameon=False)
    fig.savefig(args.out_dir / "vcg_misreport_analysis.png", dpi=180)
    plt.close(fig)

    print(f"Part 3 complete: selected path {path_label(baseline.path)}; path cost {baseline.reported_path_cost:g}.")
    print("Payments: " + ", ".join(f"{edge}={payment:g}" for edge, payment in baseline.payments.items()))
    print(f"Outputs: {args.out_dir}")


if __name__ == "__main__":
    main()
