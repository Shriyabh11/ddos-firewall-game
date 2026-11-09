"""Regenerate all figures from results/*.json (run run_analytical.py and run_montecarlo.py first)."""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.size": 8, "axes.grid": True, "grid.alpha": 0.3,
                     "figure.dpi": 150, "savefig.bbox": "tight"})
os.makedirs("figures", exist_ok=True)
A = json.load(open("results/analytical.json"))
MC = json.load(open("results/mc_vs_analytic.json"))
coarse = json.load(open("results/mc_coarse_normal60.json"))
fine = json.load(open("results/mc_fine_normal60.json"))
col = {"normal": "C0", "exponential": "C3", "poisson": "C2"}
Mx = np.arange(1, 151)

# Fig 1: best-response value vs threshold, source vs exact
fig, ax = plt.subplots(1, 2, figsize=(7, 2.6), sharey=True)
for a, m, t in zip(ax, ("source", "exact"), ("Source model (mean x probability)", "Exact truncated means")):
    for d in col:
        a.plot(Mx, A["br_curves"][m][d], color=col[d], label=d.capitalize())
    a.set_yscale("log"); a.set_xlim(10, 150); a.set_ylim(30, 2000)
    a.set_title(t); a.set_xlabel("Threshold $M$ (kbps)")
ax[0].set_ylabel(r"$\max_z V'(z,M)$"); ax[0].legend(frameon=False)
fig.savefig("figures/fig_best_response.pdf"); plt.close(fig)

# Fig 2: equilibrium payoff vs f_z
fig, ax = plt.subplots(1, 2, figsize=(7, 2.6), sharey=True)
for a, m, t in zip(ax, ("source", "exact"), ("Source model", "Exact truncated means")):
    for d in col:
        c = np.array(A["general"][m][d]["curve"])
        a.plot(c[:, 0], c[:, 1], ".", ms=3, color=col[d], label=d.capitalize())
    a.set_title(t); a.set_xlabel(r"Attacker mean rate $f_z$ (kbps)"); a.set_xlim(0, 122)
ax[0].set_ylabel("Pure-saddle payoff"); ax[0].legend(frameon=False)
fig.savefig("figures/fig_eq_vs_fz.pdf"); plt.close(fig)

# Fig 3: Monte Carlo payoff surface (ns-2-style sweep, fine grid)
Zf, Mf = np.array(fine["Zs"]), np.array(fine["Ms"])
Pm = np.array(fine["mean"])
fig, a = plt.subplots(figsize=(3.4, 2.8))
cs = a.contourf(Mf, Zf, Pm, levels=np.linspace(0, 1000, 21), cmap="viridis")
a.set_xlabel("Threshold $M$ (kbps)"); a.set_ylabel("Zombies $z$")
for z, M, v in fine["saddles"]:
    a.plot(M, z, "w*", ms=9, mec="k")
plt.colorbar(cs, label="Simulated attacker payoff")
fig.savefig("figures/fig_mc_surface.pdf"); plt.close(fig)

# Fig 4: analytic (source / exact) vs Monte Carlo payoff at selected points
lab = [f"{r['dist'][:3]}\n$f_z$={r['f_z']}\n({r['z']},{r['M']})" for r in MC]
x = np.arange(len(MC)); w = 0.27
fig, a = plt.subplots(figsize=(7, 2.8))
a.bar(x - w, [r["pay_an"] for r in MC], w, label="Source model", color="C1")
a.bar(x, [r["pay_exact"] for r in MC], w, label="Exact means", color="C0")
a.bar(x + w, [r["pay_mc"] for r in MC], w, yerr=[r["pay_ci"] for r in MC],
      label="Monte Carlo (95% CI)", color="0.35", capsize=2)
a.axhline(0, color="k", lw=0.5)
a.set_xticks(x); a.set_xticklabels(lab, fontsize=6.5); a.set_ylabel("Attacker payoff")
a.legend(frameon=False, fontsize=7)
fig.savefig("figures/fig_validation.pdf"); plt.close(fig)
print("figures written:", sorted(os.listdir("figures")))
