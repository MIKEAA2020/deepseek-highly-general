#!/usr/bin/env python3
"""Shared LP engine for M1/M3: lexicographic pFBA + L1-MOMA on HiGHS.

Variable layout for both modes: x = [v (R), a (R), b (R)]
  lex mode : a = f, b = r with v = f - r, f,r >= 0  (|v| split)
  moma mode: a = p, b = m with v = v_ref + p - m     (|v - v_ref| split)

Linking rows are IDENTICAL: [I, -I, I] x = rhs, where rhs = 0 for lex
and rhs = v_ref for moma. Stoichiometry rows: [S, 0, 0] x = 0.

Lexicographic solve (3 stages, cold & deterministic):
  1. max c_bio . v                      -> mu*
  2. min sum(f + r)  s.t. v_bio >= mu*-tol    -> s2  (pFBA)
  3. min w . v  s.t. sum(f + r) <= s2 + tol   -> unique vertex
  (lex tie-break with fixed seeded weights w; the LP realization of the
  strict regularization recommended by the joint assessment)

MOMA-L1 solve:
  min sum(p + m)  s.t. S v = 0, v in current bounds, v = v_ref + p - m
"""
import numpy as np
import scipy.sparse as sp
from scipy.optimize import linprog


class LPEngine:
    def __init__(self, model, weights, bio_coeffs):
        self.rxn_ids = [r.id for r in model.reactions]
        self.R = R = len(self.rxn_ids)
        self.index = {rid: i for i, rid in enumerate(self.rxn_ids)}
        import cobra.util.array as cua
        S = np.asarray(cua.create_stoichiometric_matrix(model))
        self.M = S.shape[0]
        I = sp.identity(R, format="csr")
        Z = sp.csr_matrix((S.shape[0], 2 * R))
        top = sp.hstack([sp.csr_matrix(S), Z], format="csr")
        bot = sp.hstack([I, -I, I], format="csr")
        self.A_eq = sp.vstack([top, bot], format="csr")
        self.b_eq0 = np.zeros(self.M + R)
        # pin row for lex stage 3: sum(f + r) <= ub
        self.A_ub = sp.csr_matrix(
            np.concatenate([np.zeros(R), np.ones(2 * R)]).reshape(1, -1))
        self.w = np.asarray(weights, float)
        self.c_bio = np.asarray(bio_coeffs, float)   # objective over v
        self.lb0 = np.array([r.lower_bound for r in model.reactions])
        self.ub0 = np.array([r.upper_bound for r in model.reactions])
        self.OPTS = {"presolve": True}

    # ---------------------------------------------------------------- lex
    def solve_lex(self, lb, ub, bio_idx, mu_tol=1e-9, pin_rel=1e-9):
        """Full 3-stage lexicographic pFBA. lb/ub: current flux bounds (R).
        Returns (v, mu, s2) or None if infeasible at any stage."""
        R = self.R
        # variable bounds: v in [lb, ub]; f in [0, max(ub,0)]; r in [0, -min(lb,0)]
        fub = np.maximum(ub, 0.0)
        rub = np.maximum(-lb, 0.0)
        vlb = np.concatenate([lb, np.zeros(R), np.zeros(R)])
        vub = np.concatenate([ub, fub, rub])

        # stage 1: max c_bio . v
        c1 = np.zeros(3 * R)
        c1[:R] = -self.c_bio            # linprog minimizes
        res = linprog(c1, A_eq=self.A_eq, b_eq=self.b_eq0,
                      bounds=np.column_stack((vlb, vub)), method="highs",
                      options=self.OPTS)
        if not res.success:
            return None
        mu = float(res.x[bio_idx])

        # stage 2: min sum(f+r), v_bio >= mu - tol
        vlb2 = vlb.copy()
        vlb2[bio_idx] = max(vlb2[bio_idx], mu - mu_tol * max(1.0, abs(mu)))
        c2 = np.concatenate([np.zeros(R), np.ones(R), np.ones(R)])
        res = linprog(c2, A_eq=self.A_eq, b_eq=self.b_eq0,
                      bounds=np.column_stack((vlb2, vub)), method="highs",
                      options=self.OPTS)
        if not res.success:
            return None
        s2 = float(res.fun)

        # stage 3: min w.v s.t. sum(f+r) <= s2 + pin
        c3 = np.zeros(3 * R)
        c3[:R] = self.w
        b_ub = np.array([s2 + pin_rel * max(1.0, abs(s2))])
        res = linprog(c3, A_ub=self.A_ub, b_ub=b_ub, A_eq=self.A_eq,
                      b_eq=self.b_eq0, bounds=np.column_stack((vlb2, vub)),
                      method="highs", options=self.OPTS)
        if not res.success:
            return None
        return res.x[:R].copy(), mu, s2

    # --------------------------------------------------------------- moma
    def solve_moma(self, lb, ub, v_ref, cap=5000.0):
        """L1-MOMA: minimal ||v - v_ref||_1 over current bounds.
        Returns v or None."""
        R = self.R
        c = np.concatenate([np.zeros(R), np.ones(R), np.ones(R)])
        b_eq = np.concatenate([np.zeros(self.M), np.asarray(v_ref, float)])
        vlb = np.concatenate([lb, np.zeros(R), np.zeros(R)])
        vub = np.concatenate([ub, np.full(R, cap), np.full(R, cap)])
        res = linprog(c, A_eq=self.A_eq, b_eq=b_eq,
                      bounds=np.column_stack((vlb, vub)), method="highs",
                      options=self.OPTS)
        if not res.success:
            return None
        return res.x[:R].copy()


