# Assignment 4: Auction Mechanisms

## 1. Purpose

This report implements and analyzes three mechanisms: second-price auctions, first-price auctions, and VCG procurement of a least-cost path. The Python scripts produce Monte Carlo CSV files and plots when run. No Monte Carlo output has been inserted into this report before those commands are run; the numeric predictions below come from the stated distributions and can be compared with the generated estimates.

## 2. Experimental setup and assumptions

- Private values and costs are independent unless a part says otherwise.
- Every random valuation is uniform on `[0, 1]`.
- Part 1 uses bidder 1's specified fixed values `v ∈ {0.2, 0.5, 0.8}` and the bid grid `0.00, 0.01, ..., 1.00`.
- Parts 1A and 1C default to 100,000 simulated auctions per value/strategy case. A fixed seed makes each run repeatable.
- Part 1C's line “Repeat parts A and C” is treated as a typo for “Repeat parts A and B”: it includes the stochastic curves and a fixed-rival truthfulness check with two rivals.
- In Part 1C's fixed-rival check, both rivals use the listed fixed bid. Tied highest bids split the allocation uniformly.
- The Part 2 brief does not give bidder 1's fixed value. The experiment uses `v=0.5` by default and accepts another value with `--value`; the other `n-1` bidders draw values independently from `[0,1]`.
- In Part 2, the multiplier grid is `0.1, 0.2, ..., 2.0` plus the exact equilibrium multiplier `(n-1)/n` for each `n`. This adds `2/3` and `0.75`, which are not on the 0.1 grid.
- In Part 2, “could have paid less and still won” is measured three ways:
  - strictly: the highest bid exceeds the runner-up bid by more than a small numerical tolerance;
  - with a bid increment (`--bid-increment`, default `0.01`): the winner could have bid one increment less and still won;
  - with the same increment, counted only over the auctions bidder 1 won.

  The script also reports the average winning-to-runner-up bid gap and bidder 1's average overpayment when it wins.
- In Part 3, suppliers are the directed edges of the Figure 7.3 graph. If paths tie in cost, the lexicographically earlier path is selected to make output deterministic.

## 3. Part 1: second-price auction

Bidder 1 wins when its bid is at least the strongest rival bid and pays that rival bid. Its utility is `v - rival_bid` when it wins and zero otherwise. The experiment sweeps all 101 focal bids for each specified value and rival strategy.

### 3.1 One rival (Part 1A)

The rival's bid distribution is uniform on `[0,1]` under both truthful bidding and random bidding independent of value. Those two strategies therefore produce the same expected-utility curve. With one rival:

| Rival strategy | Expected utility at focal bid `b` |
|---|---|
| Truthful | `v b - b²/2` |
| Random bid from `[0,1]` | `v b - b²/2` |
| Half-value | `2 v b - b²` for `b ≤ 0.5`; `v - 0.25` for `b ≥ 0.5` |

Against truthful or random bids, the curve is maximized at `b=v`. Against half-value bidding, `b=v` is optimal when `v≤0.5`; when `v>0.5`, every bid at least `0.5` has the same maximum payoff because the rival never bids above `0.5`. The plots therefore help select a bid: truthful bidding maximizes expected utility for each of these rival models, although it is not always the unique maximizer.

The nine individual plots and a combined 3-by-3 panel are saved by the Part 1A command. The CSV contains one row per value, strategy, and focal bid.

### 3.2 Fixed rival bid (Part 1B)

For a fixed rival bid `r`, bidding below `r` loses and gives zero; bidding above `r` wins and gives `v-r`. At exactly `r`, the bidders tie and split the allocation. If `r<v`, winning gives positive utility; if `r>v`, winning gives negative utility. Bidding truthfully `b=v` therefore gives the highest utility in each case. Other bids can tie that utility, so the result is weak dominance rather than a unique optimum.

The script checks every value in `{0.2, 0.5, 0.8}` against each rival bid in `{0.1, 0.4, 0.9}` and writes both the full curves and a compact truthfulness table.

### 3.3 Two rivals (Part 1C)

With two independent rivals, the second price is the maximum of their bids. For truthful or random rival bids, the maximum has density `2x` on `[0,1]`, so:

`U(b) = v b² - (2/3)b³`.

For two half-value rivals, the maximum has density `8x` on `[0,0.5]`, giving:

`U(b) = 4 v b² - (8/3)b³` for `b≤0.5`, and `U(b)=v-1/3` for `b≥0.5`.

Truthful bidding maximizes expected utility for all three continuous rival bid distributions. The truthful and random cases again have identical curves. Compared with one rival, the chance of winning at any given bid is lower, and expected utility falls. The script also repeats the fixed-rival check with both rivals bidding the same fixed amount; ties at that amount are split three ways.

## 4. Part 2: first-price deviation

Let `α=(n-1)/n` be the equilibrium multiplier used by each of the `n-1` rivals. Bidder 1 has value `v` and tests `b=kv` for `k=0.1,0.2,...,2.0` plus `k=α`. For a bid below `α`, each rival's bid is at most `b` with probability `b/α`. Therefore:

`Pr(win) = min((kv/α)^(n-1), 1)`

and

`E[utility] = (v-kv) · Pr(win)`.

