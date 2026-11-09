import numpy as np
from ddosgame import Params
from ddosgame.montecarlo import simulate_grid
from ddosgame.model import components


def test_mc_close_to_analytic_when_firewall_open():
    # large M: the firewall barely acts, so analytic and flow-level should agree
    mean, ci, vb, vu = simulate_grid("normal", 60, [40], [150], reps=300, seed=1)
    VB, VU, P = components("normal", 60, z=[40], M=[150])
    assert abs(vb[0, 0] - VB[0, 0]) < 0.02
