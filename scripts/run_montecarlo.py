"""Flow-level Monte Carlo experiments (writes results/mc_*.json)."""
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import json, sys, time
import numpy as np
from ddosgame import Params, saddles
from ddosgame.model import components
from ddosgame.montecarlo import simulate_grid

OUT = "results"
p = Params()
t0 = time.time()

# 1) ns-2-style coarse sweep, normal attackers at f_z=60, many replications
Zs = list(range(10, 121, 10)); Ms = list(range(10, 141, 10))
mean, ci, vb, vu = simulate_grid("normal", 60, Zs, Ms, p, 20.0, reps=1000, seed=2026)
iz, im = np.unravel_index(mean.argmax(), mean.shape)
# max-min / min-max on the sweep grid
col_max = mean.max(axis=0); row_min = mean.min(axis=1)
sad = [(Zs[i], Ms[j], float(mean[i, j])) for i in range(len(Zs)) for j in range(len(Ms))
       if mean[i, j] >= col_max[j] - 1e-9 and mean[i, j] <= row_min[i] + 1e-9]
# defender's minimax threshold: argmin over M of the attacker's best-response value
br = mean.max(axis=0); jm = int(br.argmin())
coarse = dict(Zs=Zs, Ms=Ms, mean=mean.tolist(), ci=ci.tolist(),
              saddles=sad, minimax_M=Ms[jm], minimax_value=float(br[jm]),
              best_z_at_minimax=Zs[int(mean[:, jm].argmax())],
              attacker_global_max=dict(z=Zs[iz], M=Ms[im], value=float(mean[iz, im])))
json.dump(coarse, open(f"{OUT}/mc_coarse_normal60.json", "w"))
print("coarse sweep saddles:", sad)
print("minimax threshold", Ms[jm], "value", round(float(br[jm]), 1), "z*", coarse["best_z_at_minimax"])
print("attacker global max", coarse["attacker_global_max"])

# 2) finer grid for the same case
Zf = list(range(5, 121, 5)); Mf = list(range(10, 151, 5))
meanf, cif, vbf, vuf = simulate_grid("normal", 60, Zf, Mf, p, 20.0, reps=600, seed=7)
brf = meanf.max(axis=0); jf = int(brf.argmin())
colf = meanf.max(axis=0); rowf = meanf.min(axis=1)
sadf = [(Zf[i], Mf[j], float(meanf[i, j])) for i in range(len(Zf)) for j in range(len(Mf))
        if meanf[i, j] >= colf[j] - 1e-9 and meanf[i, j] <= rowf[i] + 1e-9]
fine = dict(Zs=Zf, Ms=Mf, mean=meanf.tolist(), ci=cif.tolist(), saddles=sadf,
            minimax_M=Mf[jf], minimax_value=float(brf[jf]),
            best_z_at_minimax=Zf[int(meanf[:, jf].argmax())])
json.dump(fine, open(f"{OUT}/mc_fine_normal60.json", "w"))
print("fine saddles:", sadf, "minimax M", Mf[jf], round(float(brf[jf]), 1))

# 3) analytic vs MC components at selected analytical equilibria
cases = [("normal", 60, 55, 114), ("normal", 60, 54, 100), ("exponential", 60, 51, 101),
         ("exponential", 60, 31, 96), ("poisson", 60, 55, 150), ("exponential", 120, 57, 95),
         ("exponential", 120, 120, 96), ("normal", 65, 53, 88)]
rows = []
for d, f, z, M in cases:
    VB, VU, P = components(d, f, p, 20.0, z=[z], M=[M])
    VBe, VUe, Pe = components(d, f, p, 20.0, z=[z], M=[M], exact=True)
    m, c, b, u = simulate_grid(d, f, [z], [M], p, 20.0, reps=4000, seed=11)
    rows.append(dict(dist=d, f_z=f, z=z, M=M,
                     VB_an=float(VB[0, 0]), VU_an=float(VU[0, 0]), pay_an=float(P[0, 0]), pay_exact=float(Pe[0, 0]), VB_exact=float(VBe[0, 0]),
                     VB_mc=float(b[0, 0]), VU_mc=float(u[0, 0]), pay_mc=float(m[0, 0]),
                     pay_ci=float(c[0, 0])))
    print(rows[-1])
json.dump(rows, open(f"{OUT}/mc_vs_analytic.json", "w"), indent=1)
print("elapsed", round(time.time() - t0, 1), "s")
