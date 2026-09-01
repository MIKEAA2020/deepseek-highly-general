#!/usr/bin/env python3
"""Prototype: 3-stage lexicographic pFBA (biomass -> parsimony -> fixed
tie-breaking functional). Verifies determinism, correctness, timing."""
import time
import warnings

warnings.filterwarnings("ignore")

import numpy as np
import cobra
from optlang.symbolics import Zero
from cobra.flux_analysis import pfba

try:
    from cobra.flux_analysis.parsimonious import add_pfba
except ImportError:
    from cobra.flux_analysis import add_pfba

m = cobra.io.load_json_model(
    "/home/z/my-project/data/bigg_models/iML1515.json")
m.solver = "glpk"
rid = [r.id for r in m.reactions]
R = len(rid)
rng = np.random.default_rng(20240901)
W = rng.uniform(0.5, 1.5, R)


def lex_pfba(model, W, pin_rel=1e-9):
    """Unique deterministic pFBA optimum via lexicographic tie-break.
    Returns (flux_vector, biomass_flux, sum_abs_v) or None if infeasible."""
    with model:
        add_pfba(model, fraction_of_optimum=1.0)
        s2 = model.slim_optimize()
        if s2 is None or s2 != s2:
            return None
        pin = model.problem.Constraint(
            model.objective.expression, lb=None,
            ub=s2 + max(1e-9, pin_rel * abs(s2)))
        model.add_cons_vars([pin])
        model.objective = model.problem.Objective(
            Zero, direction="min", sloppy=True)
        co = {}
        for i, r in enumerate(model.reactions):
            co[r.forward_variable] = float(W[i])
            co[r.reverse_variable] = -float(W[i])
        model.objective.set_linear_coefficients(co)
        s3 = model.slim_optimize()
        if s3 is None or s3 != s3:
            return None
        v = np.empty(R)
        for i, r in enumerate(model.reactions):
            v[i] = r.forward_variable.primal - r.reverse_variable.primal
        bm = float(pin) if False else None
    return v


t0 = time.time()
v1 = lex_pfba(m, W)
v2 = lex_pfba(m, W)
v3 = lex_pfba(m, W)
dt = (time.time() - t0) / 3
print(f"lex_pfba: {dt:.2f}s/solve")
print(f"determinism: max|v1-v2| = {np.max(np.abs(v1 - v2)):.2e}, "
      f"max|v2-v3| = {np.max(np.abs(v2 - v3)):.2e}")
print(f"sum|v| = {np.abs(v1).sum():.6f} (pfba reference 769.790240)")

s = pfba(m)
vw = s.fluxes.reindex(rid).to_numpy(float)
i = m.reactions.index
bio = [r.id for r in m.reactions
       if r.id.lower().startswith("biomass") or "biomass" in r.name.lower()]
biomass_rxn = None
from cobra.util.solver import linear_reaction_coefficients
biomass_rxn = list(linear_reaction_coefficients(m).keys())[0]
print(f"biomass reaction: {biomass_rxn.id}")
j = rid.index(biomass_rxn.id)
print(f"biomass flux: lex = {v1[j]:.6f}, pfba = {vw[j]:.6f}")

# compare with pfba vertex: same parsimony value, possibly different vertex
print(f"|v_lex - v_pfba| max = {np.max(np.abs(v1 - vw)):.3f} "
      f"(degenerate ties expected)")
print(f"sum|v_lex| = {np.abs(v1).sum():.8f}, "
      f"sum|v_pfba| = {np.abs(vw).sum():.8f}")

# state restoration check: plain pfba after lex_pfba must equal earlier pfba
s2b = pfba(m)
vw2 = s2b.fluxes.reindex(rid).to_numpy(float)
print(f"restoration check: max|pfba_before - pfba_after| = "
      f"{np.max(np.abs(vw - vw2)):.2e}")

# quick bound-perturbation determinism (the sweep scenario)
m.reactions.EX_glc__D_e.lower_bound = -9.5
a = lex_pfba(m, W)
b = lex_pfba(m, W)
m.reactions.EX_glc__D_e.lower_bound = -10.0
print(f"perturbed determinism: max|a-b| = {np.max(np.abs(a - b)):.2e}")
