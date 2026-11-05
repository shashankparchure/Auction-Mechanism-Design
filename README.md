# Assignment 4: Auction Mechanism Design

This folder contains a separate Python entry point for each assignment part, a shared mechanism library, experiment outputs generated on demand, a report, and an offline interactive demonstration.

## Run the experiments

Open PowerShell, activate the existing `as_env` environment if it is not already active, then run each command from this folder:

```powershell
cd "F:\IITJ\AutonomousSystems\Auction-Mechanism-Design"
F:\IITJ\AutonomousSystems\as_env\Scripts\Activate.ps1
python part1a_second_price_single_rival.py --trials 100000 --seed 7
python part1b_second_price_fixed_rival.py
python part1c_second_price_two_rivals.py --trials 100000 --seed 19
python part2_first_price.py --trials 200000 --value 0.5 --seed 31
python part3_vcg_shortest_path.py
```

Each command is independent. It writes its CSV data, figures, and (for Part 3) a JSON summary under `results/part1a`, `results/part1b`, `results/part1c`, `results/part2`, or `results/part3`. Pass `--out-dir <folder>` to choose a different destination.

For the Part 2 sensitivity analysis, change `--value` to any value in `[0, 1]`. The default holds bidder 1's value at 0.5 because the brief gives a distribution for the other bidders but does not specify bidder 1's value.

## Open the visual demonstration

Open `demo/index.html` in a browser (or run `Invoke-Item .\demo\index.html` in PowerShell). It has controls for the second-price auction, first-price deviations, and VCG path procurement. It is self-contained and works without a web server or internet connection.

## Files

- `part1a_second_price_single_rival.py`: Part 1A, nine simulated payoff curves and plots.
- `part1b_second_price_fixed_rival.py`: Part 1B, fixed-rival best-response curves and truthfulness checks.
- `part1c_second_price_two_rivals.py`: Part 1C, two-rival simulations plus fixed-bid checks.
- `part2_first_price.py`: Part 2, Monte Carlo and exact expected utility for `n=2,3,4`.
- `part3_vcg_shortest_path.py`: Part 3, shortest-path outcome, pivot payments, and two misreport sweeps.
- `auction_core.py`: Shared auction and VCG functions.
- `experiment_io.py`: CSV output helpers.
- `report.md`: Experiment design, analytical predictions, and interpretation.
- `reports/assignment4_report.tex`: LaTeX report draft populated with the completed run results; `reports/assignment4_overleaf.zip` bundles it with its figures.
- `demo/index.html`: Offline interactive graphical demonstration.

The scripts need NumPy and Matplotlib. Both are already present in the provided `as_env`; if setting up another Python environment, install `requirements.txt` there.
