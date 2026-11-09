"""Analytical payoff of the one-shot firewall game.

Notation follows the paper: n legitimate hosts with rate ~ N(f_l, sigma_l^2),
z zombies whose rate follows a distribution chosen by the attacker, a
bottleneck of capacity BW, a hard rate threshold M at the firewall.
All rates are in kbps.
"""
from dataclasses import dataclass, replace
import numpy as np
from scipy.stats import norm, expon, poisson

GRID_Z = np.arange(0, 121)       # zombie counts
GRID_M = np.arange(1, 151)       # thresholds in kbps


@dataclass(frozen=True)
class Params:
    n: int = 80
    f_l: float = 50.0
    sigma_l: float = 20.0       # std. deviation (see README: "spread 20")
    BW: float = 5000.0          # 5 Mbps in kbps
    g: float = 10.0             # minimum useful rate
    w_b: float = 1000.0
    w_u: float = 1000.0
    w_z: float = 5.0

    def with_(self, **kw):
        return replace(self, **kw)


def zombie_cdf(dist, x, f_z, sigma_z=20.0):
    """Pr(F_z < x) for the three attacker families."""
    if dist == "normal":
        return norm.cdf(x, f_z, sigma_z)
    if dist == "exponential":
        return expon.cdf(x, scale=f_z)
    if dist == "poisson":
        return poisson.cdf(np.floor(x), f_z)
    raise ValueError(f"unknown distribution {dist!r}")


def admitted_mean(dist, f_z, x, sigma_z=20.0):
    """Exact E[F * 1{F < x}] (rates clipped at 0 for the normal family).

    The original model approximates this by f * Pr(F < x), which is only
    accurate when the distribution is concentrated well below x.
    """
    if dist == "normal":
        a, b = -f_z / sigma_z, (x - f_z) / sigma_z
        return f_z * (norm.cdf(b) - norm.cdf(a)) + sigma_z * (norm.pdf(a) - norm.pdf(b))
    if dist == "exponential":
        r = x / f_z
        return f_z * (1.0 - np.exp(-r) * (1.0 + r))
    if dist == "poisson":
        return f_z * poisson.cdf(np.floor(x) - 1, f_z)
    raise ValueError(dist)


def components(dist, f_z, p=Params(), sigma_z=20.0, z=GRID_Z, M=GRID_M, exact=False):
    """Return (V_B', V_U', payoff) matrices of shape (len(z), len(M)).

    exact=False reproduces the source model (mean * probability).
    exact=True uses exact truncated means for both traffic classes.
    """
    zz = np.asarray(z, dtype=float)[:, None]
    mm = np.asarray(M, dtype=float)[None, :]
    p_l = norm.cdf(mm, p.f_l, p.sigma_l)
    p_z = zombie_cdf(dist, mm, f_z, sigma_z)
    if exact:
        fl_p = admitted_mean("normal", p.f_l, mm, p.sigma_l)
        fz_p = admitted_mean(dist, f_z, mm, sigma_z)
    else:
        fl_p, fz_p = p.f_l * p_l, f_z * p_z
    T = p.n * fl_p + zz * fz_p
    VB = np.where(T > 0, zz * fz_p / np.where(T > 0, T, 1.0), 0.0)
    VU = norm.cdf(p.g * T / p.BW, p.f_l, p.sigma_l) + (1.0 - p_l)
    return VB, VU, p.w_b * VB + p.w_u * VU - p.w_z * zz


def payoff_matrix(dist, f_z, p=Params(), sigma_z=20.0, z=GRID_Z, M=GRID_M, exact=False):
    return components(dist, f_z, p, sigma_z, z, M, exact)[2]


def z_estimate(dist, f_z, M, p=Params(), sigma_z=20.0):
    """Closed-form best fleet size (Remark 3 in the paper)."""
    a = f_z * zombie_cdf(dist, M, f_z, sigma_z)
    b = p.n * p.f_l * norm.cdf(M, p.f_l, p.sigma_l)
    return (np.sqrt(p.w_b * a * b / p.w_z) - b) / a
