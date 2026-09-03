#!/usr/bin/env python3
"""Update SUBMISSION_PACKAGE_LINKS.md for the v3 main / companion v2
restoration: new repo name (rename completed), new file names, page
counts, new figures, restoration note."""
import sys

F = "/home/z/my-project/download/SUBMISSION_PACKAGE_LINKS.md"
src = open(F).read()


def rep(old, new, what, count=None):
    global src
    n = src.count(old)
    if count is None:
        count = 1
    if n != count:
        print(f"FAIL [{what}]: count = {n} (expected {count})")
        sys.exit(1)
    src = src.replace(old, new)
    print(f"ok  [{what}] x{n}")


# 1. Global repo URL rename
rep("MIKEAA2020/deepseek-highly-general",
    "MIKEAA2020/metabolic-curvature-measure", "repo URL", 36)

# 2. Header date + rename status
rep("Generated 2026-09-02. All repository links verified live (HTTP 200 at `main`,",
    "Generated 2026-09-03. All repository links verified live (HTTP 200 at `main`,",
    "date")
rep("""- Repository: https://github.com/MIKEAA2020/metabolic-curvature-measure""",
    """- Repository: https://github.com/MIKEAA2020/metabolic-curvature-measure
  (renamed 2026-09-03 from the earlier internal name; GitHub redirects
  the old URLs, but the links below already use the new name)""",
    "repo rename note")

# 3. Main paper: v2 -> v3, 21 pp -> 27 pp
rep("""(Original Research Article; 21 pp; subscription route — no author charges).""",
    """(Original Research Article; 27 pp; subscription route — no author charges).
""",
    "main page count")
rep("journal_manuscript_v2.pdf", "journal_manuscript_v3.pdf", "main PDF", 3)
rep("Manuscript PDF (21 pp, declarations in backmatter)",
    "Manuscript PDF (27 pp, full proofs in appendices, declarations in backmatter)",
    "main PDF row")
rep("scripts/journal_manuscript_v2.tex", "scripts/journal_manuscript_v3.tex",
    "main tex", 3)
rep("scripts/journal_manuscript_v2_bmb_refs.tex",
    "scripts/journal_manuscript_v3_bmb_refs.tex", "main refs", 3)
rep("compile standalone, 21 pp, 0 errors",
    "compile standalone, 27 pp, 0 errors", "main zip note")
rep("upload them together with `journal_manuscript_v2_bmb_refs.tex`",
    "upload them together with `journal_manuscript_v3_bmb_refs.tex`",
    "main upload note")

# 4. Companion: v1 files -> v2, 35 pp -> 57 pp
rep("""(Research Article; 35 pp; electronic-only, free — no author charges).""",
    """(Research Article; 57 pp; electronic-only, free — no author charges).""",
    "companion page count")
rep("Manuscript PDF (35 pp, self-contained theory, declarations in backmatter)",
    "Manuscript PDF (57 pp, restoration revision with the empirical "
    "verdict battery, terminal-coalgebra appendix, and declarations)",
    "companion PDF row")
rep("download/companion_categorical.pdf", "download/companion_categorical_v2.pdf",
    "companion PDF links", 3)
rep("scripts/companion_categorical.tex", "scripts/companion_categorical_v2.tex",
    "companion tex links", 3)

# 5. Companion figure table: add the eight restored figures
rep("""| Extended Hasse diagram | [download/inverse_limit_raf_extended_hasse.png](https://github.com/MIKEAA2020/metabolic-curvature-measure/blob/main/download/inverse_limit_raf_extended_hasse.png) |""",
    """| Extended Hasse diagram | [download/inverse_limit_raf_extended_hasse.png](https://github.com/MIKEAA2020/metabolic-curvature-measure/blob/main/download/inverse_limit_raf_extended_hasse.png) |
| Claim F holonomy (commuting-control test) | [download/claim_f_holonomy_plot.png](https://github.com/MIKEAA2020/metabolic-curvature-measure/blob/main/download/claim_f_holonomy_plot.png) |
| Claims A--E in the n=4 non-abelian regime | [download/claims_ae_n4_nonabelian.png](https://github.com/MIKEAA2020/metabolic-curvature-measure/blob/main/download/claims_ae_n4_nonabelian.png) |
| Claim D heavy-tail stress test | [download/claim_d_heavytail_stress.png](https://github.com/MIKEAA2020/metabolic-curvature-measure/blob/main/download/claim_d_heavytail_stress.png) |
| Levy 3/2 derivation (exact kernel constant) | [download/levy_stable_3half_derivation.png](https://github.com/MIKEAA2020/metabolic-curvature-measure/blob/main/download/levy_stable_3half_derivation.png) |
| Claim G Zeno scaling | [download/claim_g_zeno_plot.png](https://github.com/MIKEAA2020/metabolic-curvature-measure/blob/main/download/claim_g_zeno_plot.png) |
| T-iteration convergence | [download/t_iteration_convergence_plot.png](https://github.com/MIKEAA2020/metabolic-curvature-measure/blob/main/download/t_iteration_convergence_plot.png) |
| T-iteration robustness (axis-aligned) | [download/t_iteration_robustness_extension_axis_aligned.png](https://github.com/MIKEAA2020/metabolic-curvature-measure/blob/main/download/t_iteration_robustness_extension_axis_aligned.png) |
| T-iteration robustness (rotated) | [download/t_iteration_robustness_extension_rotated.png](https://github.com/MIKEAA2020/metabolic-curvature-measure/blob/main/download/t_iteration_robustness_extension_rotated.png) |""",
    "companion figure rows")