def gpr_dnf(model):
    """Parse every reaction's GPR into DNF: list of AND-clauses
    (frozensets of gene ids). Reaction is active iff >= 1 clause has all
    genes functional. Genes absent from GPR -> [{'': ...}] handled as
    always-active (empty clause list = constitutive)."""
    dnf = {}
    for r in model.reactions:
        rule = r.gene_reaction_rule.strip()
        if not rule:
            dnf[r.id] = []
            continue
        clauses = _parse_dnf(rule)
        dnf[r.id] = clauses
    return dnf


def _tokenize(rule):
    import re
    return re.findall(r"\(|\)|and|or|[A-Za-z0-9_.\-]+", rule, re.IGNORECASE)


def _parse_dnf(rule):
    """Full recursive-descent parser to AST, then AST -> DNF by
    distribution. Returns list of frozensets (AND-clauses)."""
    toks = _tokenize(rule)
    n = len(toks)
    pos = [0]

    def peek():
        return toks[pos[0]] if pos[0] < n else None

    def parse_expr():                      # OR level
        node = parse_term()
        while peek() is not None and peek().lower() == "or":
            pos[0] += 1
            node = ("or", node, parse_term())
        return node

    def parse_term():                      # AND level
        node = parse_factor()
        while peek() is not None and peek().lower() == "and":
            pos[0] += 1
            node = ("and", node, parse_factor())
        return node

    def parse_factor():
        if peek() == "(":
            pos[0] += 1
            node = parse_expr()
            assert peek() == ")", f"unbalanced GPR: {rule}"
            pos[0] += 1
            return node
        tok = toks[pos[0]]
        pos[0] += 1
        return ("g", tok)

    ast = parse_expr()
    assert pos[0] == n, f"trailing tokens in GPR: {rule}"

    def to_dnf(node):
        kind = node[0]
        if kind == "g":
            return [frozenset([node[1]])]
        left, right = to_dnf(node[1]), to_dnf(node[2])
        if kind == "or":
            return left + right
        return [a | b for a in left for b in right]

    clauses = [c for c in to_dnf(ast)]
    # drop supersets (a OR (a AND b)) == A
    minimal = [c for c in clauses
               if not any(c > d for d in clauses)]
    return minimal


def disabled_reactions(dnf, knockout_genes):
    """Reaction ids disabled when the gene set `knockout_genes` is
    non-functional: every AND-clause contains >= 1 knocked-out gene."""
    ko = set(knockout_genes)
    out = []
    for rid, clauses in dnf.items():
        if not clauses:
            continue          # constitutive / no GPR
        if all(cl & ko for cl in clauses):
            out.append(rid)
    return out
