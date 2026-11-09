import numpy as np
from ddosgame import Params, payoff_matrix, saddles, minimax_gap, best_saddle
from ddosgame.model import z_estimate


def test_poisson_subgame_matches_reported():
    z, M, v = best_saddle("poisson", 60)
    assert (z, M) == (55, 150) and abs(v - 215.4) < 0.1


def test_normal_subgame_close_to_reported():
    z, M, v = best_saddle("normal", 60)
    assert z == 55 and abs(v - 215.4) < 0.5


def test_saddle_implies_zero_gap():
    P = payoff_matrix("exponential", 60)
    assert saddles(P) and abs(minimax_gap(P)) < 1e-9


def test_gap_is_nonnegative():
    for d in ("normal", "exponential", "poisson"):
        assert minimax_gap(payoff_matrix(d, 100)) >= -1e-9


def test_low_threshold_limit_credits_attacker_with_user_loss():
    p = Params()
    P = payoff_matrix("normal", 60, p, M=np.array([1]))
    assert abs(P[0, 0] - p.w_u) < 20  # z=0 row ~ w_u as M -> 0


def test_fleet_estimate_is_close():
    assert 40 < z_estimate("normal", 60, 119) < 60
