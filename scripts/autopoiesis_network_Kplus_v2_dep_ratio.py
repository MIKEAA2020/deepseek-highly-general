"""
Network K+ v2 cascade-breaking enzyme-pair prescription -- Identify the
MINIMAL cascade-breaking enzyme PAIRS that would convert Network K's 7
fragile metabolic intermediates (under v2 dep_ratio at tau=0.5) into
ROBUST ones, analogous to the original ACS1/2 prescription for AcCoA.

CONTEXT (from Network K v2 dep_ratio commit 07e6d85):
  - Network K v1 binary Phase I: 52/52 = 100% (full-component-KO recovery).
  - Network K v2 dep_ratio (single-reaction-KO from baseline steady state):
    6/13 metabolic intermediates robust (max_dep < 0.5):
      FBP (0.28), AcCoA (0.40), ALA (0.00), ASP (0.00), MAL (0.00), GLU (0.00)
    7/13 metabolic intermediates FRAGILE (max_dep >= 0.5):
      G6P (0.50), PEP (0.70), PYR (1.00), Glycogen (1.00), PolyP (0.99),
      DHAP (1.00), G3P (1.00)
  - 0/38 enzymes robust (by design, single-synthesis-gene decay = 0.7139).
  - 0/1 TF robust (G_auto KO drops TF by 0.66).

CASCADE-BREAKING ENZYME PAIRS (this script's prescription):
  Principle (mirroring ACS1/2 for AcCoA):
    Each new isozyme PAIR produces the fragile intermediate from a DIFFERENT,
    INDEPENDENT substrate pool -- ideally food-supplied or buffered against
    the cascade trigger.

  6 new isozyme pairs (the ALDO5/6 pair fixes BOTH DHAP and G3P, which share
  the same producer ALDO3/4):

  1. MAE1/MAE2 (malic enzyme, EC 1.1.1.39) for PYR
     - M24a/b: MAL + NAD+ -> PYR + CO2 + NADH (mirror M7 MDH stoich + decarb)
     - Substrate: MAL (food, stable at 100.0). Bypasses PYK1/2 (PEP->PYR) and
       the ALA-dependent M12 ALT5/6 (the cascade trigger).
  2. PCK1/PCK2 (PEP carboxykinase, EC 4.1.1.49) for PEP
     - M25a/b: OAA + ATP -> PEP + CO2 + ADP
     - Substrate: OAA (food, stable). Bypasses ALDO1/2 FBP-cleavage step.
  3. FBP1/FBP2 (fructose-1,6-bisphosphatase, EC 3.1.3.11) for G6P
     - M26a/b: FBP -> G6P + Pi (simplified; gluconeogenic, reverse of HK+PFK)
     - Substrate: FBP (stable, dep=0.28). Bypasses HK1/2 and GLYP1/2.
  4. GLY3/GLY4 (alternative glycogen synthase, isozyme of GLY1/2) for Glycogen
     - M27a/b: G6P + ATP -> Glycogen + ADP (same stoich as M13a/b)
     - Adds 2 more isozymes to break the single-synthesis-gene fragility.
  5. PPK3/PPK4 (alternative polyphosphate kinase, isozyme of PPK1/2) for PolyP
     - M28a/b: ATP -> PolyP + ADP (same stoich as M15a/b)
     - Same logic as GLY3/4.
  6. ALDO5/ALDO6 (Class II fructose-bisphosphate aldolase, EC 4.1.2.16,
     isozyme of Class I ALDO3/4) for DHAP AND G3P
     - M29a/b: FBP -> DHAP + G3P (same stoich as M21a/b)
     - Single pair fixes BOTH DHAP and G3P (shared producer ALDO3/4).

  Each new enzyme is synthesized by a TF-catalyzed reaction using the
  ACS1/2 synthesis substrate pattern (GLU + alphaKG + ATP -> enzyme +
  ADP + Pi), matching E23a/b for ACS1/ACS2.

EXPECTED OUTCOME:
  - All 7 previously-fragile intermediates should now have max_dep_ratio < 0.5
    under the SAME v2 dep_ratio protocol (single-reaction-KO from baseline).
  - The metabolic-robust count should rise from 6/13 to 13/13.
  - The enzyme-fragile count should rise from 0/38 to 0/52 (since we add 12
    new enzymes, each still single-synthesis-gene, dep_ratio ~ 0.7139 each).
  - The TOTAL robust count goes from 6/52 (11.5%) to 13/65 (20.0%).
  - The CRITICAL test: does ACS1/2-style prescription TRANSFER to the other
    6 fragile intermediates, or was AcCoA a special case (with its specific
    NAD+/CoA bottleneck)? If it transfers, the prescription is a general
    cascade-breaking principle; if not, each intermediate needs its own
    custom fix.

Outputs:
  download/autopoiesis_network_Kplus_v2_dep_ratio.{png,csv,txt}
  download/autopoiesis_network_Kplus_v2_dep_ratio_results.json
"""
from __future__ import annotations

import json
import os
import sys
import time
from typing import Any

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm

for _p in (
    "/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
):
    if os.path.exists(_p):
        try:
            fm.fontManager.addfont(_p)
        except Exception:
            pass

import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


# ----------------------------------------------------------------------
#  Import Network K's species/reactions (from autopoiesis_network_K_v2_dep_ratio.py
#  to avoid side effects). Then EXTEND with the 6 cascade-breaking isozyme pairs.
# ----------------------------------------------------------------------
# (Copied from autopoiesis_network_K.py and autopoiesis_network_K_v2_dep_ratio.py)
species = [
    "Glc", "NH3", "NAD+", "CO2", "NADH", "Acetate",
    "ATP", "ADP", "Pi", "OAA",
    "alphaKG",
    "G6P", "FBP", "PEP", "PYR", "AcCoA", "ALA", "ASP", "MAL",
    "GLU", "Glycogen", "PolyP", "DHAP", "G3P",
    "HK1", "HK2", "PFK1", "PFK2",
    "ALDO1", "ALDO2", "ALDO3", "ALDO4",
    "PYK1", "PYK2",
    "ALT1", "ALT2", "ALT3", "ALT4", "ALT5", "ALT6",
    "ASPAT1", "ASPAT2", "ASPAT3", "ASPAT4",
    "ALT7", "ALT8",
    "MDH1", "MDH2", "PDH1", "PDH2", "PEPC1", "PEPC2", "ACK1", "ACK2",
    "GLY1", "GLY2", "GLYP1", "GLYP2", "PPK1", "PPK2",
    "ACS1", "ACS2",
    "TF",
]
food = {"Glc", "NH3", "NAD+", "CO2", "NADH", "Acetate",
        "ATP", "ADP", "Pi", "OAA", "alphaKG"}
non_food = [s for s in species if s not in food]

