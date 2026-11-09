# Firewall threshold game against DoS/DDoS flooding

Code for the paper *Choosing a Firewall Rate Threshold Against Flooding Attacks:
A Game-Theoretic Study with Independent Flow-Level Checks*.
Public repository: <https://github.com/Shriyabh11/ddos-firewall-game>.

It re-implements the one-shot, zero-sum firewall game of
[Spyridopoulos et al., *Computers & Security* 38 (2013)](https://doi.org/10.1016/j.cose.2013.03.014)
(itself an extension of Wu et al., SpringSim 2010), solves it on a grid, and
checks it with a flow-level Monte Carlo simulation. The original article is not
included here (publisher copyright); please obtain it via the DOI.

## What is in here

| Path | Purpose |
|---|---|
| `ddosgame/model.py` | Payoff of the game. `exact=False` follows the source model (mean x probability); `exact=True` uses exact truncated means |
| `ddosgame/solver.py` | Pure-strategy saddle search, minimax gap, two-level (distribution, mean rate) search |
| `ddosgame/montecarlo.py` | Flow-level simulation: random sender rates, hard threshold, fair sharing at the bottleneck |
| `scripts/run_analytical.py` | Subgames, general search, sensitivity (writes `results/analytical.json`) |
| `scripts/run_montecarlo.py` | Monte Carlo sweeps and analytic-vs-simulation comparison |
| `scripts/make_figures.py` | Regenerates every figure from `results/*.json` |
| `tests/` | Unit tests (`pytest`) |
| `paper/` | LaTeX source (IEEE conference format) and figures |

## Run

```bash
pip install -r requirements.txt
make all          # tests, analytical runs, Monte Carlo, figures (~1 minute)
```

## Setup (same as the source study)

n = 80 legitimate users, f_l = 50 kbps, bottleneck 5 Mbps, g = 10 kbps,
w_b = w_u = 1000, w_z = 5; grid z in 0..120, M in 1..150 kbps.
The source writes the spread of the normal rates as "20" (once as a variance,
once in kbps). We use a standard deviation of 20 kbps because a standard
deviation of sqrt(20) kbps gives payoffs far below the published scale.

## Main findings (see the paper for details)

1. At f_z = 60 kbps our source-model fixed-parameter subgame saddles are close
   to the published values (normal 55 zombies / payoff 215.3, Poisson 55 / 215.4,
   exponential 51 / 167.4).
2. We could not reproduce the published general-game result (120 zombies,
   payoff 331.1, threshold 96 kbps). The nested scan's highest-payoff exponential
   subgame saddle has 57 zombies, payoff 255.3, and threshold 95 kbps; the
   published configuration itself scores 172.7 under our implementation.
3. The source model approximates the mean admitted rate of a threshold-truncated
   flow by `mean x Pr(F <= M)`. This can overstate admitted exponential traffic
   by about 3x. Replacing it with the exact truncated first moment brings the
   analytical payoff within two points of simulation at the eight selected
   parameter points tested. The nested search's exponential subgame result falls
   to about 62. Neither model variant has a pure saddle in the combined
   simultaneous game on the baseline finite grid; mixed strategies were not
   computed.

## Limitations

* This is a flow-level simulation, not packet-level. We did not re-run ns-2.
* Our results hold for our reading of the source model; we have not obtained
  the original authors' Matlab code.
* Hypothetical weights, one bottleneck, UDP-only, one-shot game.
