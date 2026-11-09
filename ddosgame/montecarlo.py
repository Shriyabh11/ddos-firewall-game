"""Flow-level Monte Carlo simulation of the same game.

This is NOT packet-level (ns-2). It draws actual random sender rates, applies
the hard threshold, shares the bottleneck fairly, and counts what happens to
each legitimate user, so it tests the analytical approximations
(product-of-means for truncated rates, additive loss probability) without
relying on them.

Rates are clipped at zero. A legitimate user counts as lost if the firewall
drops it (rate > M) OR if its post-congestion rate is below g (no double count).
Common random numbers: the same draws are reused across (z, M) cells.
"""
import numpy as np
from scipy.stats import norm, expon, poisson
from .model import Params


def draw_rates(dist, f_z, sigma_z, u):
    if dist == "normal":
        return np.maximum(norm.ppf(u, f_z, sigma_z), 0.0)
    if dist == "exponential":
        return expon.ppf(u, scale=f_z)
    if dist == "poisson":
        return poisson.ppf(u, f_z).astype(float)
    raise ValueError(dist)


def simulate_grid(dist, f_z, Zs, Ms, p=Params(), sigma_z=20.0, reps=500, seed=0):
    """Return mean payoff, 95% CI half-width, mean V_B, mean V_U on a (Z, M) grid."""
    rng = np.random.default_rng(seed)
    Zs, Ms = np.asarray(Zs), np.asarray(Ms, dtype=float)
    zmax = int(Zs.max())
    shape = (len(Zs), len(Ms))
    sum_pay = np.zeros(shape); sum_sq = np.zeros(shape)
    sum_vb = np.zeros(shape); sum_vu = np.zeros(shape)
    for _ in range(reps):
        L = np.maximum(rng.normal(p.f_l, p.sigma_l, p.n), 0.0)
        Zr = draw_rates(dist, f_z, sigma_z, rng.random(zmax))
        pass_l = L[None, :] <= Ms[:, None]                        # (M, n)
        load_l = (L[None, :] * pass_l).sum(axis=1)                # (M,)
        for iz, z in enumerate(Zs):
            pass_z = Zr[None, :z] <= Ms[:, None]                  # (M, z)
            load_z = (Zr[None, :z] * pass_z).sum(axis=1)
            T = load_l + load_z
            alpha = np.minimum(1.0, p.BW / np.where(T > 0, T, 1.0))
            starved = (L[None, :] * alpha[:, None]) < p.g         # congestion loss
            lost = (~pass_l) | starved
            vu = lost.mean(axis=1)
            vb = np.where(T > 0, load_z / np.where(T > 0, T, 1.0), 0.0)
            pay = p.w_b * vb + p.w_u * vu - p.w_z * z
            sum_pay[iz] += pay; sum_sq[iz] += pay ** 2
            sum_vb[iz] += vb; sum_vu[iz] += vu
    mean = sum_pay / reps
    var = np.maximum(sum_sq / reps - mean ** 2, 0.0)
    ci = 1.96 * np.sqrt(var / reps)
    return mean, ci, sum_vb / reps, sum_vu / reps