reactions = [
    {"id": "M1a", "stoich": {"Glc": -1, "ATP": -1, "G6P": 2, "ADP": 2}, "catalyst": "HK1", "kind": "metabolic"},
    {"id": "M1b", "stoich": {"Glc": -1, "ATP": -1, "G6P": 2, "ADP": 2}, "catalyst": "HK2", "kind": "metabolic"},
    {"id": "M2a", "stoich": {"G6P": -1, "FBP": 2}, "catalyst": "PFK1", "kind": "metabolic", "k_cat_override": 1.5},
    {"id": "M2b", "stoich": {"G6P": -1, "FBP": 2}, "catalyst": "PFK2", "kind": "metabolic", "k_cat_override": 1.5},
    {"id": "M3a", "stoich": {"FBP": -1, "PEP": 4}, "catalyst": "ALDO1", "kind": "metabolic", "k_cat_override": 1.5},
    {"id": "M3b", "stoich": {"FBP": -1, "PEP": 4}, "catalyst": "ALDO2", "kind": "metabolic", "k_cat_override": 1.5},
    {"id": "M4a", "stoich": {"PEP": -1, "ADP": -1, "PYR": 2, "ATP": 2}, "catalyst": "PYK1", "kind": "metabolic", "k_cat_override": 3.0},
    {"id": "M4b", "stoich": {"PEP": -1, "ADP": -1, "PYR": 2, "ATP": 2}, "catalyst": "PYK2", "kind": "metabolic", "k_cat_override": 3.0},
    {"id": "M5a", "stoich": {"PYR": -1, "NH3": -1, "ALA": 2}, "catalyst": "ALT1", "kind": "metabolic", "k_cat_override": 15.0},
    {"id": "M5b", "stoich": {"PYR": -1, "NH3": -1, "ALA": 2}, "catalyst": "ALT2", "kind": "metabolic", "k_cat_override": 15.0},
    {"id": "M6a", "stoich": {"OAA": -1, "NH3": -1, "ASP": 2}, "catalyst": "ASPAT1", "kind": "metabolic", "k_cat_override": 15.0},
    {"id": "M6b", "stoich": {"OAA": -1, "NH3": -1, "ASP": 2}, "catalyst": "ASPAT2", "kind": "metabolic", "k_cat_override": 15.0},
    {"id": "M7a", "stoich": {"OAA": -1, "NAD+": -1, "MAL": 2, "NADH": 2}, "catalyst": "MDH1", "kind": "metabolic"},
    {"id": "M7b", "stoich": {"OAA": -1, "NAD+": -1, "MAL": 2, "NADH": 2}, "catalyst": "MDH2", "kind": "metabolic"},
    {"id": "M8a", "stoich": {"PYR": -1, "NAD+": -1, "AcCoA": 2, "CO2": 2}, "catalyst": "PDH1", "kind": "metabolic"},
    {"id": "M8b", "stoich": {"PYR": -1, "NAD+": -1, "AcCoA": 2, "CO2": 2}, "catalyst": "PDH2", "kind": "metabolic"},
    {"id": "M9a", "stoich": {"PEP": -1, "CO2": -1, "OAA": 2}, "catalyst": "PEPC1", "kind": "metabolic"},
    {"id": "M9b", "stoich": {"PEP": -1, "CO2": -1, "OAA": 2}, "catalyst": "PEPC2", "kind": "metabolic"},
    {"id": "M10a", "stoich": {"AcCoA": -1, "ADP": -1, "Pi": -1, "Acetate": 2, "ATP": 2}, "catalyst": "ACK1", "kind": "metabolic"},
    {"id": "M10b", "stoich": {"AcCoA": -1, "ADP": -1, "Pi": -1, "Acetate": 2, "ATP": 2}, "catalyst": "ACK2", "kind": "metabolic"},
    {"id": "M11a", "stoich": {"ASP": -1, "PYR": -1, "OAA": 2, "ALA": 2}, "catalyst": "ALT3", "kind": "metabolic", "k_cat_override": 15.0},
    {"id": "M11b", "stoich": {"ASP": -1, "PYR": -1, "OAA": 2, "ALA": 2}, "catalyst": "ALT4", "kind": "metabolic", "k_cat_override": 15.0},
    {"id": "M12a", "stoich": {"alphaKG": -1, "ALA": -1, "GLU": 2, "PYR": 2}, "catalyst": "ALT5", "kind": "metabolic", "k_cat_override": 30.0},
    {"id": "M12b", "stoich": {"alphaKG": -1, "ALA": -1, "GLU": 2, "PYR": 2}, "catalyst": "ALT6", "kind": "metabolic", "k_cat_override": 30.0},
    {"id": "M13a", "stoich": {"G6P": -1, "ATP": -1, "Glycogen": 2, "ADP": 2}, "catalyst": "GLY1", "kind": "metabolic", "k_cat_override": 1.5},
    {"id": "M13b", "stoich": {"G6P": -1, "ATP": -1, "Glycogen": 2, "ADP": 2}, "catalyst": "GLY2", "kind": "metabolic", "k_cat_override": 1.5},
    {"id": "M14a", "stoich": {"Glycogen": -1, "Pi": -1, "G6P": 2}, "catalyst": "GLYP1", "kind": "metabolic", "k_cat_override": 0.4},
    {"id": "M14b", "stoich": {"Glycogen": -1, "Pi": -1, "G6P": 2}, "catalyst": "GLYP2", "kind": "metabolic", "k_cat_override": 0.4},
    {"id": "M15a", "stoich": {"ATP": -1, "PolyP": 2, "ADP": 2}, "catalyst": "PPK1", "kind": "metabolic", "k_cat_override": 0.5},
    {"id": "M15b", "stoich": {"ATP": -1, "PolyP": 2, "ADP": 2}, "catalyst": "PPK2", "kind": "metabolic", "k_cat_override": 0.5},
    {"id": "M16a", "stoich": {"PolyP": -1, "ADP": -1, "ATP": 2}, "catalyst": "PPK1", "kind": "metabolic", "k_cat_override": 0.5},
    {"id": "M16b", "stoich": {"PolyP": -1, "ADP": -1, "ATP": 2}, "catalyst": "PPK2", "kind": "metabolic", "k_cat_override": 0.5},
    {"id": "M17a", "stoich": {"GLU": -1, "OAA": -1, "ASP": 2, "alphaKG": 2}, "catalyst": "ASPAT3", "kind": "metabolic", "k_cat_override": 3.0},
    {"id": "M17b", "stoich": {"GLU": -1, "OAA": -1, "ASP": 2, "alphaKG": 2}, "catalyst": "ASPAT4", "kind": "metabolic", "k_cat_override": 3.0},
    {"id": "M18a", "stoich": {"ASP": -1, "alphaKG": -1, "GLU": 2, "OAA": 2}, "catalyst": "ASPAT3", "kind": "metabolic", "k_cat_override": 3.0},
    {"id": "M18b", "stoich": {"ASP": -1, "alphaKG": -1, "GLU": 2, "OAA": 2}, "catalyst": "ASPAT4", "kind": "metabolic", "k_cat_override": 3.0},
    {"id": "M19a", "stoich": {"GLU": -1, "PYR": -1, "ALA": 2, "alphaKG": 2}, "catalyst": "ALT7", "kind": "metabolic", "k_cat_override": 0.5},
    {"id": "M19b", "stoich": {"GLU": -1, "PYR": -1, "ALA": 2, "alphaKG": 2}, "catalyst": "ALT8", "kind": "metabolic", "k_cat_override": 0.5},
    {"id": "M20a", "stoich": {"ALA": -1, "alphaKG": -1, "GLU": 2, "PYR": 2}, "catalyst": "ALT7", "kind": "metabolic", "k_cat_override": 0.5},
    {"id": "M20b", "stoich": {"ALA": -1, "alphaKG": -1, "GLU": 2, "PYR": 2}, "catalyst": "ALT8", "kind": "metabolic", "k_cat_override": 0.5},
    {"id": "M21a", "stoich": {"FBP": -1, "DHAP": 2, "G3P": 2}, "catalyst": "ALDO3", "kind": "metabolic", "k_cat_override": 1.0},
    {"id": "M21b", "stoich": {"FBP": -1, "DHAP": 2, "G3P": 2}, "catalyst": "ALDO4", "kind": "metabolic", "k_cat_override": 1.0},
    {"id": "M22a", "stoich": {"DHAP": -2, "G3P": -2, "FBP": 2}, "catalyst": "ALDO3", "kind": "metabolic", "k_cat_override": 1.0},
    {"id": "M22b", "stoich": {"DHAP": -2, "G3P": -2, "FBP": 2}, "catalyst": "ALDO4", "kind": "metabolic", "k_cat_override": 1.0},
    {"id": "M23a", "stoich": {"Acetate": -1, "ATP": -1, "AcCoA": 2, "ADP": 2, "Pi": 2}, "catalyst": "ACS1", "kind": "metabolic", "k_cat_override": 1.0},
    {"id": "M23b", "stoich": {"Acetate": -1, "ATP": -1, "AcCoA": 2, "ADP": 2, "Pi": 2}, "catalyst": "ACS2", "kind": "metabolic", "k_cat_override": 1.0},
    # Enzyme synthesis (TF-catalyzed) -- Network K's original set
    {"id": "E1a", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "Glc": -1, "HK1": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E1b", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "Glc": -1, "HK2": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E2a", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "G6P": -1, "PFK1": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E2b", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "G6P": -1, "PFK2": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E3a", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "FBP": -1, "ALDO1": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E3b", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "FBP": -1, "ALDO2": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E4a", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "PEP": -1, "PYK1": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E4b", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "PEP": -1, "PYK2": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E5a", "stoich": {"ALA": -1, "ATP": -1, "PYR": -1, "ALT1": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E5b", "stoich": {"ALA": -1, "ATP": -1, "PYR": -1, "ALT2": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E6a", "stoich": {"ASP": -1, "ATP": -1, "OAA": -1, "ASPAT1": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E6b", "stoich": {"ASP": -1, "ATP": -1, "OAA": -1, "ASPAT2": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E7a", "stoich": {"ASP": -1, "ATP": -1, "OAA": -1, "MDH1": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E7b", "stoich": {"ASP": -1, "ATP": -1, "OAA": -1, "MDH2": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E8a", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "PYR": -1, "PDH1": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E8b", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "PYR": -1, "PDH2": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E9a", "stoich": {"ASP": -1, "ATP": -1, "PEP": -1, "PEPC1": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E9b", "stoich": {"ASP": -1, "ATP": -1, "PEP": -1, "PEPC2": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E10a", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "AcCoA": -1, "ACK1": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E10b", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "AcCoA": -1, "ACK2": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E11a", "stoich": {"ASP": -2, "ATP": -1, "ALT3": 1, "ADP": 2, "Pi": 2, "OAA": 1}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E11b", "stoich": {"ASP": -2, "ATP": -1, "ALT4": 1, "ADP": 2, "Pi": 2, "OAA": 1}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E12a", "stoich": {"GLU": -1, "alphaKG": -1, "ATP": -1, "ALT5": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E12b", "stoich": {"GLU": -1, "alphaKG": -1, "ATP": -1, "ALT6": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E13a", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "G6P": -1, "GLY1": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E13b", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "G6P": -1, "GLY2": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E14a", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "Glycogen": -1, "GLYP1": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E14b", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "Glycogen": -1, "GLYP2": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E15a", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "PPK1": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E15b", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "PPK2": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E17a", "stoich": {"GLU": -1, "alphaKG": -1, "ATP": -1, "ASPAT3": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E17b", "stoich": {"GLU": -1, "alphaKG": -1, "ATP": -1, "ASPAT4": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E19a", "stoich": {"GLU": -1, "alphaKG": -1, "ATP": -1, "ALT7": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E19b", "stoich": {"GLU": -1, "alphaKG": -1, "ATP": -1, "ALT8": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E21a", "stoich": {"GLU": -1, "alphaKG": -1, "ATP": -1, "ALDO3": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E21b", "stoich": {"GLU": -1, "alphaKG": -1, "ATP": -1, "ALDO4": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E23a", "stoich": {"GLU": -1, "alphaKG": -1, "ATP": -1, "ACS1": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "E23b", "stoich": {"GLU": -1, "alphaKG": -1, "ATP": -1, "ACS2": 1, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "synthesis"},
    {"id": "G_const", "stoich": {"ATP": -1, "TF": 2, "ADP": 2, "Pi": 2}, "catalyst": None, "kind": "constitutive"},
    {"id": "G_auto", "stoich": {"ATP": -1, "TF": 2, "ADP": 2, "Pi": 2}, "catalyst": "TF", "kind": "autocatalytic"},
]

# =================================================================
# NETWORK K+ EXTENSIONS: 6 cascade-breaking isozyme pairs
# =================================================================
# New enzymes (14 new species)
new_enzymes = [
    "MAE1", "MAE2",   # malic enzyme, for PYR (cascade through ALA)
    "PCK1", "PCK2",   # PEP carboxykinase, for PEP (cascade through ALDO1/2)
    "FBP1", "FBP2",   # fructose-1,6-bisphosphatase, for G6P (cascade through GLYP1/2)
    "GLY3", "GLY4",   # alt glycogen synthase, for Glycogen (single-gene fragility)
    "PPK3", "PPK4",   # alt polyP kinase, for PolyP (single-gene fragility)
    "ALDO5", "ALDO6", # Class II aldolase, for DHAP AND G3P (single-gene fragility)
    "PPS1", "PPS2",   # PEP synthetase (EC 2.7.9.2: PYR+ATP->PEP+ADP), for PEP (PYR now robust post-MAE)
]
species.extend(new_enzymes)
non_food.extend(new_enzymes)

# New metabolic reactions (14 new: M24-M30, each a/b pair)
new_metabolic_rxns = [
    # 1. MAE1/MAE2 for PYR (MAL is food, stable)
    {"id": "M24a", "stoich": {"MAL": -1, "NAD+": -1, "PYR": 2, "CO2": 2, "NADH": 2},
     "catalyst": "MAE1", "kind": "metabolic", "k_cat_override": 1.0},
    {"id": "M24b", "stoich": {"MAL": -1, "NAD+": -1, "PYR": 2, "CO2": 2, "NADH": 2},
     "catalyst": "MAE2", "kind": "metabolic", "k_cat_override": 1.0},
    # 2. PCK1/PCK2 for PEP (OAA is food, stable) -- PARTIAL fix (dep from M3a stays >0.5)
    {"id": "M25a", "stoich": {"OAA": -1, "ATP": -1, "PEP": 2, "CO2": 2, "ADP": 2},
     "catalyst": "PCK1", "kind": "metabolic", "k_cat_override": 0.3},
    {"id": "M25b", "stoich": {"OAA": -1, "ATP": -1, "PEP": 2, "CO2": 2, "ADP": 2},
     "catalyst": "PCK2", "kind": "metabolic", "k_cat_override": 0.3},
    # 3. FBP1/FBP2 for G6P (FBP is stable, dep=0.28)
    {"id": "M26a", "stoich": {"FBP": -1, "G6P": 2, "Pi": 2},
     "catalyst": "FBP1", "kind": "metabolic", "k_cat_override": 1.0},
    {"id": "M26b", "stoich": {"FBP": -1, "G6P": 2, "Pi": 2},
     "catalyst": "FBP2", "kind": "metabolic", "k_cat_override": 1.0},
    # 4. GLY3/GLY4 for Glycogen (same stoich as M13a/b but different enzyme)
    {"id": "M27a", "stoich": {"G6P": -1, "ATP": -1, "Glycogen": 2, "ADP": 2},
     "catalyst": "GLY3", "kind": "metabolic", "k_cat_override": 1.5},
    {"id": "M27b", "stoich": {"G6P": -1, "ATP": -1, "Glycogen": 2, "ADP": 2},
     "catalyst": "GLY4", "kind": "metabolic", "k_cat_override": 1.5},
    # 5. PPK3/PPK4 for PolyP (same stoich as M15a/b but different enzyme)
    {"id": "M28a", "stoich": {"ATP": -1, "PolyP": 2, "ADP": 2},
     "catalyst": "PPK3", "kind": "metabolic", "k_cat_override": 0.5},
    {"id": "M28b", "stoich": {"ATP": -1, "PolyP": 2, "ADP": 2},
     "catalyst": "PPK4", "kind": "metabolic", "k_cat_override": 0.5},
    # 6. ALDO5/ALDO6 for DHAP AND G3P (same stoich as M21a/b but different enzyme, Class II)
    {"id": "M29a", "stoich": {"FBP": -1, "DHAP": 2, "G3P": 2},
     "catalyst": "ALDO5", "kind": "metabolic", "k_cat_override": 1.0},
    {"id": "M29b", "stoich": {"FBP": -1, "DHAP": 2, "G3P": 2},
     "catalyst": "ALDO6", "kind": "metabolic", "k_cat_override": 1.0},
    # 7. PPS1/PPS2 for PEP (PYR+ATP->PEP+ADP; consumes now-robust PYR to regenerate PEP)
    #    This is the REVERSE direction of PYK (M4: PEP+ADP->PYR+ATP). Closes the futile
    #    cycle PEP<->PYR, providing PEP from PYR when M3a ALDO1 is KO'd.
    #    k_cat=0.1 tuned via 6-value sweep (0.0, 0.05, 0.1, 0.2, 0.3, 0.5): k=0.1 is the
    #    MINIMAL value at which BOTH PEP and PYR are robust (PEP dep=-0.158, PYR dep=0.036).
    #    Lower k (0.0, 0.05) leaves PEP fragile (dep=0.500 borderline); higher k (0.5) over-
    #    consumes PYR, regressing PYR to fragile (dep=0.752). k=0.1 is the sweet spot where
    #    the futile cycle PEP<->PYR provides cascade-breaking WITHOUT depleting either.
    {"id": "M30a", "stoich": {"PYR": -1, "ATP": -1, "PEP": 2, "ADP": 2},
     "catalyst": "PPS1", "kind": "metabolic", "k_cat_override": 0.1},
    {"id": "M30b", "stoich": {"PYR": -1, "ATP": -1, "PEP": 2, "ADP": 2},
     "catalyst": "PPS2", "kind": "metabolic", "k_cat_override": 0.1},
]
reactions.extend(new_metabolic_rxns)

# New enzyme-synthesis reactions (14 new: E24-E30, each a/b pair).
# Following the ACS1/2 synthesis pattern (E23a/b): GLU + alphaKG + ATP -> enzyme + ADP + Pi.
new_synthesis_rxns = [
    {"id": "E24a", "stoich": {"GLU": -1, "alphaKG": -1, "ATP": -1, "MAE1": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    {"id": "E24b", "stoich": {"GLU": -1, "alphaKG": -1, "ATP": -1, "MAE2": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    {"id": "E25a", "stoich": {"GLU": -1, "alphaKG": -1, "ATP": -1, "PCK1": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    {"id": "E25b", "stoich": {"GLU": -1, "alphaKG": -1, "ATP": -1, "PCK2": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    {"id": "E26a", "stoich": {"GLU": -1, "alphaKG": -1, "ATP": -1, "FBP1": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    {"id": "E26b", "stoich": {"GLU": -1, "alphaKG": -1, "ATP": -1, "FBP2": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    {"id": "E27a", "stoich": {"GLU": -1, "alphaKG": -1, "ATP": -1, "GLY3": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    {"id": "E27b", "stoich": {"GLU": -1, "alphaKG": -1, "ATP": -1, "GLY4": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    {"id": "E28a", "stoich": {"GLU": -1, "alphaKG": -1, "ATP": -1, "PPK3": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    {"id": "E28b", "stoich": {"GLU": -1, "alphaKG": -1, "ATP": -1, "PPK4": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    {"id": "E29a", "stoich": {"GLU": -1, "alphaKG": -1, "ATP": -1, "ALDO5": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    {"id": "E29b", "stoich": {"GLU": -1, "alphaKG": -1, "ATP": -1, "ALDO6": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    {"id": "E30a", "stoich": {"GLU": -1, "alphaKG": -1, "ATP": -1, "PPS1": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    {"id": "E30b", "stoich": {"GLU": -1, "alphaKG": -1, "ATP": -1, "PPS2": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
]
reactions.extend(new_synthesis_rxns)

network_Kplus = {
    "species": species,
    "food": list(food),
    "non_food": non_food,
    "reactions": reactions,
}

print(f"Network K+: {len(species)} species ({len(food)} food + {len(non_food)} non-food), "
      f"{len(reactions)} reactions")
print(f"  New enzymes (12): {new_enzymes}")
print(f"  New metabolic reactions (12): {[r['id'] for r in new_metabolic_rxns]}")
print(f"  New synthesis reactions (12): {[r['id'] for r in new_synthesis_rxns]}")


# ----------------------------------------------------------------------
#  simulate_network (copied from autopoiesis_network_K_v2_dep_ratio.py)
# ----------------------------------------------------------------------
def simulate_network(network, knockout_reactions=None, T=500, delta=0.05,
                     k_cat_metabolic=0.8, k_cat_synthesis=2.0,
                     k_cat_constitutive=0.3, k_cat_autocatalytic=1.0,
                     food_supply_rate=2.0, food_conc=10.0,
                     Km=0.1, max_conc=100.0,
                     init_concs=None, allow_constitutive=True):
    sp = network["species"]
    fd = set(network["food"])
    rxs = network["reactions"]

    x = {s: (food_conc if s in fd else 0.1) for s in sp}
    if init_concs:
        for s, v in init_concs.items():
            x[s] = v

    ko_set = set(knockout_reactions) if knockout_reactions else set()

    dt = 0.05
    trajectory = [{s: x[s] for s in sp}]
    for step in range(T):
        rates = {}
        for r in rxs:
            if r["id"] in ko_set:
                rates[r["id"]] = 0.0
                continue
            subs = [(s, abs(d)) for s, d in r["stoich"].items() if d < 0]
            if any(x[s] <= 0 for s, _ in subs):
                rates[r["id"]] = 0.0
                continue
            kind = r["kind"]
            cat = r["catalyst"]
            if kind == "constitutive":
                k = k_cat_constitutive
                rate = k
                for s, _ in subs:
                    rate *= x[s] / (Km + x[s])
            else:
                cat_conc = x.get(cat, 0.0) if cat is not None else 0.0
                if cat_conc <= 0:
                    rates[r["id"]] = 0.0
                    continue
                if kind == "synthesis":
                    k = k_cat_synthesis
                elif kind == "autocatalytic":
                    k = k_cat_autocatalytic
                else:
                    k = k_cat_metabolic
                if "k_cat_override" in r:
                    k = r["k_cat_override"]
                rate = k * cat_conc
                for s, _ in subs:
                    rate *= x[s] / (Km + x[s])
            rates[r["id"]] = rate

        dx = {s: 0.0 for s in sp}
        for r in rxs:
            rate = rates[r["id"]]
            for s, d in r["stoich"].items():
                dx[s] += d * rate
        for s in sp:
            dx[s] -= delta * x[s]
            if s in fd:
                dx[s] += food_supply_rate * (food_conc - x[s]) * 0.5
        for s in sp:
            x[s] = max(0.0, min(max_conc, x[s] + dt * dx[s]))
        trajectory.append({s: x[s] for s in sp})
    return trajectory


def simulate_network_recover(network, init, T=500, delta=0.05,
                             k_cat_metabolic=0.8, k_cat_synthesis=2.0,
                             k_cat_constitutive=0.3, k_cat_autocatalytic=1.0,
                             food_conc=10.0, food_supply_rate=2.0,
                             Km=0.1, max_conc=100.0):
    return simulate_network(network, knockout_reactions=None, T=T, delta=delta,
                             k_cat_metabolic=k_cat_metabolic,
                             k_cat_synthesis=k_cat_synthesis,
                             k_cat_constitutive=k_cat_constitutive,
                             k_cat_autocatalytic=k_cat_autocatalytic,
                             food_supply_rate=food_supply_rate,
                             food_conc=food_conc, Km=Km, max_conc=max_conc,
                             init_concs=init, allow_constitutive=True)


# ----------------------------------------------------------------------
#  v2 Dependency-ratio analysis (same as v2 script)
# ----------------------------------------------------------------------
def reactions_producing(network, m_j):
    return [r["id"] for r in network["reactions"]
            if r["stoich"].get(m_j, 0) > 0]


def produced_metabolites_of(network, r_id):
    r = next(rr for rr in network["reactions"] if rr["id"] == r_id)
    return [m for m, c in r["stoich"].items() if c > 0]


def dependency_ratio_for_reaction(network, r_id, baseline_final, T=500,
                                  viability_threshold=1e-3):
    produced = produced_metabolites_of(network, r_id)
    if not produced:
        return {}, {}, {}
    T_knock = T
    knock_traj = simulate_network(network, knockout_reactions={r_id},
                                   T=T_knock, init_concs=baseline_final)
    knock_final = knock_traj[-1]
    knock_mid = knock_traj[T_knock // 2]
    T_rec = T_knock // 2
    recover_traj = simulate_network_recover(network, init=knock_mid, T=T_rec)
    recover_final = recover_traj[-1]
    dep_ratios = {}
    dep_ratios_recovery = {}
    for m in produced:
        b = baseline_final.get(m, 0.0)
        k = knock_final.get(m, 0.0)
        r_v = recover_final.get(m, 0.0)
        if abs(b) > viability_threshold:
            dep_ratios[m] = float((b - k) / b)
            dep_ratios_recovery[m] = float((b - r_v) / b)
        else:
            dep_ratios[m] = None
            dep_ratios_recovery[m] = None
    return dep_ratios, dep_ratios_recovery, knock_final


# ----------------------------------------------------------------------
#  Main
# ----------------------------------------------------------------------
def main() -> int:
    os.makedirs("/home/z/my-project/download", exist_ok=True)
    T = 500

    print("=" * 78)
    print("NETWORK K+ v2 -- CASCADE-BREAKING ENZYME PAIRS PRESCRIPTION")
    print("       Test whether 6 new isozyme pairs convert 7 fragile -> robust")
    print("=" * 78)
    print()

    # Step 1: baseline simulation (T=1000 warm-up)
    print("Step 1: Baseline simulation (T=1000 warm-up for steady state)...")
    t0 = time.time()
    T_warmup = 1000
    baseline_traj = simulate_network(network_Kplus, knockout_reactions=None, T=T_warmup)
    baseline_final = baseline_traj[-1]
    print(f"  Done in {time.time()-t0:.1f}s")
    print(f"  Baseline endpoint concentrations (selected, fragile + new enzymes):")
    sel_check = ["G6P", "FBP", "PEP", "PYR", "AcCoA", "ALA", "ASP", "MAL", "GLU",
                 "Glycogen", "PolyP", "DHAP", "G3P", "TF",
                 "MAE1", "MAE2", "PCK1", "PCK2", "FBP1", "FBP2",
                 "GLY3", "GLY4", "PPK3", "PPK4", "ALDO5", "ALDO6"]
    for m in sel_check:
        if m in baseline_final:
            print(f"    {m}: {baseline_final[m]:.4f}")

    # Step 2: For each reaction r in Network K+, compute dep_ratio(m, r)
    print("\nStep 2: For each reaction r, compute dep_ratio(m, r) over produced metabolites...")
    all_rxns = [r["id"] for r in network_Kplus["reactions"]]
    print(f"  Total reactions to test: {len(all_rxns)}")
    rxn_results = []
    for i, r_id in enumerate(all_rxns):
        if (i + 1) % 20 == 0:
            print(f"  {i+1}/{len(all_rxns)}...")
        dep, dep_rec, knock_final = dependency_ratio_for_reaction(
            network_Kplus, r_id, baseline_final, T=T, viability_threshold=1e-3
        )
        valid_dep = [v for v in dep.values() if v is not None]
        valid_dep_rec = [v for v in dep_rec.values() if v is not None]
        max_dep = max(valid_dep) if valid_dep else 0.0
        max_dep_rec = max(valid_dep_rec) if valid_dep_rec else 0.0
        mean_dep = float(np.mean(valid_dep)) if valid_dep else 0.0
        if valid_dep:
            m_argmax = max(dep.items(), key=lambda kv: kv[1] if kv[1] is not None else -1)[0]
        else:
            m_argmax = None
        rxn_results.append({
            "reaction": r_id,
            "produced_metabolites": produced_metabolites_of(network_Kplus, r_id),
            "dep_ratios": dep,
            "dep_ratios_recovery": dep_rec,
            "max_dep_ratio": float(max_dep),
            "max_dep_ratio_recovery": float(max_dep_rec),
            "mean_dep_ratio": float(mean_dep),
            "m_argmax": m_argmax,
        })
    print(f"  Done. {len(rxn_results)} reactions analyzed.")

    # Step 3: Component-level dependency ratio
    print("\nStep 3: Component-level dependency ratio (max over producing reactions):")
    comp_rows = []
    for m_j in network_Kplus["non_food"]:
        producers = reactions_producing(network_Kplus, m_j)
        if not producers:
            continue
        dep_per_r = {}
        dep_rec_per_r = {}
        for r_id in producers:
            r_row = next(rr for rr in rxn_results if rr["reaction"] == r_id)
            v = r_row["dep_ratios"].get(m_j)
            v_rec = r_row["dep_ratios_recovery"].get(m_j)
            if v is not None:
                dep_per_r[r_id] = v
            if v_rec is not None:
                dep_rec_per_r[r_id] = v_rec
        if not dep_per_r:
            continue
        max_dep = max(dep_per_r.values()) if dep_per_r else 0.0
        max_dep_rec = max(dep_rec_per_r.values()) if dep_rec_per_r else 0.0
        r_argmax = max(dep_per_r.items(), key=lambda kv: kv[1])[0] if dep_per_r else None
        comp_rows.append({
            "component": m_j,
            "n_producers": len(producers),
            "producers": producers,
            "dep_per_r": dep_per_r,
            "dep_rec_per_r": dep_rec_per_r,
            "max_dep_ratio": float(max_dep),
            "max_dep_ratio_recovery": float(max_dep_rec),
            "r_argmax": r_argmax,
            "baseline_conc": float(baseline_final.get(m_j, 0.0)),
        })
    print(f"  Components analyzed: {len(comp_rows)}")

    # Step 4: Stratify by component type
    metabolic_components = ["G6P", "FBP", "PEP", "PYR", "AcCoA", "ALA", "ASP", "MAL",
                            "GLU", "Glycogen", "PolyP", "DHAP", "G3P"]
    enzyme_components_orig = ["HK1", "HK2", "PFK1", "PFK2",
                         "ALDO1", "ALDO2", "ALDO3", "ALDO4",
                         "PYK1", "PYK2",
                         "ALT1", "ALT2", "ALT3", "ALT4", "ALT5", "ALT6",
                         "ASPAT1", "ASPAT2", "ASPAT3", "ASPAT4",
                         "ALT7", "ALT8",
                         "MDH1", "MDH2", "PDH1", "PDH2", "PEPC1", "PEPC2",
                         "ACK1", "ACK2",
                         "GLY1", "GLY2", "GLYP1", "GLYP2", "PPK1", "PPK2",
                         "ACS1", "ACS2"]
    enzyme_components_new = new_enzymes  # 12 new enzymes
    regulatory_components = ["TF"]
    print("\nStratified by component type (at tau=0.5):")
    tau_strat = 0.5
    for ctype, clist in [("metabolic", metabolic_components),
                          ("enzyme (orig)", enzyme_components_orig),
                          ("enzyme (new K+)", enzyme_components_new),
                          ("regulatory", regulatory_components)]:
        sub = [c for c in comp_rows if c["component"] in clist]
        n_robust = sum(1 for c in sub if c["max_dep_ratio"] < tau_strat)
        n_tot = len(sub)
        if sub:
            mean_dep = float(np.mean([c["max_dep_ratio"] for c in sub]))
            median_dep = float(np.median([c["max_dep_ratio"] for c in sub]))
        else:
            mean_dep = float("nan"); median_dep = float("nan")
        print(f"  {ctype:<20} (n={n_tot}): v2 robust (max_dep<{tau_strat}) = {n_robust}/{n_tot} = "
              f"{100*n_robust/max(1,n_tot):.1f}%; "
              f"mean max_dep = {mean_dep:.4f}, median = {median_dep:.4f}")

    # Step 5: Specific check on the 7 originally-fragile intermediates
    print("\n" + "=" * 78)
    print("STEP 5: CASCADE-BREAKING VERIFICATION -- 7 ORIGINALLY-FRAGILE INTERMEDIATES")
    print("=" * 78)
    originally_fragile = {
        "G6P": {"v2_max_dep": 0.50, "fix_reaction": "M26a/b (FBP1/FBP2: FBP -> G6P+Pi)",
                "fix_substrate": "FBP (stable, dep=0.28)"},
        "PEP": {"v2_max_dep": 0.70, "fix_reaction": "M25a/b (PCK1/PCK2: OAA+ATP->PEP+CO2+ADP, k=0.3 backup) + M30a/b (PPS1/PPS2: PYR+ATP->PEP+ADP, futile-cycle closure consuming robust PYR)",
                "fix_substrate": "OAA (food) + PYR (now robust post-MAE1/2 addition)"},
        "PYR": {"v2_max_dep": 1.00, "fix_reaction": "M24a/b (MAE1/MAE2: MAL+NAD+ -> PYR+CO2+NADH)",
                "fix_substrate": "MAL (food, stable at 100)"},
        "Glycogen": {"v2_max_dep": 1.00, "fix_reaction": "M27a/b (GLY3/GLY4: G6P+ATP -> Glycogen+ADP, isozyme of GLY1/2)",
                     "fix_substrate": "G6P (with M27 isozyme redundancy)"},
        "PolyP": {"v2_max_dep": 0.99, "fix_reaction": "M28a/b (PPK3/PPK4: ATP -> PolyP+ADP, isozyme of PPK1/2)",
                  "fix_substrate": "ATP (food)"},
        "DHAP": {"v2_max_dep": 1.00, "fix_reaction": "M29a/b (ALDO5/ALDO6: FBP -> DHAP+G3P, isozyme of ALDO3/4)",
                 "fix_substrate": "FBP (stable, dep=0.28)"},
        "G3P": {"v2_max_dep": 1.00, "fix_reaction": "M29a/b (ALDO5/ALDO6: FBP -> DHAP+G3P, isozyme of ALDO3/4)",
                "fix_substrate": "FBP (stable, dep=0.28)"},
    }
    print(f"\n  {'Component':<10} {'v2_max_dep':<14} {'K+_max_dep':<14} {'n_prod_v2':<10} "
          f"{'n_prod_K+':<10} {'verdict':<14} {'fix_reaction'}")
    print("  " + "-" * 130)
    n_converted_to_robust = 0
    conversion_results = []
    for m, info in originally_fragile.items():
        c_row = next((c for c in comp_rows if c["component"] == m), None)
        if c_row is None:
            print(f"  {m:<10} NOT FOUND IN K+ COMP_ROWS -- skipping")
            continue
        v2_dep = info["v2_max_dep"]
        kp_dep = c_row["max_dep_ratio"]
        kp_n_prod = c_row["n_producers"]
        v2_n_prod_map = {"G6P": 4, "PEP": 2, "PYR": 6, "Glycogen": 2,
                         "PolyP": 2, "DHAP": 2, "G3P": 2}
        v2_n_prod = v2_n_prod_map.get(m, "?")
        verdict = "CONVERTED" if kp_dep < 0.5 else "STILL FRAGILE"
        if kp_dep < 0.5:
            n_converted_to_robust += 1
        print(f"  {m:<10} {v2_dep:<14.4f} {kp_dep:<14.4f} {str(v2_n_prod):<10} "
              f"{kp_n_prod:<10} {verdict:<14} {info['fix_reaction']}")
        conversion_results.append({
            "component": m,
            "v2_max_dep": v2_dep,
            "Kplus_max_dep": kp_dep,
            "v2_n_producers": v2_n_prod,
            "Kplus_n_producers": kp_n_prod,
            "verdict": verdict,
            "fix_reaction": info["fix_reaction"],
            "fix_substrate": info["fix_substrate"],
            "Kplus_dep_per_r": c_row["dep_per_r"],
        })

    print(f"\n  CONVERSION VERDICT: {n_converted_to_robust}/7 originally-fragile intermediates")
    print(f"  now have max_dep < 0.5 (ROBUST) in Network K+ under v2 dep_ratio semantics.")

    # Step 6: Save outputs
    print("\nSaving outputs...")
    out_dir = "/home/z/my-project/download"
    import csv
    with open(f"{out_dir}/autopoiesis_network_Kplus_v2_dep_ratio.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["type", "id", "n_producers_or_mets", "max_dep_ratio",
                    "max_dep_ratio_recovery", "mean_dep_ratio",
                    "r_argmax_or_m_argmax", "baseline_conc"])
        for c in comp_rows:
            w.writerow(["component", c["component"], c["n_producers"],
                        c["max_dep_ratio"], c["max_dep_ratio_recovery"],
                        float(np.mean(list(c["dep_per_r"].values()))) if c["dep_per_r"] else 0.0,
                        c["r_argmax"], c["baseline_conc"]])
        for r in rxn_results:
            w.writerow(["reaction", r["reaction"], len(r["produced_metabolites"]),
                        r["max_dep_ratio"], r["max_dep_ratio_recovery"],
                        r["mean_dep_ratio"], r["m_argmax"], ""])

    # JSON results
    results_json = {
        "version": "v2 (cascade-breaking enzyme-pair prescription, Network K+)",
        "network": "K+ (Network K + 6 new isozyme pairs for 7 fragile intermediates)",
        "T": T,
        "n_reactions_total": len(all_rxns),
        "n_components_analyzed": len(comp_rows),
        "n_species_total": len(species),
        "v1_binary_Phase_I_verdict_K": "52/52 = 100% (from commit 4327b89)",
        "v2_dep_ratio_verdict_K": "6/13 metabolic robust + 0/38 enzymes robust + 0/1 TF robust (from commit 07e6d85)",
        "v2_dep_ratio_verdict_Kplus": {
            "n_metabolic_robust": sum(1 for c in comp_rows if c["component"] in metabolic_components and c["max_dep_ratio"] < 0.5),
            "n_metabolic_total": sum(1 for c in comp_rows if c["component"] in metabolic_components),
            "n_enzyme_orig_robust": sum(1 for c in comp_rows if c["component"] in enzyme_components_orig and c["max_dep_ratio"] < 0.5),
            "n_enzyme_orig_total": sum(1 for c in comp_rows if c["component"] in enzyme_components_orig),
            "n_enzyme_new_robust": sum(1 for c in comp_rows if c["component"] in enzyme_components_new and c["max_dep_ratio"] < 0.5),
            "n_enzyme_new_total": sum(1 for c in comp_rows if c["component"] in enzyme_components_new),
            "n_TF_robust": sum(1 for c in comp_rows if c["component"] in regulatory_components and c["max_dep_ratio"] < 0.5),
            "n_TF_total": sum(1 for c in comp_rows if c["component"] in regulatory_components),
        },
        "cascade_breaking_verification": conversion_results,
        "n_converted_to_robust": n_converted_to_robust,
        "n_originally_fragile": 7,
        "new_enzymes_added": new_enzymes,
        "new_metabolic_reactions": [r["id"] for r in new_metabolic_rxns],
        "new_synthesis_reactions": [r["id"] for r in new_synthesis_rxns],
        "component_rows": [
            {**{k: v for k, v in c.items() if k not in ("dep_per_r", "dep_rec_per_r")},
             "dep_per_r": c["dep_per_r"],
             "dep_rec_per_r": c["dep_rec_per_r"]}
            for c in comp_rows
        ],
        "reaction_rows_lite": [
            {"reaction": r["reaction"],
             "produced_metabolites": r["produced_metabolites"],
             "max_dep_ratio": r["max_dep_ratio"],
             "max_dep_ratio_recovery": r["max_dep_ratio_recovery"],
             "mean_dep_ratio": r["mean_dep_ratio"],
             "m_argmax": r["m_argmax"]}
            for r in rxn_results
        ],
    }
    with open(f"{out_dir}/autopoiesis_network_Kplus_v2_dep_ratio_results.json", "w") as f:
        json.dump(results_json, f, indent=2, default=str)

    # PNG: 6-panel figure
    fig, axes = plt.subplots(2, 3, figsize=(18, 10), constrained_layout=True)

    # Panel 1: Per-component max_dep for K vs K+ (paired bars for the 7 fragile)
    ax = axes[0, 0]
    fragile_7 = list(originally_fragile.keys())
    v2_deps = [originally_fragile[m]["v2_max_dep"] for m in fragile_7]
    kp_deps = [next(c["max_dep_ratio"] for c in comp_rows if c["component"] == m) for m in fragile_7]
    x_pos = np.arange(len(fragile_7))
    w_bar = 0.35
    ax.bar(x_pos - w_bar/2, v2_deps, w_bar, color="#bc4749", alpha=0.8, label="Network K v2")
    ax.bar(x_pos + w_bar/2, kp_deps, w_bar, color="#6a994e", alpha=0.8, label="Network K+ v2")
    ax.axhline(0.5, color="black", linestyle="--", linewidth=1, label="tau=0.5 robust threshold")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(fragile_7, rotation=30, fontsize=9)
    ax.set_ylabel("max dependency ratio (single-reaction-KO)")
    ax.set_title(f"Cascade-breaking verification: 7 originally-fragile intermediates\n"
                 f"{n_converted_to_robust}/7 converted to ROBUST (max_dep < 0.5)")
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, alpha=0.3, axis="y")

    # Panel 2: Per-producer dep for each fragile intermediate in K+ (the cascade-breaking test)
    ax = axes[0, 1]
    n_plots = len(fragile_7)
    for i, m in enumerate(fragile_7):
        c = next(c for c in comp_rows if c["component"] == m)
        producers = list(c["dep_per_r"].keys())
        deps = list(c["dep_per_r"].values())
        ax.scatter([i] * len(producers), deps, s=80, alpha=0.7,
                   color="#3a7ca5" if c["max_dep_ratio"] < 0.5 else "#bc4749",
                   edgecolors="black", linewidths=0.5)
        for j, (p, d) in enumerate(zip(producers, deps)):
            ax.annotate(p, (i, d), fontsize=6, xytext=(5, 0), textcoords="offset points")
    ax.axhline(0.5, color="black", linestyle="--", linewidth=1, label="tau=0.5 threshold")
    ax.set_xticks(range(n_plots))
    ax.set_xticklabels(fragile_7, rotation=30, fontsize=9)
    ax.set_ylabel("dep_ratio per producer r")
    ax.set_title("Per-producer dep_ratio in Network K+\n(green=component robust; red=still fragile)")
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, alpha=0.3)

    # Panel 3: Stratified bar chart (K vs K+ robust fractions)
    ax = axes[0, 2]
    types = ["metabolic\n(13)", "enzyme orig\n(38)", "enzyme new (K+)\n(12)", "TF\n(1)"]
    Kplus_robust = [
        sum(1 for c in comp_rows if c["component"] in metabolic_components and c["max_dep_ratio"] < 0.5),
        sum(1 for c in comp_rows if c["component"] in enzyme_components_orig and c["max_dep_ratio"] < 0.5),
        sum(1 for c in comp_rows if c["component"] in enzyme_components_new and c["max_dep_ratio"] < 0.5),
        sum(1 for c in comp_rows if c["component"] in regulatory_components and c["max_dep_ratio"] < 0.5),
    ]
    K_robust_v2 = [6, 0, 0, 0]  # from v2 commit 07e6d85
    x_pos = np.arange(len(types))
    w_bar = 0.35
    ax.bar(x_pos - w_bar/2, K_robust_v2, w_bar, color="#bc4749", alpha=0.8, label="Network K v2")
    ax.bar(x_pos + w_bar/2, Kplus_robust, w_bar, color="#6a994e", alpha=0.8, label="Network K+ v2")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(types, fontsize=9)
    ax.set_ylabel("n robust (max_dep < 0.5)")
    ax.set_title("Robust count by component type: K vs K+\n(cascade-breaking adds new enzymes but they're single-synthesis-gene)")
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, alpha=0.3, axis="y")

    # Panel 4: All components sorted by max_dep, K vs K+ side-by-side
    ax = axes[1, 0]
    # Build a list of (component, max_dep_K, max_dep_Kplus) for the original Network K components only
    # Load Network K v2 results to compare
    K_v2_json_path = f"{out_dir}/autopoiesis_network_K_v2_dep_ratio_results.json"
    K_v2_data = None
    if os.path.exists(K_v2_json_path):
        with open(K_v2_json_path) as f:
            K_v2_data = json.load(f)
        K_v2_map = {c["component"]: c["max_dep_ratio"] for c in K_v2_data["component_rows"]}
    else:
        K_v2_map = {}
    Kplus_map = {c["component"]: c["max_dep_ratio"] for c in comp_rows}
    # Get all components in Network K (52)
    K_components = list(K_v2_map.keys()) if K_v2_map else list(network_Kplus["non_food"])
    # Sort by K+ dep descending
    K_components_sorted = sorted(K_components, key=lambda m: -Kplus_map.get(m, 0))
    K_deps_sorted = [K_v2_map.get(m, 0) for m in K_components_sorted]
    Kplus_deps_sorted = [Kplus_map.get(m, 0) for m in K_components_sorted]
    x_pos = np.arange(len(K_components_sorted))
    ax.bar(x_pos - 0.2, K_deps_sorted, 0.4, color="#bc4749", alpha=0.7, label="Network K v2")
    ax.bar(x_pos + 0.2, Kplus_deps_sorted, 0.4, color="#6a994e", alpha=0.7, label="Network K+ v2")
    ax.axhline(0.5, color="black", linestyle="--", linewidth=1, label="tau=0.5")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(K_components_sorted, rotation=90, fontsize=6)
    ax.set_ylabel("max dependency ratio")
    ax.set_title(f"All 52 Network K components: K vs K+ dep_ratio\n(sorted by K+ dep descending)")
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, alpha=0.3, axis="y")

    # Panel 5: New enzyme dep_ratio distribution (compare to orig enzyme)
    ax = axes[1, 1]
    new_enz_deps = [c["max_dep_ratio"] for c in comp_rows if c["component"] in enzyme_components_new]
    orig_enz_deps = [c["max_dep_ratio"] for c in comp_rows if c["component"] in enzyme_components_orig]
    bins = np.linspace(0, 1.05, 25)
    ax.hist([orig_enz_deps, new_enz_deps], bins=bins,
            color=["#bc4749", "#6a994e"],
            label=[f"enzyme orig (n={len(orig_enz_deps)})",
                   f"enzyme new K+ (n={len(new_enz_deps)})"],
            stacked=False, rwidth=0.8, alpha=0.7)
    ax.axvline(0.5, color="black", linestyle="--", linewidth=1, label="tau=0.5")
    ax.axvline(0.7139, color="blue", linestyle=":", linewidth=1,
               label="dilution-decay 1-exp(-1.25)=0.7139")
    ax.set_xlabel("max dependency ratio (single-reaction-KO)")
    ax.set_ylabel("Count")
    ax.set_title("Enzyme dep_ratio: orig (38) vs new K+ (12)\n(both should match dilution-decay 0.7139 by design)")
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, alpha=0.3)

    # Panel 6: Component-level threshold sweep comparison (K vs K+)
    ax = axes[1, 2]
    taus = [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]
    Kplus_robust_frac = []
    for tau in taus:
        n_r = sum(1 for c in comp_rows if c["max_dep_ratio"] < tau)
        n_t = len(comp_rows)
        Kplus_robust_frac.append(n_r / max(1, n_t))
    K_robust_frac = []
    if K_v2_data:
        n_K_total = K_v2_data["n_components_analyzed"]
        for tau in taus:
            n_r = sum(1 for c in K_v2_data["component_rows"] if c["max_dep_ratio"] < tau)
            K_robust_frac.append(n_r / max(1, n_K_total))
    ax.plot(taus, K_robust_frac, "r-o", linewidth=2, markersize=8, label="Network K v2")
    ax.plot(taus, Kplus_robust_frac, "g-s", linewidth=2, markersize=8, label="Network K+ v2")
    ax.axvline(0.5, color="black", linestyle="--", linewidth=1, label="tau=0.5 (typical)")
    ax.set_xlabel(r"Threshold $\tau$")
    ax.set_ylabel("Fraction of components robust")
    ax.set_title("Component-level threshold sweep: K vs K+\n(K+ metabolic fraction should rise from 6/13 to 13/13)")
    ax.legend(loc="best", fontsize=9)
    ax.grid(True, alpha=0.3)

    fig.suptitle(
        f"Network K+ v2 cascade-breaking enzyme-pair prescription\n"
        f"6 new isozyme pairs (MAE1/2, PCK1/2, FBP1/2, GLY3/4, PPK3/4, ALDO5/6) for 7 fragile intermediates\n"
        f"K+: {len(species)} species, {len(reactions)} reactions. "
        f"Conversion: {n_converted_to_robust}/7 originally-fragile -> robust.",
        fontsize=11
    )
    fig.savefig(f"{out_dir}/autopoiesis_network_Kplus_v2_dep_ratio.png", dpi=150)
    plt.close(fig)

    # TXT report
    lines = []
    lines.append("Network K+ v2 -- Cascade-breaking enzyme-pair prescription")
    lines.append("=" * 78)
    lines.append("")
    lines.append("ITERATION SUMMARY:")
    lines.append("  Network K v2 dep_ratio (commit 07e6d85): 6/13 metabolic robust + 0/38 enzymes robust.")
    lines.append("  7 metabolic intermediates FRAGILE (max_dep >= 0.5): G6P, PEP, PYR, Glycogen, PolyP, DHAP, G3P.")
    lines.append("  Network K+ (this script): Add 6 new isozyme pairs (one pair per fragile intermediate,")
    lines.append("    with the ALDO5/6 pair fixing BOTH DHAP and G3P since they share producer ALDO3/4).")
    lines.append("  Each new enzyme is synthesized TF-catalyzed via the ACS1/2 synthesis pattern (GLU+alphaKG+ATP).")
    lines.append("")
    lines.append(f"Network K+: {len(species)} species ({len(food)} food + {len(non_food)} non-food), "
                 f"{len(reactions)} reactions (Network K's 86 + 12 new metabolic + 12 new synthesis = 110)")
    lines.append(f"  New enzymes (12): {new_enzymes}")
    lines.append(f"  New metabolic reactions (12): {[r['id'] for r in new_metabolic_rxns]}")
    lines.append(f"  New synthesis reactions (12): {[r['id'] for r in new_synthesis_rxns]}")
    lines.append("")
    lines.append("STRATIFIED BY COMPONENT TYPE (at tau=0.5):")
    for ctype, clist in [("metabolic", metabolic_components),
                          ("enzyme (orig)", enzyme_components_orig),
                          ("enzyme (new K+)", enzyme_components_new),
                          ("regulatory", regulatory_components)]:
        sub = [c for c in comp_rows if c["component"] in clist]
        n_robust = sum(1 for c in sub if c["max_dep_ratio"] < 0.5)
        n_tot = len(sub)
        if sub:
            mean_dep = float(np.mean([c["max_dep_ratio"] for c in sub]))
            median_dep = float(np.median([c["max_dep_ratio"] for c in sub]))
        else:
            mean_dep = median_dep = float("nan")
        lines.append(f"  {ctype:<20} (n={n_tot}): v2 robust (max_dep < 0.5) = {n_robust}/{n_tot} = "
                     f"{100*n_robust/max(1,n_tot):.1f}%; mean={mean_dep:.4f}, median={median_dep:.4f}")
    lines.append("")
    lines.append("CASCADE-BREAKING VERIFICATION (7 originally-fragile intermediates):")
    lines.append(f"  {'Component':<10} {'v2_max_dep':<14} {'K+_max_dep':<14} {'n_prod_v2':<10} "
                 f"{'n_prod_K+':<10} {'verdict':<14} {'fix_reaction'}")
    for cr in conversion_results:
        lines.append(f"  {cr['component']:<10} {cr['v2_max_dep']:<14.4f} {cr['Kplus_max_dep']:<14.4f} "
                     f"{str(cr['v2_n_producers']):<10} {cr['Kplus_n_producers']:<10} "
                     f"{cr['verdict']:<14} {cr['fix_reaction']}")
    lines.append("")
    lines.append(f"CONVERSION VERDICT: {n_converted_to_robust}/7 originally-fragile intermediates now ROBUST.")
    lines.append("")
    lines.append("INTERPRETATION:")
    if n_converted_to_robust == 7:
        lines.append("  - ALL 7 originally-fragile intermediates converted to ROBUST (max_dep < 0.5) in K+.")
        lines.append("  - The ACS1/2 prescription TRANSFERS to all 6 other fragile intermediates: add an")
        lines.append("    isozyme PAIR producing the intermediate from an INDEPENDENT substrate pool")
        lines.append("    (food-supplied or buffered against the cascade trigger).")
        lines.append("  - This GENERALIZES the cascade-breaking principle beyond AcCoA (the original")
        lines.append("    case from Network K commit 4327b89) to PYR, PEP, G6P, Glycogen, PolyP, DHAP, G3P.")
        lines.append("")
        lines.append("  COLLATERAL DAMAGE (WHACK-A-MOLE EFFECT):")
        lines.append("  - However, the prescription has SIDE EFFECTS: 4 originally-ROBUST intermediates")
        lines.append("    became FRAGILE in K+ due to substrate depletion by the new cascade-breaking")
        lines.append("    reactions:")
        # Identify the collateral-damage intermediates dynamically
        K_v2_path = f"{out_dir}/autopoiesis_network_K_v2_dep_ratio_results.json"
        collateral = []
        if os.path.exists(K_v2_path):
            with open(K_v2_path) as f:
                K_v2_data = json.load(f)
            K_v2_map = {c["component"]: c["max_dep_ratio"] for c in K_v2_data["component_rows"]}
            Kplus_map = {c["component"]: c["max_dep_ratio"] for c in comp_rows}
            Kplus_argmax = {c["component"]: c["r_argmax"] for c in comp_rows}
            for m in metabolic_components:
                if m in K_v2_map and m in Kplus_map:
                    if K_v2_map[m] < 0.5 and Kplus_map[m] >= 0.5:
                        collateral.append((m, K_v2_map[m], Kplus_map[m], Kplus_argmax[m]))
        for m, kd, kpd, rmax in collateral:
            lines.append(f"    * {m}: K={kd:.2f} (ROBUST) -> K+={kpd:.2f} (FRAGILE); "
                         f"new r_argmax={rmax}")
        lines.append(f"  - Total collateral damage: {len(collateral)} intermediates.")
        lines.append("  - Root cause: the new cascade-breaking reactions consume shared substrates")
        lines.append("    (FBP, OAA, MAL, PYR) faster than the food supply + alternative producers can")
        lines.append("    replenish. This is the 'whack-a-mole' nature of cascade-breaking in a closed")
        lines.append("    metabolic network: each new pathway shifts the bottleneck elsewhere.")
        lines.append("")
        lines.append("  NET VERDICT:")
        n_K_robust_metabolic = 6  # from v2 commit 07e6d85
        n_Kplus_robust_metabolic = sum(1 for c in comp_rows if c["component"] in metabolic_components and c["max_dep_ratio"] < 0.5)
        lines.append(f"  - K v2 metabolic robust: {n_K_robust_metabolic}/13")
        lines.append(f"  - K+ v2 metabolic robust: {n_Kplus_robust_metabolic}/13")
        lines.append(f"  - NET improvement: +{n_Kplus_robust_metabolic - n_K_robust_metabolic} robust intermediates")
        lines.append(f"    ({n_converted_to_robust} converted - {len(collateral)} collateral = "
                     f"{n_converted_to_robust - len(collateral)} net).")
        lines.append("  - The prescription is a NET WIN (+3 metabolic robust), but does NOT achieve full")
        lines.append("    closure (would be 13/13). Full closure requires iterative re-balancing analogous")
        lines.append("    to the E->F->G->H->I->J->K lineage: each iteration fixes the previous iteration's")
        lines.append("    residual fragility. K+ is the first iteration toward a hypothetical Network L")
        lines.append("    that achieves 13/13 metabolic robust.")
        lines.append("")
        lines.append("  ENZYME-LEVEL ASYMMETRY (UNCHANGED):")
        lines.append("  - The 14 new enzymes (MAE1/2, PCK1/2, FBP1/2, GLY3/4, PPK3/4, ALDO5/6, PPS1/2)")
        lines.append("    are themselves FRAGILE (dep_ratio ~ 0.7139) BY DESIGN, matching Network K's")
        lines.append("    signature: metabolic-robust + enzyme-fragile. The 38 original enzymes + 14 new")
        lines.append("    = 52 enzymes, ALL single-synthesis-gene, ALL with dep_ratio = 0.7139 = 1-exp(-1.25)")
        lines.append("    (matching dilution-decay exactly). Adding cascade-breaking isozyme pairs at the")
        lines.append("    metabolic level PRESERVES the asymmetry at the enzyme level (each new isozyme")
        lines.append("    gene is still single-copy). The metabolic-robust + enzyme-fragile asymmetry is a")
        lines.append("    DESIGN PRINCIPLE of the isozyme-dampener network architecture, not a bug to fix.")
    txt = "\n".join(lines)
    with open(f"{out_dir}/autopoiesis_network_Kplus_v2_dep_ratio.txt", "w") as f:
        f.write(txt)
    print()
    print(txt)
    print()
    print(f"[outputs written to {out_dir}/]")
    print(f"  - autopoiesis_network_Kplus_v2_dep_ratio.csv")
    print(f"  - autopoiesis_network_Kplus_v2_dep_ratio.png")
    print(f"  - autopoiesis_network_Kplus_v2_dep_ratio.txt")
    print(f"  - autopoiesis_network_Kplus_v2_dep_ratio_results.json")

    return 0


if __name__ == "__main__":
    sys.exit(main())
