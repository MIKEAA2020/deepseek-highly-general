#!/usr/bin/env python3
"""Benchmark: persistent 3-stage lexicographic pFBA solver (no per-call
sympy rebuilds). Must reproduce the slow prototype's solution and be
deterministic."""
import time
import warnings

warnings.filterwarnings("ignore")

import numpy as np
import cobra
from itertools import chain
from optlang.symbolics import Zero
from cobra.util.solver import fix_objective_as_constraint

m = cobra.io.load_json_model(
    "/home/z/my-project/data/bigg_models/iML1515.json")
m.solver = "glpk"
R = len(m.reactions)
rid = [r.id for r in m.reactions]
rng = np.random.default_rng(20240901)
W = rng.uniform(0.5, 1.5, R)


class LexSolver:
    """Persistent lexicographic (FBA, pFBA, tie-break) solver.

    Stage 1: max biomass           -> mu*
    Stage 2: min sum|v| s.t. v_bio >= mu* - tol   -> s2
    Stage 3: min w.v s.t. sum|v| <= s2 + tol      -> unique vertex
    Only constraint bounds are updated per solve; all problem structure
    (objectives, pin constraint) is built once.
    """

    def __init__(self, model, weights):
        self.model = model
        self.reactions = list(model.reactions)
        self.R = len(self.reactions)
        self.fwd = [r.forward_variable for r in self.reactions]
        self.rev = [r.reverse_variable for r in self.reactions]
        self.obj_orig = model.objective
        # biomass-fix constraint (lb updated per solve)
        fix_objective_as_constraint(model, fraction=1.0)
        self.fix = model.constraints[
            "fixed_objective_%s" % self.obj_orig.name]
        # pfba objective
        model.objective = model.problem.Objective(
            Zero, direction="min", sloppy=True, name="_pfba_objective")
        allvars = list(chain(*zip(self.fwd, self.rev)))
        model.objective.set_linear_coefficients(
            {v: 1.0 for v in allvars})
        self.obj_pfba = model.objective
        # pin constraint: sum|v| <= ub (ub updated per solve)
        model.add_cons_vars([model.problem.Constraint(
            Zero, lb=None, ub=1e20, name="lex_pin")])
        pin = model.constraints["lex_pin"]
        pin.set_linear_coefficients({v: 1.0 for v in allvars})
        self.pin = pin
        # lex tie-break objective (fixed weights)
        model.objective = model.problem.Objective(
            Zero, direction="min", sloppy=True, name="lex_obj")
        co = {}
        for i in range(self.R):
            co[self.fwd[i]] = float(weights[i])
            co[self.rev[i]] = -float(weights[i])
        model.objective.set_linear_coefficients(co)
        self.obj_lex = model.objective

    def solve(self):
        mdl = self.model
        mdl.objective = self.obj_orig
        mu = mdl.slim_optimize()
        if mu is None or mu != mu:
            return None
        self.fix.lb = mu - max(1e-9, 1e-9 * abs(mu))
        mdl.objective = self.obj_pfba
        s2 = mdl.slim_optimize()
        if s2 is None or s2 != s2:
            return None
        self.pin.ub = s2 + max(1e-9, 1e-12 * abs(s2)) * 1e3
        mdl.objective = self.obj_lex
        s3 = mdl.slim_optimize()
        if s3 is None or s3 != s3:
            return None
        v = np.empty(self.R)
        for i in range(self.R):
            v[i] = self.fwd[i].primal - self.rev[i].primal
        return v


t0 = time.time()
lx = LexSolver(m, W)
print(f"build: {time.time() - t0:.2f}s")

# timing loop
t0 = time.time()
vs = [lx.solve() for _ in range(6)]
dt = (time.time() - t0) / 6
print(f"persistent lex solve: {dt:.2f}s/solve")
print(f"determinism: max|v1-v2| = "
      f"{np.max(np.abs(vs[0] - vs[1])):.2e}, "
      f"max|v2-v3| = {np.max(np.abs(vs[1] - vs[2])):.2e}")

# correctness vs slow prototype values: sum|v| and biomass
v1 = vs[0]
print(f"sum|v| = {np.abs(v1).sum():.8f} (expect 769.79024068)")
bidx = rid.index("Ec_biomass_iML1515_core_75p37M")
print(f"biomass = {v1[bidx]:.8f} (expect 0.876997)")

# per-stage breakdown
t0 = time.time()
for _ in range(5):
    m.objective = lx.obj_orig
    mu = m.slim_optimize()
print(f"stage1: {(time.time() - t0) / 5:.3f}s (mu={mu:.6f})")
t0 = time.time()
for _ in range(5):
    m.objective = lx.obj_pfba
    s2 = m.slim_optimize()
print(f"stage2: {(time.time() - t0) / 5:.3f}s (s2={s2:.4f})")
t0 = time.time()
for _ in range(5):
    m.objective = lx.obj_lex
    s3 = m.slim_optimize()
print(f"stage3: {(time.time() - t0) / 5:.3f}s")
t0 = time.time()
for _ in range(5):
    v = np.empty(R)
    for i in range(R):
        v[i] = lx.fwd[i].primal - lx.rev[i].primal
print(f"primal read: {(time.time() - t0) / 5:.3f}s")

# perturbation + restore determinism
m.reactions.EX_glc__D_e.lower_bound = -9.5
a = lx.solve()
b = lx.solve()
m.reactions.EX_glc__D_e.lower_bound = -10.0
c = lx.solve()
print(f"perturbed determinism: {np.max(np.abs(a - b)):.2e}; "
      f"restored vs WT: {np.max(np.abs(c - v1)):.2e}")

# gene KO + restore
from cobra.manipulation.delete import knock_out_model_genes
ko = knock_out_model_genes(m, [m.genes.get_by_id("b4025")])
ka = lx.solve()
kb = lx.solve()
for r in ko:
    pass
print(f"KO(pgi) solve: growth = {ka[bidx]:.6f}, "
      f"determinism {np.max(np.abs(ka - kb)):.2e}")