Differentiating the below-cap part of this expression gives the optimal multiplier `k=α=(n-1)/n`. The continuous optima are `0.5`, `2/3`, and `0.75` for `n=2,3,4`. These are added to the tested multipliers, so the simulated maximum lands exactly on `k=α` for every `n`. On the 0.1 grid alone, the nearest point `k=0.7` gives lower utility.

At the equilibrium multiplier, a fixed bidder value `v` gives win probability `v^(n-1)` and expected utility `v^n/n`. For the default `v=0.5`, the exact expected utilities at the continuous optima are:

| Bidders `n` | Equilibrium `k` | Equilibrium bid | Win probability | Expected utility |
|---:|---:|---:|---:|---:|
| 2 | 0.500 | 0.250 | 0.500 | 0.125000 |
| 3 | 0.667 | 0.333 | 0.250 | 0.041667 |
| 4 | 0.750 | 0.375 | 0.125 | 0.015625 |

The script plots simulated estimates beside the exact expected-utility curves and records empirical win probabilities. Simulated results (200,000 auctions per `n`, seed 31):

| `n` | Best tested `k` | Simulated utility | Exact utility | Simulated utility at `k=0.7` |
|---:|---:|---:|---:|---:|
| 2 | 0.500 | 0.124734 | 0.125000 | 0.104968 |
| 3 | 0.667 | 0.041813 | 0.041667 | 0.041496 |
| 4 | 0.750 | 0.015471 | 0.015625 | 0.015145 |

Under continuous values, exact ties have probability zero. The strict “could pay less” fraction is therefore `1.000` for every `n` and `k`. The increment-based measure is more informative. At the equilibrium multiplier with a 0.01 increment:

| `n` | Strict | Any winner | Bidder 1's wins | Mean winner margin | Mean bidder 1 overpayment when winning |
|---:|---:|---:|---:|---:|---:|
| 2 | 1.000 | 0.960 | 0.959 | 0.124724 | 0.124561 |
| 3 | 1.000 | 0.955 | 0.940 | 0.139171 | 0.111475 |
| 4 | 1.000 | 0.951 | 0.923 | 0.140351 | 0.093807 |

Across all multipliers, the any-winner fraction lies between `0.927` and `1.000`. The bidder-1 fraction ranges from `0.481` (`n=4`, `k=0.1`, where bidder 1 wins rarely and narrowly) to `1.000` (once `kv` exceeds the largest possible rival bid `α` by more than the increment). A first-price winner almost always leaves money on the table, unlike a second-price winner, who pays exactly the runner-up's bid.

## 5. Part 3: VCG procurement on a path

The Figure 7.3 network uses these directed edge costs:

| Edge | Cost | Edge | Cost |
|---|---:|---|---:|
| AB | 3 | AC | 2 |
| BD | 2 | BE | 1 |
| CE | 3 | CF | 5 |
| DF | 2 | EF | 1 |

The path costs are `ABEF=5`, `ACEF=6`, `ABDF=7`, and `ACF=7`. The chosen path is `ABEF`. For each winning edge, its VCG payment is the lowest reported path cost when that edge is excluded, minus the cost of the other edges in the selected path. This gives:

| Edge | Selected? | Payment | True cost | Utility (payment − cost) |
|---|---|---:|---:|---:|
| AB | Yes | 4 | 3 | 1 |
| BE | Yes | 2 | 1 | 1 |
| EF | Yes | 3 | 1 | 2 |
| AC, BD, CE, CF, DF | No | 0 | varies | 0 |

The script defaults to misreporting `BE` (on the selected path) and `AC` (off the selected path), in increments of 0.5 from 0 to 10. For `BE`, reports below 2 keep it on the path and leave its pivot payment at 2; reports above that make the path change, so its utility drops to zero. For `AC`, a report below 1 changes the selected route to `ACEF`; the payment is 1, below AC's true cost of 2, so its utility is -1. The sweep CSV records `utility_change` (utility minus truthful utility) for every report. It is `0` or `-1` in all 42 cases and never positive, so truthful reporting is at least as good as every deviation in both sweeps.

The code allows either edge to be changed from the command line. It saves the full misreport table, the truthful baseline outcome, and a utility-versus-report plot.

## 6. Running the experiments

Run these commands from this folder with the provided `as_env` activated:

```powershell
python part1a_second_price_single_rival.py --trials 100000 --seed 7
python part1b_second_price_fixed_rival.py
python part1c_second_price_two_rivals.py --trials 100000 --seed 19
python part2_first_price.py --trials 200000 --value 0.5 --seed 31
python part3_vcg_shortest_path.py
```

CSV files and plot images appear in the part-specific subfolders under `results/`. Part 3 also writes `vcg_truthful_outcome.json`. These files contain the empirical measurements from the local run and should be kept with the report when submitting the completed experiment results.

## 7. Graphical demonstration

Open `demo/index.html` in any modern browser. It has interactive controls for the rival count and strategy, focal bids, first-price multipliers, and VCG cost reports. The page computes expected auction utilities directly from the distributions and recomputes the VCG path and payments as controls change; it does not require an internet connection.

## References

- Assignment 4 handout, supplied PDF.
- Shoham, Y. and Leyton-Brown, K. *Multiagent Systems: Algorithmic, Game-Theoretic, and Logical Foundations*. Cambridge University Press, 2009. Transportation-network VCG example; Figure 7.3 as referenced in the handout.
