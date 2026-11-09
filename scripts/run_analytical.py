"""Analytical experiments: source model vs exact-truncated-mean model (writes results/analytical.json)."""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from ddosgame import Params, payoff_matrix, saddles, best_saddle, general_search, minimax_gap
from ddosgame.model import z_estimate

DISTS = ("normal", "exponential", "poisson")
p = Params()
out = {}

out["subgames_f60"] = {m: {d: best_saddle(d, 60, p, exact=(m == "exact")) for d in DISTS}
                       for m in ("source", "exact")}
out["general"] = {}
for m in ("source", "exact"):
    out["general"][m] = {}
    for d in DISTS:
        best, rows = general_search(d, p, exact=(m == "exact"))
        out["general"][m][d] = dict(best=best, n_no_saddle=120 - len(rows),
                                    curve=[(r[0], r[3]) for r in rows])
# normal attacker with varied spread
out["normal_sigma"] = {}
for m in ("source", "exact"):
    out["normal_sigma"][m] = {}
    for s in (10, 20, 30, 40, 50):
        best, _ = general_search("normal", p, sigma_z=float(s), exact=(m == "exact"))
        out["normal_sigma"][m][s] = best
# best-response curves at f_z=60
out["br_curves"] = {}
for m in ("source", "exact"):
    out["br_curves"][m] = {}
    for d in DISTS:
        P = payoff_matrix(d, 60, p, exact=(m == "exact"))
        out["br_curves"][m][d] = P.max(axis=0).tolist()
# sensitivity (exact model, normal f_z=60, and source model exp f_z=120 for continuity)
def sens(dist, f, exact):
    rows = {}
    for k, vals in (("w_z", (2, 5, 10, 20)), ("w_u", (500, 1000, 2000))):
        for v in vals:
            rows[f"{k}={v}"] = best_saddle(dist, f, p.with_(**{k: float(v)}), exact=exact)
    return rows
out["sens_normal60_exact"] = sens("normal", 60, True)
out["sens_exp120_source"] = sens("exponential", 120, False)
# Remark-3 estimates
out["z_estimate"] = {"normal60_M119": float(z_estimate("normal", 60, 119)),
                     "exp120_M95_source": float(z_estimate("exponential", 120, 95))}
# minimax gaps
out["gaps"] = {f"{d}@{f}": minimax_gap(payoff_matrix(d, f, p)) for d, f in
               (("normal", 100), ("poisson", 100), ("exponential", 120), ("exponential", 60))}
json.dump(out, open("results/analytical.json", "w"), indent=1, default=float)
for k in ("subgames_f60",):
    print(json.dumps(out[k], indent=1, default=float))
for m in out["general"]:
    for d in DISTS:
        print(m, d, out["general"][m][d]["best"], "no-saddle:", out["general"][m][d]["n_no_saddle"])
print("normal sigma", json.dumps(out["normal_sigma"], default=float))
print("sens normal exact", json.dumps(out["sens_normal60_exact"], default=float))
print("sens exp120 source", json.dumps(out["sens_exp120_source"], default=float))
print(out["z_estimate"], out["gaps"])
