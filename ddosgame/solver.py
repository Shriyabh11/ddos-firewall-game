"""Pure-strategy saddle-point search on a finite grid."""
import numpy as np
from .model import payoff_matrix, GRID_Z, GRID_M, Params


def saddles(P, z=GRID_Z, M=GRID_M, tol=1e-9):
    """Entries that are column-maximal (attacker BR) and row-minimal (defender BR)."""
    col_max, row_min = P.max(axis=0), P.min(axis=1)
    ii, jj = np.where((P >= col_max[None, :] - tol) & (P <= row_min[:, None] + tol))
    return [(int(z[i]), int(M[j]), float(P[i, j])) for i, j in zip(ii, jj)]


def minimax_gap(P):
    """min_M max_z V - max_z min_M V  (>= 0, zero iff a pure saddle exists)."""
    return float(P.max(axis=0).min() - P.min(axis=1).max())


def best_saddle(dist, f_z, p=Params(), sigma_z=20.0, exact=False):
    s = saddles(payoff_matrix(dist, f_z, p, sigma_z, exact=exact))
    return max(s, key=lambda t: t[2]) if s else None


def general_search(dist, p=Params(), sigma_z=20.0, f_range=range(1, 121), exact=False):
    """Outer maximisation over f_z. Returns (best row, list of all rows)."""
    rows = []
    for f in f_range:
        s = best_saddle(dist, f, p, sigma_z, exact)
        if s:
            rows.append((f,) + s)
    best = max(rows, key=lambda r: r[3]) if rows else None
    return best, rows
