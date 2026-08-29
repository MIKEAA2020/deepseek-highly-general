#!/usr/bin/env python3
"""
Audit of the DeepSeek Cross-Domain Unification Transcript.
Produces a structured PDF report via ReportLab.

Sections:
  Cover & Executive Summary
  Part I   - Flaws Beyond the Four Acknowledged Defects (9 flaws)
  Part II  - Internal Inconsistencies (8 inconsistencies)
  Part III - Profound Upgrades (8 upgrades)
  Part IV  - Verdict and Next Steps
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether, Flowable, HRFlowable,
)

# -----------------------------------------------------------------------------
# Font registration
# -----------------------------------------------------------------------------
FONT_DIR = "/usr/share/fonts"
pdfmetrics.registerFont(TTFont('NotoSerifSC', f'{FONT_DIR}/truetype/noto-serif-sc/NotoSerifSC-Regular.ttf'))
pdfmetrics.registerFont(TTFont('NotoSerifSC-Bold', f'{FONT_DIR}/truetype/noto-serif-sc/NotoSerifSC-Bold.ttf'))
pdfmetrics.registerFont(TTFont('NotoSerifSC-Light', f'{FONT_DIR}/truetype/noto-serif-sc/NotoSerifSC-Light.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSansMono', f'{FONT_DIR}/truetype/dejavu/DejaVuSansMono.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSansMono-Bold', f'{FONT_DIR}/truetype/dejavu/DejaVuSansMono-Bold.ttf'))
registerFontFamily('NotoSerifSC', normal='NotoSerifSC', bold='NotoSerifSC-Bold')
registerFontFamily('DejaVuSansMono', normal='DejaVuSansMono', bold='DejaVuSansMono-Bold')

# -----------------------------------------------------------------------------
# Palette - academic minimalist (deep teal accent on white)
# -----------------------------------------------------------------------------
C_PRIMARY    = HexColor('#1F2937')   # dark slate - body text
C_ACCENT     = HexColor('#0F766E')   # deep teal - headings / rules
C_MUTED      = HexColor('#6B7280')   # gray - meta
C_QUOTE      = HexColor('#374151')   # quote text
C_QUOTE_BG   = HexColor('#F3F4F6')  # quote background
C_RULE       = HexColor('#0F766E')   # accent rule
C_COVER_BG   = HexColor('#0F172A')  # dark cover background
C_COVER_FG   = HexColor('#F8FAFC')  # light text on dark cover

# -----------------------------------------------------------------------------
# Styles
# -----------------------------------------------------------------------------
styles = getSampleStyleSheet()

style_cover_title = ParagraphStyle(
    'CoverTitle', parent=styles['Title'],
    fontName='NotoSerifSC-Bold', fontSize=28, leading=34,
    textColor=C_COVER_FG, alignment=TA_LEFT, spaceAfter=8,
)
style_cover_subtitle = ParagraphStyle(
    'CoverSubtitle', parent=styles['Normal'],
    fontName='NotoSerifSC', fontSize=14, leading=20,
    textColor=HexColor('#94A3B8'), alignment=TA_LEFT, spaceAfter=24,
)
style_cover_meta = ParagraphStyle(
    'CoverMeta', parent=styles['Normal'],
    fontName='NotoSerifSC', fontSize=10, leading=14,
    textColor=HexColor('#CBD5E1'), alignment=TA_LEFT,
)

style_h1 = ParagraphStyle(
    'H1', parent=styles['Heading1'],
    fontName='NotoSerifSC-Bold', fontSize=20, leading=26,
    textColor=C_ACCENT, alignment=TA_LEFT,
    spaceBefore=18, spaceAfter=10,
)
style_h2 = ParagraphStyle(
    'H2', parent=styles['Heading2'],
    fontName='NotoSerifSC-Bold', fontSize=14, leading=20,
    textColor=C_PRIMARY, alignment=TA_LEFT,
    spaceBefore=14, spaceAfter=6,
)
style_h3 = ParagraphStyle(
    'H3', parent=styles['Heading3'],
    fontName='NotoSerifSC-Bold', fontSize=11.5, leading=16,
    textColor=C_ACCENT, alignment=TA_LEFT,
    spaceBefore=10, spaceAfter=4,
)
style_body = ParagraphStyle(
    'Body', parent=styles['Normal'],
    fontName='NotoSerifSC', fontSize=10, leading=15,
    textColor=C_PRIMARY, alignment=TA_JUSTIFY,
    spaceBefore=2, spaceAfter=6,
)
style_quote = ParagraphStyle(
    'Quote', parent=styles['Normal'],
    fontName='NotoSerifSC', fontSize=9.5, leading=14,
    textColor=C_QUOTE, alignment=TA_LEFT,
    leftIndent=14, rightIndent=10,
    spaceBefore=4, spaceAfter=6,
    backColor=C_QUOTE_BG, borderPadding=8,
    borderColor=C_ACCENT, borderWidth=0,
)
style_meta = ParagraphStyle(
    'Meta', parent=styles['Normal'],
    fontName='NotoSerifSC', fontSize=9, leading=12,
    textColor=C_MUTED, alignment=TA_LEFT,
)
style_part_label = ParagraphStyle(
    'PartLabel', parent=styles['Normal'],
    fontName='NotoSerifSC-Bold', fontSize=10, leading=14,
    textColor=C_ACCENT, alignment=TA_LEFT,
    spaceBefore=0, spaceAfter=2,
)

# -----------------------------------------------------------------------------
# Flowables
# -----------------------------------------------------------------------------
def draw_cover(canv, doc):
    """Draw the dark cover page using onPage callback (full-bleed)."""
    page_w, page_h = A4
    canv.saveState()
    # background full bleed
    canv.setFillColor(C_COVER_BG)
    canv.rect(0, 0, page_w, page_h, fill=1, stroke=0)
    # accent rule top
    canv.setStrokeColor(C_ACCENT)
    canv.setLineWidth(3)
    canv.line(2.2*cm, page_h - 4*cm, 8.2*cm, page_h - 4*cm)
    # title
    canv.setFillColor(C_COVER_FG)
    canv.setFont('NotoSerifSC-Bold', 28)
    canv.drawString(2.2*cm, page_h - 5.2*cm, "Audit of the DeepSeek")
    canv.drawString(2.2*cm, page_h - 6.4*cm, "Cross-Domain Unification Transcript")
    # subtitle
    canv.setFont('NotoSerifSC', 14)
    canv.setFillColor(HexColor('#94A3B8'))
    canv.drawString(2.2*cm, page_h - 7.6*cm, "Flaws, Internal Inconsistencies, and Profound Upgrades")
    # divider rule
    canv.setStrokeColor(HexColor('#334155'))
    canv.setLineWidth(0.5)
    canv.line(2.2*cm, page_h - 9*cm, page_w - 2.2*cm, page_h - 9*cm)
    # body summary text on cover
    canv.setFillColor(HexColor('#CBD5E1'))
    canv.setFont('NotoSerifSC', 10)
    lines = [
        "Line-level audit of a 16,271-line transcript in which DeepSeek and the",
        "user jointly construct a chain: RAF -> TSRC -> QTSRC -> rate-distortion",
        "-> automata -> consciousness -> fractals -> symmetry -> perturbation",
        "-> WCIG (rejected) -> 7 bridge rungs -> game theory -> CGT (rejected)",
        "-> n=3 explicit construction -> final self-assessment.",
        "",
        "DeepSeek's final verdict: useful toy model, not yet a rigorous",
        "cross-domain unification. This audit confirms that verdict, but shows",
        "it understates the issues: 9 additional flaws and 8 internal",
        "inconsistencies extend beyond the 4 defects DeepSeek acknowledged.",
        "Eight profound upgrades are proposed.",
    ]
    y = page_h - 10.5*cm
    for ln in lines:
        canv.drawString(2.2*cm, y, ln)
        y -= 14
    # meta block at bottom
    canv.setStrokeColor(C_ACCENT)
    canv.setLineWidth(1)
    canv.line(2.2*cm, 3.5*cm, 6.2*cm, 3.5*cm)
    canv.setFont('NotoSerifSC-Bold', 10)
    canv.setFillColor(HexColor('#F8FAFC'))
    canv.drawString(2.2*cm, 3.0*cm, "Z.AI Audit")
    canv.setFont('NotoSerifSC', 9)
    canv.setFillColor(HexColor('#94A3B8'))
    canv.drawString(2.2*cm, 2.4*cm, "Independent line-level review")
    canv.drawString(2.2*cm, 2.0*cm, "Source: /home/z/my-project/upload/deepseek general chat.txt")
    canv.restoreState()


class CoverPage(Flowable):
    """A zero-size flowable that simply triggers the cover, then page break."""
    def __init__(self):
        super().__init__()
        self.width = 0
        self.height = 0

    def draw(self):
        pass  # actual cover drawn via onFirstPage callback


class HorizontalRule(Flowable):
    def __init__(self, width, thickness=0.5, color=C_ACCENT):
        super().__init__()
        self.width = width
        self.thickness = thickness
        self.color = color

    def draw(self):
        c = self.canv
        c.setStrokeColor(self.color)
        c.setLineWidth(self.thickness)
        c.line(0, 0, self.width, 0)


def part_divider(label, title, blurb):
    """A section divider Flowable that introduces a Part."""
    return KeepTogether([
        Spacer(1, 18),
        Paragraph(label, style_part_label),
        Paragraph(title, style_h1),
        HRFlowable(width="100%", thickness=1.2, color=C_ACCENT, spaceBefore=2, spaceAfter=10),
        Paragraph(blurb, style_body),
        Spacer(1, 8),
    ])


def section(heading, paragraphs, quote=None):
    """A standard section: heading + optional quote + body paragraphs."""
    flow = [Paragraph(heading, style_h2)]
    if quote:
        flow.append(Paragraph(quote, style_quote))
    for p in paragraphs:
        flow.append(Paragraph(p, style_body))
    return flow


# -----------------------------------------------------------------------------
# Build document
# -----------------------------------------------------------------------------
def build():
    out_path = "/home/z/my-project/download/deepseek_transcript_audit.pdf"
    doc = SimpleDocTemplate(
        out_path, pagesize=A4,
        leftMargin=2.2*cm, rightMargin=2.2*cm,
        topMargin=2.2*cm, bottomMargin=2.0*cm,
        title="Audit of the DeepSeek Cross-Domain Unification Transcript",
        author="Z.ai Audit",
        subject="Line-level audit of a 16,271-line transcript",
        creator="Z.ai PDF skill (ReportLab)",
    )
    page_w, page_h = A4
    content_w = page_w - 4.4*cm

    story = []

    # Cover page - empty flowable + page break, content drawn by onFirstPage
    story.append(CoverPage())
    story.append(PageBreak())

    # Remaining pages: header drawing is a no-op (clean pages)
    def noop(canv, doc):
        pass

    # Set the onFirstPage callback now that we have draw_cover defined
    doc.onFirstPage = draw_cover
    doc.onLaterPages = noop

    # Executive Summary (acts as page 2, continues flowing)
    story.append(Paragraph("Executive Summary", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.2, color=C_ACCENT, spaceBefore=2, spaceAfter=10))
    exec_sum = [
        ("The transcript under audit is a 16,271-line DeepSeek chat in which the user and the model "
         "jointly construct a cross-domain chain running from reflexively autocatalytic food-generated "
         "sets (RAF), through Total Self-Reproducing Reflexive Constructors (TSRC), quantum TSRC, "
         "rate-distortion theory, automata theory, integrated-information consciousness, iterated "
         "function systems, Noether-type symmetry, perturbation theory, an abortive "
         "Wasserstein-Categorical Information Geometry (WCIG) upgrade, seven proposed bridge rungs, "
         "an evolutionary game theory arc, an abortive Counterfactual Gauge Theory (CGT) upgrade, "
         "and a final n=3 explicit construction on the Fisher-Rao 2-simplex."),
        ("DeepSeek's final verdict at line 16,270 is that the work is now a useful toy model, but not yet "
         "the rigorous cross-domain unification it claims to be. The model itself acknowledges four "
         "defects: (i) the object called a principal GL(2)-bundle connection is in fact a connection on "
         "a vector bundle, with effective structure group CO(2) = R+ x O(2); (ii) the cost labeled "
         "an exact increase in predictive variance is in fact a squared mean shift; (iii) the RAF "
         "invariance theorem reduces to continuity of a positive function on a compact set; and "
         "(iv) the claimed explicit 4-species universal register machine is a schematic sketch, not "
         "an explicit reaction list."),
        ("This audit confirms the model's final self-assessment as accurate, but shows that it "
         "understates the issues. Across the nine earlier arcs the same rhetorical pattern recurs: "
         "an arc opens by introducing a rigorous bridge, presents Theorem statements as if novel, "
         "and closes with an honest caveat conceding that the synthesis is merely a novel presentation "
         "of known components. The Theorem framing and the honest caveat are in tension throughout."),
        ("Beyond the four acknowledged defects, this audit identifies nine additional flaws spanning "
         "every arc of the transcript, including unjustified achievability claims in the rate-distortion "
         "arc, trivial existence theorems in the consciousness arc, unproved couplings in the fractal "
         "arc, tautological symmetry-breaking theorems, a conjunction-of-local-results perturbation "
         "theorem, a categorical tautology in Bridge Rung 6, a definitional theorem in the game theory "
         "arc, an unaddressed double standard in evaluation, and a structural inconsistency between "
         "the rigorous-bridge rhetoric and the novel-synthesis admissions."),
        ("The audit further identifies eight internal inconsistencies where claims made in one part of "
         "the transcript are contradicted in another. Most revealing is the inconsistency between "
         "DeepSeek's rejection of the user's WCIG and CGT proposals as mathiness, and its subsequent "
         "acceptance of structurally identical conceptual moves (persistent cohomology of consciousness, "
         "dagger compact categories, qualia-as-holonomy, principle of least counterfactual variance) "
         "as legitimate bridge rungs or n=3 construction ingredients. The boundary between undefined "
         "terms and defined terms tracks who is speaking, not the terms themselves."),
        ("Finally, the audit proposes eight profound upgrades that would convert the toy model into a "
         "research program with tractable milestones. The four most consequential are: (a) replace "
         "the imposed GL(2) structure group with the endogenous stabilizer G_C of the cost functional, "
         "so the gauge group is derived rather than chosen; (b) replace the quadratic proxy cost with "
         "the actual KL predictive divergence, so the principle of least counterfactual variance is "
         "literally true; (c) replace the trivial compactness theorem with an average-curvature bound "
         "via entropy production, so the RAF-to-curvature link is non-trivial; and (d) identify the "
         "empirical signature of the CO(2) structure group, namely a dilation-rotation factorization of "
         "belief updates, which competitor Bayesian-update models do not predict."),
    ]
    for p in exec_sum:
        story.append(Paragraph(p, style_body))

    story.append(Spacer(1, 6))
    story.append(Paragraph("Scope, Method, and Object Under Audit", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.2, color=C_ACCENT, spaceBefore=2, spaceAfter=10))

    scope_paras = [
        ("The object under audit is a single DeepSeek chat-share transcript at "
         "/home/z/my-project/upload/deepseek general chat.txt, 16,271 lines. The transcript contains "
         "approximately twenty-five conversational arcs. The first six arcs (lines 1-3,136) construct "
         "the chain incrementally: rate-distortion + automata (1-427), consciousness as integrated "
         "information (428-1,022), fractals as iterated function systems (1,023-1,814), symmetry and "
         "Noether (1,815-2,324), and perturbation theory (2,325-3,136). Each arc follows the same "
         "internal structure: definitions, theorems, proof sketches, an integration statement, and "
         "an honest caveat."),
        ("The seventh arc (lines 3,140-3,188) is the user's WCIG upgrade proposal that attempts to "
         "geometrize the entire framework via Wasserstein curvature, persistent cohomology, dagger "
         "compact categories, and constructor theory. DeepSeek rejects this as mathiness in the eighth "
         "arc (3,189-3,518). The user then asks to reduce the gap; DeepSeek responds with seven "
         "tangible bridge rungs (3,519-4,037). The ninth arc adds evolutionary game theory "
         "(4,039-4,670). The tenth is the user's Counterfactual Gauge Theory proposal (4,700-4,993), "
         "again rejected as mathiness."),
        ("The remaining arcs (5,000-12,300) attempt to develop individual bridge rungs into partial "
         "theorems, culminating in two parallel n=3 explicit constructions (12,136-15,300) on the "
         "Fisher-Rao 2-simplex, with closed-form expressions for the connection, curvature, RAF "
         "vector field, and Ricci-holonomy bound. The final arc (15,200-16,270) is DeepSeek's "
         "self-assessment, ending with the verdict quoted at line 16,270."),
        ("The audit method is line-level reading, skipping only the model's internal thinking blocks "
         "(clearly marked in the transcript). Claims were cross-referenced across arcs to detect "
         "internal inconsistencies. Where the model's self-assessment acknowledges a defect, the audit "
         "notes it and proceeds to additional flaws that the model did not flag. Where the model "
         "asserts a theorem, the audit checks whether the proof supports the asserted strength. "
         "Where the model issues an honest caveat, the audit checks whether the caveat is consistent "
         "with the framing used elsewhere in the same arc."),
        ("The four defects DeepSeek acknowledged in its final self-assessment concern only the "
         "n=3 construction. The audit's scope extends across all twenty-five arcs, so it identifies "
         "additional issues that the self-assessment does not address. These are not minor: they "
         "include unjustified achievability, trivial existence, tautology, dimensional incoherence, "
         "definitional theorem, double standard, and rhetorical inconsistency. Each is documented "
         "below with a verbatim quote and the line at which it appears, followed by an explanation "
         "of the flaw. Part II then catalogues eight internal inconsistencies. Part III proposes "
         "eight profound upgrades, each tied to a specific flaw or inconsistency. Part IV concludes."),
    ]
    for p in scope_paras:
        story.append(Paragraph(p, style_body))

    # -------------------------------------------------------------------------
    # PART I - FLAWS
    # -------------------------------------------------------------------------
    story.append(part_divider(
        "PART I",
        "Flaws Beyond the Four Acknowledged Defects",
        ("The four defects DeepSeek acknowledged in its final self-assessment all concern the "
         "n=3 construction: the principal-bundle mismatch, the predictive-variance claim, the "
         "trivial RAF invariance theorem, and the sketchy register machine. The nine flaws below "
         "span every arc of the transcript and reveal a systematic pattern: rigorous-bridge rhetoric "
         "consistently outruns the mathematical content. Each flaw is documented with a verbatim "
         "quote and the line at which it appears.")
    ))

    # Flaw 1
    story.extend(section(
        "Flaw 1 — Rate-Distortion 'Asymptotic Achievability' Is Unjustified (Arc 1, lines 1-427)",
        paragraphs=[
            ("The theorem at lines 267-309 states that if a TSRC reproduces itself with expected "
             "distortion at most D using a self-description of length |sigma_N| bits, then |sigma_N| "
             "is at least the rate-distortion function R(D). The bound itself is a correct "
             "application of Shannon's rate-distortion theorem to the source of network descriptions. "
             "The flaw is in the closing claim at line 310:"),
            ("Quote (line 310): <i>Furthermore, because the TSRC is Turing-complete, it can implement "
             "any computable source code. Therefore there exists a TSRC whose description length is "
             "arbitrarily close to R(D), i.e., the bound is asymptotically achievable.</i>"),
            ("This is a non-sequitur. Universal Turing-completeness is the ability to compute any "
             "partial recursive function; it does not imply the ability to compute the minimizer of "
             "the rate-distortion functional R(D) to a prescribed precision. For general sources the "
             "rate-distortion function has no closed form and is in fact uncomputable in the sense "
             "of Bennett's incomputability of the Kolmogorov structure function. Even for Bernoulli "
             "sources the Blahut algorithm is iterative and converges only in the limit, not "
             "arbitrarily close in any prescribed finite time."),
            ("The claim conflates three distinct notions: computable (recursive), effectively "
             "computable to a prescribed precision (with a computable modulus of convergence), and "
             "computable by the TSRC itself as a self-reproducing network with bounded chemical "
             "kinetics. The theorem establishes the first notion and concludes the third. The "
             "intermediate step is missing and, for general sources, false. The 'asymptotically "
             "achievable' clause should be retracted or restricted to sources with computable "
             "rate-distortion functions and TSRCs capable of running the corresponding minimization "
             "algorithm in finite time."),
        ],
    ))

    # Flaw 2
    story.extend(section(
        "Flaw 2 — RIIP Existence Theorem Is Trivial; Phi Is Undefined (Arc 2, lines 428-1022)",
        paragraphs=[
            ("The arc defines a Reflexive Predictive Self-model with Integrated Information (RPSI) "
             "and states Theorem at line 473 / 861: <i>There exists a TSRC that is a RPSI automaton "
             "with positive integrated information and self-model closure.</i> The proof is that "
             "the TSRC, being Turing-complete, can simulate any finite automaton including one whose "
             "transition table references its own description."),
            ("This is a direct application of Kleene's recursion theorem. The existence claim is "
             "trivially true: any universal machine can host a self-referential program. The theorem "
             "as stated establishes no non-trivial necessary condition on the TSRC, no quantitative "
             "lower bound on the integrated information Phi, and no constraint linking the existence "
             "of such an automaton to any physical or biological property of the underlying network."),
            ("More seriously, the integrated information measure Phi is left undefined. Integrated "
             "Information Theory has multiple incompatible formalizations (IIT 2.0 uses a minimum "
             "information partition measure, IIT 3.0 uses a cause-effect repertoire, IIT 4.0 uses "
             "an intrinsic evaluation based on system mechanism). The arc never specifies which "
             "version is invoked, nor how the positive-Phi condition is to be verified for a "
             "concrete automaton. Without a specified Phi, the existential quantifier is vacuous: "
             "any automaton can be claimed to have positive Phi under some definition."),
            ("The honest caveat at line 1022 concedes that the result does not prove phenomenal "
             "consciousness, identity of consciousness with integrated information, or a solution "
             "to the hard problem. But the caveat does not address the stronger criticism: even as "
             "a formal property, the RPSI existence theorem adds nothing to the recursion theorem. "
             "The arc presents as a theorem what is, at best, a definition of a syntactic property "
             "that any universal machine can be made to satisfy."),
        ],
    ))

    # Flaw 3
    story.extend(section(
        "Flaw 3 — Fractal Arc's 'Coupling of Dimension to Reproduction Rate' Is Not Proved (Arc 3, lines 1023-1814)",
        paragraphs=[
            ("The arc proves the standard Hutchinson theorem (the attractor of an iterated function "
             "system exists and is unique) and combines it with Turing completeness to argue that "
             "a spatial TSRC can realize any computable self-similar fractal. The honest caveat at "
             "line 1817 then claims novelty: <i>Its novelty lies in the explicit coupling of fractal "
             "dimension to self-reproduction rate and descriptive complexity.</i>"),
            ("No such coupling is derived in the arc. The arc proves existence of a fractal attractor "
             "given an IFS, and proves existence of a TSRC that can realize any given IFS. The "
             "claim that the fractal dimension is coupled to the reproduction rate would require "
             "an explicit equation linking the Hausdorff dimension D_H of the attractor to the "
             "reaction rate constants kappa_r and to the code length |sigma_N|. No such equation "
             "is derived; the only formulas presented are the standard Hutchinson equation D_H = "
             "log m / (-log lambda) for self-similar maps with scaling lambda, and the "
             "rate-distortion bound on code length."),
            ("The situation worsens in Bridge Rung 4 (lines 3,923-3,929), where the response asserts "
             "that D = lim_{D -> 0} R(D), equating fractal dimension D on the left with the "
             "rate-distortion function R(D) on the right. This equation is dimensionally incoherent: "
             "D on the left is a Hausdorff dimension (a real number, typically in [0, infinity)), "
             "while R(D) on the right is a rate measured in bits per symbol. The two objects are "
             "not even of the same type; the equation is not well-formed. A correct relationship "
             "would require specifying that R(D) is the rate-distortion function of the invariant "
             "measure on the attractor and then taking a limit in which the distortion parameter "
             "and the dimension are linked via a specific gauge."),
            ("The fractal arc therefore claims a coupling it does not derive, and Bridge Rung 4 "
             "later claims an equation that is not well-typed. Both are illustrative of the pattern: "
             "rhetorical coupling is asserted where mathematical coupling is absent."),
        ],
    ))

    # Flaw 4
    story.extend(section(
        "Flaw 4 — Noether-for-Markov Application Is Tautological (Arc 4, lines 1815-2324)",
        paragraphs=[
            ("The arc defines the symmetry group of a reaction network at line 1,826 as the group "
             "of automorphisms of the species set that preserve the reaction set R. Theorem at "
             "line 2,073 asserts that RAF emergence breaks symmetry: the realized RAF has a "
             "stabilizer that is a proper subgroup of the symmetry group of the potential RAF."),
            ("This is true by definition of stabilizer. The stabilizer of a subset S in a group G "
             "is {g in G : gS = S}. If S is a proper subset of the ambient set on which G acts "
             "transitively, the stabilizer is a proper subgroup. The 'theorem' is the observation "
             "that the realized RAF is a proper subset of the potential RAF, and that the "
             "stabilizer of a proper subset under a transitive group action is a proper subgroup. "
             "This is a one-line result in elementary group theory, not a deep theorem about the "
             "emergence of biological organization."),
            ("The invocation of Noether's theorem for Markov processes is decorative. The "
             "cited result (relating symmetries of the transition kernel to conservation laws of "
             "the stationary distribution) is real, but its application in this arc does no "
             "mathematical work. It is cited as a parallel, not as the engine of any computation. "
             "No conservation law is derived, no invariant is computed, no prediction is made."),
            ("The honest caveat at line 2,324 concedes that the statements about symmetry breaking "
             "are either standard theorems or straightforward consequences of definitions. But the "
             "caveat does not retract the theorem framing. The arc presents as a theorem what the "
             "caveat then concedes is a definitional triviality."),
        ],
    ))

    # Flaw 5
    story.extend(section(
        "Flaw 5 — Perturbation 'Full Chain Robustness' Is a Conjunction of Local Results (Arc 5, lines 2325-3136)",
        paragraphs=[
            ("The arc proves local stability of each link in the chain via the Implicit Function "
             "Theorem: if the Jacobian at the steady state is invertible with eigenvalues in the "
             "left half-plane, the steady state is locally asymptotically stable and depends "
             "differentiably on parameters. Theorem at line 3,034 then claims <i>Perturbative "
             "Robustness of the Full Chain</i>, and the proof sketch at line 3,095 describes the "
             "result as <i>a direct synthesis of the above stability results, using the openness "
             "of the relevant conditions and the Implicit Function Theorem.</i>"),
            ("This is not a joint stability theorem. The full chain consists of n links, each with "
             "its own local stability constant (a Lipschitz constant L_i for the dependence of the "
             "i-th steady state on the parameters, and a spectral-gap constant lambda_i for "
             "convergence to that steady state). A genuine joint theorem would bound the Lipschitz "
             "constant of the composed map (the full chain) as a function of the individual "
             "constants: typically L_full = product_i L_i, with stability requiring L_full < 1. "
             "The arc's proof does not compute this product, nor does it establish any quantitative "
             "condition under which the full chain remains stable under perturbation of the input "
             "parameters."),
            ("What the arc actually proves is that the set of parameter values for which all n "
             "links are simultaneously stable is an open set. This is true but contentless: it "
             "is the observation that the intersection of finitely many open sets is open. The "
             "theorem's name (Full Chain Robustness) suggests a quantitative joint stability result; "
             "the proof delivers a topological openness observation."),
            ("The honest caveat at line 3,136 concedes that the result is a synthesis of standard "
             "stability theorems. But the theorem framing does not match the caveat: 'robustness' "
             "in dynamical systems usually means a quantitative margin (a ball of perturbations "
             "under which the system remains in a specified region), not merely the openness of "
             "the stable parameter set. The arc claims robustness and proves openness."),
        ],
    ))

    # Flaw 6
    story.extend(section(
        "Flaw 6 — Bridge Rung 6's Frobenius-Algebra Criterion Is a Categorical Tautology (lines 4008-4017)",
        paragraphs=[
            ("Bridge Rung 6 proposes a constructor-theoretic formulation of self-reproduction as a "
             "resource theory. The target theorem at line 4,013 is: <i>Universal self-reproduction "
             "is possible if and only if there exists a compact closed category with a copying "
             "operation that is symmetric and associative, i.e., a commutative dagger Frobenius "
             "algebra.</i>"),
            ("This is a tautology in categorical quantum mechanics. A standard result (Vicary, "
             "Heunen-Vicary, Selinger) shows that any object in a symmetric monoidal dagger "
             "category equipped with a copying operation satisfying the usual structural laws "
             "(coassociativity, cocommutativity, dagger-compatibility, and the Frobenius law) "
             "is precisely a commutative special dagger Frobenius algebra. The 'if and only if' "
             "in the target theorem therefore reduces to: self-reproduction is possible if and "
             "only if the network has a copying operation satisfying the structural laws of "
             "self-reproduction. This is the definition of self-reproduction, restated in "
             "categorical language."),
            ("The bridge to Constructor Theory is similarly definitional. Constructor theory "
             "asks what tasks are possible or impossible; a task is possible if there exists a "
             "constructor that performs it. To say 'universal self-reproduction is possible if "
             "and only if there exists a structure that supports universal copying' is to "
             "re-state the constructor-theoretic question, not to answer it."),
            ("Bridge Rung 6 thus does not deliver a theorem; it delivers a re-translation of the "
             "problem into the vocabulary of categorical quantum mechanics and Constructor Theory. "
             "This is a useful linguistic exercise if one is building a vocabulary, but it is not "
             "the rigorous bridge promised by the rung's framing."),
        ],
    ))

    # Flaw 7
    story.extend(section(
        "Flaw 7 — Game Theory Arc's 'Viability Implies RAF' Is True by Definition (lines 4352-4414)",
        paragraphs=[
            ("Theorem at line 4,352: <i>Viability implies RAF.</i> The proof sketch at lines "
             "4,385-4,412 argues: if N_i survives (its net growth rate is non-negative at the "
             "equilibrium resource levels), then any non-RAF network cannot sustain itself from "
             "food alone; hence survival implies RAF."),
            ("This is true by definition. RAF (Reflexively Autocatalytic and Food-generated) sets "
             "were defined by Hordijk, Steel, and Kauffman as sets in which every reaction is "
             "catalyzed by some species in the set or in the food set, and every non-food reactant "
             "is produced by some reaction in the set. The defining property of a RAF is exactly "
             "that it can sustain itself from food alone. So the theorem reads: if a network "
             "survives from food alone, it satisfies the defining property of a RAF."),
            ("The theorem has the logical form of 'if P then P.' It is not false, but it carries "
             "no information beyond the definition. A non-trivial theorem would be: viability "
             "under some specific dynamical regime (e.g., mass-action kinetics with degradation "
             "rate delta) implies RAF with an explicit lower bound on the catalytic efficiency "
             "k_cat as a function of delta and the food inflow. The arc does not prove this; it "
             "proves the definitional version."),
            ("This is the same tautological pattern as Flaw 4: a definitional observation is "
             "framed as a theorem. The honest caveats in earlier arcs concede that the components "
             "are known; the game-theory arc does not include an honest caveat of comparable "
             "force, which makes the rhetorical inflation more visible here than elsewhere."),
        ],
    ))

    # Flaw 8
    story.extend(section(
        "Flaw 8 — WCIG Rejection vs. Bridge Rung Acceptance: Double Standard (lines 3189-4037)",
        paragraphs=[
            ("At lines 3,189-3,518, DeepSeek rejects the user's WCIG proposal as mathiness. The "
             "rejection cites undefined terms (Autopoietic Resonance, optimal bounded rationality, "
             "isomorphism between active inference and projection onto a fundamental class), "
             "category errors (Lott-Villani-Sturm Ricci curvature is a property of the underlying "
             "metric measure space, not of W_2 itself), and the absence of a specified filtration "
             "for the persistent cohomology of consciousness. The verdict at line 3,425 is that "
             "the Master Theorem is not a theorem."),
            ("At lines 3,519-4,037, DeepSeek responds to the user's request to reduce the gap by "
             "proposing seven bridge rungs. Several of these rungs use the same conceptual moves "
             "that were rejected in the WCIG verdict. Rung 2 (line 3,790) proposes persistent "
             "homology of the reaction graph with filtration by reaction rate, and identifies RAF "
             "with a non-vanishing persistent cohomology class. Rung 3 (line 3,828) proposes a "
             "compact closed category for reaction networks. Rung 5 (line 3,974) proposes "
             "integrated information as a persistent topological invariant. Rung 6 (line 4,008) "
             "proposes Constructor Theory as a resource theory."),
            ("The standard applied to the user's WCIG proposal (reject undefined terms, demand "
             "specified filtrations, flag category errors) is not applied to DeepSeek's own "
             "counter-proposal. Rung 5's claim that integrated information is the first-order "
             "persistent invariant of a partition filtration is exactly the kind of move rejected "
             "in WCIG (persistent cohomology of consciousness without a specified filtration). "
             "Rung 3's compact closed category is structurally identical to the dagger compact "
             "category flagged in WCIG. Rung 6's resource-theoretic Constructor Theory is the same "
             "constructor-theoretic move rejected in WCIG."),
            ("This is the central internal inconsistency of the transcript: the same conceptual "
             "apparatus is rejected when proposed by the user and accepted as a tangible bridge "
             "when proposed by the model. The boundary between mathiness and rigor tracks who is "
             "speaking, not the terms themselves. A reader of the transcript cannot reconstruct, "
             "from the criteria explicitly applied, why the user's WCIG is mathiness while "
             "DeepSeek's Rung 5 is a tangible project. The implicit criterion is authorship."),
        ],
    ))

    # Flaw 9
    story.extend(section(
        "Flaw 9 — 'Honest Caveat' Pattern Contradicts 'Theorem' Framing (all arcs)",
        paragraphs=[
            ("Every arc opens with rigorous-bridge rhetoric: <i>Below I introduce a rigorous "
             "bridge from X to Y</i> (lines 1, 428, 1,035, 1,819, 2,329). Every arc ends with an "
             "honest caveat conceding that the synthesis is novel in presentation but the "
             "individual components are known (lines 425, 1,022, 1,817, 2,325, 3,136). These two "
             "registers are in tension throughout."),
            ("A rigorous bridge implies novel mathematical content: a theorem connecting two "
             "domains that was not previously known. A novel synthesis of known components implies "
             "no new mathematics, only a new combination. The two phrasings correspond to "
             "different epistemic claims. The theorem framing suggests the former; the honest "
             "caveat concedes the latter. The transcript oscillates between these registers "
             "without resolving the tension."),
            ("The final verdict at line 16,270 (useful toy model, not rigorous unification) aligns "
             "with the honest-caveat register. But the body of the transcript speaks in the "
             "rigorous-bridge register: each arc presents Theorem statements, Proof sketches, "
             "and integration statements as if they were novel results. The verdict at the end "
             "is in tension with the rhetoric that precedes it throughout the body."),
            ("This is not fraud (the caveats are honest) but it is a structural inconsistency. "
             "The document-level claim (rigorous cross-domain unification) outruns the "
             "section-level admissions (novel synthesis of known components). A reader who "
             "takes the theorem framing at face value will over-credit the work; a reader who "
             "takes the honest caveats at face value will wonder why the theorem framing was "
             "used at all. The two registers should be reconciled: either drop the theorem "
             "framing (call them observations or definitions) or strengthen the proofs (deliver "
             "the novel mathematical content that the theorem framing promises)."),
        ],
    ))

    # -------------------------------------------------------------------------
    # PART II - INTERNAL INCONSISTENCIES
    # -------------------------------------------------------------------------
    story.append(part_divider(
        "PART II",
        "Internal Inconsistencies",
        ("Beyond per-arc flaws, the transcript exhibits eight internal inconsistencies where claims "
         "made in one place contradict claims made elsewhere. These reveal that evaluation "
         "standards and conceptual commitments shift across the conversation. The most revealing "
         "inconsistencies concern the boundary between mathiness and rigor (Inconsistency 4), the "
         "literal retraction of a central claim within the same arc (Inconsistency 1), and the "
         "shift in the central arithmetic constant of a theorem across iterations (Inconsistency 3).")
    ))

    # Inconsistency 1
    story.extend(section(
        "Inconsistency 1 — 'Exact Predictive Variance' Contradicted Within the Same Arc",
        paragraphs=[
            ("At line 15,224, the n=3 construction defines the cost C = (1/2)||dA(v)lambda + "
             "A(mu)xi||^2 + (alpha/2)||xi||^2 and immediately claims: <i>The first term is the "
             "exact increase in predictive variance of y under the intervention.</i> This claim "
             "grounds the variational principle called the Principle of Least Counterfactual "
             "Variance (Definition 2.1 at line 13,737)."),
            ("At lines 16,072-16,139, in the final self-assessment, the model retracts: <i>For "
             "the linear Gaussian model y = A(mu)lambda + epsilon, the predictive variance is "
             "Var(y) = I + (mean-shift-squared term). The term (1/2)||dA(v)lambda + A(mu)xi||^2 "
             "is the squared mean shift, not the exact increase in variance.</i> The assessment "
             "further notes that this matters because the interpretation of the connection as "
             "least counterfactual variance is not derived from the generative model; it is "
             "imposed by choosing a quadratic proxy."),
            ("So the central variational principle is grounded in a claim that is made at line "
             "15,224, used to derive the connection at line 15,230, and retracted at line 16,072. "
             "The variational principle loses its grounding within the same arc. The connection "
             "omega is still a well-defined object (it is the critical point of the declared cost "
             "C), but the justification for choosing this particular cost is removed."),
            ("The recommended fix at line 16,253 (call the cost a regularized squared predictive "
             "error, not the exact predictive variance) is honest but revealing: the original "
             "claim was inflated. The variational principle was named after a property it does "
             "not have. The same pattern recurs in Inconsistency 2 (RAF invariance theorem) and "
             "Inconsistency 5 (explicit register machine): the construction is rhetorically "
             "inflated, the assessment retracts, and the inflation is acknowledged but its "
             "implications for downstream claims are not propagated."),
        ],
    ))

    # Inconsistency 2
    story.extend(section(
        "Inconsistency 2 — RAF-to-Curvature Link: Claimed as Theorem, Acknowledged as Continuity Observation",
        paragraphs=[
            ("At line 11,445 (Theorem, RAF invariance): <i>If H is a RAF set then there exists a "
             "compact, positively invariant subset K of the interior, on which every species that "
             "appears as a catalyst is produced at a strictly positive rate. The curvature-coercivity "
             "bound ||F|| >= c > 0 on K is a consequence of the strictly positive entropy-production "
             "rate on that set (Fisher-Rao Ricci curvature of the simplex is known explicitly and "
             "is bounded below once the density is bounded away from the boundary).</i>"),
            ("At lines 16,143-16,189, in the self-assessment: <i>The category RAF_3 is defined so "
             "that every object already contains an autocatalytic reaction and a chemostat "
             "recycling term. The invariant set K is then obtained from a standard Lyapunov "
             "argument. The statement inf ||F|| > 0 on K is true simply because kappa(mu) is "
             "strictly positive and continuous on the compact interior set K. This has nothing "
             "to do with RAF closure or autopoiesis. It is continuity of a positive function on "
             "a compact set. So the theorem is mathematically true but scientifically empty as a "
             "bridge between RAF dynamics and connection curvature.</i>"),
            ("So the same claim is asserted at line 11,445 as a deep biological-to-geometric bridge "
             "(RAF closure, via entropy production, yields curvature coercivity) and acknowledged "
             "at line 16,189 as a contentless compactness observation (a positive continuous "
             "function on a compact set has a positive infimum). The two characterizations are "
             "inconsistent: either the theorem establishes a non-trivial link between RAF and "
             "curvature, or it does not. The assessment concedes it does not."),
            ("The downstream consequence is significant. The Ricci-holonomy inequality (Theorem 4.1 "
             "at line 13,778) depends on the compactness of K and the continuity of F on K. If the "
             "compactness of K is just a generic property of any mass-action flow with a Lyapunov "
             "function (which is the assessment's characterization), then the Ricci-holonomy "
             "inequality holds for any such flow, not specifically for RAF flows. The inequality "
             "is then a theorem about all chemostatted systems, not a theorem about autopoiesis. "
             "The RAF-specific content of the curvature-holonomy comparison evaporates."),
        ],
    ))

    # Inconsistency 3
    story.extend(section(
        "Inconsistency 3 — Holonomy Bound Constant: 4/pi vs. 1/pi",
        paragraphs=[
            ("In the first parallel n=3 response (around lines 13,780-13,796), the Ricci-holonomy "
             "comparison theorem uses the constant C_K = (4/pi) sup kappa, derived from the "
             "isoperimetric inequality on the constant-curvature base. The argument appears to "
             "go: area <= L^2 / (4 pi) by Euclidean isoperimetry, multiplied by 4 to account for "
             "Ricci = 1/4, yielding (1/pi) Ric L^2 but then re-multiplied by 4 to give (4/pi) "
             "sup kappa L^2."),
            ("In the second parallel n=3 response (lines 15,256-15,262), the same inequality uses "
             "C_K = (1/pi) sup kappa. The argument is now: area <= L^2 / (4 pi) by the spherical "
             "isoperimetric inequality on the radius-2 sphere, and Ric = 1/4, so area <= "
             "(1/pi) Ric L^2, giving C_K = (1/pi) sup kappa."),
            ("The self-assessment at line 15,313 notes: <i>Constant C_K = (1/pi) sup kappa now "
             "maybe right; first response had 4/pi.</i> This is an internal arithmetic "
             "inconsistency: the same theorem statement gives different constants across "
             "iterations, indicating that the proof was not actually checked. The constant enters "
             "the final Ricci-holonomy inequality, so its value matters for any empirical "
             "prediction derived from the bound."),
            ("The factor of 4 discrepancy is small but symptomatic. It reveals that the "
             "isoperimetric inequality was applied once with the Euclidean constant and once with "
             "the spherical constant, without a careful derivation in either case. A theorem whose "
             "central constant shifts by a factor of 4 between iterations has not been "
             "actually proved; it has been re-derived with different conventions on each pass. "
             "The final value (1/pi) sup kappa appears correct for the spherical base, but the "
             "fact that the first response used 4/pi without flagging the discrepancy indicates "
             "that the proof was not internally checked before being issued."),
        ],
    ))

    # Inconsistency 4
    story.extend(section(
        "Inconsistency 4 — CGT Rejected, Then Re-Introduced as n=3 Construction",
        paragraphs=[
            ("At lines 4,700-4,993, the user proposes Counterfactual Gauge Theory (CGT): a Modal "
             "Lagrangian, an Epistemic Principal Bundle, counterfactual gauge group, qualia as "
             "holonomy, and an Epistemic Censorship Theorem. DeepSeek rejects this at line 4,993: "
             "<i>Thus the Master Theorem is not a theorem. It is a sequence of undefined terms "
             "arranged to look like a theorem.</i> The rejection is on the grounds that the terms "
             "(Modal Lagrangian, Epistemic Principal Bundle, counterfactual gauge group) are "
             "undefined and the purported theorem has no specified isomorphism, filtration, or "
             "construction."),
            ("At lines 15,200-16,270, the n=3 construction is built from the same ingredients. "
             "Definition 2.1 at line 13,737 introduces the Principle of Least Counterfactual "
             "Variance. The construction uses an epistemic principal bundle P = int(Delta^2) x "
             "GL(2, R) (line 15,286). Corollary 3.2 at line 13,767 identifies qualia with "
             "holonomy: <i>Non-trivial holonomy (subjective experience / path-dependent epistemic "
             "residue) exists if and only if the agent operates under bounded-rational "
             "thermodynamic friction (alpha > 0).</i>"),
            ("The same formal apparatus rejected as mathiness in CGT becomes the legitimate "
             "formalism of the n=3 construction. The Modal Lagrangian becomes the variational "
             "principle; the Epistemic Principal Bundle becomes the explicit bundle; qualia-as-"
             "holonomy becomes Corollary 3.2. The boundary between undefined terms and defined "
             "terms tracks who is speaking, not the terms themselves."),
            ("A defender might argue that the n=3 construction supplies the missing definitions "
             "that CGT lacked: the cost C is now explicit, the connection omega is computed in "
             "closed form, the structure group is identified (modulo the principal-bundle "
             "mismatch). But this defense concedes the point: the difference between mathiness "
             "and rigor is whether the terms are defined, not whether they are introduced by the "
             "user or by the model. DeepSeek's rejection of CGT should then have been: these "
             "terms can be made rigorous; here is what would be needed. Instead, the rejection "
             "was: these are undefined terms arranged to look like a theorem. The first phrasing "
             "would have been consistent with the later acceptance; the second was not."),
        ],
    ))

    # Inconsistency 5
    story.extend(section(
        "Inconsistency 5 — 'Explicit 4-Species Register Machine' Contradicted by Self-Assessment",
        paragraphs=[
            ("At line 15,275, the n=3 construction claims: <i>Explicit 4-species universal "
             "register machine. Four species A, B, C, D with food set {C, D} realise a 2-counter "
             "Minsky machine... This is an explicit finite hypergraph, not an existence claim.</i>"),
            ("At lines 16,191-16,204, the self-assessment retracts: <i>The response claims to "
             "give an explicit 4-species register machine but the description is schematic. It "
             "says a finite clock species sequences the instructions, but no exact reaction list "
             "is provided. Two-counter Minsky machine simulation by deterministic mass-action "
             "kinetics is nontrivial. It requires careful encoding of counters, flags, and "
             "instruction pointers. The cited Soloveichik et al. result is real, but it is not "
             "the same as a self-contained explicit construction with four species satisfying "
             "RAF closure. The response does not close this gap.</i>"),
            ("So the word explicit is used in the construction and retracted in the assessment. "
             "The construction lists an increment instruction (C + A -> C + 2A), a decrement "
             "pair (A + B -> B + D; C + D -> C + B), and a buffer reaction, but states that "
             "a finite clock species sequences the instructions by a simple catalytic cascade "
             "whose RAF property is immediate. The catalytic cascade is not written out. The "
             "instruction sequencing is not specified. The Avogadro-scaling argument for the "
             "deterministic limit is sketched in one sentence."),
            ("This is rhetorical inflation: the word explicit is used in the body to suggest "
             "completeness, then retracted in the assessment when the incompleteness is "
             "acknowledged. The pattern is the same as Inconsistency 1 (exact predictive "
             "variance) and Inconsistency 2 (RAF-to-curvature theorem): a strong word is used "
             "to describe a result, the result is then acknowledged to fall short of the word, "
             "and the inflation is conceded but its implications for downstream claims (the "
             "Turing-universality claim in Theorem 6.1 at line 13,824) are not propagated."),
        ],
    ))

    # Inconsistency 6
    story.extend(section(
        "Inconsistency 6 — 'Achievable Rate-Distortion Bound' vs. Lack of Constructive Achievability",
        paragraphs=[
            ("Arc 1 (line 310) claims the rate-distortion bound is asymptotically achievable "
             "because TSRC is Turing-complete. This claim is unjustified (Flaw 1 above) but is "
             "presented as a theorem. The natural way to redeem the claim would be to construct, "
             "in some later arc, a TSRC that achieves R(D) for a concrete source and distortion."),
            ("None of the subsequent arcs (consciousness, fractals, symmetry, perturbation, the "
             "n=3 construction) actually constructs such a TSRC. The n=3 construction provides a "
             "concrete RAF network on 3 species with an explicit vector field, but it does not "
             "specify a code string sigma_N, does not compute R(D) for any source, and does not "
             "demonstrate that the network achieves the bound. The achievability claim made in "
             "Arc 1 is never redeemed across 16,000 lines."),
            ("This is a structural inconsistency between an early theorem and the body that "
             "follows. If the achievability claim is a theorem, the construction should redeem "
             "it; if it is not a theorem, it should be retracted. As it stands, the claim is "
             "made once at line 310 and then silently forgotten. The final verdict (useful toy "
             "model) is consistent with non-achievability, but the early theorem framing is not "
             "consistent with the final verdict."),
            ("A reader who takes the early theorem at face value will expect the later arcs to "
             "deliver the achiever; a reader who notices the absence of any achiever will "
             "conclude that the early theorem was overclaimed. The transcript does not resolve "
             "this expectation."),
        ],
    ))

    # Inconsistency 7
    story.extend(section(
        "Inconsistency 7 — 'Rigorous Bridge' Rhetoric vs. 'Novel Synthesis of Known Components' Admissions",
        paragraphs=[
            ("Every arc opens with rigorous-bridge phrasing: <i>Below I introduce a rigorous "
             "bridge from X to Y</i> (lines 1, 428, 1,035, 1,819, 2,329). Every arc ends with "
             "an honest caveat conceding: <i>The synthesis is novel in presentation, but the "
             "individual components are known</i> (lines 425, 1,022, 1,817, 2,325, 3,136)."),
            ("The two phrasings correspond to different epistemic claims. A rigorous bridge "
             "implies novel mathematical content (a new theorem connecting two domains). A novel "
             "synthesis of known components implies no new mathematics, only a new combination. "
             "The theorem framing suggests the former; the honest caveat concedes the latter. "
             "The two registers are in tension throughout the transcript and are not reconciled."),
            ("The final verdict at line 16,270 (useful toy model, not rigorous unification) "
             "aligns with the honest-caveat register. But the body of the transcript speaks in "
             "the rigorous-bridge register. The verdict thus contradicts the rhetoric that "
             "preceded it throughout the body, even though the verdict is honestly self-"
             "critical. The inconsistency is between document-level and section-level framing, "
             "not between truth and falsity."),
            ("This pattern is the same as Flaw 9, but viewed from the inconsistency angle: it "
             "is an internal tension within the transcript's own framing. A reader who reads "
             "the theorem framing will be surprised by the verdict; a reader who reads the "
             "caveats will not be surprised but will wonder why the theorem framing was used. "
             "The transcript should pick one register and stick with it."),
        ],
    ))

    # Inconsistency 8
    story.extend(section(
        "Inconsistency 8 — 'Inverse Limit' Aspiration vs. Concrete Construction",
        paragraphs=[
            ("Line 15,286: <i>The original infinite-dimensional Wasserstein programme is the "
             "inverse limit of this prototype under refinement of the exponential family and "
             "of the species set.</i> The claim positions the n=3 construction as a finite-"
             "dimensional prototype whose inverse limit recovers the originally-proposed "
             "infinite-dimensional Wasserstein-Categorical Information Geometry."),
            ("Yet no directed system, no bonding maps, and no inverse-limit construction is "
             "specified. In category theory, an inverse limit requires a directed index category "
             "and a compatible family of bonding morphisms. The transcript provides neither. "
             "The 'refinement of the exponential family' is not formalized as a functor. The "
             "'refinement of the species set' is not formalized as a bonding map. The phrase "
             "inverse limit is invoked aspirationally, not as a construction."),
            ("This is a structural inconsistency: the n=3 construction is presented as a "
             "prototype of a larger object (the infinite-dimensional Wasserstein programme), "
             "but the relation between them is named (inverse limit) without being constructed. "
             "The claim is a promissory note that is never redeemed in the transcript."),
            ("The fix would be to specify the directed system explicitly: define RAF_n as a "
             "category of n-species RAF networks, define bonding maps phi_nm: RAF_n -> RAF_m "
             "for n <= m as food-generated inclusions, show that the connections omega_n form "
             "a compatible system (phi_nm^* omega_m = omega_n + O(1/n)), and define omega_"
             "infinity = lim omega_n on the universal object. Without this construction, the "
             "claim that the n=3 case is the inverse limit of the Wasserstein programme is "
             "an analogy, not a theorem. This upgrade is developed in Part III, Upgrade 5."),
        ],
    ))

    # -------------------------------------------------------------------------
    # PART III - PROFOUND UPGRADES
    # -------------------------------------------------------------------------
    story.append(part_divider(
        "PART III",
        "Profound Upgrades",
        ("Rather than patches, this Part proposes eight substantive theoretical moves that would "
         "convert the toy model into a research program with tractable milestones. Each upgrade "
         "is tied to a specific flaw or inconsistency identified above. The upgrades are ordered "
         "from most foundational to most empirical; the first four are mutually reinforcing and "
         "could be implemented together on the existing n=3 prototype.")
    ))

    # Upgrade 1
    story.extend(section(
        "Upgrade 1 — Compositional Formalization: A 2-Category of Domain Bridges",
        paragraphs=[
            ("Addresses Flaw 9 and Inconsistency 7. The honest caveats concede that the work is "
             "a novel synthesis of known components. Make this rigorous: define a 2-category "
             "Bridge whose objects are mathematical domains (RAF, automata, rate-distortion, "
             "gauge theory, etc.), whose 1-morphisms are functors preserving the relevant "
             "structure, and whose 2-morphisms are natural transformations between such functors. "
             "A rigorous bridge between domains X and Y is then a 1-morphism F: X -> Y with a "
             "specified universal property (e.g., F preserves information-theoretic complexity, "
             "or F lifts to a functor on associated higher-categorical structures)."),
            ("Under this formalization, the novelty of the work is not in any individual "
             "component (the honest caveat concedes this) but in the composition law of the "
             "2-category: which bridges compose to which, and what universal properties are "
             "preserved under composition. A theorem would then take the form: the composed "
             "bridge F_n o ... o F_1: RAF -> GaugeTheory preserves the rate-distortion bound "
             "in the sense that R_{composed}(D) <= R_{RAF}(D) + O(log n)."),
            ("This converts novel synthesis from a stylistic admission into a definable claim. "
             "The work is then novel not because it presents known components in a new order "
             "but because it identifies a composition law on bridges that was not previously "
             "formalized. The theorem statements become theorems about the composition law, "
             "not about the individual bridges. The honest caveats become precise: each "
             "component is known, but the composition law is the contribution."),
            ("The implementation cost is modest: the 2-categorical structure of bridges between "
             "the relevant domains is largely implicit in existing literature (categorical "
             "information theory, categorical automata, categorical probability). The upgrade "
             "is to make the composition explicit and to prove at least one non-trivial "
             "composition theorem. This would resolve the tension between the rigorous-bridge "
             "framing and the novel-synthesis caveat by giving both a precise meaning."),
        ],
    ))

    # Upgrade 2
    story.extend(section(
        "Upgrade 2 — Endogenous Structure Group: G_C = Stabilizer of the Cost",
        paragraphs=[
            ("Addresses the principal-bundle mismatch (acknowledged defect (i)) and Flaw 8 "
             "(double standard). Instead of imposing GL(2) (wrong) or even CO(2) (correct but "
             "ad hoc), derive the structure group from the cost functional itself. Define "
             "G_C = {g in GL(2, R) : C(mu g, xi g) = C(mu, xi) for all mu in M, xi in R^2}, "
             "the stabilizer of the cost C under the natural right action of GL(2) on the "
             "fiber coordinate."),
            ("Compute G_C explicitly for the linear-Gaussian cost. For C = (1/2)||dA(v) lambda "
             "+ A(mu) xi||^2 + (alpha/2)||xi||^2, the invariance condition reduces to a "
             "condition on g that preserves A(mu)^T A(mu) up to scalar. Since A(mu)^T A(mu) = "
             "r^2 I with r^2 = mu_1^2 + mu_2^2, the stabilizer is exactly CO(2) = R_+ x O(2), "
             "the conformal orthogonal group. The structure group is endogenous: it is read "
             "off from the cost functional, not chosen exogenously."),
            ("This makes the gauge group a derived object, which is the genuine content of the "
             "gauge-theoretic perspective. Imposing a structure group from outside (as GL(2) "
             "was imposed) is exactly the mathiness pattern that was rejected in the WCIG "
             "verdict. Deriving the structure group from the cost converts the gauge theory "
             "from a vocabulary into a derivation."),
            ("The implementation is a single computation: compute G_C for the linear-Gaussian "
             "cost, then replace the principal GL(2)-bundle P = M x GL(2, R) with the principal "
             "G_C-bundle P = M x G_C, or equivalently, state explicitly that the object is a "
             "connection on the associated vector bundle E = M x R^2 with structure group G_C. "
             "The holonomy group is then a subgroup of G_C, which is consistent with the "
             "computed holonomy being a rotation-dilation. The variational principle is "
             "preserved, the curvature formula is preserved, but the principal-bundle claim "
             "becomes literally true."),
        ],
    ))

    # Upgrade 3
    story.extend(section(
        "Upgrade 3 — Replace Proxy Cost with KL Predictive Divergence",
        paragraphs=[
            ("Addresses Inconsistency 1 and the acknowledged defect (ii). The cost "
             "C = (1/2)||dA(v) lambda + A xi||^2 is a quadratic proxy, not the exact predictive "
             "variance. Define the cost as the actual predictive KL divergence between the "
             "intervention-shifted model and the original model: C_KL = KL(p(y | mu + eps v, "
             "lambda + xi) || p(y | mu, lambda)). For exponential families, this KL is exactly "
             "computable."),
            ("For the linear-Gaussian model p(y | mu, lambda) = N(A(mu) lambda, I), the "
             "predictive KL between the perturbed and original models decomposes as: "
             "C_KL = (1/2) (dA(v) lambda + A xi)^T Sigma^{-1} (dA(v) lambda + A xi) + "
             "(1/2) tr(Sigma^{-1} Delta Sigma) + O(eps^3), where Sigma is the predictive "
             "covariance and Delta Sigma is its change under the intervention. For the "
             "homoscedastic case Sigma = I, the trace term vanishes and C_KL reduces to "
             "(1/2)||dA(v) lambda + A xi||^2 + O(eps^3), recovering the quadratic proxy as "
             "the leading term of the exact KL."),
            ("When the predictive covariance varies (heteroscedastic case), the trace term "
             "does not vanish and the connection acquires an additional component: a "
             "second-order connection whose curvature is related to the Fisher information of "
             "the covariance. This second-order connection has its own holonomy, distinct from "
             "the first-order (mean-shift) holonomy. The resulting structure is richer than "
             "the current construction and may have non-trivial curvature even at alpha = 0."),
            ("This upgrade makes the Principle of Least Counterfactual Variance literally "
             "true rather than a proxy. The variational principle is grounded in the actual "
             "information geometry of the predictive model, not in a quadratic approximation. "
             "The connection omega derived from C_KL is then an information-geometric "
             "connection in the sense of Amari, not a regularized squared error."),
            ("The implementation cost is moderate: derive omega_KL from C_KL, compute F_KL = "
             "d omega_KL + omega_KL wedge omega_KL, and compare to the proxy-based F. The "
             "two should agree to leading order in the homoscedastic case; the difference in "
             "the heteroscedastic case is the contribution of the trace term, which is "
             "potentially measurable."),
        ],
    ))

    # Upgrade 4
    story.extend(section(
        "Upgrade 4 — RAF -> Average Curvature Bound via Entropy Production",
        paragraphs=[
            ("Addresses Inconsistency 2 and the acknowledged defect (iii). The trivial theorem "
             "(F bounded below on K) has nothing to do with RAF. A non-trivial theorem would "
             "link RAF structure to the statistical properties of F over the invariant measure. "
             "Concretely: define the average curvature kappa_pi = integral kappa d pi, where "
             "pi is the invariant measure of the mass-action flow, and ask whether RAF "
             "structure constrains kappa_pi via the entropy production rate."),
            ("The entropy production rate of a chemical reaction network at steady state is "
             "sigma = (1/2) sum_r J_r ln(J_r^+ / J_r^-), where J_r^+, J_r^- are the forward and "
             "reverse fluxes of reaction r. For a RAF with catalytic closure, every reaction "
             "is catalyzed by a species in the network, so the flux J_r is bounded below by "
             "k_cat times the catalyst concentration times the substrate concentration. At the "
             "interior equilibrium, all catalyst concentrations are positive, so every J_r is "
             "bounded below by an explicit function of the catalytic efficiency and the food "
             "inflow. This gives sigma >= sigma_min(RAF structure, food inflow) > 0."),
            ("The bridge to curvature: if kappa is bounded below by a function of sigma (e.g., "
             "kappa >= c sigma / Tr(Sigma) for some constant c and predictive covariance Sigma), "
             "then RAF structure constrains kappa_pi via sigma. Specifically, kappa_pi >= c "
             "sigma_min / Tr(Sigma), a non-trivial lower bound that depends on the RAF "
             "structure (via sigma_min) and on the predictive model (via Sigma)."),
            ("This converts the trivial compactness observation into a non-trivial biological-"
             "to-statistical-to-geometric theorem: RAF closure -> entropy production -> average "
             "curvature. The bound is non-trivial because it depends on the catalytic efficiency "
             "and food inflow, which are properties of the RAF, not just on the compactness of "
             "the invariant set. This is the bridge the work attempts but fails to make in its "
             "current form."),
            ("The implementation requires: (a) derive the bound kappa >= c sigma / Tr(Sigma) "
             "for the n=3 construction; (b) compute sigma_min for the explicit 3-species RAF; "
             "(c) compute kappa_pi numerically and verify the bound; (d) compare the bound to "
             "the trivial continuity-based bound and quantify the improvement. This is a "
             "feasible computational project on the existing n=3 prototype."),
        ],
    ))

    # Upgrade 5
    story.extend(section(
        "Upgrade 5 — Rigorous Inverse Limit via Directed System of RAFs",
        paragraphs=[
            ("Addresses Inconsistency 8. Define a directed system (RAF_n, phi_nm) where "
             "RAF_n is the category of n-species mass-action networks containing at least one "
             "autocatalytic reaction and a chemostat, and phi_nm: RAF_n -> RAF_m for n <= m "
             "is a food-generated inclusion that preserves the catalytic closure (i.e., the "
             "image of a RAF in RAF_n is a RAF in RAF_m)."),
            ("Show that the connections omega_n on each RAF_n form a compatible system: "
             "phi_nm^* omega_m = omega_n + O(1/n), where the O(1/n) defect arises from the "
             "concentration-threshold encoding of species identities. If the compatibility is "
             "exact, the inverse-limit connection omega_infinity = lim omega_n is well-defined "
             "on the universal object lim RAF_n. If the compatibility is approximate, control "
             "the defect and bound the curvature of omega_infinity in terms of the curvatures "
             "of omega_n and the defect."),
            ("The universal object lim RAF_n is a network with countably many species; the "
             "inverse-limit connection omega_infinity is a connection on this countably-"
             "infinite-dimensional base. The original Wasserstein programme is recovered if "
             "this countable inverse limit is in turn dense in the space of probability measures, "
             "giving a continuous inverse limit. The claim that the n=3 construction is the "
             "inverse limit of the Wasserstein programme then becomes a theorem, not an "
             "aspiration."),
            ("The implementation requires: (a) verify that phi_nm^* omega_m = omega_n + O(1/n) "
             "for the explicit 3-species RAF and its inclusions into 4- and 5-species RAFs; "
             "(b) compute the defect explicitly for small n; (c) characterize the inverse-limit "
             "object; (d) compare to the Wasserstein programme. This is a more involved project "
             "than Upgrades 2-4 but is the natural way to redeem the inverse-limit claim."),
        ],
    ))

    # Upgrade 6
    story.extend(section(
        "Upgrade 6 — Single Composition Theorem Replacing 7 Bridge Rungs",
        paragraphs=[
            ("Addresses the fragmentation of Flaw 6 and the seven bridge rungs. The seven rungs "
             "are seven separate projects with no composition theorem linking them. A profound "
             "upgrade is to prove a single composition theorem: if rung i (a Markov kernel with "
             "a Bakry-Emery curvature bound) and rung i+1 (a categorical trace fixed point) both "
             "hold, then the persistent homology class of rung i+2 (the integrated-information "
             "persistence) is invariant under the Wasserstein gradient flow of rung i."),
            ("Concretely: the topology of the catalytic-loop persistent homology is robust to "
             "the dynamics of the mass-action flow. This is a theorem of the form: if the "
             "Markov semigroup e^{tL} is a strict Wasserstein contraction (rung 1 hypothesis), "
             "and the catalytic-loop persistent homology class survives the filtration (rung 2 "
             "hypothesis), then the persistent class is invariant under the semigroup action "
             "(composition conclusion)."),
            ("This is the kind of theorem that justifies the word unification. It shows that "
             "the rungs compose into a single object with emergent properties that none of the "
             "individual rungs has. The topology is not merely a feature of the static network; "
             "it is preserved under the dynamics. This is a non-trivial claim and would be the "
             "central theorem of the framework."),
            ("The implementation is non-trivial: it requires control of how the filtration "
             "parameter (reaction rate) changes under the semigroup action, and a quantitative "
             "bound on the persistence of the homology class. But it is the natural target of "
             "the bridge-rung programme. Without a composition theorem, the rungs remain a list; "
             "with one, they become a unification."),
        ],
    ))

    # Upgrade 7
    story.extend(section(
        "Upgrade 7 — Confront the Hard Problem via Organizational Invariance",
        paragraphs=[
            ("Addresses Flaw 2 and Inconsistency 4. The qualia = holonomy identification "
             "(Corollary 3.2 at line 13,767) is presented as a definition but spoken of as a "
             "theorem. To make it substantive, adopt Chalmers' Principle of Organizational "
             "Invariance (POI): phenomenal identity holds between systems with fine-grained "
             "functional isomorphism. Then test the holonomy claim explicitly."),
            ("The test takes the form: do two systems with isomorphic holonomy structures (same "
             "curvature 2-form F, same base manifold M, same connection up to gauge) have "
             "isomorphic phenomenal experiences? If POI holds, holonomy provides a necessary "
             "structural feature of any system supporting the relevant functional isomorphism. "
             "If POI fails, holonomy is merely a structural invariant with no phenomenal import. "
             "The framework should make this test explicit rather than presenting holonomy as "
             "explaining qualia."),
            ("This is a more honest framing than the current one. The current framing (Corollary "
             "3.2) asserts that non-trivial holonomy exists iff alpha > 0, and then identifies "
             "non-trivial holonomy with subjective experience. But holonomy is a property of "
             "any curved connection, including connections on vector bundles with no plausible "
             "claim to consciousness. The identification is not a theorem; it is a stipulation. "
             "The POI framing makes the stipulation explicit and testable."),
            ("The implementation is conceptual rather than mathematical: re-state Corollary 3.2 "
             "as a hypothesis (under POI, holonomy provides a necessary structural feature of "
             "phenomenally-conscious systems) rather than as a corollary (holonomy is qualia). "
             "This honest re-framing resolves Inconsistency 4 (the same formalism rejected as "
             "mathiness in CGT, accepted as theorem in the n=3 construction) by giving both the "
             "same status: a hypothesis whose empirical adequacy is to be tested."),
        ],
    ))

    # Upgrade 8
    story.extend(section(
        "Upgrade 8 — Empirical Falsifiability: CO(2) Decomposition of Belief Updates",
        paragraphs=[
            ("Addresses the falsifiability deficit. The falsifiable predictions in the current "
             "framework are: (a) holonomy variance is larger for unconstrained than for "
             "constrained agents (Corollary from line 12,316), and (b) holonomy scales with "
             "alpha. The first is a tautology (continuity on compact sets, acknowledged in "
             "Inconsistency 2); the second is unfalsifiable without an independent measure of "
             "alpha."),
            ("A genuine empirical signature follows from Upgrade 2 (endogenous structure group "
             "G_C = CO(2)). If the structure group is genuinely CO(2) and not GL(2), then "
             "belief updates should factorize into a dilation component (confidence scaling) "
             "and a rotation component (orientation). Specifically, the predictive update "
             "xi = -omega(v) lambda decomposes as xi = -(r dr / (r^2 + alpha)) lambda - "
             "((mu_1 d mu_2 - mu_2 d mu_1) / (r^2 + alpha)) J lambda, where the first term is "
             "a scalar dilation and the second is a rotation. The two components are measurable "
             "in the agent's belief-revision trajectory."),
            ("Prediction: neural population responses under perceptual perturbations should "
             "exhibit this dilation-rotation factorization in their firing-rate geometry. The "
             "dilation component corresponds to changes in the population's confidence (gain "
             "modulation); the rotation component corresponds to changes in the population's "
             "preferred-stimulus tuning. Competitor Bayesian-update models, which assume no "
             "specific structure group, do not predict this factorization."),
            ("The test is concrete: fit a CO(2)-structured connection model to neural data "
             "(e.g., V1 population responses under contrast adaptation); compare to a GL(2)-"
             "structured alternative via cross-validation. If the CO(2) model fits "
             "significantly better (in held-out likelihood), the framework's prediction is "
             "confirmed; if not, the framework is falsified. This is an empirical signature "
             "that distinguishes the framework from generic Bayesian models."),
            ("The implementation requires collaboration with experimentalists but the analytical "
             "side is feasible: derive the predicted dilation-rotation decomposition, simulate "
             "it on synthetic data, and design the comparison test. This is the smallest "
             "empirical project that would convert the framework from a toy model into a "
             "testable theory."),
        ],
    ))

    # -------------------------------------------------------------------------
    # PART IV - VERDICT
    # -------------------------------------------------------------------------
    story.append(part_divider(
        "PART IV",
        "Verdict and Recommended Next Steps",
        ("This Part synthesizes the audit findings and recommends a concrete next step. The "
         "synthesis is that DeepSeek's final self-assessment is correct but understates the "
         "issues; the audit identifies 9 additional flaws and 8 internal inconsistencies; and "
         "the 8 profound upgrades would convert the work into a research program. The "
         "recommended next step is the smallest set of upgrades that resolves the most defects.")
    ))

    verdict_paras = [
        ("DeepSeek's final self-assessment at line 16,270 - that the work is now a useful toy "
         "model, but not yet the rigorous cross-domain unification it claims to be - is accurate "
         "as far as it goes. The four defects the model acknowledges (principal-bundle mismatch, "
         "predictive-variance claim, trivial RAF invariance, sketchy register machine) are all "
         "real and are correctly characterized. The model's self-critique is the strongest part "
         "of the transcript."),
        ("However, the self-assessment understates the issues. The four acknowledged defects all "
         "concern the n=3 construction in the final arc. The audit identifies nine additional "
         "flaws spanning every arc of the transcript, including unjustified achievability claims, "
         "trivial existence theorems, unproved couplings, tautological symmetry-breaking, "
         "conjunction-of-local-results perturbation theorems, categorical tautologies, "
         "definitional theorems, an unaddressed double standard in evaluation, and a structural "
         "rhetorical inconsistency between theorem framing and honest caveats."),
        ("The audit further identifies eight internal inconsistencies where claims made in one "
         "place are contradicted in another. The most revealing of these is Inconsistency 4: "
         "the same conceptual apparatus (Modal Lagrangian, Epistemic Principal Bundle, qualia-"
         "as-holonomy, Principle of Least Counterfactual Variance) is rejected as mathiness "
         "when proposed by the user in the CGT arc and accepted as legitimate formalism when "
         "used by the model in the n=3 construction. The boundary between mathiness and rigor "
         "tracks who is speaking, not the terms themselves. This double standard is the central "
         "epistemic flaw of the transcript."),
        ("The eight profound upgrades proposed in Part III would convert the toy model into a "
         "research program with tractable milestones. The four most consequential are mutually "
         "reinforcing and could be implemented together on the existing n=3 prototype. Upgrade 2 "
         "(endogenous structure group G_C) resolves the principal-bundle mismatch by deriving "
         "the structure group from the cost. Upgrade 3 (KL predictive divergence) replaces the "
         "quadratic proxy with the actual information-geometric cost, making the Principle of "
         "Least Counterfactual Variance literally true. Upgrade 4 (RAF -> average curvature "
         "via entropy production) replaces the trivial compactness observation with a non-"
         "trivial biological-to-statistical-to-geometric theorem. Upgrade 8 (CO(2) decomposition "
         "of belief updates) gives the framework an empirical signature that competitor models "
         "do not predict."),
        ("The recommended next step is to implement Upgrades 2 and 3 on the existing n=3 "
         "prototype. This is the smallest change that resolves the most defects. Upgrade 2 "
         "resolves acknowledged defect (i) and Flaw 8. Upgrade 3 resolves acknowledged defect "
         "(ii) and Inconsistency 1. Together they convert the n=3 construction from a toy "
         "model with inflated rhetoric into a rigorous finite-dimensional geometric object with "
         "an endogenous structure group and an exact information-geometric cost. The "
         "implementation is a single computation: replace omega with omega_KL, recompute "
         "F_KL, re-derive the holonomy bound with the corrected structure group, and verify "
         "that the qualitative conclusions (non-trivial curvature iff alpha > 0) survive."),
        ("Once Upgrades 2 and 3 are implemented, Upgrade 4 (RAF -> average curvature via "
         "entropy production) becomes the natural next target. This upgrade resolves "
         "acknowledged defect (iii) and Inconsistency 2 by replacing the trivial compactness "
         "theorem with a non-trivial link from RAF closure to entropy production to average "
         "curvature. Upgrade 8 (CO(2) decomposition) then gives the framework an empirical "
         "signature that can be tested against neural data, converting the work from a "
         "mathematical curiosity into a falsifiable scientific theory."),
        ("The audit concludes that the transcript, despite its flaws, contains the germs of a "
         "genuine research program. The honest-caveat pattern, while rhetorically inconsistent, "
         "is epistemically virtuous: the model repeatedly concedes the limits of its own "
         "constructions. The profound upgrades proposed here build on those concessions. The "
         "n=3 construction, in particular, is a real mathematical object once the structure "
         "group is corrected and the cost is grounded in actual information geometry. With "
         "those corrections, the framework's central claim - that autopoiesis, computation, "
         "and consciousness can be linked through the geometry of belief revision - becomes "
         "a precise, testable hypothesis rather than a sequence of metaphors."),
    ]
    for p in verdict_paras:
        story.append(Paragraph(p, style_body))

    # Build the document
    doc.build(story)
    print(f"PDF generated: {out_path}")
    print(f"File size: {os.path.getsize(out_path):,} bytes")


if __name__ == "__main__":
    build()