# 6. Replace the outdated optional-rename note with the completed status
rep("""Optional (2026-09-02 formal-cleanup round): the repository NAME still
contains "deepseek" (rendered once per paper in the Data Availability
URL). To make it neutral, rename the repository in GitHub
(Settings -> General -> Repository name -> e.g.
`metabolic-curvature-measure`); GitHub auto-redirects all old URLs, and
the tex files / cover letters / this document then need the URL string
updated (a one-line change per file, recompile). The rename could not be
done from the PAT used in this session (no repository-administration
scope).""",
"""Repository rename COMPLETED (2026-09-03): the repository is now
`metabolic-curvature-measure`; the URL string has been updated in both
manuscripts (Data Availability), both cover letters, and this document.""",
    "rename status note")

# 7. Restoration note appended to the cleanup history
rep("""Formal cleanup executed (2026-09-02): all "Artifact: ... .png/.json"
caption lines removed (source-data linkage now carried by the Data
Availability statement); all internal experiment codes (E-V5, M4b, V8,
Route 5, RC6, BT1, D-N1...), bracketed block tags, changelog/diary
references to predecessor versions, and self-commentary wording removed
from both papers; the Reproducibility and counts-appendix sections were
reworded to formal conventions; the audit passes 98/98 after the edits
(main now 21 pp, companion 35 pp, 0 errors, 0 undefined refs).""",
"""Formal cleanup executed (2026-09-02): all "Artifact: ... .png/.json"
caption lines removed (source-data linkage now carried by the Data
Availability statement); all internal experiment codes (E-V5, M4b, V8,
Route 5, RC6, BT1, D-N1...), bracketed block tags, changelog/diary
references to predecessor versions, and self-commentary wording removed
from both papers; the Reproducibility and counts-appendix sections were
reworded to formal conventions; the audit passes 98/98 after the edits
(main then 21 pp, companion 35 pp, 0 errors, 0 undefined refs).

Restoration revision executed (2026-09-03), on new frozen-lineage files
(journal_manuscript_v3.tex + journal_manuscript_v3_bmb_refs.tex;
companion_categorical_v2.tex — the v2 main and v1 companion are frozen
and untouched at tag manuscript-v2-final): full proofs for every main-
paper result (two long technical proofs in a second appendix, textbook
material cited); companion restoration of the lost empirical battery —
Claims F/G verdicts, the n=4 non-abelian regime, the Claim D heavy-tail
stress test, the Levy 3/2 derivation REPAIRED to the exact kernel
constant C_fat = sqrt(5 nu)/2 (verified against the frozen Monte-Carlo
data to 1.5%; the figure regenerated with the corrected theoretical
curve), the CPTP-Zeno lift with the Holevo ensemble correction, the
375-configuration contraction battery, the P4-repaired smooth-envelope
chain, the terminal-coalgebra characterization of the maximal RAF
(deflationary closure operator, full proof in the appendix, the
functorial-realization statement demoted to a conjecture), and the
network closure-test battery (A--K summary, RAF-to-Zeno transfer bound,
persistent-homology Phase III test, fixed-model essentiality validation
at kappa = 0.835). Main now 27 pp, companion 57 pp; both compile with
0 errors and 0 undefined refs; the v3 audit passes 98/98; every
restored number is artifact-traced; ZIPs rebuilt and standalone-
reverified. Remaining script-name mentions in the companion were
formalized to deposited-artifact conventions.""",
    "restoration note")

open(F, "w").write(src)
print("links document updated:", len(src), "bytes")
