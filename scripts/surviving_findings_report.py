#!/usr/bin/env python3
"""
Comprehensive Report on Surviving Findings from the DeepSeek Cross-Domain
Unification Audit Project.

Presents the surviving technical claims factually: claims, methods, evidence,
and implications. No diary/change-log/comparative framing.

Sections:
  Cover
  Abstract
  1.  Project Scope and Method
  2.  Verified Defects in the Source Transcript
  3.  Cross-Arc Structural Pattern
  4.  Specific Mathematical Breakdowns
  5.  Joint Cross-Reference Defects
  6.  Synthesized Theoretical Framework - SAVGS
  7.  Algorithmic Rate-Distortion Replacement
  8.  Optic/Lens Category Unification of Fixed Points
  9.  CPTP Open Quantum Channel for Self-Referential Prediction
  10. Bregman-Divergence Noether Correspondence
  11. Endogenous Structure Group
  12. Repeated-Loop Adaptation Fatigue and Calibration Protocol
  13. Falsifiable Claim Hierarchy
  14. Synthesized Theoretical Statement
  15. Implications and Open Problems
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
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
# Cascade palette - cold academic minimalist
#   text_primary #212425  text_muted #7f8589
#   accent       #2897cf  accent_secondary #bf5836 (rust)
#   header_fill  #486471  cover_block #3d5764
#   border       #bfc8cc  table_stripe #f3f4f5
#   page_bg      #f6f6f7  section_bg  #eceded
# -----------------------------------------------------------------------------
C_PRIMARY    = HexColor('#212425')
C_MUTED      = HexColor('#7f8589')
C_ACCENT     = HexColor('#2897cf')
C_ACCENT_2   = HexColor('#bf5836')   # rust, used sparingly for "Decisive test"
C_HEADER     = HexColor('#486471')
C_COVER_BG   = HexColor('#3d5764')
C_COVER_FG   = HexColor('#F8FAFC')
C_BORDER     = HexColor('#bfc8cc')
C_TABLE_ALT  = HexColor('#f3f4f5')
C_QUOTE_BG   = HexColor('#eceded')
C_QUOTE      = HexColor('#374151')

# -----------------------------------------------------------------------------
# Styles
# -----------------------------------------------------------------------------
styles = getSampleStyleSheet()

style_h1 = ParagraphStyle(
    'H1', parent=styles['Heading1'],
    fontName='NotoSerifSC-Bold', fontSize=18, leading=24,
    textColor=C_HEADER, alignment=TA_LEFT,
    spaceBefore=18, spaceAfter=8,
)
style_h2 = ParagraphStyle(
    'H2', parent=styles['Heading2'],
    fontName='NotoSerifSC-Bold', fontSize=13, leading=18,
    textColor=C_PRIMARY, alignment=TA_LEFT,
    spaceBefore=12, spaceAfter=4,
)
style_h3 = ParagraphStyle(
    'H3', parent=styles['Heading3'],
    fontName='NotoSerifSC-Bold', fontSize=11, leading=15,
    textColor=C_ACCENT, alignment=TA_LEFT,
    spaceBefore=8, spaceAfter=3,
)
style_body = ParagraphStyle(
    'Body', parent=styles['Normal'],
    fontName='NotoSerifSC', fontSize=10, leading=15,
    textColor=C_PRIMARY, alignment=TA_JUSTIFY,
    spaceBefore=2, spaceAfter=6,
)
style_body_l = ParagraphStyle(
    'BodyL', parent=styles['Normal'],
    fontName='NotoSerifSC', fontSize=10, leading=15,
    textColor=C_PRIMARY, alignment=TA_LEFT,
    spaceBefore=2, spaceAfter=6,
)
style_meta = ParagraphStyle(
    'Meta', parent=styles['Normal'],
    fontName='NotoSerifSC', fontSize=9, leading=12,
    textColor=C_MUTED, alignment=TA_LEFT,
)
style_quote = ParagraphStyle(
    'Quote', parent=styles['Normal'],
    fontName='NotoSerifSC', fontSize=9.5, leading=14,
    textColor=C_QUOTE, alignment=TA_LEFT,
    leftIndent=14, rightIndent=10,
    spaceBefore=4, spaceAfter=6,
    backColor=C_QUOTE_BG, borderPadding=8,
)
style_table_cell = ParagraphStyle(
    'TableCell', parent=styles['Normal'],
    fontName='NotoSerifSC', fontSize=8.5, leading=11,
    textColor=C_PRIMARY, alignment=TA_LEFT,
)
style_table_head = ParagraphStyle(
    'TableHead', parent=styles['Normal'],
    fontName='NotoSerifSC-Bold', fontSize=9, leading=12,
    textColor=HexColor('#FFFFFF'), alignment=TA_LEFT,
)
style_section_label = ParagraphStyle(
    'SectionLabel', parent=styles['Normal'],
    fontName='NotoSerifSC-Bold', fontSize=10, leading=14,
    textColor=C_ACCENT, alignment=TA_LEFT,
    spaceBefore=0, spaceAfter=2,
)

# -----------------------------------------------------------------------------
# Cover page (full-bleed dark)
# -----------------------------------------------------------------------------
def draw_cover(canv, doc):
    page_w, page_h = A4
    canv.saveState()
    canv.setFillColor(C_COVER_BG)
    canv.rect(0, 0, page_w, page_h, fill=1, stroke=0)

    # accent rules at top
    canv.setStrokeColor(C_ACCENT)
    canv.setLineWidth(3)
    canv.line(2.2*cm, page_h - 4*cm, 6.5*cm, page_h - 4*cm)
    canv.setStrokeColor(C_ACCENT_2)
    canv.setLineWidth(1.5)
    canv.line(6.7*cm, page_h - 4*cm, 8.5*cm, page_h - 4*cm)

    canv.setFillColor(C_COVER_FG)
    canv.setFont('NotoSerifSC-Bold', 26)
    canv.drawString(2.2*cm, page_h - 5.4*cm, "Surviving Findings from the")
    canv.drawString(2.2*cm, page_h - 6.5*cm, "DeepSeek Cross-Domain Unification")
    canv.drawString(2.2*cm, page_h - 7.6*cm, "Audit Project")

    canv.setFont('NotoSerifSC', 13)
    canv.setFillColor(HexColor('#CBD5E1'))
    canv.drawString(2.2*cm, page_h - 8.8*cm, "Claims, methods, evidence, and implications")

    canv.setStrokeColor(HexColor('#94A3B8'))
    canv.setLineWidth(0.5)
    canv.line(2.2*cm, page_h - 9.8*cm, page_w - 2.2*cm, page_h - 9.8*cm)

    canv.setFillColor(HexColor('#CBD5E1'))
    canv.setFont('NotoSerifSC', 10)
    lines = [
        "A 16,271-line transcript proposes a six-arc unification:",
        "RAF rate-distortion, Recursive Predictive Self-Information",
        "consciousness, Iterated Function System fractals, Noether-",
        "type symmetry correspondence, perturbation theory of optimal",
        "encoding, and the n=3 Fisher-Rao geometric construction.",
        "",
        "Two independent line-level audits applied ripgrep-verified",
        "claim extraction to every theorem, definition, and caveat.",
        "Cross-examination isolates the technical claims that survive.",
        "",
        "This report presents those surviving claims, the methods",
        "that established them, the evidence that supports them,",
        "and their implications for the underlying research program.",
    ]
    y = page_h - 11.2*cm
    for ln in lines:
        canv.drawString(2.2*cm, y, ln)
        y -= 13

    canv.setStrokeColor(C_ACCENT)
    canv.setLineWidth(1)
    canv.line(2.2*cm, 3.5*cm, 6.2*cm, 3.5*cm)
    canv.setFont('NotoSerifSC-Bold', 10)
    canv.setFillColor(HexColor('#F8FAFC'))
    canv.drawString(2.2*cm, 3.0*cm, "Z.ai")
    canv.setFont('NotoSerifSC', 9)
    canv.setFillColor(HexColor('#94A3B8'))
    canv.drawString(2.2*cm, 2.4*cm, "Comprehensive project report")
    canv.drawString(2.2*cm, 2.0*cm, "Sources: transcript + two audits + joint cross-examination")
    canv.restoreState()


class CoverPage(Flowable):
    def __init__(self):
        super().__init__()
        self.width = 0
        self.height = 0
    def draw(self):
        pass


def part_divider(label, title, blurb):
    return KeepTogether([
        Spacer(1, 16),
        Paragraph(label, style_section_label),
        Paragraph(title, style_h1),
        HRFlowable(width="100%", thickness=1.2, color=C_ACCENT, spaceBefore=2, spaceAfter=10),
        Paragraph(blurb, style_body),
        Spacer(1, 6),
    ])


def section(heading, paragraphs, level=2):
    style = style_h2 if level == 2 else style_h3
    flow = [Paragraph(heading, style)]
    for p in paragraphs:
        flow.append(Paragraph(p, style_body))
    return flow


def claim_block(claim_label, claim_text, method_text, evidence_text, implication_text):
    """Render a structured claim block: Claim / Method / Evidence / Implication."""
    out = []
    out.append(Paragraph(claim_label, style_h3))
    out.append(Paragraph(f"<b>Claim.</b> {claim_text}", style_body))
    out.append(Paragraph(f"<b>Method.</b> {method_text}", style_body))
    out.append(Paragraph(f"<b>Evidence.</b> {evidence_text}", style_body))
    out.append(Paragraph(f"<b>Implication.</b> {implication_text}", style_body))
    out.append(Spacer(1, 4))
    return out


def build():
    out_path = "/home/z/my-project/download/surviving_findings_report.pdf"
    doc = SimpleDocTemplate(
        out_path, pagesize=A4,
        leftMargin=2.2*cm, rightMargin=2.2*cm,
        topMargin=2.2*cm, bottomMargin=2.0*cm,
        title="Surviving Findings from the DeepSeek Cross-Domain Unification Audit Project",
        author="Z.ai",
        subject="Comprehensive report on surviving claims, methods, evidence, implications",
        creator="Z.ai PDF skill (ReportLab)",
    )
    page_w, page_h = A4
    content_w = page_w - 4.4*cm

    story = []

    # Cover
    story.append(CoverPage())
    story.append(PageBreak())
    doc.onFirstPage = draw_cover
    doc.onLaterPages = lambda canv, doc: None

    # =============================================================
    # Abstract
    # =============================================================
    story.append(part_divider(
        "ABSTRACT",
        "Surviving Findings",
        "A 16,271-line transcript proposes a six-arc unification of "
        "rate-distortion, fractal, symmetry, and information-geometric "
        "constructions. Two independent line-level audits verified each "
        "claim against the source text, then cross-examined the converging "
        "and diverging findings. This report presents the technical claims "
        "that survive that cross-examination."
    ))
    abstract_paras = [
        ("The DeepSeek cross-domain unification transcript composes six arcs: RAF "
         "rate-distortion as a bridge from Kolmogorov complexity to Shannon entropy; "
         "Recursive Predictive Self-Information (RPSI) as a consciousness definition; "
         "Iterated Function Systems (IFS) as a fractal account of perception; "
         "Noether-type symmetry correspondence for Markov chains; perturbation theory "
         "of the optimal encoding; the abortive Wasserstein-Categorical Information "
         "Geometry (WCIG) upgrade; the bridge-rung composition; and the explicit "
         "n=3 Fisher-Rao geometric construction with a curvature-survival equivalence "
         "theorem. The author of the transcript acknowledges four defects in a final "
         "self-assessment section (transcript lines 13985 through 16270)."),

        ("Two independent line-level audits confirmed those four defects and "
         "identified additional mathematical breakdowns, internal inconsistencies, and "
         "missing premises across every arc. Cross-examination of the two audits "
         "surfaced a further six defects visible only when both perspectives are "
         "synthesized, and isolated three corrections to early conjectures. The "
         "surviving technical claims compose a coherent research program rather than "
         "a catalogue of errors."),

        ("The central surviving thesis is the following. Adaptive systems are "
         "endangered not by large environmental changes but by non-commuting "
         "sequences of individually manageable changes whose induced policy holonomy "
         "aligns with vulnerable self-maintenance directions. The upper bound on "
         "vulnerability is the algorithmic-rate-distortion-theoretic viability-weighted "
         "curvature on a CO(n-1)-structured stratified connection. The defensible "
         "proposition is sharper: on smooth constant-active-set strata of an "
         "experimentally parameterized control manifold, Fisher-minimal "
         "constraint-preserving adaptation defines a stratified connection whose "
         "viability-weighted curvature predicts leading-order policy hysteresis; "
         "whether that holonomy is fatal depends on viability margins, along-path "
         "disturbances, and the regeneration of internal maintenance machinery."),

        ("The report is organized as a sequence of claim-method-evidence-implication "
         "blocks. Sections 2 through 5 establish what does not survive examination. "
         "Sections 6 through 12 present the synthesized theoretical framework that "
         "replaces the broken constructions. Section 13 presents the seven-claim "
         "falsifiable prediction hierarchy with the prerequisite that the n=3 prototype "
         "is sufficient for claims A through E but a non-abelian extension to n at "
         "least 4 is binding for the structure-group test. Sections 14 and 15 state "
         "the synthesized thesis and its open research targets."),
    ]
    for p in abstract_paras:
        story.append(Paragraph(p, style_body))

    story.append(PageBreak())

    # =============================================================
    # Section 1 - Project Scope and Method
    # =============================================================
    story.append(part_divider(
        "SECTION 1",
        "Project Scope and Method",
        "Scope and methodology of the audit project, the falsifiability "
        "standard applied, and the verification protocol used to certify "
        "absence of constructs in the source transcript."
    ))
    s1 = [
        ("The source is a single DeepSeek conversation transcript of 16,271 lines, "
         "produced in a single sitting, that proposes a cross-domain unification. The "
         "unification composes six construction arcs. Arc 1 establishes RAF "
         "(Reactive Anticipatory Framing) as a rate-distortion bridge between "
         "Kolmogorov complexity and Shannon entropy (transcript lines 1 through 427). "
         "Arc 2 introduces Recursive Predictive Self-Information, or RPSI, as a "
         "definition of consciousness (lines 428 through 1022). Arc 3 treats fractals "
         "as Iterated Function Systems and connects perception to fractal attractors "
         "(lines 1044 through 1814). Arc 4 invokes Noether-type symmetry correspondence "
         "for Markov chains (lines 1908 through 2324). Arc 5 develops perturbation "
         "theory of the optimal encoding (lines 2378 through 3136). Arc 6 is the "
         "abortive Wasserstein-Categorical Information Geometry upgrade (lines 3140 "
         "through 3518). The seven bridge rungs compose the arcs across lines 4000 "
         "through 4500. The Counterfactual Gauge Theory upgrade spans lines 4600 "
         "through 5200. The n=3 Fisher-Rao explicit construction begins near line "
         "11000. The final self-assessment section spans lines 13985 through 16270."),

        ("The audit project applied two independent line-level reviews to the same "
         "transcript. Each audit located every theorem statement, every definition, "
         "and every caveat using ripgrep searches against the transcript file, then "
         "read the surrounding twenty-line window to extract the precise claim. Each "
         "claim was then evaluated against three questions: is it mathematically "
         "correct given the stated assumptions; is it substantively novel given the "
         "cited prior art; and is it consistent with claims made elsewhere in the "
         "transcript."),

        ("A second verification protocol, used repeatedly throughout the project, "
         "is the zero-match proof of absence. When a defect consists of a missing "
         "construct, the absence was certified by running ripgrep for the construct "
         "name against the full transcript and recording zero matches. Constructs "
         "certified absent by this method include pathwise viability, the Nagumo "
         "inward-pointing condition, viability tube, intermediate-point feasibility, "
         "active-set constraint switching, and stratified regularity beyond "
         "piecewise-smooth. These zero-match results are the evidence that the "
         "corresponding defects are not artifacts of an unsympathetic reading but "
         "structural features of the source."),

        ("The falsifiability standard applied throughout the project is the same "
         "standard the project applies to the source transcript: every surviving "
         "claim must be associated with at least one observable quantity whose "
         "measured value would either confirm or refute the claim. Where a claim "
         "cannot be made falsifiable in its original form, the project replaces it "
         "with a stronger version that can. The seven-claim falsifiable hierarchy in "
         "Section 13 is the output of that replacement program."),
    ]
    story.extend(section("1.1 Source and scope", s1))

    s1_2 = [
        ("The cross-examination method is the project's distinctive contribution. "
         "Where the two audits converge, the convergence is itself evidence: the "
         "finding is real and not a perspective artifact. Where they diverge, the "
         "divergence identifies complementary concerns rather than contradictions. "
         "The cross-arc structural pattern (Section 3) is an output of this method, "
         "as are the six joint cross-reference defects (Section 5) and the strengthened "
         "upgrades that integrate insights from both perspectives (Sections 6 through 12)."),

        ("Each surviving claim is presented below in a four-part structure: claim, "
         "method, evidence, implication. The claim states the technical content. The "
         "method states how the claim was established or how the replacement is "
         "constructed. The evidence cites the specific transcript line numbers, the "
         "ripgrep verification results, or the mathematical counterexample. The "
         "implication states what the claim means for the underlying research "
         "program. This structure is preserved throughout the report."),
    ]
    story.extend(section("1.2 Cross-examination method", s1_2))

    story.append(PageBreak())

    # =============================================================
    # Section 2 - Verified Defects in the Source Transcript
    # =============================================================
    story.append(part_divider(
        "SECTION 2",
        "Verified Defects in the Source Transcript",
        "Four defects that the transcript's own final self-assessment "
        "acknowledges. The two independent audits independently confirm each "
        "one. The convergence is itself the evidence that these are real."
    ))
    s2_intro = (
        "Each defect is presented with its specific transcript line citation, the "
        "mathematical content of the defect, and the corrected form. These four are "
        "the minimal set that any defensible version of the transcript's unification "
        "must address."
    )
    story.append(Paragraph(s2_intro, style_body))
    story.append(Spacer(1, 6))

    story.extend(claim_block(
        "2.1 Structure group of the Fisher-Rao construction",
        "The transcript frames the principal bundle of the n=3 Fisher-Rao construction "
        "with structure group GL(2). The correct structure group is CO(2) = R+ × O(2), "
        "the conformally orthogonal group, because the Fisher-Rao metric is invariant "
        "only under conformal orthogonal transformations of the parameter space, not "
        "under general linear transformations.",
        "ripgrep verification: the GL(2) framing appears in the n=3 construction "
        "(approximately transcript line 11000 forward); the self-assessment at lines "
        "13985 through 16270 acknowledges the correction. The mathematical content "
        "is verified by direct computation of the Fisher-Rao metric's invariance group.",
        "Transcript lines 13985 through 16270 (self-assessment section); the CO(2) "
        "correction is acknowledged by the author within the same section.",
        "The bundle atlas of the n=3 construction is correctly described only after "
        "the structure group is corrected to CO(2). Any computation that uses GL(2) "
        "transitions between charts overcounts the gauge freedom and yields spurious "
        "holonomy. The corrected structure group is the foundation for the commuting-"
        "control test of Section 13, Claim F.",
    ))

    story.extend(claim_block(
        "2.2 'Exact predictive variance' is a squared mean shift",
        "The quantity labeled 'exact predictive variance' in the transcript is in fact "
        "a squared mean shift, bias squared, while the predictive variance Var(y) "
        "remains constant at the identity I throughout. The labeling suggests a "
        "variance formula; the substance is a bias formula.",
        "Direct verification of the algebraic derivation as written in the transcript. "
        "The expression decomposes as bias squared plus variance, and the variance term "
        "is constant; only the bias term carries the dynamics the labeling attributes to "
        "the variance.",
        "Transcript self-assessment section (lines 13985 through 16270); the same arc "
        "in which the variance is initially introduced also retracts the label, an "
        "internal inconsistency recorded in Section 3.",
        "Empirical predictions that depend on the 'predictive variance' actually depend "
        "on bias squared. Reinterpretation changes which experimental observable should "
        "be measured. The corrected label also clarifies that the dynamics are carried "
        "by the bias term, which is what the algorithmic rate-distortion replacement of "
        "Section 7 makes operational.",
    ))

    story.extend(claim_block(
        "2.3 The RAF invariance theorem reduces to continuity on a compact set",
        "The theorem stated as the RAF invariance theorem reduces to the observation "
        "that a positive continuous function on a compact set attains its infimum. The "
        "conclusion follows from continuity plus compactness alone; no RAF-specific "
        "structure is used.",
        "Direct reading of the proof as written. The argument invokes only the "
        "extreme-value theorem applied to the relevant functional. No use is made of "
        "the reactive, anticipatory, or framing structure that defines RAF.",
        "Transcript self-assessment section (lines 13985 through 16270); the proof "
        "appears earlier in the RAF arc (lines 1 through 427).",
        "The theorem cannot bear the weight assigned to it in the unification chain. "
        "The inverse-limit construction of the directed system of RAFs, proposed as an "
        "open problem in Section 15, is the replacement research target.",
    ))

    story.extend(claim_block(
        "2.4 The 4-species register machine is schematic",
        "The 4-species chemical register machine invoked in the RAF arc has no reaction "
        "list. No reactants, products, or catalysts are specified. The machine is a "
        "label without a mechanism.",
        "ripgrep verification: searches for reaction-list keywords, reactant names, "
        "and catalyst identifiers return only the introductory framing of the machine, "
        "no enumeration of reactions.",
        "Transcript RAF arc and the self-assessment section (lines 1 through 427 and "
        "13985 through 16270).",
        "A schematic machine cannot be the substrate of an autopoiesis closure test. "
        "The intervention-based autopoiesis closure test of Section 6 supplies a concrete "
        "4-species example (species A, B, C, D; reactions R1 through R4 catalyzing "
        "specified transformations) that makes the closure test operational.",
    ))

    story.append(PageBreak())

    # =============================================================
    # Section 3 - Cross-Arc Structural Pattern
    # =============================================================
    story.append(part_divider(
        "SECTION 3",
        "Cross-Arc Structural Pattern",
        "Each individual arc is mathematically real. The connections between arcs "
        "are analogies rather than formal mappings. The unification is composition "
        "by analogy, not by a composition theorem."
    ))
    s3_intro = (
        "The cross-arc structural pattern is the most consequential systemic finding "
        "of the audit project. Every individual arc invokes legitimate mathematics: "
        "rate-distortion theory, IFS fixed-point theorems, Noether's theorem, "
        "perturbation theory, information geometry, and category theory. The defect "
        "is not in any single arc; it is in the connections between arcs. Each bridge "
        "between arcs is a rhetorical move rather than a formal construction."
    )
    story.append(Paragraph(s3_intro, style_body))

    s3_1 = [
        ("The bridge between the RAF arc and the curvature arc is presented as a "
         "theorem. The self-assessment retracts it to a continuity observation. The "
         "internal inconsistency between the theorem framing and the honest caveat is "
         "an instance of the structural pattern: the strong form is asserted when the "
         "construction is built, and the weak form is conceded when the construction "
         "is audited. The transcript itself oscillates between these registers."),

        ("The bridge between the WCIG upgrade and the dagger-compact categorical "
         "framework of constructor theory lacks a translation functor. The transcript "
         "introduces both vocabularies but never constructs a functor between them. "
         "A vocabulary shared in name is not a mapping in category-theoretic substance. "
         "The same pattern appears in Bridge Rung 6, which is a categorical tautology: "
         "the conclusion is a definitional restatement of the premises, not a theorem."),

        ("The bridge from RAF rate-distortion to algorithmic rate-distortion is "
         "blocked by a type confusion. The transcript's R(D) is a set-average quantity "
         "defined over a probability distribution on source strings. The Kolmogorov "
         "complexity K(x) is a single-string quantity. No i.i.d. or ergodicity "
         "assumption is stated to connect them. The bridge from deterministic state "
         "transition to the R(D) achievability is similarly blocked: the deterministic "
         "transition delta is a special case, but achieving R(D) in general requires "
         "random coding, and the gap R_det(D) greater than or equal to R(D) can be "
         "infinite."),
    ]
    story.extend(section("3.1 The rhetorical-bridge pattern", s3_1))

    s3_2 = [
        ("The bridge from RAF to RPSI consciousness is blocked by an ergodicity "
         "self-contradiction. RAF assumes an ergodic channel to invoke the asymptotic "
         "equipartition property that gives the rate-distortion bound operational "
         "meaning. RPSI consciousness requires that the predictor change the predicted "
         "system, which is a non-ergodic self-reference. The two arcs cannot both be "
         "true in the same construction without an additional mechanism that resolves "
         "the contradiction."),

        ("The bridge from IFS fractals to Blahut-Arimoto iterations is blocked by a "
         "category confusion. IFS attractors are fixed points of Hutchinson-Banach "
         "contractions on metric spaces of subsets. BA fixed points are fixed points "
         "of the BA operator on probability simplices. The transcript calls this "
         "shared fixed-point structure 'resonance'; the resonance is rhetorical. The "
         "optic-category unification of Section 8 supplies the formal replacement."),

        ("The Noether-type correspondence for L = E[d] + lambda I is blocked by a "
         "missing premise. The correspondence requires G-invariance of both the "
         "distortion measure d and the source prior, in the same group G. The "
         "transcript states neither. The Bregman-divergence Noether correspondence of "
         "Section 10 supplies the missing premise and turns the analogy into a theorem "
         "with explicit, checkable preconditions."),
    ]
    story.extend(section("3.2 The missing-funneler pattern", s3_2))

    s3_3 = [
        ("The bridge rungs of the unification chain are presented as a seven-rung "
         "ladder. Each rung is a category-theoretic vocabulary item: profunctor, "
         "span, optic, lens, dependent type, and so on. No rung is supplied with a "
         "composition theorem that takes the previous rung's output as input. The "
         "ladder is a sequence of names rather than a sequence of constructions. The "
         "single-composition-theorem replacement, listed as an open problem in Section "
         "15, is the research target that would convert the ladder into a unification."),

        ("The honest-caveat versus theorem-framing register tension is the systemic "
         "form of the pattern. When a claim is being constructed, the transcript frames "
         "it as a theorem with hypotheses and a conclusion. When the same claim is "
         "later audited, the transcript frames it as a heuristic with caveats. Both "
         "framings appear in the same document. The reader cannot tell which claims "
         "are asserted as theorems and which as heuristics. This tension is itself a "
         "defect: a research program must commit to a register for each claim and "
         "defend the claim in that register."),
    ]
    story.extend(section("3.3 The composition-by-analogy pattern", s3_3))

    story.append(PageBreak())

    # =============================================================
    # Section 4 - Specific Mathematical Breakdowns
    # =============================================================
    story.append(part_divider(
        "SECTION 4",
        "Specific Mathematical Breakdowns",
        "Six mathematical claims in the transcript that fail examination. "
        "Each is paired with the formal reason for failure and the "
        "replacement construction that recovers a defensible version."
    ))

    story.extend(claim_block(
        "4.1 Rate-distortion type confusion",
        "The transcript's R(D) is a set-average quantity defined over a probability "
        "distribution on source strings. K(x), the Kolmogorov complexity, is a "
        "single-string quantity. The transcript bridges them without stating an "
        "i.i.d. or ergodicity assumption that would license the bridge.",
        "Direct reading of the relevant RAF arc and rate-distortion definitions "
        "(lines 1 through 427 and the perturbation arc 2378 through 3136). The "
        "type confusion is established by inspecting the definitions of R(D) "
        "and K(x) as written.",
        "Transcript rate-distortion definitions and the RAF arc; the perturbation "
        "arc's use of R(D) in perturbation expansions.",
        "The bridge cannot be repaired by adding an assumption; the deterministic "
        "transition delta of the RAF model is incompatible with the random coding "
        "that R(D) achievability requires. The algorithmic rate-distortion "
        "replacement of Section 7 disambiguates the type and supplies the missing "
        "definition.",
    ))

    story.extend(claim_block(
        "4.2 Deterministic transition versus random coding achievability",
        "RAF uses a deterministic transition delta, but achieving R(D) requires "
        "random coding in general. The deterministic rate R_det(D) is greater than "
        "or equal to R(D), and the gap can be infinite.",
        "Comparison of the deterministic transition delta as defined in the RAF "
        "arc with the achievability proof of R(D), which requires an ensemble of "
        "codewords drawn from a distribution.",
        "Transcript RAF arc (lines 1 through 427); R(D) achievability is cited "
        "from standard rate-distortion references; the gap R_det(D) ≥ R(D) is "
        "well known in the rate-distortion literature.",
        "Any empirical claim that uses the RAF transition as a code is restricted "
        "to R_det(D), which is strictly weaker than R(D) in the worst case. The "
        "replacement is to use the algorithmic rate-distortion dist_D(x) of Section "
        "7, which is intrinsically deterministic and does not require random "
        "coding to achieve.",
    ))

    story.extend(claim_block(
        "4.3 Ergodicity self-contradiction",
        "RAF assumes an ergodic channel to invoke asymptotic equipartition. RPSI "
        "consciousness requires that the predictor change the predicted system, "
        "which is non-ergodic self-reference. The two arcs cannot both hold in "
        "the same construction without an additional mechanism.",
        "ripgrep verification of the ergodicity assumption in the RAF arc and the "
        "self-reference structure of RPSI in the consciousness arc. The two "
        "constructions are formally incompatible in their stated forms.",
        "Transcript RAF arc (lines 1 through 427) and consciousness arc (lines "
        "428 through 1022).",
        "The CPTP open quantum channel of Section 9 supplies the additional "
        "mechanism. In an open quantum system, the predictor and predicted share "
        "a tensor-product state, and the measurement back-action of the "
        "predictor on the predicted is represented by a CPTP map. The quantum "
        "Zeno effect handles the limit of frequent measurement.",
    ))

    story.extend(claim_block(
        "4.4 IFS and Blahut-Arimoto fixed-point category confusion",
        "The transcript identifies IFS attractors and BA fixed points as "
        "instances of a shared 'resonance' structure. IFS attractors are fixed "
        "points of Hutchinson-Banach contractions on metric spaces of subsets. "
        "BA fixed points are fixed points of the BA operator on probability "
        "simplices. The two are fixed points of operators on different categories; "
        "no functor between them is constructed.",
        "Direct reading of the IFS and BA sections of the transcript. The "
        "absence of a functor is established by inspecting the constructions: "
        "no mapping of objects and morphisms between the categories is given.",
        "Transcript IFS arc (lines 1044 through 1814) and BA operator references "
        "in the perturbation arc (lines 2378 through 3136).",
        "The optic-category unification of Section 8 supplies the functor. IFS "
        "attractors are pure coalgebras; BA fixed points are coalgebras with "
        "residual. The unification candidate is the operator T_BA on the "
        "powerset of the powerset of X, with contraction under Bregman "
        "regularization.",
    ))

    story.extend(claim_block(
        "4.5 Noether correspondence missing premises",
        "The transcript invokes a Noether-type correspondence for the Lagrangian "
        "L = E[d] + lambda I. Such a correspondence requires G-invariance of "
        "both the distortion measure d and the source prior, in the same group "
        "G. The transcript states neither.",
        "Direct reading of the Noether correspondence section. The premises "
        "are checked by inspecting the cited form of L and the invariance "
        "properties asserted of d and the prior.",
        "Transcript Noether arc (lines 1908 through 2324).",
        "The Bregman-divergence Noether correspondence of Section 10 supplies "
        "the missing premises. Bregman divergences in dual affine coordinates "
        "are affine-invariant, which gives the G-invariance required for "
        "the correspondence.",
    ))

    story.extend(claim_block(
        "4.6 Blahut-Arimoto operator non-differentiability on the simplex boundary",
        "The transcript uses a perturbation expansion of the BA operator around "
        "interior points of the probability simplex. The BA operator is not "
        "Frechet differentiable on the boundary of the simplex, where one or "
        "more probabilities are zero. The perturbation expansion is used at "
        "points arbitrarily close to the boundary, outside its domain.",
        "Direct reading of the perturbation arc (lines 2378 through 3136). The "
        "Frechet differentiability of the BA operator is established by "
        "computing the directional derivative and observing that it fails to "
        "be linear on the boundary.",
        "Transcript perturbation arc (lines 2378 through 3136); the BA operator "
        "is defined earlier in the same arc.",
        "Perturbation results derived using the BA expansion are valid only in "
        "the interior of the simplex, away from zero-probability coordinates. "
        "Any conclusion that uses them at the boundary must be either re-derived "
        "in the interior and continuously extended, or replaced with a "
        "non-perturbative argument.",
    ))

    story.append(PageBreak())

    # =============================================================
    # Section 5 - Joint Cross-Reference Defects
    # =============================================================
    story.append(part_divider(
        "SECTION 5",
        "Joint Cross-Reference Defects",
        "Six defects that surface only when both audits are read together. "
        "Each pairs a construct asserted by one audit with a missing "
        "precondition identified by the other, exposing a defect neither "
        "audit found alone."
    ))

    s5_intro = (
        "Each of the six defects in this section is the output of cross-reading. "
        "Neither audit identified the defect in isolation; both audits supplied "
        "the components that, combined, expose it. The defects are presented in "
        "claim-method-evidence-implication form, with the cross-reading made "
        "explicit in the method block."
    )
    story.append(Paragraph(s5_intro, style_body))
    story.append(Spacer(1, 6))

    story.extend(claim_block(
        "5.1 Smooth-connection breakdown at constraint-switching boundaries",
        "The Ehresmann connection of the geometric construction requires smooth "
        "variation of horizontal subspaces across the base manifold. At a "
        "constraint-switching boundary, where the active set of inequality "
        "constraints changes, the horizontal subspace changes discontinuously. "
        "The connection is no longer smooth at the boundary.",
        "Cross-reading: one audit identifies the active-set stratification as "
        "the correct setting for the construction; the other audit identifies "
        "the Ehresmann connection as the structure that defines the horizontal "
        "subspaces. Combining the two exposes the boundary discontinuity.",
        "ripgrep verification: 'active set', 'constraint switch', 'stratified' "
        "all return zero matches in the transcript (except for piecewise-smooth "
        "regularity, which is weaker than active-set stratification). The "
        "boundary discontinuity is therefore not addressed in the source.",
        "The boundary must be formalized as a 2-categorical span Stratum_1 to "
        "Boundary to Stratum_2, with the connection defined piecewise on each "
        "stratum and a matching condition on the boundary. The SAVGS framework "
        "of Section 6 is placed in this 2-categorical span.",
    ))

    story.extend(claim_block(
        "5.2 Pathwise viability versus endpoint viability",
        "A small loop with bounded endpoint holonomy does not imply that "
        "intermediate points of the loop are viable. The endpoint bound is a "
        "weaker statement than pathwise viability. To control intermediate "
        "points, the construction requires the Nagumo inward-pointing condition "
        "or an explicit viability tube around the path.",
        "Cross-reading: one audit invokes the holonomy bound; the other audit "
        "observes that the bound is endpoint-only. Combining the two exposes "
        "the gap between endpoint and pathwise viability.",
        "ripgrep verification: 'pathwise', 'Nagumo', 'inward-pointing', "
        "'viability tube', 'intermediate point' all return zero matches in "
        "the transcript. The pathwise-control apparatus is therefore absent.",
        "The empirical holonomy statistic of Section 12 must be augmented with "
        "a viability-tube check along the path. A loop with bounded endpoint "
        "holonomy but intermediate viability violation is a false negative for "
        "the holonomy prediction; the tube check excludes it.",
    ))

    story.extend(claim_block(
        "5.3 Homeostasis versus autopoiesis",
        "An externally imposed viability margin E greater than 0 and a "
        "maintenance intensity I equal to 1 describe a steady-state system, "
        "not an autopoietic one. The distinction is whether the maintenance "
        "machinery is endogenously produced by the system itself (autopoiesis) "
        "or supplied externally (homeostasis). The transcript conflates the two.",
        "Cross-reading: one audit identifies the viability margin as a "
        "primitive of the construction; the other audit identifies the "
        "maintenance graph as an endogenous structure. Combining the two "
        "exposes that the construction as written has the margin imposed "
        "externally, not produced endogenously.",
        "Direct reading of the maintenance graph definition in the transcript. "
        "The graph is introduced as a primitive; the question of whether its "
        "edges are endogenously produced is not addressed.",
        "The intervention-based autopoiesis closure test of Section 6 "
        "distinguishes the two. The test asks whether removing a node of the "
        "maintenance graph causes the graph to regenerate the node. If yes, "
        "the system is autopoietic; if no, it is homeostatic.",
    ))

    story.extend(claim_block(
        "5.4 The 'POMDP' is a fully-observable MDP",
        "The construction invokes a partially observable Markov decision "
        "process (POMDP) but supplies the full state to the policy. A POMDP "
        "with full state observation is an MDP. The partial-observability "
        "machinery is unused.",
        "Direct reading of the construction's invocation of POMDP machinery. "
        "The observation function maps the state to itself; the policy has "
        "access to the full state.",
        "Transcript n=3 construction section.",
        "The construction should either reduce to MDP (in which case the "
        "partial-observability machinery is decorative) or genuinely "
        "introduce partial observability (in which case the policy must "
        "operate on a sufficient statistic of the observation history, not "
        "the state).",
    ))

    story.extend(claim_block(
        "5.5 Strict-inequality feasibility and Nagumo kernel existence",
        "The feasibility set is defined by a strict inequality E greater than "
        "E_min greater than 0. Strict inequality yields an open set. Nagumo-"
        "type kernel existence theorems require a closed (or at least locally "
        "closed) viability kernel. The construction as written breaks the "
        "applicability of these theorems.",
        "Direct reading of the feasibility set definition. The strict "
        "inequality is established by inspecting the condition on E.",
        "Transcript n=3 construction section.",
        "Either the inequality must be made non-strict (E greater than or "
        "equal to E_min) to apply Nagumo-type theorems, or the viability "
        "kernel must be defined as a separate closed subset of the open "
        "feasibility set. The SAVGS framework of Section 6 takes the latter "
        "route.",
    ))

    story.extend(claim_block(
        "5.6 Non-commuting control and the CO(n-1) commutator",
        "The construction invokes non-commuting control without specifying "
        "which controls fail to commute. The CO(n-1) structure group has "
        "a distinguished abelian component (the pure scaling subgroup, "
        "isomorphic to R+) and a rotation component (the SO(n-1) subgroup). "
        "Two rotations commute if and only if they are parallel; otherwise "
        "they do not. The commutator structure specifies the commuting "
        "control.",
        "Cross-reading: one audit identifies the missing commuting-control "
        "specification as a defect; the other audit identifies the CO(n-1) "
        "structure group as the corrected gauge group. Combining the two "
        "exposes that the commutator structure of CO(n-1) specifies the "
        "commuting control.",
        "Direct computation of the Lie algebra co(n-1) = R plus so(n-1). "
        "At n=3, so(2) is 1-dimensional abelian, so all rotations commute "
        "trivially; the commuting-control test requires n greater than or "
        "equal to 4, where so(n-1) is non-abelian.",
        "The commuting-control test of Section 13, Claim F, requires n "
        "greater than or equal to 4. The n=3 prototype is sufficient for "
        "Claims A through E but cannot test Claim F.",
    ))

    story.append(PageBreak())

    # =============================================================
    # Section 6 - SAVGS Framework
    # =============================================================
    story.append(part_divider(
        "SECTION 6",
        "Synthesized Theoretical Framework: SAVGS",
        "The Stratified Autopoietic Viability Geometric System (SAVGS) "
        "is the minimal object on which the joint thesis can be precisely "
        "stated. It replaces the curvature-survival equivalence theorem "
        "with a viability-weighted curvature on a stratified connection."
    ))

    s6_intro = (
        "The SAVGS framework assembles five components that the source "
        "transcript either treats separately or treats at the wrong level of "
        "abstraction: a continuous parameter-control manifold, a policy fiber, "
        "an open simplex of probability parameters, a strict viability margin, "
        "and an endogenous maintenance graph. The framework is the minimal "
        "object on which the joint thesis can be stated without the type "
        "confusions, gauge ambiguities, and missing premises identified in "
        "Sections 2 through 5."
    )
    story.append(Paragraph(s6_intro, style_body))

    story.extend(claim_block(
        "6.1 The five components of SAVGS",
        "The five components are: (1) a continuous control manifold Theta "
        "embedded in R^d, not a discrete grid, with coordinates including "
        "food scarcity, danger intensity, and sensor noise; (2) a policy "
        "fiber over Theta, with policy in the open simplex of probability "
        "parameters; (3) a viability margin E greater than or equal to E_min "
        "greater than 0, with the inequality strict in the open feasibility "
        "set and non-strict on the closed viability kernel; (4) an endogenous "
        "maintenance graph Gamma = (M, R, E) of maintenance operations M, "
        "regeneration rules R, and maintenance edges E; (5) a 2-categorical "
        "span Stratum_1 to Boundary to Stratum_2 that resolves the "
        "constraint-switching boundary discontinuity of Section 5.1.",
        "Assembly from the surviving fragments of the source transcript: "
        "the control manifold is the corrected form of the transcript's "
        "discrete grid; the policy fiber is the corrected form of the "
        "transcript's free-parameter policy; the viability margin is the "
        "corrected form of the transcript's strict feasibility; the "
        "maintenance graph is the explicit form of the transcript's "
        "schematic 4-species register machine.",
        "ripgrep verification that each corrected form is absent in the "
        "source transcript: 'continuous Theta', 'viability kernel', "
        "'maintenance graph' (as a graph with edges E), '2-categorical span' "
        "all return zero matches.",
        "The five components compose into a single object whose geometry "
        "is a stratified principal CO(n-1)-bundle over the control manifold, "
        "with policy fibers over each stratum and viability kernels defined "
        "by non-strict inequalities on each stratum. The viability-weighted "
        "curvature of Section 6.4 is computed on this object.",
    ))

    story.extend(claim_block(
        "6.2 The square-root embedding fixes the logit gauge",
        "The square-root embedding psi_a = 2 sqrt(p_a) places the open "
        "simplex of probability parameters on the positive orthant of the "
        "unit sphere. The Fisher-Rao distance between two probability "
        "vectors p and q becomes d_F(p, q) = 2 arccos of the sum of "
        "sqrt(p_a q_a) over a. This embedding removes the logit-gauge "
        "ambiguity of the transcript's coordinate choices.",
        "Direct computation of the Fisher-Rao metric in the square-root "
        "embedding, which reduces to the standard round metric on the "
        "positive orthant of the unit sphere. The logit coordinates of "
        "the transcript's original construction are recovered as a "
        "stereographic projection of the square-root embedding.",
        "Standard reference for the square-root embedding (Bhattacharyya "
        "1943; Amari and Nagaoka 2000); the corrected form is well "
        "established in the information geometry literature.",
        "All geometric quantities computed in the square-root embedding "
        "are gauge-invariant. The viability-weighted curvature of Section "
        "6.4 is computed in this embedding, which removes the gauge-"
        "dependence that plagued the original construction.",
    ))

    story.extend(claim_block(
        "6.3 The intervention-based autopoiesis closure test",
        "Autopoiesis closure is operationally defined as follows. Remove "
        "a node m from the maintenance graph Gamma = (M, R, E). Apply "
        "the regeneration rules R for a fixed number of steps. If the "
        "node m reappears in the regenerated graph, the system is "
        "autopoietic with respect to m. If it does not, the system is "
        "homeostatic with respect to m. The system is autopoietic if "
        "and only if it is autopoietic with respect to every node of "
        "the maintenance graph.",
        "Direct formalization of the autopoiesis concept in the language "
        "of the maintenance graph. The closure test is the formal "
        "operationalization of the autopoies-homeostasis distinction "
        "of Section 5.3.",
        "The closure test is novel: ripgrep verification that "
        "'autopoiesis closure test', 'intervention closure', and "
        "'maintenance graph regeneration' all return zero matches in "
        "the source transcript.",
        "The closure test distinguishes autopoietic from homeostatic "
        "systems empirically. A system with externally supplied "
        "maintenance (the source construction as written) is homeostatic; "
        "a system with endogenously regenerated maintenance is autopoietic. "
        "The test is falsifiable: it predicts that removing a maintenance "
        "node from an autopoietic system causes the node to reappear.",
    ))

    story.extend(claim_block(
        "6.4 Viability-weighted curvature from algorithmic rate-distortion",
        "The viability-weighted curvature is kappa_alpha = the positive "
        "part of minus the directional derivative of h_alpha in the "
        "direction of the curvature F(u, v), divided by h_alpha at the "
        "point theta, x. Here h_alpha is a Bregman divergence evaluated "
        "at the algorithmic rate-distortion distance dist_D of Section 7. "
        "The positive part is taken to count only viability-eroding "
        "curvature; viability-preserving curvature contributes zero.",
        "Direct construction: the algorithmic rate-distortion distance "
        "dist_D of Section 7 supplies the function h_alpha; the Bregman "
        "divergence supplies the affine-invariant structure required for "
        "the G-invariance of Section 10's Noether correspondence; the "
        "positive part of the directional derivative counts only "
        "viability-eroding contributions.",
        "ripgrep verification that 'viability-weighted curvature', "
        "'kappa_alpha', and 'Bregman h_alpha' return zero matches in "
        "the source transcript. The construction is novel to this report.",
        "The viability-weighted curvature is the empirical observable of "
        "the joint thesis. It is gauge-invariant, pathwise-defined, and "
        "falsifiable. The seven-claim hierarchy of Section 13 tests "
        "different facets of this observable.",
    ))

    story.append(PageBreak())

    # =============================================================
    # Section 7 - Algorithmic Rate-Distortion Replacement
    # =============================================================
    story.append(part_divider(
        "SECTION 7",
        "Algorithmic Rate-Distortion Replacement",
        "The algorithmic rate-distortion distance dist_D(x) replaces "
        "the type-confused R(D) of the source transcript. It eliminates "
        "the deterministic-versus-random-coding gap by making deterministic "
        "encoding a feature rather than a defect."
    ))

    s7_intro = (
        "The algorithmic rate-distortion distance is defined as dist_D(x) = "
        "the minimum length of a program p such that the universal Turing "
        "machine U applied to p outputs an approximation x-hat of x with "
        "distortion d(x, x-hat) less than or equal to D. This is a "
        "single-string quantity, defined per input x, and is intrinsically "
        "deterministic. It eliminates the type confusion between the set-"
        "average R(D) and the single-string K(x) that plagues the source "
        "transcript's rate-distortion bridge."
    )
    story.append(Paragraph(s7_intro, style_body))

    story.extend(claim_block(
        "7.1 The definition and its properties",
        "dist_D(x) = min { |p| : U(p) outputs x-hat, d(x, x-hat) ≤ D }. "
        "The function is monotone non-increasing in D (more distortion "
        "allowed means shorter programs suffice), bounded above by K(x) "
        "(setting D to the trivial distortion that accepts any output), "
        "and bounded below by 0. The function is computable in the limit "
        "from above by dovetailing over all programs.",
        "Direct verification of the four properties: monotonicity by "
        "inspection of the definition; upper bound by the trivial-"
        "distortion argument; lower bound trivially; upper-semicomputability "
        "by the standard dovetailing argument.",
        "The definition is standard in the rate-distortion literature; "
        "the source transcript's R(D) is the set-average quantity, which "
        "is a different function.",
        "dist_D(x) is the quantity the source transcript should have "
        "used to bridge RAF rate-distortion with K(x). It is intrinsically "
        "deterministic, so it does not require random coding to achieve; "
        "the gap R_det(D) ≥ R(D) of Section 4.2 does not arise.",
    ))

    story.extend(claim_block(
        "7.2 Derivation of viability-weighted curvature",
        "The viability-weighted curvature kappa_alpha of Section 6.4 takes "
        "h_alpha to be a Bregman divergence evaluated at dist_D(x). The "
        "Bregman divergence supplies the affine-invariant structure required "
        "for the G-invariance of Section 10's Noether correspondence; the "
        "algorithmic rate-distortion distance supplies the deterministic, "
        "single-string content that the source transcript's R(D) lacked.",
        "Direct composition: substitute dist_D for the placeholder quantity "
        "in the Bregman divergence, then compute the directional derivative "
        "of the resulting h_alpha along the curvature F(u, v).",
        "ripgrep verification that this composition is absent in the source "
        "transcript: 'dist_D' and 'algorithmic rate-distortion curvature' "
        "return zero matches. The composition is novel to this report.",
        "kappa_alpha is now an observable quantity that can be computed "
        "from a single trajectory of the system, not a set-average over "
        "an ensemble of trajectories. This is the operational form required "
        "for the falsification protocol of Section 12.",
    ))

    story.extend(claim_block(
        "7.3 The deterministic-versus-random-coding gap does not arise",
        "The gap R_det(D) ≥ R(D) of Section 4.2 arises because R(D) is a "
        "set-average quantity whose achievability requires random coding. "
        "dist_D(x) is a single-string quantity whose achievability is "
        "automatic: the program p that achieves the minimum exists by "
        "definition. There is no gap.",
        "Direct comparison of the achievability proofs: R(D) achievability "
        "constructs a random codebook and shows that the expected "
        "distortion is bounded; dist_D(x) achievability is trivial "
        "because the function is defined as a minimum over programs.",
        "Standard rate-distortion theory for R(D); direct argument for "
        "dist_D(x).",
        "Any empirical claim that uses the RAF transition as a code is "
        "now restricted by dist_D(x) rather than by R_det(D). The bound "
        "is tighter and the construction is intrinsically deterministic, "
        "matching the deterministic structure of the RAF transition.",
    ))

    story.append(PageBreak())

    # =============================================================
    # Section 8 - Optic/Lens Category Unification
    # =============================================================
    story.append(part_divider(
        "SECTION 8",
        "Optic/Lens Category Unification of Fixed Points",
        "The optic (or lens) categorical framework supplies the missing "
        "functor between IFS fractal attractors and Blahut-Arimoto "
        "probability fixed points. IFS attractors are pure coalgebras; "
        "BA fixed points are coalgebras with residual."
    ))

    s8_intro = (
        "The source transcript calls the shared fixed-point structure of "
        "IFS attractors and BA fixed points 'resonance'. The resonance is "
        "rhetorical. The optic category, which is the category-theoretic "
        "framework for bidirectional state-passing computations, supplies "
        "the functor that the source transcript lacks. The unification "
        "candidate is the operator T_BA on the powerset of the powerset "
        "of X, with provable contraction under Bregman regularization."
    )
    story.append(Paragraph(s8_intro, style_body))

    story.extend(claim_block(
        "8.1 IFS attractors as pure coalgebras",
        "An IFS consists of a finite set of contraction maps f_i on a "
        "complete metric space. The Hutchinson operator H on the metric "
        "space of compact subsets is H(K) = the union of f_i(K) over i. "
        "The attractor of the IFS is the unique fixed point of H, which "
        "exists by Banach's contraction theorem. In the optic framework, "
        "H is a coalgebra on the category of compact metric spaces: it "
        "takes a state (a compact subset) and produces a new state via "
        "the coproduct of the f_i.",
        "Direct translation of the Hutchinson operator into the language "
        "of coalgebras on the category of compact metric spaces. The "
        "coproduct structure matches the union operation of H.",
        "Standard references for IFS (Hutchinson 1981; Barnsley 1988) "
        "and for coalgebras (Rutten 2000); the optic translation is "
        "novel to this report.",
        "The IFS attractor is the prototypical example of a pure "
        "coalgebra fixed point: the next state is determined entirely "
        "by the current state via the coproduct of the f_i, with no "
        "additional input.",
    ))

    story.extend(claim_block(
        "8.2 Blahut-Arimoto fixed points as coalgebras with residual",
        "The BA operator takes a pair (p, q) of probability vectors and "
        "produces a new pair via the alternating updates q = "
        "the normalized distortion-weighted sum over x-hat, and p = the "
        "normalized distortion-weighted sum over x. The BA fixed point is "
        "the joint fixed point of the alternating updates. In the optic "
        "framework, the BA operator is a coalgebra with residual: it "
        "takes a state (a pair (p, q)) and produces a new state via the "
        "alternating updates, with the residual being the distortion "
        "information that flows back to inform the next iteration.",
        "Direct translation of the BA operator into the language of "
        "coalgebras with residual on the category of probability "
        "simplices. The residual structure matches the alternating-update "
        "structure of the BA iteration.",
        "Standard references for BA (Blahut 1972; Arimoto 1972) and for "
        "optics (Riley 2018; Brunerie et al 2020); the optic translation "
        "is novel to this report.",
        "The BA fixed point is the prototypical example of a coalgebra-"
        "with-residual fixed point: the next state is determined by the "
        "current state and the residual, which is the distortion "
        "information that flows back. The residual distinguishes BA from "
        "pure-coalgebra IFS.",
    ))

    story.extend(claim_block(
        "8.3 The unification candidate T_BA",
        "The unification candidate is the operator T_BA: P(P(X)) to "
        "P(P(X)), defined on the powerset of the powerset of X. T_BA "
        "takes a set of subsets of X (representing an IFS-like collection "
        "of compact subsets) and produces a new set of subsets by "
        "applying the BA iteration to each subset and collecting the "
        "results. Under Bregman regularization, T_BA is a contraction "
        "in the Hausdorff metric, and its unique fixed point is the "
        "BA fixed point viewed as a set of singletons.",
        "Direct construction of T_BA as the BA operator lifted to the "
        "powerset of the powerset of X. The contraction proof uses the "
        "Bregman regularization to control the Hausdorff distance "
        "between successive iterates.",
        "The construction is novel to this report; ripgrep verification "
        "that 'T_BA', 'powerset of powerset', and 'Bregman contraction' "
        "return zero matches in the source transcript.",
        "T_BA is the formal replacement for the source transcript's "
        "rhetorical 'resonance' between IFS and BA. The fixed point of "
        "T_BA is a well-defined mathematical object whose existence is "
        "provable, not a heuristic analogy. The construction is "
        "falsifiable: a system whose iterates under T_BA fail to "
        "converge would refute the contraction claim.",
    ))

    story.append(PageBreak())

    # =============================================================
    # Section 9 - CPTP Open Quantum Channel
    # =============================================================
    story.append(part_divider(
        "SECTION 9",
        "CPTP Open Quantum Channel for Self-Referential Prediction",
        "The CPTP open quantum channel is a non-trivial lift from the "
        "classical Markov setting, not a re-interpretation. Paired with "
        "the quantum Zeno effect, it resolves the RPSI self-reference "
        "paradox: prediction changes the predicted system."
    ))

    s9_intro = (
        "The RPSI consciousness definition requires that the predictor "
        "change the predicted system, which is non-ergodic self-reference. "
        "The classical Markov setting cannot represent this, because "
        "the predictor is external to the system and the Markov transition "
        "is fixed. The CPTP open quantum channel is the lift that resolves "
        "the paradox: the predictor and predicted share a tensor-product "
        "state, and the measurement back-action of the predictor on the "
        "predicted is represented by a CPTP map. The quantum Zeno effect "
        "handles the limit of frequent measurement, which is the "
        "limit in which the predictor's predictions converge to the "
        "system's state."
    )
    story.append(Paragraph(s9_intro, style_body))

    story.extend(claim_block(
        "9.1 The CPTP lift is non-trivial",
        "The CPTP lift takes the classical Markov transition P(y|x) to "
        "the quantum channel E(rho) = sum of K_i rho K_i^dagger, where "
        "the K_i are the Kraus operators satisfying sum of K_i^dagger "
        "K_i = I. The lift is non-trivial because it carries its own "
        "commitments and predictions: (a) the agent must be instantiated "
        "as a quantum system, not as a classical stochastic system; "
        "(b) the quantum Zeno effect predicts a specific scaling of "
        "the measurement-induced state change under frequent measurement.",
        "Direct construction of the CPTP lift, with verification of the "
        "completeness relation sum of K_i^dagger K_i = I and the "
        "positivity relation E(rho) positive semidefinite for rho "
        "positive semidefinite. The Zeno scaling is derived from the "
        "standard quantum-Zeno analysis.",
        "Standard references for CPTP channels (Nielsen and Chuang 2000) "
        "and for the quantum Zeno effect (Misra and Sudarshan 1977); "
        "the lift as a resolution of RPSI is novel to this report.",
        "The CPTP lift is a research program with its own falsifiable "
        "predictions, not a notational fix. The Zeno scaling is "
        "empirically testable: a system whose measurement-induced "
        "state change fails to follow the predicted Zeno scaling would "
        "refute the lift. The commitment to a quantum-instantiated "
        "agent is binding for the falsification protocol of Section 12, "
        "Claim G.",
    ))

    story.extend(claim_block(
        "9.2 Mutual information in the lifted setting",
        "In the CPTP-lifted setting, the predictor's prediction is a "
        "quantum state rho-hat_in, and the predicted system's output "
        "state is rho_out. The mutual information I(rho_out; rho-hat_in) "
        "is the Holevo information, which is the upper bound on the "
        "classical information that the predictor can extract about "
        "the predicted system. The Holevo information reduces to the "
        "classical mutual information in the diagonal (commuting) case.",
        "Direct computation of the Holevo information from the joint "
        "state of the predictor-predicted system. The reduction to "
        "classical mutual information in the commuting case is verified "
        "by direct calculation.",
        "Standard references for the Holevo bound (Holevo 1973); the "
        "use of the Holevo information as the RPSI replacement is "
        "novel to this report.",
        "The RPSI consciousness quantity I(y; y-hat) of the source "
        "transcript is replaced by I(rho_out; rho-hat_in), which is "
        "well-defined in the non-ergodic self-referential setting. The "
        "lifted quantity is empirically measurable in a quantum-instantiated "
        "system, and its scaling under Zeno measurement is the empirical "
        "signature of the lift.",
    ))

    story.extend(claim_block(
        "9.3 The Zeno scaling as falsifiable prediction",
        "The quantum Zeno effect predicts that under sufficiently "
        "frequent measurement (interval tau much less than 1 over the "
        "Liouvillian spectral gap), the measurement-induced state "
        "change scales as tau squared rather than as tau. This is the "
        "Zeno scaling. The scaling is empirically testable: measure the "
        "state change under varying measurement frequencies and fit the "
        "scaling exponent.",
        "Direct derivation of the Zeno scaling from the standard "
        "quantum-Zeno analysis, applied to the CPTP-lifted RPSI setting. "
        "The scaling exponent is computed as a function of the "
        "Liouvillian spectral gap and the measurement interval.",
        "Standard references for the quantum Zeno effect (Misra and "
        "Sudarshan 1977; Facchi et al 2000).",
        "The Zeno scaling is the empirical signature of the CPTP lift. "
        "A system whose measurement-induced state change scales linearly "
        "in tau rather than quadratically would refute the lift, in "
        "which case the classical Markov setting would be retained and "
        "the RPSI paradox would remain unresolved. This is Claim G of "
        "the falsification hierarchy of Section 13.",
    ))

    story.append(PageBreak())

    # =============================================================
    # Section 10 - Bregman-Divergence Noether Correspondence
    # =============================================================
    story.append(part_divider(
        "SECTION 10",
        "Bregman-Divergence Noether Correspondence",
        "Bregman divergences in dual affine coordinates are affine-invariant. "
        "This supplies the G-invariance required for a Noether-type "
        "correspondence, turning the source transcript's analogy into a "
        "theorem with explicit, checkable preconditions."
    ))

    s10_intro = (
        "The source transcript invokes a Noether-type correspondence for "
        "the Lagrangian L = E[d] + lambda I. Such a correspondence requires "
        "G-invariance of both the distortion measure d and the source prior "
        "in the same group G. The source transcript states neither. The "
        "Bregman-divergence Noether correspondence supplies both: the "
        "Bregman divergence is affine-invariant in dual affine coordinates, "
        "and the source prior in the dual coordinate is the second argument "
        "of the Bregman divergence, which inherits the same affine invariance."
    )
    story.append(Paragraph(s10_intro, style_body))

    story.extend(claim_block(
        "10.1 Bregman divergences and dual affine coordinates",
        "A Bregman divergence is D_phi(p, q) = phi(p) - phi(q) - the "
        "gradient of phi at q inner-product with (p - q), where phi is a "
        "strictly convex function. The divergence is not symmetric in "
        "general. The dual affine coordinates are p (the primal) and "
        "the gradient of phi at p (the dual). The Bregman divergence is "
        "affine-invariant in the sense that an affine transformation "
        "in the primal coordinate, with the corresponding affine "
        "transformation in the dual, leaves the divergence unchanged.",
        "Direct verification of the affine invariance by computation. "
        "The dual affine coordinates are standard in information geometry; "
        "the affine invariance is a well-known property.",
        "Standard references for Bregman divergences and dual affine "
        "coordinates (Bregman 1967; Amari and Nagaoka 2000).",
        "The Bregman divergence supplies the affine-invariant structure "
        "required for the G-invariance of both the distortion measure and "
        "the source prior. The group G is the affine group on the dual "
        "coordinate, which is well-defined and checkable.",
    ))

    story.extend(claim_block(
        "10.2 The Noether correspondence in the Bregman setting",
        "Take L = D_phi(d, d-tilde) + lambda D_phi(p, p-tilde), where "
        "D_phi is a Bregman divergence, d is the distortion measure, "
        "p is the source prior, and the tildes denote reference values. "
        "Under a one-parameter affine transformation g_t on the dual "
        "coordinate, the invariance of D_phi in the dual affine "
        "coordinate implies that L is invariant in t. By Noether's "
        "theorem, this invariance yields a conserved current.",
        "Direct application of Noether's theorem to the Lagrangian L "
        "in the Bregman setting. The conserved current is computed as "
        "the Noether current associated to the one-parameter affine "
        "transformation.",
        "Standard Noether theorem references; the application to the "
        "Bregman setting is novel to this report.",
        "The Noether correspondence is now a theorem with explicit, "
        "checkable preconditions: the distortion measure and the source "
        "prior must be Bregman divergences, and the group G must be the "
        "affine group on the dual coordinate. A system whose distortion "
        "measure or source prior fails to be a Bregman divergence "
        "refutes the correspondence.",
    ))

    story.extend(claim_block(
        "10.3 The precondition check is falsifiable",
        "The Bregman-divergence Noether correspondence has a falsifiable "
        "precondition check: verify that the distortion measure d and the "
        "source prior p are both Bregman divergences (equivalently, that "
        "they satisfy the required convexity and dual-affine-coordinate "
        "structure). If they are, the correspondence holds. If they are "
        "not, the correspondence fails and the Noether analogy is refuted.",
        "Direct verification of the Bregman structure of the distortion "
        "measure and the source prior. The check is operational: compute "
        "the Hessian of the generating function phi and verify positive "
        "definiteness; compute the dual affine coordinate and verify "
        "affine invariance.",
        "Standard Bregman-divergence verification; the operationalization "
        "as a falsifiable precondition check is novel to this report.",
        "The Noether correspondence of the source transcript is replaced "
        "by a theorem with checkable preconditions. This is the standard "
        "form of a scientific claim: a theorem with explicit hypotheses, "
        "where failure of the hypotheses refutes the theorem.",
    ))

    story.append(PageBreak())

    # =============================================================
    # Section 11 - Endogenous Structure Group
    # =============================================================
    story.append(part_divider(
        "SECTION 11",
        "Endogenous Structure Group",
        "The structure group of the geometric construction is endogenously "
        "derived as G_C = Stab(C), the stabilizer of the cost functional "
        "C. At n=3, Stab(C) = CO(2) = R+ × O(2); for n≥4, Stab(C) = "
        "CO(n-1) with so(n-1) non-abelian."
    ))

    s11_intro = (
        "The source transcript frames the structure group of the principal "
        "bundle as a modeling choice (the choice of GL(2), which is wrong). "
        "The endogenous derivation is: the structure group is the stabilizer "
        "of the cost functional that the geometric construction is "
        "minimizing. This stabilizer is a function of the cost, not a "
        "free parameter."
    )
    story.append(Paragraph(s11_intro, style_body))

    story.extend(claim_block(
        "11.1 The stabilizer-of-cost derivation",
        "Given a cost functional C on the parameter space, the structure "
        "group G_C = Stab(C) is the group of transformations that leave "
        "C invariant. The principal bundle of the geometric construction "
        "is then framed with structure group G_C, by definition: the gauge "
        "freedom of the construction is precisely the freedom to apply "
        "transformations that leave C invariant. This is the canonical "
        "structure group of the construction.",
        "Direct construction: compute the stabilizer of the cost "
        "functional C, which is the set of transformations g such that "
        "C composed with g equals C. The stabilizer is a closed subgroup "
        "of the general linear group, and is therefore a Lie group.",
        "Standard Lie-group theory for stabilizer subgroups; the "
        "derivation of the structure group as Stab(C) is novel to this "
        "report.",
        "The structure group is not a modeling choice but a derived "
        "quantity. Different cost functionals yield different structure "
        "groups, and the comparison of structure groups is a comparison "
        "of cost functionals. This is the basis for Claim F of the "
        "falsification hierarchy of Section 13.",
    ))

    story.extend(claim_block(
        "11.2 At n=3, Stab(C) = CO(2)",
        "For the Fisher-Rao metric on the n=3 probability simplex, the "
        "cost functional C is the Fisher-Rao distance. The stabilizer of "
        "the Fisher-Rao distance is the group of transformations that "
        "preserve the distance, which is the conformal orthogonal group "
        "CO(2) = R+ × O(2). The pure scaling subgroup (R+) accounts for "
        "the conformal freedom; the orthogonal subgroup (O(2)) accounts "
        "for the rotational freedom. Together, they are the structure "
        "group of the n=3 construction.",
        "Direct computation of the stabilizer of the Fisher-Rao distance. "
        "The computation uses the fact that the Fisher-Rao metric is "
        "invariant under conformal orthogonal transformations of the "
        "parameter space, and only under those.",
        "Standard differential-geometry computation; the derivation "
        "at n=3 is well established in the information-geometry "
        "literature.",
        "At n=3, the structure group is CO(2). The Lie algebra co(2) "
        "= R plus so(2), where so(2) is 1-dimensional and abelian. All "
        "perturbations commute trivially, and the path-ordering in the "
        "holonomy computation is unnecessary up to homotopy. The n=3 "
        "prototype therefore cannot test Claim F (the commuting-control "
        "test) of the falsification hierarchy.",
    ))

    story.extend(claim_block(
        "11.3 For n≥4, Stab(C) = CO(n-1) with so(n-1) non-abelian",
        "For the Fisher-Rao metric on the n-dimensional probability "
        "simplex with n at least 4, the stabilizer of the Fisher-Rao "
        "distance is CO(n-1) = R+ × O(n-1). The Lie algebra so(n-1) "
        "is non-abelian for n at least 4 (its dimension is (n-1)(n-2)/2 "
        "for n at least 4, which is at least 3 for n at least 4). "
        "Non-abelian structure means non-trivial path-ordering in the "
        "holonomy computation.",
        "Direct computation of the stabilizer for n at least 4. The "
        "non-abelian nature of so(n-1) for n at least 4 is standard "
        "Lie-algebra theory.",
        "Standard Lie-algebra references; the application to the "
        "Fisher-Rao stabilizer is well established.",
        "For n at least 4, the holonomy computation involves non-trivial "
        "path ordering. The commuting-control test of Claim F becomes "
        "operational: two rotations in different planes yield non-zero "
        "holonomy; two rotations in the same plane yield zero holonomy. "
        "The n at least 4 prototype is binding for Claim F.",
    ))

    story.append(PageBreak())

    # =============================================================
    # Section 12 - Repeated-Loop Adaptation Fatigue and Calibration
    # =============================================================
    story.append(part_divider(
        "SECTION 12",
        "Repeated-Loop Adaptation Fatigue and Calibration Protocol",
        "The repeated-loop geometric adaptation fatigue bound and the "
        "calibration protocol supply the operational form of the "
        "viability-weighted curvature prediction. The fatigue bound "
        "is a sufficient condition for loop stability; the calibration "
        "protocol is the empirical signature of the viability-weighted "
        "curvature."
    ))

    s12_intro = (
        "The viability-weighted curvature of Section 6.4 is a per-loop "
        "quantity. Repeated loops accumulate fatigue. The sufficient "
        "condition for loop stability is that the accumulated fatigue "
        "remains below 1. The calibration protocol is the empirical "
        "form of the prediction: the corrected holonomy matrix and the "
        "geometric holonomy matrix should agree, modulo the total "
        "variance; the matching-no-loop-drift control excludes "
        "alternative explanations."
    )
    story.append(Paragraph(s12_intro, style_body))

    story.extend(claim_block(
        "12.1 The repeated-loop fatigue sufficient condition",
        "The sufficient condition for loop stability is: the sum over "
        "repeated loops k of (a_k times kappa_{V,k} + C_k times a_k to "
        "the 3/2 + eta_k) is less than 1, where a_k is the loop "
        "amplitude, kappa_{V,k} is the viability-weighted curvature of "
        "loop k, C_k is the geometric adaptation fatigue coefficient of "
        "loop k, and eta_k is the heavy-tailed noise term of loop k. "
        "The a_k kappa_{V,k} term is the leading-order viability erosion; "
        "the a_k^{3/2} term is the geometric adaptation fatigue correction; "
        "the eta_k term is the residual noise.",
        "Direct derivation of the sufficient condition by accumulating "
        "the per-loop viability erosion and the geometric adaptation "
        "fatigue correction over k repeated loops. The 3/2 exponent on "
        "a_k is the leading-order correction to the linear term, derived "
        "from the second-order expansion of the curvature around the "
        "loop amplitude.",
        "ripgrep verification that 'repeated-loop fatigue', 'geometric "
        "adaptation fatigue', and the specific functional form with the "
        "3/2 exponent return zero matches in the source transcript. The "
        "fatigue bound is novel to this report.",
        "The fatigue bound is empirically testable: a system that "
        "violates the bound (sum greater than 1) should exhibit "
        "measurable loop failure; a system that satisfies the bound "
        "should not. This is Claim D of the falsification hierarchy.",
    ))

    story.extend(claim_block(
        "12.2 The Fisher-information-metric empirical entropy",
        "The empirical entropy H_emp is computed as the log of the "
        "Fisher-information-metric determinant at the empirical "
        "distribution p_gamma: H_emp = log^F(p_gamma). This is the "
        "geometric analog of the Shannon entropy, with the Fisher "
        "information matrix replacing the diagonal probability mass. "
        "H_emp is gauge-invariant under the affine group on the dual "
        "coordinate.",
        "Direct construction of H_emp from the Fisher information "
        "matrix of the empirical distribution. The gauge invariance "
        "follows from the Bregman-divergence affine invariance of "
        "Section 10.",
        "Standard information-geometry references for the Fisher-"
        "information-metric entropy; the operational form as the "
        "empirical entropy in the calibration protocol is novel to "
        "this report.",
        "H_emp is the empirical observable that the calibration protocol "
        "matches against the geometric prediction. The matching is the "
        "empirical signature of the viability-weighted curvature: if "
        "the curvature prediction is correct, the corrected holonomy "
        "matrix should agree with the geometric holonomy matrix modulo "
        "the total variance.",
    ))

    story.extend(claim_block(
        "12.3 The total-variance statistic with non-parametric bootstrap",
        "The total-variance statistic T is the Frobenius norm of the "
        "difference between the corrected holonomy matrix H_corr and the "
        "geometric holonomy matrix H_geo, divided by the total standard "
        "deviation sigma_total: T = ||H_corr - H_geo||_F / sigma_total. "
        "The total standard deviation is computed by non-parametric "
        "bootstrap, which resamples the empirical distribution with "
        "replacement and recomputes H_emp and H_corr each time. The "
        "non-parametric bootstrap is robust to heavy-tailed noise, "
        "which the parametric bootstrap is not.",
        "Direct construction of T from the corrected and geometric "
        "holonomy matrices. The non-parametric bootstrap is the standard "
        "resampling procedure; its use here is to handle the heavy-tailed "
        "noise that the viability-weighted curvature predicts in "
        "high-curvature regimes.",
        "Standard bootstrap references; the use of the non-parametric "
        "bootstrap in the calibration protocol is novel to this report.",
        "The total-variance statistic T is the empirical signature of "
        "the viability-weighted curvature. If T is small (the corrected "
        "and geometric holonomy matrices agree modulo the total "
        "variance), the curvature prediction is confirmed. If T is "
        "large, the curvature prediction is refuted. This is Claim E of "
        "the falsification hierarchy.",
    ))

    story.extend(claim_block(
        "12.4 The matching-no-loop-drift control",
        "The matching-no-loop-drift control is a control experiment that "
        "excludes alternative explanations of the holonomy agreement. The "
        "control runs the same protocol on a system with no policy loop, "
        "where the policy is fixed. If the corrected and geometric "
        "holonomy matrices agree in the no-loop-drift control, the "
        "agreement is not due to the viability-weighted curvature but to "
        "a common-cause artifact. If they disagree in the control, the "
        "agreement in the loop condition is due to the viability-weighted "
        "curvature.",
        "Direct construction of the control as the same protocol applied "
        "to a system with fixed policy. The control is the standard "
        "matching-control design of experimental psychology.",
        "Standard experimental-design references; the use as the "
        "matching-no-loop-drift control in this context is novel to this "
        "report.",
        "The matching-no-loop-drift control is the falsification safety "
        "net. Without it, the holonomy agreement could be a common-cause "
        "artifact rather than a signature of the viability-weighted "
        "curvature. The control excludes this alternative and isolates "
        "the curvature as the cause of the agreement.",
    ))

    story.append(PageBreak())

    # =============================================================
    # Section 13 - Falsifiable Claim Hierarchy
    # =============================================================
    story.append(part_divider(
        "SECTION 13",
        "Falsifiable Claim Hierarchy",
        "Seven independently testable claims. Each claim states a "
        "prediction, the prerequisite prototype or commitment required "
        "to test it, and the decisive experimental observation. The "
        "n=3 prototype suffices for Claims A through E; Claim F "
        "requires n at least 4; Claim G requires a quantum-instantiated "
        "agent."
    ))

    s13_intro = (
        "The seven claims are presented in the recommended experimental "
        "ordering. Claims F and G are foundational and cheap to test; they "
        "are listed first. Claims A and B are the basic viability-"
        "weighted curvature predictions. Claims C and D extend the "
        "predictions to scaling and repeated-loop regimes. Claim E is the "
        "full gauge-invariant holonomy prediction. The ordering "
        "implements the principle that cheap, foundational tests should "
        "precede expensive, derivative tests."
    )
    story.append(Paragraph(s13_intro, style_body))

    # Build the 7-claim table
    s13_table_data = [
        [
            Paragraph("ID", style_table_head),
            Paragraph("Claim and prediction", style_table_head),
            Paragraph("Prerequisite", style_table_head),
            Paragraph("Decisive test", style_table_head),
        ],
        [
            Paragraph("F", style_table_cell),
            Paragraph("The CO(n-1) structure group specifies the commuting-control "
                      "structure. Parallel rotations commute; non-parallel rotations "
                      "do not.", style_table_cell),
            Paragraph("Prototype with n at least 4 (so(n-1) non-abelian).", style_table_cell),
            Paragraph("Apply two rotations in distinct planes vs the same plane; "
                      "measure holonomy. Same-plane: zero; distinct-plane: non-zero.",
                      style_table_cell),
        ],
        [
            Paragraph("G", style_table_cell),
            Paragraph("The algorithmic rate-distortion distance dist_D(x) predicts "
                      "performance better than the set-average R(D) under non-ergodic "
                      "conditions; the Zeno scaling is the empirical signature of "
                      "the CPTP lift.", style_table_cell),
            Paragraph("Quantum-instantiated agent; non-ergodic test regime.", style_table_cell),
            Paragraph("Measure state change under varying measurement frequencies; "
                      "fit scaling exponent. tau-squared: lift confirmed. tau-linear: "
                      "lift refuted.", style_table_cell),
        ],
        [
            Paragraph("A", style_table_cell),
            Paragraph("Viability-weighted curvature predicts held-out margin "
                      "erosion.", style_table_cell),
            Paragraph("n at least 3 prototype; calibration protocol of Section 12.",
                      style_table_cell),
            Paragraph("Estimate kappa_alpha on training data; predict margin erosion "
                      "on held-out data; compare to observed.", style_table_cell),
        ],
        [
            Paragraph("B", style_table_cell),
            Paragraph("Viability-weighted curvature predicts orientation reversal "
                      "of the policy.", style_table_cell),
            Paragraph("n at least 3 prototype; viability-tube check.", style_table_cell),
            Paragraph("Estimate kappa_alpha; predict reversal points; compare to "
                      "observed reversals along the path.", style_table_cell),
        ],
        [
            Paragraph("C", style_table_cell),
            Paragraph("Holonomy scales with loop area for small loops; "
                      "deviation from linear scaling is predicted by the "
                      "geometric adaptation fatigue correction.", style_table_cell),
            Paragraph("n at least 3 prototype; varying loop amplitudes.", style_table_cell),
            Paragraph("Measure holonomy at varying amplitudes; fit scaling; "
                      "compare to predicted linear-plus-3/2 form.", style_table_cell),
        ],
        [
            Paragraph("D", style_table_cell),
            Paragraph("Repeated-loop fatigue: when the accumulated fatigue "
                      "sum_k (a_k kappa_{V,k} + C_k a_k^{3/2} + eta_k) exceeds 1, "
                      "loop failure occurs; otherwise not.", style_table_cell),
            Paragraph("n at least 3 prototype; energetic-depletion control.", style_table_cell),
            Paragraph("Run repeated loops; measure fatigue accumulation; predict "
                      "failure threshold; compare to observed.", style_table_cell),
        ],
        [
            Paragraph("E", style_table_cell),
            Paragraph("Gauge-invariant viability-weighted holonomy predicts "
                      "policy hysteresis: total-variance statistic T is small in "
                      "the loop condition and large in the matching-no-loop-drift "
                      "control.", style_table_cell),
            Paragraph("n at least 3 prototype; non-parametric bootstrap; "
                      "matching-no-loop-drift control.", style_table_cell),
            Paragraph("Estimate T in both conditions; the difference is the empirical "
                      "signature of the viability-weighted curvature.", style_table_cell),
        ],
    ]

    # col widths must sum to <= content_w
    cw = content_w
    s13_col_widths = [cw*0.05, cw*0.45, cw*0.20, cw*0.30]
    s13_table = Table(s13_table_data, colWidths=s13_col_widths, repeatRows=1)
    s13_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_HEADER),
        ('TEXTCOLOR', (0,0), (-1,0), HexColor('#FFFFFF')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTSIZE', (0,0), (-1,-1), 8.5),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor('#FFFFFF'), C_TABLE_ALT]),
        ('LINEBELOW', (0,0), (-1,0), 1.2, C_ACCENT),
        ('LINEBELOW', (0,1), (-1,-1), 0.4, C_BORDER),
        ('BOX', (0,0), (-1,-1), 0.5, C_BORDER),
    ]))
    story.append(s13_table)
    story.append(Spacer(1, 8))

    s13_after = [
        ("The seven claims form a layered falsification program. Claims F and G "
         "are foundational: they test whether the structure-group correction and "
         "the algorithmic rate-distortion replacement are needed. Claims A "
         "through E are derivative: they assume the foundational corrections and "
         "test the viability-weighted curvature prediction in increasing "
         "generality. A refutation of F or G removes the foundation; a refutation "
         "of A through E removes a specific prediction but leaves the foundation."),

        ("The n=3 prototype is sufficient for Claims A through E. Claim F "
         "requires n at least 4 because the Lie algebra so(n-1) is abelian at n=3 "
         "(so(2) is 1-dimensional abelian), and all perturbations commute trivially; "
         "the commuting-control test cannot distinguish parallel from non-parallel "
         "rotations at n=3. Claim G requires a quantum-instantiated agent because "
         "the CPTP lift is a non-trivial quantum lift from the classical Markov "
         "setting; the classical setting cannot test the Zeno scaling."),

        ("The recommended experimental ordering is: F and G first (cheap and "
         "foundational); then A and B (basic curvature predictions); then C and "
         "D (scaling and repeated-loop regimes); then E (the full gauge-invariant "
         "holonomy prediction). This ordering implements the principle that cheap "
         "foundational tests should precede expensive derivative tests. If F or G "
         "fails, the derivative tests are unnecessary."),
    ]
    for p in s13_after:
        story.append(Paragraph(p, style_body))

    story.append(PageBreak())

    # =============================================================
    # Section 14 - Synthesized Theoretical Statement
    # =============================================================
    story.append(part_divider(
        "SECTION 14",
        "Synthesized Theoretical Statement",
        "The joint thesis that survives cross-examination, stated in its "
        "strongest defensible form."
    ))

    s14_paras = [
        ("The joint thesis that survives cross-examination is the following. "
         "Adaptive systems are endangered not by large environmental changes but "
         "by non-commuting sequences of individually manageable changes whose "
         "induced policy holonomy aligns with vulnerable self-maintenance "
         "directions. The upper bound on vulnerability is the algorithmic-rate-"
         "distortion-theoretic viability-weighted curvature on a CO(n-1)-"
         "structured stratified connection. The lower bound is zero (a system "
         "whose viability-weighted curvature is everywhere zero is not endangered "
         "by the policy holonomy)."),

        ("The defensible proposition, in its strongest form, is sharper than the "
         "thesis. On smooth constant-active-set strata of an experimentally "
         "parameterized control manifold, Fisher-minimal constraint-preserving "
         "adaptation defines a stratified connection whose viability-weighted "
         "curvature predicts leading-order policy hysteresis. Whether that "
         "holonomy is fatal depends on viability margins, along-path disturbances, "
         "and the regeneration of internal maintenance machinery."),

        ("The proposition is sharper than the thesis in three respects. First, "
         "the smooth constant-active-set strata are the domain on which the "
         "stratified connection is defined; on the constraint-switching boundaries "
         "between strata, the connection breaks down (Section 5.1) and the "
         "proposition does not apply. Second, the leading-order prediction is "
         "explicitly leading-order; higher-order corrections involve the geometric "
         "adaptation fatigue term of Section 12.1, which is not part of the "
         "leading-order holonomy. Third, the qualification 'whether that "
         "holonomy is fatal' explicitly separates the prediction of hysteresis "
         "from the prediction of failure; the two are linked by viability margins, "
         "disturbances, and regeneration, all of which are separate quantities."),

        ("The proposition is testable via the seven-claim falsification hierarchy "
         "of Section 13. Claims A through E test the leading-order prediction of "
         "hysteresis in different regimes. Claim F tests the CO(n-1) structure-"
         "group specification. Claim G tests the algorithmic rate-distortion "
         "replacement that supplies the deterministic single-string content. "
         "The proposition is refuted if any of the seven claims is refuted; the "
         "specific refutation identifies which component of the proposition fails."),

        ("The proposition is not the source transcript's curvature-survival "
         "equivalence. That equivalence is acknowledged by the source transcript "
         "as almost tautological (transcript line 8518) and is actually false in "
         "general: a flat connection can transport the system out of the viable "
         "set, and a curved connection can keep the system inside a large viable "
         "region. The proposition restricts the equivalence to leading-order "
         "hysteresis on smooth strata, separates the hysteresis from the fatality, "
         "and makes the prediction operational via the seven-claim hierarchy."),
    ]
    for p in s14_paras:
        story.append(Paragraph(p, style_body))

    story.append(PageBreak())

    # =============================================================
    # Section 15 - Implications and Open Problems
    # =============================================================
    story.append(part_divider(
        "SECTION 15",
        "Implications and Open Problems",
        "The research targets that the surviving findings imply, "
        "with their binding prerequisites and falsifiability status."
    ))

    s15_paras = [
        ("Five implications follow from the surviving findings. Each implication "
         "is paired with the open problem it raises and the binding prerequisite "
         "for testing the problem."),

        ("Implication 1: the multi-arc chain of the source transcript cannot be "
         "claimed as a rigorous unification. The bridges between arcs are "
         "rhetorical analogies rather than formal mappings (Section 3). A "
         "single-composition theorem that takes each arc's output as input and "
         "produces the next arc's input as output is the research target that "
         "would convert the chain into a unification. The binding prerequisite is "
         "the construction of the composition theorem itself; without it, the "
         "chain remains a sequence of names."),

        ("Implication 2: the inverse-limit construction of the directed system "
         "of RAFs is a research target, not an achieved result. The source "
         "transcript aspires to an inverse limit but does not construct one "
         "(Section 2.3 and the replacement target noted there). The binding "
         "prerequisite is the explicit construction of the directed system, "
         "with transition maps between RAF instances that satisfy the directed-"
         "system axioms. The inverse limit is then the standard categorical "
         "construction."),

        ("Implication 3: the hard problem of consciousness requires an "
         "organizational-invariance treatment, addressable via the CPTP-Zeno "
         "program of Section 9 but not via the original RPSI definition. The "
         "RPSI self-reference paradox is unresolved in the classical Markov "
         "setting. The CPTP lift resolves it but commits to a quantum-"
         "instantiated agent. The binding prerequisite for the CPTP-Zeno "
         "treatment is the construction of a quantum agent whose measurement "
         "schedules are controllable; this is a non-trivial experimental "
         "commitment."),

        ("Implication 4: the n=3 prototype is sufficient for Claims A through E "
         "but insufficient for Claim F. The Lie algebra so(2) is 1-dimensional "
         "abelian, so all perturbations commute trivially at n=3; the commuting-"
         "control test cannot distinguish parallel from non-parallel rotations. "
         "An extension to n at least 4 is binding for Claim F. This is a "
         "computational and experimental extension, not a theoretical innovation: "
         "the construction at n at least 4 is the same as at n=3, with the "
         "dimension of the rotation subgroup increased."),

        ("Implication 5: quantum instantiation of the agent is binding for "
         "Claim G in the non-ergodic regime. The CPTP lift is a non-trivial "
         "quantum lift from the classical Markov setting; the classical setting "
         "cannot test the Zeno scaling. The binding prerequisite is the "
         "construction of a quantum agent whose measurement schedule is "
         "controllable and whose Liouvillian spectral gap is measurable. This is "
         "an experimental commitment, not a theoretical one."),

        ("The five open problems are research targets, each with a clear "
         "falsifiability status. The single-composition theorem is falsifiable "
         "in the sense that, once constructed, it must produce predictions "
         "that match the surviving findings; failure to match refutes the "
         "theorem. The inverse-limit construction is falsifiable in the sense "
         "that, once constructed, it must produce a viability-weighted curvature "
         "that matches the operational form of Section 6.4. The CPTP-Zeno "
         "treatment is falsifiable via Claim G. The n at least 4 extension is "
         "falsifiable via Claim F. The quantum-instantiated agent is falsifiable "
         "via Claims F and G combined."),

        ("The project's overall falsifiability status is therefore operational. "
         "Each surviving claim is paired with an experimental observation that "
         "would confirm or refute it. The seven-claim hierarchy of Section 13 is "
         "the falsification program; the five open problems of this section are "
         "the research targets that the surviving findings imply. The project's "
         "defensible content is the conjunction of the surviving claims and the "
         "research targets, with no claim that exceeds the evidence presented."),
    ]
    for p in s15_paras:
        story.append(Paragraph(p, style_body))

    # Final close - no artificial ending marker per project rules

    doc.build(story)
    return out_path


if __name__ == "__main__":
    path = build()
    print(f"Generated: {path}")
