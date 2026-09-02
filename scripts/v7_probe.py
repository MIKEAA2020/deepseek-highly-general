#!/usr/bin/env python3
"""V7 probe: design the two robustness trajectories before the full run.

P1 (oxygen limitation at fixed glucose): find the q_o2 at which the
chamber switches from glucose-limited to O2-limited at q_glc = 5.
P2 (acetate switch): check EX_ac_e uptake bounds and growth levels on
acetate, and feasibility of a glucose->acetate anchor line at q_o2=22.
"""
import os
import sys

import numpy as np

BASE = "/home/z/my-project"
sys.path.insert(0, os.path.join(BASE, "scripts"))

import cobra
from cobra.util.solver import linear_reaction_coefficients
from lp_engine import LPEngine

model = cobra.io.load_json_model(
    os.path.join(BASE, "data", "bigg_models", "iJO1366.json"))
co = linear_reaction_coefficients(model)
c_bio = np.zeros(len(model.reactions))
for r, c in co.items():
    c_bio[model.reactions.index(r)] = c
bio_id = list(co.keys())[0].id
rng = np.random.default_rng(20240901)
W = rng.uniform(0.5, 1.5, len(model.reactions))
eng = LPEngine(model, W, c_bio)
bi = eng.index[bio_id]
i_glc, i_o2, i_ac = (eng.index["EX_glc__D_e"], eng.index["EX_o2_e"],
                     eng.index["EX_ac_e"])
print("EX_ac_e default bounds:", eng.lb0[i_ac], eng.ub0[i_ac])
print("EX_glc default bounds:", eng.lb0[i_glc], eng.ub0[i_glc])
print("EX_o2 default bounds:", eng.lb0[i_o2], eng.ub0[i_o2])


def mu_of(g, o, ac=0.0):
    lb, ub = eng.lb0.copy(), eng.ub0.copy()
    lb[i_glc] = -g
    lb[i_o2] = -o
    if ac > 0:
        lb[i_ac] = -ac
    out = eng.solve_lex(lb, ub, bi)
    return None if out is None else out[1]


print("\n=== P1 probe: q_glc = 5 fixed, q_o2 scan ===")
for o in [22.0, 20.0, 19.0, 18.5, 18.0, 17.5, 17.0, 16.5, 16.0, 15.0,
          12.0, 9.0, 6.0, 4.0, 3.0, 2.0, 1.5, 1.2, 1.0]:
    m = mu_of(5.0, o)
    print(f"  q_o2={o:5.1f}  mu={m if m is None else round(m, 5)}")

print("\n=== P2 probe: q_o2 = 22 fixed, acetate growth ===")
for ac in [0.0, 2.0, 5.0, 8.0, 10.0, 12.0, 15.0, 20.0]:
    m = mu_of(0.0, 22.0, ac)
    print(f"  glc=0, q_ac={ac:5.1f}  mu={m if m is None else round(m, 5)}")
print("with glucose co-feed:")
for g, ac in [(5.0, 0.0), (4.2, 2.0), (3.4, 4.0), (2.7, 5.0), (2.0, 6.0),
              (1.5, 7.0), (1.2, 8.0), (1.0, 8.0), (0.5, 9.0), (0.25, 10.0),
              (0.1, 10.0), (0.0, 10.0)]:
    m = mu_of(g, 22.0, ac)
    print(f"  glc={g:4.2f}, q_ac={ac:5.1f}  mu={m if m is None else round(m, 5)}")

print("\n=== P2 o2 demand on pure acetate (q_ac = 10) ===")
for o in [22.0, 18.0, 15.0, 13.0, 12.0, 11.0, 10.0, 9.0]:
    m = mu_of(0.0, o, 10.0)
    print(f"  q_ac=10, q_o2={o:5.1f}  mu={m if m is None else round(m, 5)}")
