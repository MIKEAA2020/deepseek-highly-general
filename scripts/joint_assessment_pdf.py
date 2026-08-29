#!/usr/bin/env python3
"""
Joint Assessment of Two Audits of the DeepSeek Cross-Domain Unification Transcript.

Combines:
  Audit A (mine, Z.ai): /home/z/my-project/download/deepseek_transcript_audit.pdf
  Audit B (uploaded GPT): /home/z/my-project/external_audits/gpt_audit_highly_general.txt

This document strengthens, augments, improves, and corrects weaker suggestions
and defects across both audits, then proposes a unified upgrade program.

Sections:
  Cover & Executive Summary
  Part I  - Scope and Method of the Two Audits
  Part II - Agreement: The Four Acknowledged Defects (verified by both)
  Part III- Where the GPT Audit Strengthens Mine (full adoption recommended)
  Part IV - Where My Audit Strengthens the GPT Audit (full adoption recommended)
  Part V  - New Defects Surfaced by Joint Cross-Reference
  Part VI - Strengthened Upgrades (synthesizing both audits)
  Part VII- Unified Falsification Hierarchy (extending GPT Claims A-E)
  Part VIII- Final Verdict
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
# Palette - academic minimalist with two-tone accent (deep teal + plum)
# Teal signals "Z.ai audit"; plum signals "GPT audit"; both = joint synthesis
# -----------------------------------------------------------------------------
C_PRIMARY    = HexColor('#1F2937')
C_ACCENT_A   = HexColor('#0F766E')   # deep teal - my audit + main heading rules
C_ACCENT_B   = HexColor('#7C3AED')   # plum - GPT audit references
C_ACCENT_JOINT = HexColor('#B45309')  # warm amber - joint synthesis statements
C_MUTED      = HexColor('#6B7280')
C_QUOTE      = HexColor('#374151')
C_QUOTE_BG   = HexColor('#F3F4F6')
C_TABLE_HEAD = HexColor('#0F766E')
C_TABLE_ALT  = HexColor('#F8FAFC')
C_COVER_BG   = HexColor('#0F172A')
C_COVER_FG   = HexColor('#F8FAFC')

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
    textColor=C_ACCENT_A, alignment=TA_LEFT,
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
    textColor=C_ACCENT_A, alignment=TA_LEFT,
    spaceBefore=10, spaceAfter=4,
)
style_h3_b = ParagraphStyle(
    'H3b', parent=styles['Heading3'],
    fontName='NotoSerifSC-Bold', fontSize=11.5, leading=16,
    textColor=C_ACCENT_B, alignment=TA_LEFT,
    spaceBefore=10, spaceAfter=4,
)
style_h3_joint = ParagraphStyle(
    'H3j', parent=styles['Heading3'],
    fontName='NotoSerifSC-Bold', fontSize=11.5, leading=16,
    textColor=C_ACCENT_JOINT, alignment=TA_LEFT,
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
    borderColor=C_ACCENT_A, borderWidth=0,
)
style_meta = ParagraphStyle(
    'Meta', parent=styles['Normal'],
    fontName='NotoSerifSC', fontSize=9, leading=12,
    textColor=C_MUTED, alignment=TA_LEFT,
)
style_part_label = ParagraphStyle(
    'PartLabel', parent=styles['Normal'],
    fontName='NotoSerifSC-Bold', fontSize=10, leading=14,
    textColor=C_ACCENT_A, alignment=TA_LEFT,
    spaceBefore=0, spaceAfter=2,
)
style_table_cell = ParagraphStyle(
    'TableCell', parent=styles['Normal'],
    fontName='NotoSerifSC', fontSize=9, leading=12,
    textColor=C_PRIMARY, alignment=TA_LEFT,
)
style_table_head = ParagraphStyle(
    'TableHead', parent=styles['Normal'],
    fontName='NotoSerifSC-Bold', fontSize=9.5, leading=12,
    textColor=HexColor('#FFFFFF'), alignment=TA_LEFT,
)

# -----------------------------------------------------------------------------
# Cover page (full-bleed dark, drawn via onFirstPage callback)
# -----------------------------------------------------------------------------
def draw_cover(canv, doc):
    page_w, page_h = A4
    canv.saveState()
    canv.setFillColor(C_COVER_BG)
    canv.rect(0, 0, page_w, page_h, fill=1, stroke=0)

    # dual accent rules at top (teal + plum = two audits)
    canv.setStrokeColor(C_ACCENT_A)
    canv.setLineWidth(3)
    canv.line(2.2*cm, page_h - 4*cm, 5.5*cm, page_h - 4*cm)
    canv.setStrokeColor(C_ACCENT_B)
    canv.line(5.7*cm, page_h - 4*cm, 8.2*cm, page_h - 4*cm)

    canv.setFillColor(C_COVER_FG)
    canv.setFont('NotoSerifSC-Bold', 28)
    canv.drawString(2.2*cm, page_h - 5.4*cm, "Joint Assessment of Two Audits")
    canv.drawString(2.2*cm, page_h - 6.6*cm, "of the DeepSeek Unification Transcript")

    canv.setFont('NotoSerifSC', 14)
    canv.setFillColor(HexColor('#94A3B8'))
    canv.drawString(2.2*cm, page_h - 7.8*cm, "Strengthening, augmenting, and correcting weaker suggestions")

    canv.setStrokeColor(HexColor('#334155'))
    canv.setLineWidth(0.5)
    canv.line(2.2*cm, page_h - 9.2*cm, page_w - 2.2*cm, page_h - 9.2*cm)

    canv.setFillColor(HexColor('#CBD5E1'))
    canv.setFont('NotoSerifSC', 10)
    lines = [
        "Two independent line-level audits of the same 16,271-line DeepSeek",
        "transcript are compared: one authored by Z.ai (broad, covering all",
        "six arcs and the bridge-rung structure), one authored by GPT (deep,",
        "focusing on the final n=3 Fisher-Rao construction and its central",
        "curvature-survival equivalence theorem).",
        "",
        "Both audits independently converge on the four defects DeepSeek",
        "itself acknowledges. Each audit then identifies additional issues the",
        "other does not address. The Z.ai audit exposes cross-arc rhetorical",
        "bridges that are analogies rather than mappings; the GPT audit exposes",
        "specific mathematical gaps in the final geometric construction. The",
        "two audits are complementary: together they cover both the systemic",
        "rhetorical pattern and the specific mathematical breakdown.",
        "",
        "This joint assessment adopts the strongest recommendations from",
        "each audit, corrects weaker suggestions, and proposes a unified",
        "falsification hierarchy with seven independently testable claims.",
    ]
    y = page_h - 10.7*cm
    for ln in lines:
        canv.drawString(2.2*cm, y, ln)
        y -= 13

    # meta block at bottom
    canv.setStrokeColor(C_ACCENT_A)
    canv.setLineWidth(1)
    canv.line(2.2*cm, 3.5*cm, 6.2*cm, 3.5*cm)
    canv.setFont('NotoSerifSC-Bold', 10)
    canv.setFillColor(HexColor('#F8FAFC'))
    canv.drawString(2.2*cm, 3.0*cm, "Z.AI + GPT Joint Assessment")
    canv.setFont('NotoSerifSC', 9)
    canv.setFillColor(HexColor('#94A3B8'))
    canv.drawString(2.2*cm, 2.4*cm, "Sources:")
    canv.drawString(2.2*cm, 2.0*cm, "  Z.ai: /home/z/my-project/download/deepseek_transcript_audit.pdf")
    canv.drawString(2.2*cm, 1.6*cm, "  GPT:  audit round 1/gpt audit_highly general.txt")
    canv.restoreState()


class CoverPage(Flowable):
    def __init__(self):
        super().__init__()
        self.width = 0
        self.height = 0
    def draw(self):
        pass


class HorizontalRule(Flowable):
    def __init__(self, width, thickness=0.5, color=C_ACCENT_A):
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
    return KeepTogether([
        Spacer(1, 18),
        Paragraph(label, style_part_label),
        Paragraph(title, style_h1),
        HRFlowable(width="100%", thickness=1.2, color=C_ACCENT_A, spaceBefore=2, spaceAfter=10),
        Paragraph(blurb, style_body),
        Spacer(1, 8),
    ])


def section(heading, paragraphs, quote=None, level=2):
    style = style_h2 if level == 2 else (style_h3 if level == 3 else style_h3)
    flow = [Paragraph(heading, style)]
    if quote:
        flow.append(Paragraph(quote, style_quote))
    for p in paragraphs:
        flow.append(Paragraph(p, style_body))
    return flow


# -----------------------------------------------------------------------------
# Build document
# -----------------------------------------------------------------------------
def build():
    out_path = "/home/z/my-project/download/joint_assessment_two_audits.pdf"
    doc = SimpleDocTemplate(
        out_path, pagesize=A4,
        leftMargin=2.2*cm, rightMargin=2.2*cm,
        topMargin=2.2*cm, bottomMargin=2.0*cm,
        title="Joint Assessment of Two Audits of the DeepSeek Unification Transcript",
        author="Z.ai (joint with GPT audit)",
        subject="Synthesis of two independent line-level audits",
        creator="Z.ai PDF skill (ReportLab)",
    )
    page_w, page_h = A4
    content_w = page_w - 4.4*cm

    story = []

    # Cover
    story.append(CoverPage())
    story.append(PageBreak())

    def noop(canv, doc):
        pass
    doc.onFirstPage = draw_cover
    doc.onLaterPages = noop

    # =============================================================
    # Executive Summary
    # =============================================================
    story.append(Paragraph("Executive Summary", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.2, color=C_ACCENT_A, spaceBefore=2, spaceAfter=10))

    exec_paras = [
        ("Two independent line-level audits of the same 16,271-line DeepSeek transcript are jointly "
         "assessed in this document. The Z.ai audit (referred to as Audit A throughout) is broad, "
         "covering all six construction arcs from RAF through the final n=3 Fisher-Rao geometry, "
         "identifying nine additional flaws beyond the four DeepSeek acknowledges, eight internal "
         "inconsistencies that recur across arcs, and eight profound upgrades. The GPT audit "
         "(referred to as Audit B throughout) is deep, focusing on the final n=3 construction and "
         "its central curvature-survival equivalence theorem, replacing that equivalence with a "
         "precise theory of viability-weighted holonomy in an endogenously self-maintaining system "
         "(the SAVGS object), and proposing a concrete experimental falsification protocol with "
         "five independently testable claims."),

        ("Both audits independently converge on the same four defects that DeepSeek itself "
         "acknowledges at lines 13985 through 16270: the principal GL(2)-bundle framing is wrong "
         "(correct structure group is CO(2) = R+ x O(2)); the cost labeled exact predictive variance "
         "is in fact a squared mean shift; the RAF invariance theorem reduces to continuity of a "
         "positive function on a compact set; and the claimed explicit 4-species register machine "
         "is schematic. This convergence is itself a finding: the four acknowledged defects are "
         "real, not artifacts of either reviewer's perspective. The deeper value of the joint "
         "assessment is that the non-overlapping findings of each audit complement rather than "
         "contradict each other. Audit A finds that every layer is mathematically real but every "
         "inter-layer bridge is rhetoric; Audit B finds that one specific layer's central theorem "
         "is not just tautological (as DeepSeek concedes) but actually false in general."),

        ("This joint assessment makes six moves. First, it adopts in full the GPT-proposed SAVGS "
         "object, viability-weighted curvature kappa_alpha, repeated-loop geometric adaptation "
         "fatigue prediction, and the five-claim falsification hierarchy. Second, it adopts in "
         "full the Z.ai-proposed algorithmic rate-distortion fix (replacing the R(D) versus K(x) "
         "type confusion), the optic-category unification of Hutchinson and Blahut-Arimoto fixed "
         "points, the CPTP channel resolution of the ergodicity self-contradiction, and the "
         "Bregman-divergence derivation of the Noether correspondence. Third, it identifies six "
         "new defects that surface only when both audits are read together: smooth-connection "
         "breakdown at constraint-switching boundaries (pathwise vs endpoint viability), strict "
         "vs non-strict viability margins, homeostasis versus autopoiesis, fully-observable POMDP "
         "being simply an MDP, finite grid not being a differentiable base manifold, and the "
         "missing commuting-control specification via the CO(2) structure group. Fourth, it "
         "strengthens five of the upgrades by combining insights from both audits: the SAVGS is "
         "placed in a 2-categorical span framework (jointly from Audit A's category-theory "
         "observation and Audit B's stratification observation), viability-weighted curvature is "
         "derived from algorithmic rate-distortion rather than imposed by definition, the "
         "intervention-based autopoiesis closure test is formalized via the RAF catalytic subgraph, "
         "the commuting control is specified via CO(2) commutator structure, and the empirical "
         "holonomy statistic is augmented with a non-parametric bootstrap. Fifth, it extends the "
         "five-claim falsification hierarchy with two additional claims (F and G) testing the "
         "structure-group correction and the rate-distortion type fix respectively. Sixth, it "
         "delivers a revised final verdict that is sharper than either audit alone."),

        ("The revised verdict: the project should not claim survival is equivalent to bounded "
         "information-geometric curvature (GPT finding), nor that the multi-arc chain is a "
         "rigorous unification rather than a rhetorical composition (Z.ai finding). Its rigorous "
         "result, after both audits' corrections are applied, is narrower and stronger than "
         "either DeepSeek's own self-assessment or either audit alone proposed. On smooth "
         "constant-active-set strata of an experimentally parameterized control manifold, "
         "Fisher-minimal constraint-preserving adaptation defines a stratified connection whose "
         "viability-weighted curvature predicts leading-order policy hysteresis; whether that "
         "holonomy is fatal depends on viability margins, along-path disturbances, and the "
         "regeneration of internal maintenance machinery. The decisive empirical test is whether "
         "independently estimated, gauge-invariant, viability-weighted holonomy predicts held-out "
         "margin erosion, orientation reversal, area scaling, repeated-loop failure after "
         "energetic depletion is controlled, and whether the structure-group correction (CO(2) not "
         "GL(2)) survives an independent commuting-control test."),
    ]
    for p in exec_paras:
        story.append(Paragraph(p, style_body))

    story.append(PageBreak())

    # =============================================================
    # Part I — Scope and Method of the Two Audits
    # =============================================================
    story.append(part_divider(
        "PART I",
        "Scope and Method of the Two Audits",
        "The two audits were produced independently and reviewed the same 16,271-line "
        "transcript. They differ in scope, depth, and method. The complementary "
        "distribution of their findings is what makes the joint assessment more than "
        "the sum of its parts."
    ))

    story.extend(section(
        "1.1 Audit A (Z.ai) - broad arc-by-arc review",
        [
            ("Audit A reads the transcript in ten line-level passes, one pass per construction "
             "arc, then a cross-arc pass to identify inconsistencies. The arcs covered are: "
             "(1) RAF as rate-distortion bridge (lines 1-427); (2) consciousness as Recursive "
             "Predictive Self-Information (lines 428-1022); (3) fractals as Iterated Function "
             "Systems (lines 1044-1814); (4) symmetry and Noether-type correspondence "
             "(lines 1908-2324); (5) perturbation theory of the optimal encoding (lines "
             "2378-3136); (6) the abortive Wasserstein-Categorical Information Geometry upgrade "
             "(lines 3140-3518); (7) the seven bridge rungs (lines 4000-4500); (8) the "
             "abortive Counterfactual Gauge Theory upgrade (lines 4600-5200); (9) the n=3 "
             "Fisher-Rao explicit construction (lines 11000+); and (10) the final "
             "self-assessment (lines 13985-16270)."),
            ("The method of Audit A is to locate each theorem statement, each definition, and "
             "each caveat using ripgrep, then read the surrounding twenty-line window to "
             "extract the precise claim. The audit then asks three questions of each claim: "
             "is it mathematically correct, is it substantively novel given prior art, and "
             "is it consistent with claims made elsewhere in the transcript? The output is "
             "a list of nine flaws, eight internal inconsistencies, and eight profound "
             "upgrades. The unifying observation is that each layer is mathematically real "
             "but each inter-layer bridge is rhetorical."),
            ("The strength of Audit A is breadth. Its weakness is that its upgrades are "
             "primarily theoretical; it does not propose an experimental falsification "
             "protocol, nor does it provide a single testable prediction. This weakness is "
             "precisely what Audit B remedies."),
        ]
    ))

    story.extend(section(
        "1.2 Audit B (GPT) - deep single-theorem review",
        [
            ("Audit B reads the same 16,271-line transcript but focuses almost exclusively on "
             "the final n=3 Fisher-Rao construction (lines 11000 through 16270), and within "
             "that construction on the central proposed equivalence theorem: that bounded "
             "information-geometric curvature is equivalent to survival under perturbation. "
             "The audit identifies that this equivalence is not merely tautological (as "
             "DeepSeek itself concedes at line 8518) but actually false in general: a flat "
             "connection can transport an agent directly out of its viable set, while a "
             "highly curved connection can remain entirely inside a large viable region."),
            ("The method of Audit B is constructive. Rather than merely criticizing, it "
             "replaces the false equivalence with a precise mathematical object called the "
             "Stratified Autopoietic Viability-Geometric System (SAVGS), consisting of an "
             "experimental base manifold, policy fibers, Fisher geometry without logit gauge "
             "errors, viability and maintenance states, a Fisher-minimal transport law, a "
             "viability-weighted curvature, a small-loop viability-holonomy theorem, a "
             "repeated-loop fatigue prediction, an endogenous maintenance graph with "
             "intervention-based closure test, and a five-claim falsification hierarchy."),
            ("The strength of Audit B is depth, mathematical rigor, and falsifiability. Its "
             "weakness is that it treats the final construction as if it were the entire "
             "transcript, omitting the earlier arcs whose defects propagate into the final "
             "construction. This weakness is precisely what Audit A remedies."),
        ]
    ))

    story.extend(section(
        "1.3 Complementarity and the rationale for joint assessment",
        [
            ("The two audits have non-overlapping defect sets beyond the four acknowledged "
             "ones, and non-overlapping upgrade sets beyond the SAVGS framework. The joint "
             "assessment therefore does not have to choose between breadth and depth; it "
             "can adopt both. The Z.ai finding that each inter-layer bridge is rhetorical "
             "rather than a mapping, combined with the GPT finding that the final layer's "
             "central theorem is actually false, produces a sharper diagnosis than either "
             "audit alone: the rhetorical bridges conceal the fact that the final layer's "
             "equivalence is unsupported by the earlier layers' constructions."),
            ("Concretely: Audit B's SAVGS object presupposes a continuous base manifold, "
             "Fisher-minimal transport, and a smooth horizontal lift. Audit A shows that "
             "the upstream arcs fail to provide these as derived consequences: the rate-"
             "distortion arc confuses R(D) with K(x), the consciousness arc presupposes "
             "non-ergodicity while the RAF arc presupposes ergodicity, the fractal arc "
             "conflates Hutchinson fixed points with Blahut-Arimoto fixed points, and the "
             "Noether arc fails to verify the Lagrangian's G-invariance. Each of these "
             "upstream defects blocks a different precondition of the SAVGS construction. "
             "The joint assessment therefore specifies, for each SAVGS component, which "
             "upstream fix is required for it to hold."),
        ]
    ))

    # Comparison table
    story.append(Spacer(1, 6))
    story.append(Paragraph("1.4 Comparison of the two audits at a glance", style_h2))
    cmp_data = [
        [Paragraph("Dimension", style_table_head),
         Paragraph("Audit A (Z.ai)", style_table_head),
         Paragraph("Audit B (GPT)", style_table_head)],
        [Paragraph("Transcript coverage", style_table_cell),
         Paragraph("All 6 arcs + bridge rungs + final self-assessment", style_table_cell),
         Paragraph("Final n=3 construction only", style_table_cell)],
        [Paragraph("Reading method", style_table_cell),
         Paragraph("10 passes, arc-by-arc with ripgrep", style_table_cell),
         Paragraph("Single deep pass on final theorem", style_table_cell)],
        [Paragraph("Defects beyond the 4 acknowledged", style_table_cell),
         Paragraph("9 additional flaws, 8 internal inconsistencies", style_table_cell),
         Paragraph("4 corrections + 4 gaps in the final theorem", style_table_cell)],
        [Paragraph("Central finding", style_table_cell),
         Paragraph("Layers are math, bridges are rhetoric", style_table_cell),
         Paragraph("Central theorem is false in general, not tautological", style_table_cell)],
        [Paragraph("Upgrade style", style_table_cell),
         Paragraph("Theoretical (category, algorithmic R(D), CPTP, Bregman)", style_table_cell),
         Paragraph("Constructive (SAVGS, kappa_V, fatigue, falsification)", style_table_cell)],
        [Paragraph("Falsifiability", style_table_cell),
         Paragraph("Implicit; no testable prediction", style_table_cell),
         Paragraph("Explicit 5-claim hierarchy with controls", style_table_cell)],
        [Paragraph("Verdict on DeepSeek self-assessment", style_table_cell),
         Paragraph("Accurate but understates issues", style_table_cell),
         Paragraph("Accurate on final layer; silent on earlier layers", style_table_cell)],
    ]
    col_widths = [content_w * 0.22, content_w * 0.39, content_w * 0.39]
    cmp_tbl = Table(cmp_data, colWidths=col_widths, repeatRows=1)
    cmp_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_TABLE_HEAD),
        ('TEXTCOLOR', (0,0), (-1,0), HexColor('#FFFFFF')),
        ('FONTNAME', (0,0), (-1,0), 'NotoSerifSC-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9.5),
        ('ALIGN', (0,0), (-1,0), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor('#FFFFFF'), C_TABLE_ALT]),
        ('GRID', (0,0), (-1,-1), 0.4, HexColor('#CBD5E1')),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(cmp_tbl)
    story.append(Spacer(1, 12))

    story.append(PageBreak())

    # =============================================================
    # Part II — Agreement: The Four Acknowledged Defects
    # =============================================================
    story.append(part_divider(
        "PART II",
        "Agreement: The Four Acknowledged Defects",
        "Both audits independently converge on the four defects DeepSeek itself "
        "acknowledges. This convergence validates the defects. The joint assessment "
        "adopts all four corrections as binding prerequisites for any future version "
        "of the framework."
    ))

    story.extend(section(
        "2.1 Structure group: GL(2) is wrong; correct is CO(2)",
        [
            ("DeepSeek proposes a principal GL(2, R)-bundle connection on the Fisher-Rao "
             "2-simplex. The Fisher-Rao metric is only invariant under conformal orthogonal "
             "transformations, not under the full general linear group. The correct structure "
             "group is therefore CO(2) = R+ x O(2). Both audits identify this independently. "
             "Audit A traces the error to a conflation of the vector bundle of tangent directions "
             "with the principal bundle of frames; Audit B notes the implication that the "
             "commuting-control test (Section 9.3 of Audit B) must use the CO(2) commutator "
             "structure, not the GL(2) commutator."),
            ("The correction is binding: every claim that depends on the GL(2) framing must "
             "be re-derived under CO(2). In particular, the holonomy group is a subgroup of "
             "CO(2), and the curvature 2-form takes values in the Lie algebra of CO(2) (which "
             "is one-dimensional, generated by the rotation generator; the dilatation component "
             "is central and contributes only a trace term to holonomy). This dramatically "
             "narrows the predicted holonomy group and is itself a testable claim (see "
             "Claim F in Part VII)."),
        ]
    ))

    story.extend(section(
        "2.2 The cost is not exact predictive variance; it is squared mean shift",
        [
            ("DeepSeek labels the term (1/2) ||dA(v) lambda + A(mu) xi||^2 as the exact increase "
             "in predictive variance. Both audits verify (by direct computation in the linear-"
             "Gaussian model y = A(mu) lambda + epsilon with epsilon ~ N(0, I)) that Var(y) = "
             "I (constant) while the mean shift is A(mu) xi + dA(v) lambda. The term in "
             "question is the squared mean shift, not a variance term. Calling it predictive "
             "variance is a misnomer."),
            ("The correction is to call the cost what it is: a regularized squared predictive "
             "error, and to derive the connection from that declared cost. Audit B observes "
             "that this matters because the later interpretation of the connection as least "
             "counterfactual variance is then not derived from the generative model; it is "
             "imposed by choosing a quadratic proxy. Audit A generalizes this observation: the "
             "BA-operator's Frechet differentiability at the simplex boundary requires the cost "
             "to be KL-divergence-like (which is finite on the boundary) rather than squared-"
             "error-like (which can be infinite). The joint upgrade in Part VI replaces the "
             "squared mean shift with a Bregman-divergence cost, which simultaneously fixes "
             "the misnomer and the differentiability gap."),
        ]
    ))

    story.extend(section(
        "2.3 RAF invariance theorem is continuity on a compact set, not a theorem",
        [
            ("DeepSeek's RAF invariance theorem states that inf_{mu in K} ||F|| > 0 where K "
             "is an invariant set. Both audits verify that this follows trivially from "
             "continuity of the strictly positive function kappa(mu) on the compact interior "
             "set K. The theorem is true but scientifically empty: it has nothing to do with "
             "RAF closure or autopoiesis per se."),
            ("The correction is to separate the RAF example (a single vector field on a "
             "compact set, where the bound is trivial) from any general invariance theorem "
             "(which would require RAF closure to enter non-trivially). Audit B adds that "
             "the genuine autopoiesis claim requires the maintenance graph criterion "
             "(Section 7 of Audit B), not just a viability margin. Audit A adds that the "
             "RAF formalism must be re-embedded in the algorithmic rate-distortion framework "
             "if the closure property is to enter as a theorem rather than a definition. "
             "The joint upgrade in Part VI combines both: the maintenance graph is given an "
             "algorithmic-rate-distortion semantics."),
        ]
    ))

    story.extend(section(
        "2.4 The 4-species register machine is schematic, not explicit",
        [
            ("DeepSeek claims to give an explicit 4-species register machine but provides only "
             "a schematic. Two-counter Minsky machine simulation by deterministic mass-action "
             "kinetics is non-trivial: it requires careful encoding of counters, flags, and "
             "instruction pointers. The cited Soloveichik et al. result is real, but it is "
             "not the same as a self-contained explicit construction with four species "
             "satisfying RAF closure. Both audits flag this."),
            ("The correction is to either write down the full reaction list or honestly "
             "concede that this part is an external result. Audit B's intervention-based "
             "closure test (Section 7.2 of Audit B) is also relevant here: if the 4-species "
             "machine is provided externally as a black box, the autopoiesis claim fails the "
             "intervention test because hidden external mechanisms are doing the regeneration. "
             "Audit A's algorithmic-rate-distortion framing adds that the 4-species machine, "
             "if it is to be the encoding substrate, must satisfy an algorithmic complexity "
             "lower bound. The joint upgrade in Part VI specifies the minimum reaction list "
             "and connects it to the algorithmic rate-distortion semantics."),
        ]
    ))

    story.append(PageBreak())

    # =============================================================
    # Part III — Where the GPT Audit Strengthens Mine
    # =============================================================
    story.append(part_divider(
        "PART III",
        "Where the GPT Audit Strengthens Mine",
        "Audit B contributes five substantial advances that Audit A does not make. "
        "All five are adopted in full. Each is restated briefly here, then "
        "integrated with Audit A's findings in Part VI."
    ))

    story.extend(section(
        "3.1 The SAVGS object as the rigorous replacement",
        [
            ("Audit B proposes a Stratified Autopoietic Viability-Geometric System (SAVGS) "
             "consisting of an experimental base manifold Theta (a continuous control-manifold "
             "of environmental parameters, not the discrete grid), policy fibers P (a product "
             "of open simplices int Delta^(A-1)), Fisher geometry without logit gauge errors "
             "(via the square-root embedding psi_a = 2 sqrt(p_a) into the positive orthant "
             "of a sphere of radius 2, giving the exact Fisher-Rao distance d_F(p, q) = "
             "2 arccos(sum_a sqrt(p_a q_a))), viability and maintenance states (with strict "
             "margins E >= E_min > 0 rather than E > 0), and an endogenous maintenance graph "
             "Gamma = (M, R, E)."),
            ("This object is adopted in full. The grid-as-base-manifold error (Section 1.3 "
             "of Audit B) is a real defect that Audit A did not flag. The strict-vs-non-strict "
             "viability margin distinction (Section 2.4 of Audit B) is also a real defect "
             "that Audit A did not flag; standard viability kernel existence theorems "
             "(Aubin, Nagumo) require closed viable sets. The logit gauge ambiguity (Section "
             "2.3 of Audit B) is the same issue Audit A identified in the GL(2) versus CO(2) "
             "structure-group error, but Audit B's square-root embedding gives the cleaner "
             "fix."),
        ],
        quote=(
            "Curvature predicts adaptation hysteresis; viability margins determine whether "
            "that hysteresis is fatal. (Audit B, Section 1.1)"
        )
    ))

    story.extend(section(
        "3.2 Viability-weighted curvature kappa_alpha",
        [
            ("Audit B replaces raw curvature ||F|| with the viability-weighted curvature "
             "kappa_alpha(theta, x; u, v) = [-D_p h_alpha(F(u, v))]_+ / h_alpha(theta, x), "
             "defined whenever h_alpha > 0. The aggregate index kappa_V is the worst "
             "fractional loss of viability margin per unit oriented environmental-loop area, "
             "to leading order. This is more meaningful than ||F|| alone because it contracts "
             "the geometric defect with experimentally specified survival covectors."),
            ("This construction is adopted in full. Audit A's contribution is to derive "
             "kappa_alpha from an information-theoretic first principle rather than imposing "
             "it by definition. Specifically, if the viability function h_alpha is taken to "
             "be a Bregman divergence from the optimal policy (in the dual-affine coordinates "
             "of the exponential family), then D_p h_alpha(F(u, v)) is the second-order "
             "predictive-information loss, and the positivity part [-.]_+ is the "
             "irreducible loss after the optimal repair. This gives kappa_alpha a derivation "
             "from algorithmic rate-distortion theory (Audit A's Upgrade 1), connecting "
             "Audit B's geometric construction to Audit A's information-theoretic foundation."),
        ]
    ))

    story.extend(section(
        "3.3 Repeated-loop geometric adaptation fatigue as a novel prediction",
        [
            ("Audit B proposes that repeated noncommuting adaptation accumulates a fraction "
             "of available viability margin bounded approximately by sum_k (a_k kappa_{V,k} "
             "+ C_k a_k^(3/2) + eta_k), with a sufficient condition that this sum is less "
             "than 1. The testable phenomenon is: an agent may survive every environmental "
             "transition in isolation yet fail after repeated closed cycles because "
             "noncommuting adaptations accumulate irreversible organizational drift. If "
             "reversed loops cancel the drift to leading order, the mechanism is geometric; "
             "if they do not, secular learning, resource depletion, or irreversible damage "
             "is dominating."),
            ("This is adopted in full as the central novel prediction of the joint framework. "
             "Audit A's contribution is a caveat: the small-loop expansion holds only on "
             "constant-active-set strata. When a loop crosses a constraint-switching "
             "boundary, the leading-order term is no longer O(epsilon^2) but can be O(epsilon) "
             "due to the discontinuity in the active set. The fatigue prediction therefore "
             "requires that all loops in the sequence remain within a single stratum, OR "
             "that the stratification corrections are explicitly included. This is a "
             "refinement, not a restriction: it tells the experimenter to either keep loops "
             "small enough to avoid stratum crossings or to model the crossing contributions."),
        ]
    ))

    story.extend(section(
        "3.4 Experimental falsification protocol with calibration / held-out split",
        [
            ("Audit B specifies a calibration-versus-held-out experimental protocol: "
             "estimate local transport operators from independent open-edge perturbations "
             "(theta -> theta + epsilon e_i) on calibration data; compose the independently "
             "estimated edge transports to predict the policy after an unseen loop on held-out "
             "test data; compare with actual loop execution. The empirical holonomy is "
             "H_emp = log^F_{p_0}(p_gamma); a matched no-loop drift control is subtracted; "
             "the geometric prediction is H_geo = epsilon^2 F_12 + O(epsilon^3); a natural "
             "discrepancy statistic T = ||H_corr - H_geo||_F / sigma_total is proposed."),
            ("This protocol is adopted in full. It closes a real circularity that Audit A "
             "did not address: estimating curvature from the same closed-loop endpoint used "
             "to validate it is tautological. Audit A's contribution is to add a "
             "non-parametric bootstrap component to sigma_total (in addition to Audit B's "
             "hierarchical bootstrap), because the discrete-grid stochasticity can produce "
             "heavy-tailed disturbances that the hierarchical bootstrap underestimates. The "
             "joint upgrade in Part VI formalizes this."),
        ]
    ))

    story.extend(section(
        "3.5 Five-claim falsification hierarchy",
        [
            ("Audit B splits the framework into five independently falsifiable claims: "
             "(A) local transport law, (B) holonomy law with orientation reversal and area "
             "scaling, (C) viability relevance of kappa_V over raw Fisher displacement or "
             "exposure-only baselines, (D) repeated-loop fatigue, and (E) autopoietic closure. "
             "Each claim has a specified falsification criterion."),
            ("This hierarchy is adopted in full. Audit A's contribution is to extend it with "
             "two additional claims: (F) the structure-group correction CO(2) versus GL(2), "
             "testable by a commuting-control experiment using perturbations whose CO(2) "
             "commutator vanishes; and (G) the rate-distortion type fix, testable by "
             "comparing the predictive performance of the algorithmic-rate-distortion-derived "
             "kappa_alpha against an ensemble-average-R(D)-derived alternative. The full "
             "extended hierarchy is given in Part VII."),
        ]
    ))

    story.append(PageBreak())

    # =============================================================
    # Part IV — Where My Audit Strengthens the GPT Audit
    # =============================================================
    story.append(part_divider(
        "PART IV",
        "Where My Audit Strengthens the GPT Audit",
        "Audit A contributes five substantial advances that Audit B does not make. "
        "All five are adopted in full. Each is restated briefly here, then "
        "integrated with Audit B's findings in Part VI."
    ))

    story.extend(section(
        "4.1 The R(D) versus K(x) type confusion and its algorithmic-rate-distortion fix",
        [
            ("Audit A identifies that the rate-distortion arc (lines 1-427) conflates the "
             "Shannon rate-distortion function R(D), which is an ensemble-average lower "
             "bound on coding rate achieved by random coding, with the Kolmogorov complexity "
             "K(x), which is a single-string quantity. The two coincide only in the "
             "asymptotic equipartition property limit under i.i.d. assumptions, which the "
             "transcript never states. The bridge from RAF to rate-distortion theory is "
             "therefore a category error at the type level: the deterministic transition "
             "function delta of the automaton is not the same kind of object as the "
             "randomized encoder achieving R(D)."),
            ("This matters for the SAVGS object because SAVGS presupposes that the "
             "Fisher-minimal transport law is a well-defined deterministic map. Under the "
             "ensemble-average R(D) framework, the optimal encoder is randomized; under "
             "the algorithmic rate-distortion framework (where dist_D(x) = min {|p| : U(p) "
             "outputs x_hat, d(x, x_hat) <= D}), the optimal encoder is deterministic and "
             "Turing-computable. The deterministic Fisher-minimal transport law is "
             "therefore a feature, not a bug, but only if the underlying rate-distortion "
             "framework is the algorithmic one. The joint upgrade in Part VI formalizes "
             "this: the SAVGS transport law is derived as the optimal-encoding projection "
             "in the algorithmic-rate-distortion sense."),
        ]
    ))

    story.extend(section(
        "4.2 The IFS versus Blahut-Arimoto fixed-point category error",
        [
            ("Audit A identifies that the fractals arc (lines 1044-1814) uses an Iterated "
             "Function System (IFS) attractor, which is a Hutchinson-Banach metric fixed "
             "point in the (Metric, Lipschitz) category, and conflates it with the "
             "Blahut-Arimoto fixed point of the rate-distortion optimal encoder, which is "
             "a probability-simplex fixed point in the (Prob, Markov) category. The two "
             "categories are different; the transcript connects them by the word resonance "
             "without providing a functor."),
            ("This matters for the SAVGS object because SAVGS's viability-weighted "
             "curvature kappa_alpha presupposes that the holonomy operator is well-defined "
             "as a continuous map. If the underlying state space mixes a Hutchinson metric "
             "fixed point with a Blahut-Arimoto probability fixed point, the holonomy's "
             "regularity breaks. The joint upgrade in Part VI formalizes the unification: "
             "the Hutchinson operator on the Wasserstein space of probability measures is "
             "the proper generalization of the IFS attractor; the Blahut-Arimoto iteration "
             "is its special case for the Kullback-Leibler divergence. The optic/lens "
             "category provides the unified framework: an IFS is a pure coalgebra (no "
             "residual), while the BA iteration is a coalgebra with residual. The SAVGS "
             "connection lives naturally in this optic category."),
        ]
    ))

    story.extend(section(
        "4.3 The ergodicity self-contradiction and its CPTP-channel resolution",
        [
            ("Audit A identifies a contradiction between the RAF arc's assumption of an "
             "ergodic channel (the rate-distortion function is well-defined only for ergodic "
             "sources) and the consciousness arc's definition of Recursive Predictive "
             "Self-Information, which requires the system to predict its own future state "
             "in a way that changes the predicted system (a non-ergodic, self-referential "
             "loop). The transcript never reconciles these. The contradiction propagates "
             "to the final n=3 construction, which assumes a stationary policy distribution "
             "(an ergodic property) while also modeling the agent as adapting its policy "
             "in response to its own predictions (a non-ergodic property)."),
            ("This matters for the SAVGS object because SAVGS's viability margin h_alpha "
             "presupposes a well-defined long-run average policy distribution. The joint "
             "upgrade in Part VI resolves the contradiction by adopting the CPTP-channel "
             "framework from quantum information: the predicting agent is an open system, "
             "and the self-referential prediction is the channel composition Phi composed "
             "with Phi-hat, where Phi-hat is the agent's internal model of itself. The RPSI "
             "definition becomes I(rho_out; rho-hat_in), where rho-hat is the agent's "
             "internal-model quantum state. This naturally accommodates non-ergodicity via "
             "the quantum Zeno effect (the recursive measurement that stabilizes the "
             "predicted state), which is the rigorous version of the self-referential "
             "prediction loop. The SAVGS viability margin then becomes the minimum of "
             "h_alpha over the Zeno-stabilized steady state."),
        ]
    ))

    story.extend(section(
        "4.4 The Noether correspondence's missing G-invariance precondition",
        [
            ("Audit A identifies that the symmetry/Noether arc (lines 1908-2324) proposes "
             "a correspondence between the rate-distortion optimal encoder's symmetry and "
             "Noether's conservation laws, but never verifies that the Lagrangian L = "
             "E[d] + lambda I is G-invariant under the data group G's action on the source "
             "X. Noether's theorem requires a continuous symmetry group acting on the "
             "configuration manifold that leaves the Lagrangian invariant. The rate-"
             "distortion Lagrangian is G-invariant only if both the distortion measure d "
             "and the source prior P are G-invariant. The transcript assumes this without "
             "statement."),
            ("This matters for the SAVGS object because SAVGS's viability-weighted curvature "
             "kappa_alpha, if it is to inherit a Noether-type conservation law, requires "
             "the viability functions h_alpha to be invariant under the connection's gauge "
             "transformations. The joint upgrade in Part VI derives this from the dual-"
             "affine-coordinate structure of the exponential family: the Bregman divergence "
             "is invariant under dual-affine coordinate changes, so if the viability "
             "functions are Bregman divergences (which Part VI's kappa_alpha derivation "
             "ensures), the Noether correspondence holds automatically. This gives the "
             "first genuinely provable Noether-type conservation law in the framework: "
             "each pair of dual coordinates (theta, eta) produces a conserved generalized "
             "momentum."),
        ]
    ))

    story.extend(section(
        "4.5 The BA operator's Frechet differentiability gap at the simplex boundary",
        [
            ("Audit A identifies that the perturbation-theory arc (lines 2378-3136) develops "
             "a perturbation expansion of the optimal encoder around its stationary point, "
             "but never verifies that the Blahut-Arimoto operator is Frechet differentiable "
             "at the simplex boundary (where some probabilities are zero). The BA operator "
             "is in fact not Frechet differentiable at the boundary, because the "
             "multiplicative update q(x_hat|x) = p(x_hat) exp(-lambda d(x, x_hat)) / "
             "Z(x_hat) is singular when p(x_hat) = 0. The perturbation expansion is "
             "therefore valid only in the simplex interior, but the transcript applies it "
             "to the boundary."),
            ("This matters for the SAVGS object because SAVGS's viability-weighted curvature "
             "kappa_alpha presupposes that the transport operator A_i is C^2 (Section 5 of "
             "Audit B, hypothesis 4). The transport operator is C^2 only where the BA "
             "operator is C^2, which is the simplex interior. The joint upgrade in Part VI "
             "addresses this by adopting the Bregman-divergence cost (which is finite and "
             "smooth on the closed simplex) instead of the squared-mean-shift cost (which "
             "is not), and by restricting the SAVGS small-loop theorem to the interior "
             "plus a separate boundary analysis."),
        ]
    ))

    story.append(PageBreak())

    # =============================================================
    # Part V — New Defects Surfaced by Joint Cross-Reference
    # =============================================================
    story.append(part_divider(
        "PART V",
        "New Defects Surfaced by Joint Cross-Reference",
        "Reading the two audits together surfaces six defects that neither audit "
        "alone identifies. Each is a real gap in the DeepSeek transcript. They are "
        "ordered by severity."
    ))

    story.extend(section(
        "5.1 Smooth-connection breakdown at constraint-switching boundaries",
        [
            ("Audit B observes (Section 1.2) that the map from environmental velocity "
             "theta-dot to policy velocity v is piecewise nonlinear because viability "
             "constraints enter and leave the active set; an Ehresmann connection requires "
             "a smoothly varying linear horizontal subspace. The correct object is a "
             "stratified viability transport law, with a smooth connection on each "
             "constant-rank active stratum and explicit transition rules between strata. "
             "Audit A adds that the stratification is a span in the 2-category of "
             "categories: each stratum is a category, the transition rules are functors, "
             "and the global object is a span Stratum_1 <- Boundary -> Stratum_2."),
            ("This defect is invisible to Audit A alone (which does not focus on the final "
             "construction) and is hinted at but not formalized by Audit B (which uses the "
             "informal word stratified). The joint assessment formalizes the stratification "
             "as a 2-categorical span, which gives it a precise mathematical type and "
             "enables the systematic derivation of transition rules between strata. The "
             "transcript never addresses this: searches for active set, constraint switch, "
             "stratified, piecewise, and hybrid system in the transcript return only the "
             "regularity-condition matches for piecewise-smooth loops, not stratification."),
        ]
    ))

    story.extend(section(
        "5.2 Pathwise versus endpoint viability",
        [
            ("Audit B observes (Section 5, What this theorem does not claim) that the "
             "small-loop viability-holonomy theorem does not guarantee viability at every "
             "intermediate point of the loop. For pathwise survival, one additionally "
             "needs either a positive viability tube around the entire horizontally "
             "lifted path, or a Nagumo-type inward-pointing condition on the boundary of "
             "the viable set, with robustness slack exceeding implementation disturbances. "
             "The DeepSeek transcript conflates pathwise and endpoint viability throughout "
             "the final construction."),
            ("Searches of the transcript for pathwise, intermediate point, during the "
             "loop, Nagumo, tangency condition, inward-pointing, and viability tube "
             "return zero matches outside the Audit B commentary. This confirms that "
             "DeepSeek never addresses the distinction. The defect is severe because the "
             "claimed equivalence between curvature and survival depends on it: a small-"
             "loop holonomy that is bounded at the endpoint does not imply that the agent "
             "remained viable at every intermediate point, only that it returned viable. "
             "A flat connection that transports the agent through a non-viable region and "
             "back is a counterexample."),
        ]
    ))

    story.extend(section(
        "5.3 Homeostasis versus autopoiesis distinction",
        [
            ("Audit B observes (Section 1.4) that an agent constrained by externally "
             "imposed conditions such as E > 0 and I = 1 is homeostatic, but not yet "
             "demonstrably autopoietic. Autopoiesis requires the system to maintain the "
             "mechanisms that maintain those constraints. The distinction is: homeostasis "
             "keeps the agent inside a prescribed viable set; autopoiesis regenerates the "
             "sensing, control, repair, and boundary-maintenance machinery required to "
             "remain there. Audit A's 4-species-register critique flags that the "
             "construction is schematic; Audit B's homeostasis-versus-autopoiesis critique "
             "flags that even if it were schematic-detail-completed, it might still not be "
             "autopoietic."),
            ("This defect is invisible to Audit A alone (which does not separate "
             "homeostasis from autopoiesis) and is mentioned but not fully integrated by "
             "Audit B (which proposes the intervention-based closure test in Section 7.2 "
             "but does not connect it to the algorithmic-rate-distortion framework). The "
             "joint assessment formalizes the closure test via the RAF catalytic subgraph: "
             "a component is causally internal to organizational closure if and only if "
             "its intervention disrupts a positive catalytic flux in the RAF formalism. "
             "This gives the closure test a precise mathematical type."),
        ]
    ))

    story.extend(section(
        "5.4 Fully observable POMDP is simply an MDP",
        [
            ("Audit B observes (Section 1.3) that the transcript uses the term POMDP for "
             "a grid-world in which the state is fully observable. If the grid state is "
             "fully observable, the correct term is MDP. If observations are partial or "
             "noisy, the correct term is POMDP, but then the framework needs belief states "
             "(which DeepSeek acknowledges at line 9952 as a non-trivial extension that "
             "the framework lacks). The transcript uses POMDP loosely."),
            ("This defect is invisible to Audit A (which does not focus on the "
             "decision-theoretic terminology) and is mentioned by Audit B (Section 1.3) "
             "but not connected to the deeper grid-as-base-manifold error. The joint "
             "assessment connects them: a finite grid is not naturally a differentiable "
             "base manifold; differential curvature should not be defined directly on "
             "grid squares in physical state space. The fix is to define a continuous "
             "experimental-control manifold Theta subset R^d whose coordinates are food "
             "scarcity, hazard intensity, sensor noise, energy price, repair latency, etc. "
             "Plaquettes are then loops in Theta while the agent acts inside the grid-world "
             "at each parameter value. This also resolves the MDP-versus-POMDP terminology: "
             "the grid-world is an MDP at each fixed theta, but the meta-control problem "
             "over theta is a POMDP because the agent does not directly observe theta."),
        ]
    ))

    story.extend(section(
        "5.5 Strict versus non-strict viability margins",
        [
            ("Audit B observes (Section 2.4) that the transcript uses strict inequalities "
             "like E > 0 and I = 1 to define the viable set. Strict inequalities do not "
             "define a closed safe set and are unsuitable for standard viability theorems "
             "(which require compact viable sets for the existence of viable kernels via "
             "Nagumo's theorem). The correct definition uses strict positive margins: E "
             ">= E_min > 0, I >= I_min, R_j >= R_{j, min}."),
            ("This defect is a real mathematical subtlety that neither audit fully develops. "
             "The transcript's strict-inequality formulation is not just a notational "
             "choice: it breaks the existence theorems that the framework implicitly relies "
             "on. Specifically, the viability kernel Viab_K(t_0, t_f) = {x_0 : there "
             "exists a control u(.) such that x(t) stays in K for t in [t_0, t_f]} is "
             "guaranteed to be non-empty and closed only when K is closed. With strict "
             "inequalities, K is open, and the viability kernel may fail to exist. The "
             "joint assessment adopts the strict-positive-margin fix and notes that it is "
             "a binding prerequisite for any viability-theorem invocation."),
        ]
    ))

    story.extend(section(
        "5.6 The missing commuting-control specification via CO(2)",
        [
            ("Audit B proposes (Section 9.3) a commuting control: choose two perturbations "
             "expected to induce commuting updates, and the predicted leading holonomy "
             "should be approximately zero. But Audit B does not specify which perturbations "
             "commute. Audit A's structure-group correction (CO(2) not GL(2)) provides the "
             "answer: two perturbations commute if and only if their CO(2) commutator "
             "vanishes. Since CO(2) = R+ x O(2), the Lie algebra decomposes as the direct "
             "sum of the dilatation generator (central, trace part) and the rotation "
             "generator (antisymmetric part). Two perturbations commute if their rotation "
             "components are parallel (or both zero) and their dilatation components are "
             "arbitrary (since dilatations commute with everything)."),
            ("This gives the commuting-control experiment a precise design: choose one "
             "perturbation direction with a pure dilatation component (e.g., a uniform "
             "rescaling of the policy probabilities) and another with the same dilatation "
             "component but a non-parallel rotation component. The predicted holonomy "
             "should be approximately zero for the parallel case and non-zero for the "
             "non-parallel case. This is a sharper prediction than the Audit B version, "
             "and it is testable. It also gives Claim F in Part VII its experimental "
             "specification."),
        ]
    ))

    story.append(PageBreak())

    # =============================================================
    # Part VI — Strengthened Upgrades (synthesizing both audits)
    # =============================================================
    story.append(part_divider(
        "PART VI",
        "Strengthened Upgrades: Synthesizing Both Audits",
        "Five upgrades are strengthened by combining insights from both audits. "
        "Each upgrade is restated with the joint improvement, the upstream fix "
        "it requires, and the downstream claim it underwrites."
    ))

    story.extend(section(
        "6.1 SAVGS in a 2-categorical span framework",
        [
            ("Audit B's SAVGS object is placed in a 2-categorical framework. The "
             "stratified viability transport law is formalized as a span of categories "
             "Stratum_1 <- Boundary -> Stratum_2, where each stratum is a category (with "
             "objects the policies in that stratum and morphisms the policy updates), the "
             "boundary is the active-set-switching surface, and the span functors are the "
             "inclusion and projection maps. The global SAVGS is then a 2-functor from "
             "the base manifold Theta (as a 2-category with points, paths, and 2-paths) "
             "to the 2-category of such spans."),
            ("This formalization gives SAVGS a precise mathematical type that the "
             "informal stratified system lacks. It also enables the systematic derivation "
             "of transition rules between strata via the boundary's universal property. "
             "Upstream fixes required: Audit A's algorithmic-rate-distortion framework "
             "(so the stratum objects have an information-theoretic semantics) and Audit "
             "A's optic-category unification (so the boundary is a span of optics, not just "
             "of plain categories). Downstream claim underwritten: Claim A (local transport "
             "law) and Claim B (holonomy law) of the falsification hierarchy, both within "
             "a single stratum. The inter-stratum transition is itself testable as part "
             "of Claim D (repeated-loop fatigue)."),
        ]
    ))

    story.extend(section(
        "6.2 Viability-weighted curvature derived from algorithmic rate-distortion",
        [
            ("Audit B's viability-weighted curvature kappa_alpha is derived from "
             "algorithmic rate-distortion theory rather than imposed by definition. Take "
             "the viability function h_alpha to be a Bregman divergence from the optimal "
             "policy p_star in the dual-affine coordinates of the exponential family: "
             "h_alpha(p) = D_phi(p, p_star), where phi is the cumulant-generating function. "
             "Then D_p h_alpha(F(u, v)) is the second-order predictive-information loss, "
             "and the positivity part [-.]_+ is the irreducible loss after the optimal "
             "repair. The kappa_alpha of Audit B is then exactly the algorithmic-rate-"
             "distortion-theoretic quantity: the worst fractional loss of viability margin "
             "per unit oriented environmental-loop area equals the worst fractional "
             "increase in the algorithmic rate-distortion function per unit loop area."),
            ("This derivation closes Audit A's Upgrade 1 (algorithmic rate-distortion "
             "replaces the ensemble-average R(D)) and Audit B's kappa_alpha definition. "
             "Upstream fixes required: Audit A's R(D)-versus-K(x) type fix (so the "
             "single-string algorithmic rate-distortion function is the right object) "
             "and Audit A's Bregman-divergence Noether correspondence (so the viability "
             "function is G-invariant under the connection's gauge transformations). "
             "Downstream claim underwritten: Claim C (viability relevance) of the "
             "falsification hierarchy. The kappa_V provides an out-of-sample predictive "
             "gain over raw Fisher displacement or exposure-only baselines precisely "
             "because it is the algorithmic-rate-distortion quantity, not a geometric "
             "imposition."),
        ]
    ))

    story.extend(section(
        "6.3 Intervention-based autopoiesis closure test via the RAF catalytic subgraph",
        [
            ("Audit B's intervention-based closure test (Section 7.2) is formalized via "
             "the RAF catalytic subgraph. A component m_j is causally internal to "
             "organizational closure if and only if its intervention (setting its internal "
             "repair flux to zero, keeping external energy and raw-material supply "
             "unchanged) disrupts a positive catalytic flux in the RAF formalism. "
             "Specifically: let the RAF be (X, F, R, kappa) with catalytic function kappa: "
             "R -> X; let the maintenance graph Gamma = (M, R, E) of Audit B have edges "
             "(m, r) in E if and only if kappa(r) = m (component m is regenerated by "
             "reaction r); then m_j is causally internal iff there exists r in R with "
             "kappa(r) = m_j such that the catalytic flux through r is positive, and "
             "intervening on m_j (zeroing its repair flux) reduces this catalytic flux "
             "below threshold."),
            ("This formalization gives the closure test a precise mathematical type that "
             "Audit B's informal protocol lacks. It also connects to Audit A's algorithmic-"
             "rate-distortion framework: the catalytic flux through r is the rate at which "
             "the RAF is producing the description of m_j; zeroing the repair flux is "
             "the intervention; the disruption is the negative impact on the algorithmic "
             "rate-distortion function. Upstream fixes required: Audit A's 4-species-"
             "register specification (so the RAF formalism has a concrete substrate) and "
             "Audit A's R(D)-versus-K(x) type fix (so the catalytic flux has the right "
             "type). Downstream claim underwritten: Claim E (autopoietic closure)."),
        ]
    ))

    story.extend(section(
        "6.4 Commuting control specified via the CO(2) commutator structure",
        [
            ("Audit B's commuting control (Section 9.3) is specified via the CO(2) "
             "commutator structure. The structure group is CO(2) = R+ x O(2); its Lie "
             "algebra decomposes as the direct sum of the dilatation generator (central, "
             "scalar multiples of the identity) and the rotation generator (antisymmetric "
             "2x2 matrices). Two perturbations commute if their rotation components are "
             "parallel (or both zero) and their dilatation components are arbitrary. The "
             "commuting-control experiment is therefore: choose one perturbation direction "
             "with a pure dilatation component (e.g., a uniform rescaling of the policy "
             "probabilities, which corresponds to a central CO(2) element) and another "
             "with the same dilatation but a non-parallel rotation component (which "
             "corresponds to a non-central CO(2) element)."),
            ("The predicted holonomy should be approximately zero for the parallel case "
             "(both perturbations in the same CO(2) coset, hence commuting) and non-zero "
             "for the non-parallel case. This sharpens Audit B's informal commuting control "
             "into a precise experimental design. It also gives Claim F (structure-group "
             "correction) its experimental specification. Upstream fixes required: Audit "
             "A's structure-group correction (CO(2) not GL(2)) and Audit B's logit gauge "
             "fix (square-root embedding, so the CO(2) action is explicit). Downstream "
             "claim underwritten: Claim F. Failure of the CO(2) commuting-control "
             "prediction would suggest the effective structure group is even smaller than "
             "CO(2), or that the gauge is misidentified."),
        ]
    ))

    story.extend(section(
        "6.5 Empirical holonomy statistic with non-parametric bootstrap",
        [
            ("Audit B's empirical holonomy statistic T = ||H_corr - H_geo||_F / "
             "sigma_total is augmented with a non-parametric bootstrap component in "
             "sigma_total. The hierarchical bootstrap (Audit B's proposal) handles "
             "between-trial variance but underestimates the heavy-tailed disturbances "
             "that the discrete-grid stochasticity can produce. The non-parametric "
             "bootstrap resamples the within-trial trajectory with replacement, giving "
             "a robust estimate of the within-trial variance. The combined sigma_total "
             "is the root-sum-square of the hierarchical and non-parametric components, "
             "with a Hartigan correction for small-sample bias."),
            ("This augmentation closes a real gap in Audit B's protocol. Upstream fixes "
             "required: Audit A's BA-operator Frechet-differentiability gap (so the "
             "boundary case where some policy probabilities are zero is handled by the "
             "bootstrap rather than by an invalid smoothness assumption). Downstream claim "
             "underwritten: Claim B (holonomy law). The discrepancy statistic T is the "
             "primary test of the holonomy law; without the non-parametric bootstrap, "
             "small-sample heavy-tailed disturbances could produce false positives or "
             "false negatives."),
        ]
    ))

    story.append(PageBreak())

    # =============================================================
    # Part VII — Unified Falsification Hierarchy
    # =============================================================
    story.append(part_divider(
        "PART VII",
        "Unified Falsification Hierarchy",
        "The joint framework is split into seven independently falsifiable claims. "
        "The first five extend Audit B's Claims A through E with upstream-fix "
        "specifications. The last two (F and G) are new, drawn from Audit A's "
        "structure-group correction and rate-distortion type fix."
    ))

    # Build a table of claims
    claims_data = [
        [Paragraph("Claim", style_table_head),
         Paragraph("Statement", style_table_head),
         Paragraph("Falsified if", style_table_head),
         Paragraph("Required upstream fix", style_table_head)],
        [Paragraph("A", style_table_cell),
         Paragraph("Open-edge policy changes agree with Fisher-minimal constraint-preserving "
                   "transport (single-stratum).", style_table_cell),
         Paragraph("Another preregistered transport model consistently predicts held-out edge "
                   "updates better.", style_table_cell),
         Paragraph("Algorithmic-rate-distortion framing (A-Upg-1); BA Frechet fix (A-Upg-2).", style_table_cell)],
        [Paragraph("B", style_table_cell),
         Paragraph("Held-out loop drift agrees with ordered geometric transport, shows "
                   "orientation reversal, area scaling, and bootstrap-valid uncertainty.", style_table_cell),
         Paragraph("Corrected loop drift remains O(epsilon), fails orientation reversal, or "
                   "lies outside bootstrap predictive uncertainty.", style_table_cell),
         Paragraph("Non-parametric bootstrap (joint Upg-6.5); BA Frechet fix (A-Upg-2).", style_table_cell)],
        [Paragraph("C", style_table_cell),
         Paragraph("Contraction of holonomy with viability gradients predicts margin erosion "
                   "better than raw Fisher displacement or exposure-only baselines.", style_table_cell),
         Paragraph("kappa_V provides no out-of-sample predictive gain.", style_table_cell),
         Paragraph("Algorithmic-rate-distortion derivation of kappa_alpha (joint Upg-6.2); "
                   "Bregman-divergence Noether (A-Upg-4).", style_table_cell)],
        [Paragraph("D", style_table_cell),
         Paragraph("Repeated loops accumulate viability loss according to ordered local "
                   "holonomy bounds (within-stratum).", style_table_cell),
         Paragraph("Failure probability is explained entirely by cumulative resource "
                   "expenditure, irrespective of loop orientation and order.", style_table_cell),
         Paragraph("2-categorical span for stratification (joint Upg-6.1).", style_table_cell)],
        [Paragraph("E", style_table_cell),
         Paragraph("Internal maintenance interventions produce the causal dependencies "
                   "predicted by the RAF-formalized maintenance graph Gamma.", style_table_cell),
         Paragraph("Indispensable modules are effectively restored by hidden external "
                   "mechanisms, or knockout effects do not follow the closure graph.", style_table_cell),
         Paragraph("RAF catalytic subgraph closure test (joint Upg-6.3); 4-species register "
                   "specification (A-Upg-3).", style_table_cell)],
        [Paragraph("F", style_table_cell),
         Paragraph("Commuting-control experiment via CO(2) commutator structure: parallel-"
                   "rotation perturbations produce zero leading holonomy; non-parallel "
                   "rotations produce non-zero leading holonomy.", style_table_cell),
         Paragraph("Both perturbations produce equal leading holonomy, or non-parallel "
                   "rotations produce zero leading holonomy, or parallel rotations produce "
                   "non-zero leading holonomy.", style_table_cell),
         Paragraph("CO(2) structure-group correction (joint defect 2.1); logit gauge fix "
                   "via square-root embedding (B-Upg-3.1).", style_table_cell)],
        [Paragraph("G", style_table_cell),
         Paragraph("Algorithmic-rate-distortion-derived kappa_alpha predicts held-out "
                   "margin erosion better than an ensemble-average-R(D)-derived alternative "
                   "under non-ergodic conditions.", style_table_cell),
         Paragraph("The ensemble-average alternative matches or outperforms the "
                   "algorithmic version under non-ergodic conditions.", style_table_cell),
         Paragraph("R(D) versus K(x) type fix (A-Upg-1); CPTP-channel resolution of "
                   "ergodicity contradiction (A-Upg-3).", style_table_cell)],
    ]
    col_widths = [content_w * 0.07, content_w * 0.34, content_w * 0.30, content_w * 0.29]
    claims_tbl = Table(claims_data, colWidths=col_widths, repeatRows=1)
    claims_tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C_TABLE_HEAD),
        ('TEXTCOLOR', (0,0), (-1,0), HexColor('#FFFFFF')),
        ('FONTNAME', (0,0), (-1,0), 'NotoSerifSC-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9.5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor('#FFFFFF'), C_TABLE_ALT]),
        ('GRID', (0,0), (-1,-1), 0.4, HexColor('#CBD5E1')),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(claims_tbl)
    story.append(Spacer(1, 12))

    story.extend(section(
        "7.1 Why seven claims, not five",
        [
            ("Audit B's five claims cover the local transport, the holonomy law, the "
             "viability relevance, the repeated-loop fatigue, and the autopoietic closure. "
             "These are the testable consequences of the SAVGS construction itself. The "
             "two additional claims (F and G) test the upstream fixes that SAVGS depends on. "
             "Without testing these, SAVGS could pass its own tests while being built on "
             "wrong foundations: the structure group could be GL(2) instead of CO(2), or "
             "the rate-distortion framework could be the ensemble-average R(D) instead of "
             "the algorithmic one, and SAVGS would still appear to work because both "
             "errors happen to compensate at the SAVGS level."),
            ("Concretely: if the structure group is misidentified as GL(2), the commuting-"
             "control experiment would use the wrong commutator structure, and might "
             "appear to pass even though the underlying gauge is wrong. If the rate-"
             "distortion framework is the ensemble-average R(D) rather than the "
             "algorithmic one, the kappa_alpha derivation would still produce a number, "
             "but it would not be the algorithmic-rate-distortion quantity, and its "
             "predictive gain might be coincidental. The two additional claims make these "
             "upstream errors independently detectable."),
        ]
    ))

    story.extend(section(
        "7.2 Independence and joint testability",
        [
            ("The seven claims are independent: each can fail without the others failing. "
             "If Claim A fails (local transport law is wrong) but Claims B through G pass, "
             "the framework's local transport model is wrong but its global structure is "
             "right. If Claim F fails (the CO(2) commuting-control prediction is wrong), "
             "the gauge is misidentified even if the holonomy law (Claim B) happens to "
             "hold. This modular structure ensures that failure of the grand "
             "interpretation does not obscure which mathematical component failed."),
            ("The joint testability is a feature: the seven claims can be tested in a "
             "single experimental sequence using the same agent and the same "
             "environmental manifold, because they probe different aspects of the same "
             "system. The recommended experimental order is: (1) Claims F and G first "
             "(they test the foundations and are cheap); (2) Claims A and B next (they "
             "test the local transport and holonomy, which are the basis for everything "
             "else); (3) Claims C and D (they test the viability relevance and fatigue); "
             "(4) Claim E last (it tests the autopoietic closure and requires the longest "
             "experimental runs)."),
        ]
    ))

    story.append(PageBreak())

    # =============================================================
    # Part VIII — Final Verdict
    # =============================================================
    story.append(part_divider(
        "PART VIII",
        "Final Verdict",
        "The verdict of the joint assessment, sharpened by the synthesis of both audits."
    ))

    verdict_paras = [
        ("The project should not claim that survival is equivalent to bounded information-"
         "geometric curvature. This is the central finding of Audit B and is adopted without "
         "qualification. The equivalence is not merely tautological (as DeepSeek concedes); "
         "it is false in general. A flat connection can transport an agent directly out of "
         "its viable set; a highly curved connection can remain entirely inside a large "
         "viable region; endpoint holonomy does not guarantee pathwise viability; and a "
         "norm bound on curvature is sufficient only after combining it with loop area, "
         "viability margin, transport regularity, and disturbance bounds."),

        ("The project should not claim that the multi-arc chain from RAF through the n=3 "
         "Fisher-Rao construction is a rigorous cross-domain unification. This is the "
         "central finding of Audit A and is adopted without qualification. Each layer is "
         "mathematically real, but each inter-layer bridge is rhetorical rather than a "
         "mapping. The rate-distortion arc confuses R(D) with K(x); the consciousness arc "
         "presupposes non-ergodicity while the RAF arc presupposes ergodicity; the fractal "
         "arc conflates Hutchinson fixed points with Blahut-Arimoto fixed points; the "
         "Noether arc fails to verify the Lagrangian's G-invariance; and the perturbation "
         "arc applies a Frechet-differentiability-expansion outside its domain of validity."),

        ("The rigorous result, after both audits' corrections are applied, is narrower "
         "and stronger than either DeepSeek's own self-assessment or either audit alone "
         "proposed. On smooth constant-active-set strata of an experimentally "
         "parameterized control manifold, the Fisher-minimal constraint-preserving "
         "adaptation of an open CPTP channel defines a stratified connection whose "
         "viability-weighted curvature (derived from algorithmic rate-distortion theory) "
         "predicts the leading-order policy hysteresis generated by closed environmental "
         "perturbations. Whether that hysteresis is fatal depends on the viability margins, "
         "the along-path disturbances, the resource costs, and the regeneration of the "
         "internal maintenance machinery (formalized via the RAF catalytic subgraph)."),

        ("The decisive empirical test is therefore not merely whether empirical and "
         "theoretical holonomy agree. It is whether independently estimated, gauge-"
         "invariant (CO(2)-corrected), viability-weighted holonomy predicts held-out "
         "margin erosion, orientation reversal, area scaling, repeated-loop failure "
         "after ordinary energetic depletion has been controlled, and whether the "
         "structure-group correction (CO(2) not GL(2)) and the rate-distortion type fix "
         "(algorithmic not ensemble-average) survive their respective independent "
         "commuting-control and predictive-performance tests. The seven claims of the "
         "Part VII hierarchy operationalize these tests."),

        ("If those predictions fail, the geometric mechanism fails. If they hold, and if "
         "the agent demonstrably regenerates its own maintenance machinery under the RAF-"
         "formalized intervention-based closure test, the framework would advance from "
         "metaphorical algorithmic life to a genuine experimental theory of path-dependent "
         "self-maintenance. This is the strongest defensible thesis available to the "
         "framework after both audits' corrections are applied. It is mathematically "
         "meaningful, algorithmically implementable, and experimentally falsifiable. "
         "It is also genuinely novel: the combination of stratified Fisher-minimal "
         "viability transport, viability-weighted algorithmic-rate-distortion-derived "
         "curvature, repeated-loop geometric adaptation fatigue, interventionally "
         "verified RAF-formalized endogenous maintenance closure, CO(2) structure-group "
         "specification, and algorithmic-rate-distortion type fix has not been proposed "
         "before in the literature known to either audit."),

        ("The recommended next iteration of the framework is to implement the seven "
         "upgrades of Part VI on the existing n=3 prototype, in the order: (1) "
         "structure-group correction to CO(2) (binding prerequisite for all subsequent "
         "work); (2) algorithmic-rate-distortion framework (binding prerequisite for the "
         "kappa_alpha derivation); (3) Bregman-divergence cost (binding prerequisite for "
         "the BA-operator Frechet fix); (4) SAVGS in 2-categorical span framework "
         "(formalizes the stratification); (5) intervention-based closure test via RAF "
         "catalytic subgraph (operationalizes autopoiesis); (6) commuting-control "
         "specification via CO(2) commutator (operationalizes the structure-group test); "
         "(7) non-parametric bootstrap augmentation (operationalizes the holonomy test). "
         "This sequence resolves the most defects with the smallest changes and produces "
         "a framework ready for experimental test."),
    ]
    for p in verdict_paras:
        story.append(Paragraph(p, style_body))

    # Closing highlighted block
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=1.2, color=C_ACCENT_JOINT, spaceBefore=2, spaceAfter=10))
    story.append(Paragraph(
        "Joint thesis (adopted from both audits, sharpened by synthesis):",
        style_h3_joint
    ))
    closing = (
        "Adaptive systems are endangered not merely by large environmental changes, "
        "but by noncommuting sequences of individually manageable changes whose induced "
        "policy holonomy is aligned with vulnerable self-maintenance directions, and "
        "whose cumulative effect is bounded by the algorithmic-rate-distortion-"
        "theoretic viability-weighted curvature on a CO(2)-structured stratified "
        "connection. The test of this thesis is whether the seven claims of Part VII "
        "survive independent experimental test."
    )
    story.append(Paragraph(closing, style_quote))

    # -----------------------------------------------------------------
    # Build
    # -----------------------------------------------------------------
    doc.build(story, onFirstPage=draw_cover, onLaterPages=noop)
    print(f"PDF generated: {out_path}")
    print(f"File size: {os.path.getsize(out_path)} bytes")


if __name__ == "__main__":
    build()
