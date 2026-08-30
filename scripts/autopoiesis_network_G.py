"""
Task 2(i): Network G -- push Network F toward FULL autopoiesis by adding
ALT5/ALT6 (alanine--2-oxoglutarate transaminase isozymes using alpha-KG
as amino acceptor; produces PYR via alternative pathway, breaking the
G6P -> FBP -> PEP -> PYR cascade dependency) AND storage compounds
(glycogen for G6P buffering, polyphosphate for ATP buffering).

FAILURE-MODE ANALYSIS OF NETWORK F (29/31 verdict):
  Network F (script autopoiesis_network_F.py) scored:
    - 6/8 metabolic intermediates causally internal (G6P, PEP, AcCoA,
      ALA, ASP, MAL)
    - 22/22 enzymes causally internal
    - 1/1 TF causally internal
  Two metabolic failures: FBP and PYR.
  Failure-mode diagnosis:
    (i) FBP baseline = 0.0000 (fast-turnover intermediate): produced by
        M2 (k_cat=0.8) and consumed by M3 (k_cat=0.8) at the same rate,
        so FBP never accumulates past viability_threshold=0.1. Knockout
        reduces FBP to 0; at recovery, M2 + M3 fire and the cycle
        resumes, but FBP still does not accumulate. Recover=0.0 ->
        FBP HOMEOSTATIC.
    (ii) PYR baseline = 0.0000 (heavily over-consumed): produced by
        M4 (k_cat=0.8) and consumed by M5 (k_cat_boost=15), M8
        (k_cat=0.8), M11 (k_cat_boost=15). Production ~ 2*0.8*99 =
        158 units/s; consumption ~ 2*15*99 + 0.8*99 + 2*15*99 ~ 6000
        units/s. A 40-fold deficit -> PYR is at 0 in baseline.
        During knockout, M4 removed; at recovery, M4 fires (PYK1/2
        high) but PYR is immediately consumed by boosted M5/M11 -> PYR
        stays at 0. PYR HOMEOSTATIC.

NETWORK G DESIGN -- break the FBP+PYR cascade:

  (7) ALT5/ALT6 -- L-alanine:2-oxoglutarate aminotransferase isozymes
      (EC 2.6.1.2):
          M12: alpha-KG + ALA -> GLU + PYR  (cat. ALT5 / ALT6)
      alpha-KG (alpha-ketoglutarate) is the amino acceptor; ALA is the
      amino donor. This produces PYR via a DIFFERENT pathway than M4
      (PYK: PEP + ADP -> PYR + ATP). The substrate ALA is now a major
      carbon-skeleton source for PYR production.

      KEY design choice: ALT5/ALT6 SYNTHESIS (E12a/E12b) uses
      alpha-KG (NOT PYR) as inducer, so ALT5/ALT6 stay high during
      PYR knockout. The synthesis uses GLU + ATP + alpha-KG -> ALT5/ALT6
      (inducer = alpha-KG). GLU is the amino-acid substrate for
      translation; alpha-KG is the inducer (signaling TCA cycle
      activity). The aspartate/alpha-KG-rich translation profile
      ensures ALT5/ALT6 synthesis is independent of ALA/PYR cascades.

      k_cat for M12 boosted to 30.0 to overcome PYR's chronic
      over-consumption: with 2 ALT5/6 isozymes at k_cat=30, production
      ~ 2*30*99 = 5940 PYR/s, matching M5+M8+M11 consumption ~ 6000/s.

      ADDITIONAL FIX for FBP fast-turnover: boost M2 (PFK) k_cat to
      1.5 and M3 (ALDO) k_cat to 0.4. M2 produces FBP faster than M3
      consumes it, allowing FBP to accumulate past 0.1.

  (8) GLYCOGEN STORAGE -- GLY1/GLY2 (glycogen synthase EC 2.4.1.11)
      and GLYP1/GLYP2 (glycogen phosphorylase EC 2.7.4.1):
          M13: G6P + ATP -> Glycogen + ADP  (cat. GLY1 / GLY2; synthesis)
          M14: Glycogen + Pi -> G6P         (cat. GLYP1 / GLYP2; breakdown)
      Glycogen acts as a SINK for G6P (when G6P is high) and a SOURCE
      for G6P (when G6P is low). During G6P knockout:
        - M1 (Glc+ATP -> G6P) removed (G6P product).
        - M14 (Glycogen -> G6P) removed (G6P product).
        - M13 (G6P -> Glycogen) NOT removed (G6P is substrate; rate=0
          because G6P=0).
        - Glycogen stays at baseline value (no reaction touches it
          effectively during knockout window).
      At recovery (T/2):
        - M1 unblocked -> G6P produced from Glc+ATP (HK1/2 high).
        - M14 unblocked -> Glycogen releases G6P (GLYP1/2 high).
        - G6P recovers FASTER via dual pathway (M1 + M14) than via M1
          alone. The Glycogen storage acts as a buffer that bypasses
          the lag of de-novo enzyme production.

  (9) POLYPHOSPHATE STORAGE -- PPK1/PPK2 (polyphosphate kinase
      EC 2.7.4.1, reversible):
          M15: ATP + Pi -> PolyP + ADP     (cat. PPK1 / PPK2; synthesis)
          M16: PolyP + ADP -> ATP + Pi     (cat. PPK1 / PPK2; breakdown)
      Polyphosphate is a phosphate reserve. During ATP depletion,
      PolyP can regenerate ATP. ATP is food (always supplied), so
      this doesn't directly fix any closure-test failure; the design
      rationale is to demonstrate storage-compound closure under the
      autopoiesis test: PolyP itself must be causally internal
      (knock out PolyP, can the network regenerate PolyP from ATP?).

  Total Network G: 53 species (11 food + 42 non-food), 54 reactions.
  Non-food: 42 (31 Network F + 2 ALT enzymes + 6 storage enzymes +
                3 metabolites GLU/Glycogen/PolyP).

  EXPECTED VERDICT:
    - All 28 enzymes causally internal (22 from Network F + ALT5/6 +
      GLY1/2 + GLYP1/2 + PPK1/2)
    - 1 TF causally internal
    - 8 metabolic intermediates + 3 new (GLU, Glycogen, PolyP) = 11
      metabolic intermediates, of which the prior 2 failures (FBP, PYR)
      should now recover via the boosted/alternative pathways.
    - Target: >= 31/42 (> 73.8% Network E baseline) AND >= 29/31
      Network F causally-internal count. Ideally 42/42 (100%).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.font_manager as fm
for p in [
    "/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]:
    try:
        fm.fontManager.addfont(p)
    except Exception:
        pass
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["Noto Sans SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

import os, csv

rng = np.random.default_rng(20260831)

# ----------------------------------------------------------------------
# Network G: Network F + ALT5/ALT6 + Glycogen storage + PolyP storage
# ----------------------------------------------------------------------
# Species: all Network F species (41) + 12 new = 53
# Food / external cofactors: Network F's 10 + alpha-KG = 11
# Metabolic intermediates (non-food): Network F's 8 + GLU, Glycogen, PolyP = 11
# Enzymes (non-food): Network F's 22 + ALT5/6 + GLY1/2 + GLYP1/2 + PPK1/2 = 30
# Regulatory (non-food): TF (1)

species = [
    # Food / external cofactors / dumps
    "Glc", "NH3", "NAD+", "CO2", "NADH", "Acetate",
    "ATP", "ADP", "Pi", "OAA",
    "alphaKG",               # NEW: alpha-ketoglutarate (food; TCA-cycle input)
    # Metabolic intermediates (non-food)
    "G6P", "FBP", "PEP", "PYR", "AcCoA", "ALA", "ASP", "MAL",
    "GLU",                   # NEW: glutamate (product of ALT5/6)
    "Glycogen",              # NEW: glucose storage polymer
    "PolyP",                 # NEW: inorganic phosphate polymer (ATP buffer)
    # Enzymes (non-food; 2 isozymes per reaction + ALT3/ALT4 + ALT5/ALT6
    #           + storage enzymes GLY/GLYP/PPK)
    "HK1", "HK2",
    "PFK1", "PFK2",
    "ALDO1", "ALDO2",
    "PYK1", "PYK2",
    "ALT1", "ALT2",
    "ALT3", "ALT4",          # Network F: aspartate-pyruvate transaminase
    "ALT5", "ALT6",          # NEW: alanine-alphaKG transaminase (EC 2.6.1.2)
    "ASPAT1", "ASPAT2",
    "MDH1", "MDH2",
    "PDH1", "PDH2",
    "PEPC1", "PEPC2",
    "ACK1", "ACK2",
    "GLY1", "GLY2",          # NEW: glycogen synthase (EC 2.4.1.11)
    "GLYP1", "GLYP2",        # NEW: glycogen phosphorylase (EC 2.7.4.1)
    "PPK1", "PPK2",          # NEW: polyphosphate kinase (EC 2.7.4.1)
    # Regulatory (non-food)
    "TF",
]

food = {"Glc", "NH3", "NAD+", "CO2", "NADH", "Acetate",
        "ATP", "ADP", "Pi", "OAA", "alphaKG"}
non_food = [s for s in species if s not in food]

reactions = [
    # ===== LAYER 1: METABOLIC (with isozymes as separate catalysts) =====
    # M1a, M1b: Glc + ATP -> G6P + ADP  (HK1 / HK2)
    {"id": "M1a", "stoich": {"Glc": -1, "ATP": -1, "G6P": 2, "ADP": 2},
     "catalyst": "HK1", "kind": "metabolic"},
    {"id": "M1b", "stoich": {"Glc": -1, "ATP": -1, "G6P": 2, "ADP": 2},
     "catalyst": "HK2", "kind": "metabolic"},
    # M2a, M2b: G6P -> FBP  (PFK1 / PFK2)
    # k_cat boosted to 1.5 to allow FBP to accumulate past viability_threshold
    # (Network F had k_cat=0.8 default, giving FBP baseline = 0.0).
    {"id": "M2a", "stoich": {"G6P": -1, "FBP": 2},
     "catalyst": "PFK1", "kind": "metabolic", "k_cat_override": 1.5},
    {"id": "M2b", "stoich": {"G6P": -1, "FBP": 2},
     "catalyst": "PFK2", "kind": "metabolic", "k_cat_override": 1.5},
    # M3a, M3b: FBP -> 2 PEP  (ALDO1 / ALDO2)
    # k_cat boosted to 1.5 (matching M2 PFK's k_cat=1.5) so PEP
    # production capacity matches M4 PYK's boosted k_cat=3.0 consumption
    # (M4 uses 1 PEP per reaction with 2 PYR produced, so M3 produces
    # 4 PEP per FBP at k_cat=1.5 -> 6 PEP/FBP equivalent, vs M4 consumes
    # 1 PEP at k_cat=3 -> net PEP production capacity ~ 3 PEP per FBP).
    {"id": "M3a", "stoich": {"FBP": -1, "PEP": 4},
     "catalyst": "ALDO1", "kind": "metabolic", "k_cat_override": 1.5},
    {"id": "M3b", "stoich": {"FBP": -1, "PEP": 4},
     "catalyst": "ALDO2", "kind": "metabolic", "k_cat_override": 1.5},
    # M4a, M4b: PEP + ADP -> PYR + ATP  (PYK1 / PYK2)
    # k_cat boosted to 3.0 to increase PYR production capacity
    # (Network F had k_cat=0.8 default, PYR baseline = 0.0 due to
    # over-consumption by boosted M5/M11).
    {"id": "M4a", "stoich": {"PEP": -1, "ADP": -1, "PYR": 2, "ATP": 2},
     "catalyst": "PYK1", "kind": "metabolic", "k_cat_override": 3.0},
    {"id": "M4b", "stoich": {"PEP": -1, "ADP": -1, "PYR": 2, "ATP": 2},
     "catalyst": "PYK2", "kind": "metabolic", "k_cat_override": 3.0},
    # M5a, M5b: PYR + NH3 -> ALA  (ALT1 / ALT2)
    {"id": "M5a", "stoich": {"PYR": -1, "NH3": -1, "ALA": 2},
     "catalyst": "ALT1", "kind": "metabolic", "k_cat_override": 15.0},
    {"id": "M5b", "stoich": {"PYR": -1, "NH3": -1, "ALA": 2},
     "catalyst": "ALT2", "kind": "metabolic", "k_cat_override": 15.0},
    # M6a, M6b: OAA + NH3 -> ASP  (ASPAT1 / ASPAT2)
    {"id": "M6a", "stoich": {"OAA": -1, "NH3": -1, "ASP": 2},
     "catalyst": "ASPAT1", "kind": "metabolic", "k_cat_override": 15.0},
    {"id": "M6b", "stoich": {"OAA": -1, "NH3": -1, "ASP": 2},
     "catalyst": "ASPAT2", "kind": "metabolic", "k_cat_override": 15.0},
    # M7a, M7b: OAA + NAD+ -> MAL + NADH  (MDH1 / MDH2)
    {"id": "M7a", "stoich": {"OAA": -1, "NAD+": -1, "MAL": 2, "NADH": 2},
     "catalyst": "MDH1", "kind": "metabolic"},
    {"id": "M7b", "stoich": {"OAA": -1, "NAD+": -1, "MAL": 2, "NADH": 2},
     "catalyst": "MDH2", "kind": "metabolic"},
    # M8a, M8b: PYR + NAD+ -> AcCoA + CO2  (PDH1 / PDH2)
    {"id": "M8a", "stoich": {"PYR": -1, "NAD+": -1, "AcCoA": 2, "CO2": 2},
     "catalyst": "PDH1", "kind": "metabolic"},
    {"id": "M8b", "stoich": {"PYR": -1, "NAD+": -1, "AcCoA": 2, "CO2": 2},
     "catalyst": "PDH2", "kind": "metabolic"},
    # M9a, M9b: PEP + CO2 -> OAA  (PEPC1 / PEPC2; anaplerotic)
    {"id": "M9a", "stoich": {"PEP": -1, "CO2": -1, "OAA": 2},
     "catalyst": "PEPC1", "kind": "metabolic"},
    {"id": "M9b", "stoich": {"PEP": -1, "CO2": -1, "OAA": 2},
     "catalyst": "PEPC2", "kind": "metabolic"},
    # M10a, M10b: AcCoA + ADP + Pi -> Acetate + ATP  (ACK1 / ACK2; backup ATP)
    {"id": "M10a", "stoich": {"AcCoA": -1, "ADP": -1, "Pi": -1,
                              "Acetate": 2, "ATP": 2},
     "catalyst": "ACK1", "kind": "metabolic"},
    {"id": "M10b", "stoich": {"AcCoA": -1, "ADP": -1, "Pi": -1,
                              "Acetate": 2, "ATP": 2},
     "catalyst": "ACK2", "kind": "metabolic"},
    # M11a, M11b: ASP + PYR -> OAA + ALA  (ALT3 / ALT4; from Network F)
    {"id": "M11a", "stoich": {"ASP": -1, "PYR": -1, "OAA": 2, "ALA": 2},
     "catalyst": "ALT3", "kind": "metabolic", "k_cat_override": 15.0},
    {"id": "M11b", "stoich": {"ASP": -1, "PYR": -1, "OAA": 2, "ALA": 2},
     "catalyst": "ALT4", "kind": "metabolic", "k_cat_override": 15.0},
    # M12a, M12b: alpha-KG + ALA -> GLU + PYR  (ALT5 / ALT6; NEW)
    # EC 2.6.1.2: alanine--2-oxoglutarate aminotransferase.
    # Produces PYR via an ALTERNATIVE pathway independent of M4 (PYK).
    # k_cat boosted to 30.0 to match the over-consumption by M5+M11
    # (each boosted to 15.0). With 2 ALT5/6 isozymes, production
    # capacity ~ 2*30*99 = 5940 PYR/s, matching the ~ 6000 consumption.
    {"id": "M12a", "stoich": {"alphaKG": -1, "ALA": -1, "GLU": 2, "PYR": 2},
     "catalyst": "ALT5", "kind": "metabolic", "k_cat_override": 30.0},
    {"id": "M12b", "stoich": {"alphaKG": -1, "ALA": -1, "GLU": 2, "PYR": 2},
     "catalyst": "ALT6", "kind": "metabolic", "k_cat_override": 30.0},
    # M13a, M13b: G6P + ATP -> Glycogen + ADP  (GLY1 / GLY2; glycogen synthase)
    # EC 2.4.1.11. Stores excess G6P as glycogen. k_cat=1.5 (boosted to
    # allow Glycogen to accumulate past viability_threshold=0.1 in
    # steady-state baseline; otherwise Glycogen stays at 0 due to fast
    # turnover between M13 and M14).
    {"id": "M13a", "stoich": {"G6P": -1, "ATP": -1, "Glycogen": 2, "ADP": 2},
     "catalyst": "GLY1", "kind": "metabolic", "k_cat_override": 1.5},
    {"id": "M13b", "stoich": {"G6P": -1, "ATP": -1, "Glycogen": 2, "ADP": 2},
     "catalyst": "GLY2", "kind": "metabolic", "k_cat_override": 1.5},
    # M14a, M14b: Glycogen + Pi -> G6P  (GLYP1 / GLYP2; glycogen phosphorylase)
    # EC 2.7.4.1. Releases G6P from glycogen storage. k_cat=0.4 (slightly
    # lower than M13's 1.5 to allow Glycogen to accumulate in baseline).
    {"id": "M14a", "stoich": {"Glycogen": -1, "Pi": -1, "G6P": 2},
     "catalyst": "GLYP1", "kind": "metabolic", "k_cat_override": 0.4},
    {"id": "M14b", "stoich": {"Glycogen": -1, "Pi": -1, "G6P": 2},
     "catalyst": "GLYP2", "kind": "metabolic", "k_cat_override": 0.4},
    # M15a, M15b: ATP -> PolyP + ADP  (PPK1 / PPK2 forward; polyP synthesis)
    # EC 2.7.4.1. Stores phosphate as polyP. k_cat=0.5.
    {"id": "M15a", "stoich": {"ATP": -1, "PolyP": 2, "ADP": 2},
     "catalyst": "PPK1", "kind": "metabolic", "k_cat_override": 0.5},
    {"id": "M15b", "stoich": {"ATP": -1, "PolyP": 2, "ADP": 2},
     "catalyst": "PPK2", "kind": "metabolic", "k_cat_override": 0.5},
    # M16a, M16b: PolyP + ADP -> ATP  (PPK1 / PPK2 reverse; polyP breakdown)
    # Regenerates ATP from polyP. k_cat=0.5.
    {"id": "M16a", "stoich": {"PolyP": -1, "ADP": -1, "ATP": 2},
     "catalyst": "PPK1", "kind": "metabolic", "k_cat_override": 0.5},
    {"id": "M16b", "stoich": {"PolyP": -1, "ADP": -1, "ATP": 2},
     "catalyst": "PPK2", "kind": "metabolic", "k_cat_override": 0.5},

    # ===== LAYER 2: ENZYME SYNTHESIS (substrate-induced, with isozymes) =====
    # E1: HK1/HK2 synthesis -- inducer = Glc (substrate of M1)
    {"id": "E1a", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "Glc": -1,
                              "HK1": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    {"id": "E1b", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "Glc": -1,
                              "HK2": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    # E2: PFK synthesis -- inducer = G6P (substrate of M2)
    {"id": "E2a", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "G6P": -1,
                              "PFK1": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    {"id": "E2b", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "G6P": -1,
                              "PFK2": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    # E3: ALDO synthesis -- inducer = FBP (substrate of M3)
    {"id": "E3a", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "FBP": -1,
                              "ALDO1": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    {"id": "E3b", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "FBP": -1,
                              "ALDO2": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    # E4: PYK synthesis -- inducer = PEP (substrate of M4)
    {"id": "E4a", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "PEP": -1,
                              "PYK1": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    {"id": "E4b", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "PEP": -1,
                              "PYK2": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    # E5: ALT1/ALT2 synthesis -- inducer = PYR (substrate of M5)
    {"id": "E5a", "stoich": {"ALA": -1, "ATP": -1, "PYR": -1,
                              "ALT1": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    {"id": "E5b", "stoich": {"ALA": -1, "ATP": -1, "PYR": -1,
                              "ALT2": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    # E6: ASPAT synthesis -- inducer = OAA (substrate of M6)
    {"id": "E6a", "stoich": {"ASP": -1, "ATP": -1, "OAA": -1,
                              "ASPAT1": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    {"id": "E6b", "stoich": {"ASP": -1, "ATP": -1, "OAA": -1,
                              "ASPAT2": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    # E7: MDH synthesis -- inducer = OAA (substrate of M7)
    {"id": "E7a", "stoich": {"ASP": -1, "ATP": -1, "OAA": -1,
                              "MDH1": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    {"id": "E7b", "stoich": {"ASP": -1, "ATP": -1, "OAA": -1,
                              "MDH2": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    # E8: PDH synthesis -- inducer = PYR (substrate of M8)
    {"id": "E8a", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "PYR": -1,
                              "PDH1": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    {"id": "E8b", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "PYR": -1,
                              "PDH2": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    # E9: PEPC synthesis -- inducer = PEP (substrate of M9)
    {"id": "E9a", "stoich": {"ASP": -1, "ATP": -1, "PEP": -1,
                              "PEPC1": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    {"id": "E9b", "stoich": {"ASP": -1, "ATP": -1, "PEP": -1,
                              "PEPC2": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    # E10: ACK synthesis -- inducer = AcCoA (substrate of M10)
    {"id": "E10a", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "AcCoA": -1,
                               "ACK1": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    {"id": "E10b", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "AcCoA": -1,
                               "ACK2": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    # E11a, E11b: ALT3/ALT4 synthesis -- ASP-based (NOT ALA-based)
    {"id": "E11a", "stoich": {"ASP": -2, "ATP": -1, "ALT3": 1,
                              "ADP": 2, "Pi": 2, "OAA": 1},
     "catalyst": "TF", "kind": "synthesis"},
    {"id": "E11b", "stoich": {"ASP": -2, "ATP": -1, "ALT4": 1,
                              "ADP": 2, "Pi": 2, "OAA": 1},
     "catalyst": "TF", "kind": "synthesis"},
    # E12a, E12b: ALT5/ALT6 synthesis -- alpha-KG + GLU based (NOT PYR-based)
    # Inducer = alpha-KG (substrate of M12). Uses GLU + alpha-KG + ATP
    # as substrates. This means: during PYR knockout (which would block
    # E5a/b synthesis since they use PYR as inducer), ALT5/ALT6 synthesis
    # CONTINUES (using alpha-KG as inducer, which is food and unaffected
    # by PYR knockout). ALT5/ALT6 stay at high level during PYR knockout.
    # At recovery, M12 fires (ALT5/6 high, alpha-KG from food, ALA via M5/11
    # as PYR rises) and produces PYR via the alternative pathway.
    {"id": "E12a", "stoich": {"GLU": -1, "alphaKG": -1, "ATP": -1,
                              "ALT5": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    {"id": "E12b", "stoich": {"GLU": -1, "alphaKG": -1, "ATP": -1,
                              "ALT6": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    # E13: GLY1/GLY2 synthesis -- inducer = G6P (substrate of M13)
    {"id": "E13a", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "G6P": -1,
                              "GLY1": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    {"id": "E13b", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "G6P": -1,
                              "GLY2": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    # E14: GLYP1/GLYP2 synthesis -- inducer = Glycogen (substrate of M14)
    # NOTE: Glycogen as inducer means: during Glycogen knockout (which
    # would block all reactions producing Glycogen, i.e., M13), E14
    # synthesis is also blocked (Glycogen=0). But during G6P knockout,
    # Glycogen stays at baseline (M13 uses G6P as substrate, rate=0,
    # so Glycogen doesn't deplete via consumption; M14 is removed
    # during G6P knockout). So Glycogen stays high, and GLYP1/2 stay
    # high (E14 synthesis continues because Glycogen is high).
    {"id": "E14a", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "Glycogen": -1,
                              "GLYP1": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    {"id": "E14b", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1, "Glycogen": -1,
                              "GLYP2": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    # E15: PPK1/PPK2 synthesis -- inducer = ATP (substrate of M15)
    {"id": "E15a", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1,
                              "PPK1": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},
    {"id": "E15b", "stoich": {"ALA": -1, "ASP": -1, "ATP": -1,
                              "PPK2": 1, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "synthesis"},

    # ===== LAYER 3: GENE REGULATORY (basal + autocatalytic TF) =====
    {"id": "G_const", "stoich": {"ATP": -1, "TF": 2, "ADP": 2, "Pi": 2},
     "catalyst": None, "kind": "constitutive"},
    {"id": "G_auto", "stoich": {"ATP": -1, "TF": 2, "ADP": 2, "Pi": 2},
     "catalyst": "TF", "kind": "autocatalytic"},
]

network_G = {
    "species": species,
    "food": list(food),
    "non_food": non_food,
    "reactions": reactions,
}


def simulate_network(network, knockout_species=None, T=500, delta=0.05,
                     k_cat_metabolic=0.8, k_cat_synthesis=2.0,
                     k_cat_constitutive=0.3, k_cat_autocatalytic=1.0,
                     food_supply_rate=2.0, food_conc=10.0,
                     Km=0.1, max_conc=100.0,
                     init_concs=None, allow_constitutive=True):
    """Simulate the network dynamics for T steps.

    Uses Michaelis-Menten saturation for each substrate to prevent
    runaway positive feedback: rate = k * [cat] * prod(s_i / (Km + s_i)).
    """
    sp = network["species"]
    fd = set(network["food"])
    rxs = network["reactions"]

    x = {s: (food_conc if s in fd else 0.1) for s in sp}
    if init_concs:
        for s, v in init_concs.items():
            x[s] = v

    knockout_reactions = set()
    if knockout_species is not None:
        for r in rxs:
            produced = [s for s, d in r["stoich"].items() if d > 0]
            if knockout_species in produced:
                knockout_reactions.add(r["id"])

    dt = 0.05
    trajectory = [{s: x[s] for s in sp}]
    for step in range(T):
        rates = {}
        for r in rxs:
            if r["id"] in knockout_reactions:
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
    """Simulate from a given initial condition (recovery test)."""
    sp = network["species"]
    fd = set(network["food"])
    rxs = network["reactions"]
    x = {s: init.get(s, 0.0) for s in sp}
    for s in fd:
        x[s] = max(x[s], food_conc)
    if x.get("ATP", 0) < 1.0:
        x["ATP"] = max(x["ATP"], 2.0)
    if x.get("TF", 0) < 0.05:
        x["TF"] = max(x["TF"], 0.1)
    dt = 0.05
    trajectory = [{s: x[s] for s in sp}]
    for step in range(T):
        rates = {}
        for r in rxs:
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


def closure_test(network, network_name, T=500, viability_threshold=0.1):
    """Run the autopoiesis closure test of Definition def:autopoiesis."""
    baseline = simulate_network(network, knockout_species=None, T=T)
    baseline_final = baseline[-1]
    records = []
    for m_j in network["non_food"]:
        knock = simulate_network(network, knockout_species=m_j, T=T)
        knock_final = knock[-1]
        knock_traj = [t[m_j] for t in knock]
        recover_start_idx = T // 2
        recover_init = knock[recover_start_idx]
        recover = simulate_network_recover(network, init=recover_init, T=T - recover_start_idx)
        recover_final = recover[-1]
        knock_success = knock_final[m_j] < viability_threshold
        recover_success = recover_final[m_j] > viability_threshold
        causally_internal = knock_success and recover_success
        records.append({
            "network": network_name,
            "component": m_j,
            "baseline_conc": baseline_final[m_j],
            "knockout_conc_final": knock_final[m_j],
            "knockout_min": min(knock_traj),
            "recover_conc_final": recover_final[m_j],
            "knockout_success": knock_success,
            "recover_success": recover_success,
            "causally_internal": causally_internal,
            "verdict": "AUTOPOIETIC" if causally_internal else "HOMEOSTATIC",
        })
    return records, baseline


# ----------------------------------------------------------------------
# Run closure test on Network G
# ----------------------------------------------------------------------
print("=" * 78)
print("TASK 2(i): NETWORK G -- push Network F toward FULL autopoiesis")
print("       ALT5/ALT6 (alanine--alphaKG transaminase, EC 2.6.1.2) break PYR cascade")
print("       + Glycogen storage (G6P buffer) + Polyphosphate storage (ATP buffer)")
print("=" * 78)
print()
print("Network G design (extension of Network F):")
print("  (1-6) [same as Network F]: isozymes + substrate induction + basal TF +")
print("       backup ATP (ACK) + anaplerotic PEPC + ALT3/ALT4 (ASP-PYR transaminase)")
print("  (7) ALT5/ALT6 (alanine--alphaKG transaminase isozymes, EC 2.6.1.2):")
print("      M12: alpha-KG + ALA -> GLU + PYR (PRODUCES PYR via alternative pathway)")
print("      -> PYR-independent: ALT5/6 synthesis uses alpha-KG (NOT PYR) as inducer,")
print("         so ALT5/6 stay high during PYR knockout")
print("      -> k_cat=30 to match M5/M11 over-consumption of PYR")
print("  (8) GLYCOGEN STORAGE (GLY1/2 synthase + GLYP1/2 phosphorylase):")
print("      M13: G6P + ATP -> Glycogen (synthesis, k_cat=0.5)")
print("      M14: Glycogen -> G6P (breakdown, k_cat=0.5) -> buffers G6P recovery")
print("  (9) POLYPHOSPHATE STORAGE (PPK1/2 polyphosphate kinase):")
print("      M15: ATP -> PolyP (synthesis); M16: PolyP -> ATP (breakdown)")
print("  ALSO: M2 (PFK) k_cat=1.5, M3 (ALDO) k_cat=1.5 -> balanced FBP/PEP accumulation")
print("        M4 (PYK) k_cat=3.0 -> increases PYR production capacity")
print(f"  Total: {len(species)} species ({len(food)} food + {len(non_food)} non-food), "
      f"{len(reactions)} reactions")
print()
print("Closed loop (Network G): Network F + ALT5/6 (alternative PYR source) +")
print("             Glycogen (G6P buffer) + PolyP (ATP buffer)")
print("             ALT5/6 catalyze M12 (alphaKG+ALA -> GLU+PYR) -> PYR via alt route")
print("             Glycogen <-> G6P (M13/M14, GLY/GLYP isozymes)")
print("             PolyP <-> ATP (M15/M16, PPK isozymes)")
print()

records_G, baseline_G = closure_test(network_G, "G: Network F + ALT5/6 + storage", T=500)
print("Closure test verdicts for Network G (Network F + ALT5/6 + storage):")
print(f"  {'Component':<10} {'Baseline':<12} {'Knockout':<12} {'Recover':<12} {'Verdict':<14}")
for r in records_G:
    print(f"  {r['component']:<10} {r['baseline_conc']:<12.4f} "
          f"{r['knockout_conc_final']:<12.4f} {r['recover_conc_final']:<12.4f} "
          f"{r['verdict']:<14}")

n_autopoietic_G = sum(1 for r in records_G if r["causally_internal"])
n_total_G = len(records_G)
pct_G = 100.0 * n_autopoietic_G / n_total_G if n_total_G > 0 else 0.0
print(f"\n  Network G verdict: {n_autopoietic_G}/{n_total_G} components causally internal ({pct_G:.1f}%).")
print(f"  Network G is "
      f"{'FULLY AUTOPOIETIC' if n_autopoietic_G == n_total_G else 'PARTIALLY AUTOPOIETIC' if n_autopoietic_G > 0 else 'HOMEOSTATIC'}"
      f" per Definition def:autopoiesis.")
print()

# Compare to Network F (29/31 = 93.5%)
pct_F = 100.0 * 29 / 31  # Network F's 29/31
print("Comparison:")
print("  Network B (bare metabolic, 10 species):              0/10  (0.0%)   HOMEOSTATIC")
print("  Network D (integrated MR-GR, Network D v1):           5/17  (29.4%)  PARTIALLY AUTOPOIETIC")
print("  Network E (fully autopoietic MR-GR with isozymes):  24/29  (82.8%)  PARTIALLY AUTOPOIETIC")
print("  Network F (Network E + ALT3/ALT4 ASP-PYR isozymes): 29/31  (93.5%)  PARTIALLY AUTOPOIETIC")
print(f"  Network G (Network F + ALT5/6 + storage):           {n_autopoietic_G}/{n_total_G}  ({pct_G:.1f}%)  "
      f"{'FULLY' if n_autopoietic_G == n_total_G else 'PARTIALLY'} AUTOPOIETIC")
print()
if n_autopoietic_G > 29 or pct_G > pct_F:
    print(f"  VERDICT: Network G ({n_autopoietic_G}/{n_total_G}, {pct_G:.1f}%) compared to")
    print(f"  Network F (29/31, {pct_F:.1f}%):")
    if n_autopoietic_G > 29:
        print(f"    - Absolute causally-internal count: {n_autopoietic_G} > 29  (strictly greater)")
    if pct_G > pct_F:
        print(f"    - Fraction: {pct_G:.1f}% > {pct_F:.1f}%  (strictly greater)")
    elif pct_G < pct_F:
        print(f"    - Fraction: {pct_G:.1f}% < {pct_F:.1f}%  (NOT strictly greater; Network G has")
        print(f"      {n_total_G - 31} more components than Network F, growing the denominator faster")
        print(f"      than the causally-internal count)")
    if n_autopoietic_G == n_total_G:
        print(f"  Network G achieves FULL AUTOPOIESIS ({n_total_G}/{n_total_G}).")
else:
    print(f"  WARNING: Network G ({n_autopoietic_G}/{n_total_G}, {pct_G:.1f}%) is NOT strictly greater than")
    print(f"  Network F (29/31, {pct_F:.1f}%); further tuning needed.")
print()

# Stratify by component type
print("Stratified by component type:")
metabolic_components = ["G6P", "FBP", "PEP", "PYR", "AcCoA", "ALA", "ASP", "MAL",
                        "GLU", "Glycogen", "PolyP"]
enzyme_components = ["HK1", "HK2", "PFK1", "PFK2", "ALDO1", "ALDO2", "PYK1", "PYK2",
                     "ALT1", "ALT2", "ALT3", "ALT4", "ALT5", "ALT6",
                     "ASPAT1", "ASPAT2", "MDH1", "MDH2",
                     "PDH1", "PDH2", "PEPC1", "PEPC2", "ACK1", "ACK2",
                     "GLY1", "GLY2", "GLYP1", "GLYP2", "PPK1", "PPK2"]
regulatory_components = ["TF"]

n_met_auto = sum(1 for r in records_G if r["component"] in metabolic_components and r["causally_internal"])
n_met_tot = sum(1 for r in records_G if r["component"] in metabolic_components)
n_ez_auto = sum(1 for r in records_G if r["component"] in enzyme_components and r["causally_internal"])
n_ez_tot = sum(1 for r in records_G if r["component"] in enzyme_components)
n_reg_auto = sum(1 for r in records_G if r["component"] in regulatory_components and r["causally_internal"])
n_reg_tot = sum(1 for r in records_G if r["component"] in regulatory_components)
print(f"  Metabolic intermediates (incl. GLU/Glycogen/PolyP): {n_met_auto}/{n_met_tot} causally internal")
print(f"  Enzymes (incl. ALT5/6, GLY/GLYP/PPK isozymes):     {n_ez_auto}/{n_ez_tot} causally internal")
print(f"  Regulatory (TF):                                    {n_reg_auto}/{n_reg_tot} causally internal")
print()

# Save outputs
out_dir = "/home/z/my-project/download"
os.makedirs(out_dir, exist_ok=True)

with open(f"{out_dir}/autopoiesis_network_G.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["network", "component", "baseline_conc", "knockout_conc_final",
                "knockout_min", "recover_conc_final", "knockout_success",
                "recover_success", "causally_internal", "verdict"])
    for r in records_G:
        w.writerow([r["network"], r["component"], r["baseline_conc"],
                    r["knockout_conc_final"], r["knockout_min"], r["recover_conc_final"],
                    r["knockout_success"], r["recover_success"],
                    r["causally_internal"], r["verdict"]])

with open(f"{out_dir}/autopoiesis_network_G.txt", "w") as f:
    f.write("TASK 2(i): NETWORK G -- push Network F toward FULL autopoiesis\n")
    f.write("       ALT5/ALT6 (alanine--alphaKG transaminase, EC 2.6.1.2) break PYR cascade\n")
    f.write("       + Glycogen storage (G6P buffer) + Polyphosphate storage (ATP buffer)\n")
    f.write("=" * 78 + "\n\n")
    f.write("Network G design (extension of Network F):\n")
    f.write("  (1-6) [same as Network F]: isozymes + substrate induction + basal TF +\n")
    f.write("       backup ATP (ACK) + anaplerotic PEPC + ALT3/ALT4 (ASP-PYR transaminase)\n")
    f.write("  (7) ALT5/ALT6 (alanine--alphaKG transaminase isozymes, EC 2.6.1.2):\n")
    f.write("      M12: alpha-KG + ALA -> GLU + PYR (PRODUCES PYR via alternative pathway)\n")
    f.write("      -> PYR-independent: ALT5/6 synthesis uses alpha-KG (NOT PYR) as inducer\n")
    f.write("      -> k_cat=30 to match M5/M11 over-consumption of PYR\n")
    f.write("  (8) GLYCOGEN STORAGE (GLY1/2 synthase + GLYP1/2 phosphorylase):\n")
    f.write("      M13: G6P + ATP -> Glycogen (synthesis, k_cat=0.5)\n")
    f.write("      M14: Glycogen -> G6P (breakdown, k_cat=0.5) -> buffers G6P recovery\n")
    f.write("  (9) POLYPHOSPHATE STORAGE (PPK1/2 polyphosphate kinase):\n")
    f.write("      M15: ATP -> PolyP (synthesis); M16: PolyP -> ATP (breakdown)\n")
    f.write("  ALSO: M2 (PFK) k_cat=1.5, M3 (ALDO) k_cat=1.5 -> balanced FBP/PEP accumulation\n")
    f.write("        M4 (PYK) k_cat=3.0 -> increases PYR production capacity\n")
    f.write(f"  Total: {len(species)} species ({len(food)} food + {len(non_food)} non-food), "
            f"{len(reactions)} reactions\n\n")
    f.write("Closed loop (Network G): Network F + ALT5/6 (alternative PYR source) +\n")
    f.write("             Glycogen (G6P buffer) + PolyP (ATP buffer)\n")
    f.write("             ALT5/6 catalyze M12 (alphaKG+ALA -> GLU+PYR) -> PYR via alt route\n")
    f.write("             Glycogen <-> G6P (M13/M14, GLY/GLYP isozymes)\n")
    f.write("             PolyP <-> ATP (M15/M16, PPK isozymes)\n\n")
    f.write("Closure test verdicts for Network G:\n")
    f.write(f"  {'Component':<10} {'Baseline':<12} {'Knockout':<12} {'Recover':<12} {'Verdict':<14}\n")
    for r in records_G:
        f.write(f"  {r['component']:<10} {r['baseline_conc']:<12.4f} "
                f"{r['knockout_conc_final']:<12.4f} {r['recover_conc_final']:<12.4f} "
                f"{r['verdict']:<14}\n")
    f.write(f"\n  Network G verdict: {n_autopoietic_G}/{n_total_G} components causally internal ({pct_G:.1f}%).\n")
    f.write(f"  Network G is "
            f"{'FULLY AUTOPOIETIC' if n_autopoietic_G == n_total_G else 'PARTIALLY AUTOPOIETIC' if n_autopoietic_G > 0 else 'HOMEOSTATIC'}\n"
            f"  per Definition def:autopoiesis.\n\n")
    f.write("Comparison:\n")
    f.write("  Network B (bare metabolic, 10 species):              0/10  (0.0%)   HOMEOSTATIC\n")
    f.write("  Network D (integrated MR-GR, Network D v1):           5/17  (29.4%)  PARTIALLY AUTOPOIETIC\n")
    f.write("  Network E (fully autopoietic MR-GR with isozymes):  24/29  (82.8%)  PARTIALLY AUTOPOIETIC\n")
    f.write("  Network F (Network E + ALT3/ALT4 ASP-PYR isozymes): 29/31  (93.5%)  PARTIALLY AUTOPOIETIC\n")
    f.write(f"  Network G (Network F + ALT5/6 + storage):           {n_autopoietic_G}/{n_total_G}  ({pct_G:.1f}%)  "
            f"{'FULLY' if n_autopoietic_G == n_total_G else 'PARTIALLY'} AUTOPOIETIC\n\n")
    if n_autopoietic_G > 29 or pct_G > pct_F:
        f.write(f"  Comparison vs Network F (29/31, {pct_F:.1f}%):\n")
        if n_autopoietic_G > 29:
            f.write(f"    - Absolute causally-internal count: {n_autopoietic_G} > 29  (strictly greater)\n")
        if pct_G > pct_F:
            f.write(f"    - Fraction: {pct_G:.1f}% > {pct_F:.1f}%  (strictly greater)\n")
        elif pct_G < pct_F:
            f.write(f"    - Fraction: {pct_G:.1f}% < {pct_F:.1f}%  (NOT strictly greater; Network G has\n")
            f.write(f"      {n_total_G - 31} more components than Network F, growing the denominator\n")
            f.write(f"      faster than the causally-internal count)\n")
        if n_autopoietic_G == n_total_G:
            f.write(f"  Network G achieves FULL AUTOPOIESIS ({n_total_G}/{n_total_G} = 100%).\n\n")
    f.write("Stratified by component type:\n")
    f.write(f"  Metabolic intermediates (incl. GLU/Glycogen/PolyP): {n_met_auto}/{n_met_tot} causally internal\n")
    f.write(f"  Enzymes (incl. ALT5/6, GLY/GLYP/PPK isozymes):     {n_ez_auto}/{n_ez_tot} causally internal\n")
    f.write(f"  Regulatory (TF):                                    {n_reg_auto}/{n_reg_tot} causally internal\n\n")

# Plot: knockout trajectories for representative components from each layer
fig, axes = plt.subplots(1, 4, figsize=(16, 4.5), constrained_layout=True)
# Pick 4 components: PYR (cascade target broken by ALT5/6), ALT5 (new enzyme),
#                    G6P (buffered by Glycogen), Glycogen (new storage)
for col, m_j in enumerate(["PYR", "ALT5", "G6P", "Glycogen"]):
    ax = axes[col]
    knock = simulate_network(network_G, knockout_species=m_j, T=500)
    t_arr = np.arange(len(knock))
    concs = [t[m_j] for t in knock]
    verdict = next(r for r in records_G if r["component"] == m_j)
    color = "#3a7ca5"
    if m_j == "ALT5":
        color = "#6a994e"  # green for new enzyme
    if m_j == "PYR":
        color = "#bc4749"  # red for cascade target
    if m_j == "Glycogen":
        color = "#f4a259"  # orange for storage
    ax.plot(t_arr, concs, color=color, linewidth=1.8, label=f"Knockout of {m_j}")
    ax.axhline(0.1, color="black", linestyle="--", linewidth=1, alpha=0.6,
               label="Viability threshold")
    ax.set_xlabel("Time step")
    ax.set_ylabel(f"Concentration [{m_j}]")
    ax.set_title(f"Network G: knockout of {m_j}\n"
                 f"({'causally internal' if verdict['causally_internal'] else 'homeostatic'})")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(True, alpha=0.3)

fig.suptitle("Network G: Network F + ALT5/ALT6 (alphaKG transaminase) + Glycogen + PolyP storage\n"
             f"Verdict: {n_autopoietic_G}/{n_total_G} causally internal ({pct_G:.1f}%) "
             f"-- {'FULLY AUTOPOIETIC' if n_autopoietic_G == n_total_G else 'PARTIALLY AUTOPOIETIC'}",
             fontsize=11)
fig.savefig(f"{out_dir}/autopoiesis_network_G.png", dpi=150)
plt.close(fig)

print(f"\n[outputs written to {out_dir}/]")
print(f"  - autopoiesis_network_G.csv")
print(f"  - autopoiesis_network_G.png")
print(f"  - autopoiesis_network_G.txt")
