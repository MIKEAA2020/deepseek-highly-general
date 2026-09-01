#!/usr/bin/env python3
"""
Joint Assessment of Three Second-Wave Audits of the v20 Manuscript.

Audits under assessment (external_audits/2nd wave/):
  A1 (GLM):      "glm audit highly general.txt" — line-level reading report (A-E sections)
  A2 (DeepSeek): "deepseek highly general audit.txt" — 33 flaws + 28 improvement items
  A3 (Editorial): "Line_Level_Review_Report.pdf" — 81 line-referenced findings, editorial verdict

This joint assessment:
  1. VERIFIES every audit claim against the manuscript (LaTeX source,
     compiled PDF, result JSONs, analysis scripts, render-level VLM checks).
  2. REFUTES / CORRECTS audit claims that fail verification.
  3. STRENGTHENS and COMPLETES weaker audit suggestions.
  4. Produces a unified, prioritized, implementation-ready repair plan.

Deliverable: /home/z/my-project/download/joint_assessment_2nd_wave.pdf
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether, Flowable, HRFlowable,
)

# -----------------------------------------------------------------------------
# Fonts
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
# Palette — three-tone: one accent per audit + joint slate
#   teal  = A1 (GLM)      plum = A2 (DeepSeek)     amber = A3 (Editorial AU)
#   slate = joint synthesis / this assessment
# -----------------------------------------------------------------------------
C_PRIMARY    = HexColor('#1F2937')
C_A1         = HexColor('#0F766E')   # teal    — GLM audit
C_A2         = HexColor('#7C3AED')   # plum    — DeepSeek audit
C_A3         = HexColor('#B45309')   # amber   — Line-Level Review (Editorial AU)
C_JOINT      = HexColor('#334155')   # slate   — joint verdicts
C_MUTED      = HexColor('#6B7280')
C_QUOTE      = HexColor('#374151')
C_QUOTE_BG   = HexColor('#F3F4F6')
C_VERIFIED   = HexColor('#166534')   # deep green — confirmed
C_REFUTED    = HexColor('#991B1B')   # deep red   — audit error
C_CORR       = HexColor('#92400E')   # deep amber — corrected/nuanced
C_TABLE_HEAD = HexColor('#334155')
C_TABLE_ALT  = HexColor('#F8FAFC')
C_COVER_BG   = HexColor('#0F172A')
C_COVER_FG   = HexColor('#F8FAFC')

# -----------------------------------------------------------------------------
# Styles
# -----------------------------------------------------------------------------
styles = getSampleStyleSheet()

style_cover_title = ParagraphStyle('CoverTitle', parent=styles['Title'],
    fontName='NotoSerifSC-Bold', fontSize=26, leading=32,
    textColor=C_COVER_FG, alignment=TA_LEFT, spaceAfter=8)
style_h1 = ParagraphStyle('H1', parent=styles['Heading1'],
    fontName='NotoSerifSC-Bold', fontSize=19, leading=25,
    textColor=C_JOINT, alignment=TA_LEFT, spaceBefore=18, spaceAfter=8)
style_h1a1 = ParagraphStyle('H1a1', parent=style_h1, textColor=C_A1)
style_h1a2 = ParagraphStyle('H1a2', parent=style_h1, textColor=C_A2)
style_h1a3 = ParagraphStyle('H1a3', parent=style_h1, textColor=C_A3)
style_h2 = ParagraphStyle('H2', parent=styles['Heading2'],
    fontName='NotoSerifSC-Bold', fontSize=13.5, leading=19,
    textColor=C_PRIMARY, alignment=TA_LEFT, spaceBefore=13, spaceAfter=5)
style_h3 = ParagraphStyle('H3', parent=styles['Heading3'],
    fontName='NotoSerifSC-Bold', fontSize=11, leading=15,
    textColor=C_JOINT, alignment=TA_LEFT, spaceBefore=9, spaceAfter=4)
style_body = ParagraphStyle('Body', parent=styles['Normal'],
    fontName='NotoSerifSC', fontSize=9.6, leading=14.2,
    textColor=C_PRIMARY, alignment=TA_JUSTIFY, spaceBefore=2, spaceAfter=6)
style_body_first = ParagraphStyle('BodyFirst', parent=style_body, spaceBefore=0)
style_quote = ParagraphStyle('Quote', parent=styles['Normal'],
    fontName='NotoSerifSC', fontSize=9.2, leading=13.5,
    textColor=C_QUOTE, alignment=TA_LEFT,
    leftIndent=14, rightIndent=10, spaceBefore=4, spaceAfter=6,
    backColor=C_QUOTE_BG, borderPadding=8)
style_meta = ParagraphStyle('Meta', parent=styles['Normal'],
    fontName='NotoSerifSC', fontSize=8.6, leading=11.5,
    textColor=C_MUTED, alignment=TA_LEFT)
style_part_label = ParagraphStyle('PartLabel', parent=styles['Normal'],
    fontName='NotoSerifSC-Bold', fontSize=9.5, leading=13,
    textColor=C_MUTED, alignment=TA_LEFT, spaceBefore=0, spaceAfter=2)
style_tc = ParagraphStyle('TC', parent=styles['Normal'],
    fontName='NotoSerifSC', fontSize=8.3, leading=11.3,
    textColor=C_PRIMARY, alignment=TA_LEFT)
style_tcb = ParagraphStyle('TCB', parent=style_tc, fontName='NotoSerifSC-Bold')
style_th = ParagraphStyle('TH', parent=styles['Normal'],
    fontName='NotoSerifSC-Bold', fontSize=8.6, leading=11.5,
    textColor=HexColor('#FFFFFF'), alignment=TA_LEFT)
style_verd_v = ParagraphStyle('VerdV', parent=style_tc,
    textColor=C_VERIFIED, fontName='NotoSerifSC-Bold')
style_verd_r = ParagraphStyle('VerdR', parent=style_tc,
    textColor=C_REFUTED, fontName='NotoSerifSC-Bold')
style_verd_c = ParagraphStyle('VerdC', parent=style_tc,
    textColor=C_CORR, fontName='NotoSerifSC-Bold')

VERIF = 'VERIFIED'; REFUT = 'REFUTED'; CORR = 'CORRECTED'

# -----------------------------------------------------------------------------
# Cover
# -----------------------------------------------------------------------------
def draw_cover(canv, doc):
    page_w, page_h = A4
    canv.saveState()
    canv.setFillColor(C_COVER_BG)
    canv.rect(0, 0, page_w, page_h, fill=1, stroke=0)

    # triple accent rules
    y0 = page_h - 3.9*cm
    canv.setStrokeColor(C_A1); canv.setLineWidth(3)
    canv.line(2.2*cm, y0, 4.8*cm, y0)
    canv.setStrokeColor(C_A2); canv.setLineWidth(3)
    canv.line(5.0*cm, y0, 7.3*cm, y0)
    canv.setStrokeColor(C_A3); canv.setLineWidth(3)
    canv.line(7.5*cm, y0, 10.4*cm, y0)

    canv.setFillColor(C_COVER_FG)
    canv.setFont('NotoSerifSC-Bold', 25)
    canv.drawString(2.2*cm, page_h - 5.0*cm, "Joint Assessment of Three")
    canv.drawString(2.2*cm, page_h - 6.1*cm, "Second-Wave Audits")
    canv.drawString(2.2*cm, page_h - 7.2*cm, "of the v20 Manuscript")
    canv.setFont('NotoSerifSC', 13)
    canv.setFillColor(HexColor('#94A3B8'))
    canv.drawString(2.2*cm, page_h - 8.1*cm, "Full claim-level verification · audit errors refuted · strengthened repair plan")

    canv.setStrokeColor(HexColor('#334155')); canv.setLineWidth(0.5)
    canv.line(2.2*cm, page_h - 9.2*cm, page_w - 2.2*cm, page_h - 9.2*cm)

    canv.setFillColor(HexColor('#CBD5E1'))
    canv.setFont('NotoSerifSC', 9.5)
    lines = [
        "Three external line-level audits of the 131-page v20 manuscript",
        "\u201cA Categorical Viability-Weighted Curvature Framework\u201d were read",
        "twice at granular level, then EVERY material claim was independently",
        "verified against the LaTeX source, the compiled PDF, the deposited",
        "result files, and the analysis scripts, with render-level (pixel)",
        "verification of every typesetting claim.",
        "",
        "Outcome: the audits are substantially accurate. 90+ findings are",
        "confirmed with line-level evidence, including the clipped step",
        "labels of the Definition 3.18 protocol, the six conflicting network",
        "counts, the iML1515 \u22120.008 / \u22120.018 inconsistency (\u22120.018 is",
        "correct), the 12 never-cited references with 6 false \u201cCited in \u00a7X\u201d",
        "annotations, the [\u003f] broken citation key, and the documented",
        "definition-shopping and label-leakage passages.",
        "",
        "Four audit claims FAIL verification and are refuted or corrected,",
        "including one major diagnostic error (the \u00a718.4 \u201ctext vs code\u201d",
        "claim, replaced here by the sharper protocol-degeneracy finding)",
        "and one extraction artifact misreported as a defect (the \u201cstray Q\u201d",
        "is a correctly rendered \u220f product symbol).",
        "",
        "The three audits are complementary: the Editorial line-level review",
        "supplies the de-construction strategy, the DeepSeek checklist supplies",
        "the tactical fixes, and the GLM report supplies the structural",
        "diagnosis of why in-place repair keeps failing. This assessment",
        "merges them into one prioritized, implementation-ready repair plan",
        "with P0\u2013P5 tiers, and completes the weaker suggestions before",
        "implementation.",
    ]
    y = page_h - 10.4*cm
    for ln in lines:
        canv.drawString(2.2*cm, y, ln)
        y -= 12.6

    canv.setStrokeColor(C_JOINT); canv.setLineWidth(1)
    canv.line(2.2*cm, 3.3*cm, 6.6*cm, 3.3*cm)
    canv.setFont('NotoSerifSC-Bold', 10)
    canv.setFillColor(HexColor('#F8FAFC'))
    canv.drawString(2.2*cm, 2.85*cm, "Z.ai — Joint Assessment (2nd wave)")
    canv.setFont('NotoSerifSC', 8.5)
    canv.setFillColor(HexColor('#94A3B8'))
    canv.drawString(2.2*cm, 2.35*cm, "Sources: external_audits/2nd wave/ — glm audit · deepseek audit · Line_Level_Review_Report.pdf")
    canv.drawString(2.2*cm, 1.95*cm, "Evidence base: scripts/journal_manuscript.tex (10,670 lines) · download/journal_manuscript.pdf (131 pp) · 8 result JSONs")
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
        Paragraph(label, style_part_label),
        Paragraph(title, style_h1),
        HRFlowable(width="100%", thickness=1.2, color=C_JOINT, spaceBefore=2, spaceAfter=10),
        Paragraph(blurb, style_body),
        Spacer(1, 6),
    ])


def ledger_table(rows, col_fracs, header):
    """rows: list of (finding, source, verdict, evidence) tuples."""
    page_w, page_h = A4
    cw = page_w - 4.4*cm
    widths = [cw*f for f in col_fracs]
    data = [[Paragraph(h, style_th) for h in header]]
    for finding, src, verdict, ev in rows:
        vs = style_verd_v if verdict == VERIF else (style_verd_r if verdict == REFUT else style_verd_c)
        data.append([
            Paragraph(finding, style_tc),
            Paragraph(src, style_tc),
            Paragraph(verdict, vs),
            Paragraph(ev, style_tc),
        ])
    t = Table(data, colWidths=widths, repeatRows=1, hAlign='LEFT')
    st = [
        ('BACKGROUND', (0, 0), (-1, 0), C_TABLE_HEAD),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.4, HexColor('#D1D5DB')),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            st.append(('BACKGROUND', (0, i), (-1, i), C_TABLE_ALT))
    t.setStyle(TableStyle(st))
    return t


def simple_table(header, rows, col_fracs, head_color=C_TABLE_HEAD):
    page_w, page_h = A4
    cw = page_w - 4.4*cm
    widths = [cw*f for f in col_fracs]
    data = [[Paragraph(h, style_th) for h in header]]
    for r in rows:
        data.append([Paragraph(c, style_tc) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1, hAlign='LEFT')
    st = [
        ('BACKGROUND', (0, 0), (-1, 0), head_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.4, HexColor('#D1D5DB')),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            st.append(('BACKGROUND', (0, i), (-1, i), C_TABLE_ALT))
    t.setStyle(TableStyle(st))
    return t


def kv_block(title, pairs, accent=C_JOINT):
    flow = [Paragraph(title, style_h3)]
    for k, v in pairs:
        flow.append(Paragraph(f'<b>{k}</b> — {v}', style_body))
    return flow


# =============================================================================
# CONTENT
# =============================================================================
def build_content(story):
    W = None  # placeholder

    # ===================== EXECUTIVE SUMMARY =====================
    story.append(Paragraph("Executive Summary", style_h1))
    story.append(HRFlowable(width="100%", thickness=1.2, color=C_JOINT, spaceBefore=2, spaceAfter=10))

    story.append(Paragraph(
        "Three second-wave audits of the 131-page v20 manuscript \u201cA Categorical "
        "Viability-Weighted Curvature Framework: From Autopoietic Sets to Non-Abelian "
        "Holonomy\u201d were read in full, twice, at line level: the GLM line-level reading "
        "report (52 lines, sections A\u2013E), the DeepSeek \u201cFlaws and Inconsistencies\u201d "
        "audit (366 lines, 33 numbered flaws plus 28 improvement items), and the "
        "\u201cLine-Level Review Report\u201d from an Editorial Assessment Unit (19 pages, "
        "81 consolidated line-referenced findings in five categories, ending in an editorial "
        "verdict of \u201cnot publishable, deconstruct into three papers\u201d). In accordance "
        "with the review instruction, no claim from any audit was taken at face value: every "
        "material claim was re-derived against the manuscript\u2019s LaTeX source (10,670 lines), "
        "the compiled PDF (131 pages), the deposited result JSONs, and the analysis scripts, "
        "with render-level visual verification of all typesetting claims and code-level reading "
        "of the analysis implementations.", style_body_first))

    story.append(Paragraph(
        "The headline outcome is that the three audits are substantially accurate and "
        "mutually reinforcing. More than ninety distinct findings are confirmed at line "
        "level, including every one of the Editorial report\u2019s Critical items: the Definition "
        "3.18 protocol step labels are physically clipped off the rendered page (render-"
        "verified: step numbers missing, first words cut mid-word at x-coordinates below "
        "zero); the broken citation marker \u201c[\u003f]\u201d is a real missing bibliography key "
        "(<font face='DejaVuSansMono'>orth2011comprehensive</font> is cited at source line 1299 "
        "but never defined); the network count is stated six different ways (2 / 4-with-five-"
        "listed / 2 / 4 / 10, against roughly thirteen networks actually present); the "
        "limitations section denies the 52/52 = 100% verdict the body headlines; the "
        "manuscript documents its own definition-shopping and label leakage in its own "
        "words; and the bibliography contains twelve never-cited entries of which six carry "
        "false \u201cCited in \u00a7X\u201d annotations \u2014 including the single most important "
        "prior-art attribution, Vereshchagin\u2013Vit\u00e1nyi at Definition 4.1.", style_body))

    story.append(Paragraph(
        "Verification also produced results the audits did not have. The iML1515 Pearson "
        "discrepancy is resolved against ground truth: the deposited result file gives "
        "r = \u22120.0178, so \u22120.018 (E16 table, E18 re-run table) is correct and \u22120.008 "
        "(three narrative sites) is wrong, with the derived stability gap 0.103 correct and "
        "0.093 wrong. A new count mismatch was found (the manuscript\u2019s nprod \u2265 5 stratum "
        "is stated as 9/10 but the deposited CSV gives 10/11). Four audit claims failed "
        "verification outright and are refuted or corrected here, most importantly the "
        "Editorial report\u2019s \u00a718.4 \u201ctext vs code\u201d finding: the code does knock out all "
        "producers exactly as written, but the written protocol is itself degenerate \u2014 "
        "under an all-producers knockout the \u201cdrop\u201d is structurally trivial and the "
        "\u201crecovery\u201d re-solves the identical baseline FBA, so the verdict collapses to "
        "\u201cbaseline production flux exceeds 10\u207b\u2076\u201d. That corrected diagnosis is sharper "
        "and more damaging than the audit\u2019s version, and it generalizes to the E2 "
        "dependency-ratio studies. The DeepSeek audit\u2019s \u201cstray Q characters\u201d item is an "
        "extraction artifact, not a defect: pixel-level inspection shows a correctly "
        "rendered product symbol \u220f.", style_body))

    story.append(Paragraph(
        "The joint verdict merges the three audits\u2019 complementary strengths. The Editorial "
        "line-level review is methodologically the strongest (it is the only audit that "
        "explicitly excluded extraction artifacts after pixel verification, and its "
        "strategic recommendation \u2014 deconstruct into three papers \u2014 is sound). The "
        "DeepSeek checklist is the most complete tactical inventory (abstract staleness, "
        "conjecture-section redundancy, Table 4, SAVGS tuple, Figure 7 caption, Theorem 4.11 "
        "computability, Theorem 8.2 \u201cunconditional\u201d). The GLM report is the best structural "
        "diagnosis (three objects named \u03ba_V that never touch each other; the empirical "
        "program validates the FBA statistic while the theory concerns the geometric object). "
        "Part VI merges all of this into a single prioritized P0\u2013P5 repair plan with concrete "
        "fixes, severities, and effort estimates, ready for implementation.", style_body))

    # ===================== PART I: THE THREE AUDITS =====================
    story.append(part_divider("PART I", "The Three Audits and the Verification Method",
        "What each audit actually contains, how its claims were checked, and what "
        "evidence base the verification used. The verification method matters: five "
        "independent evidence layers were consulted, and two classes of audit error "
        "(extraction artifacts and code-reading inference errors) could only be caught "
        "by consulting the right layer."))

    story.append(Paragraph("1.1 Audit identities", style_h2))
    story.append(Paragraph(
        "Audit A1 (GLM) is a compact line-level reading report structured in five lettered "
        "sections: manuscript identity (131 pp, ~71k words, v2\u2192v3 delta table), structural "
        "delta versus the 90-page v2, citation forensics (bracket-level counts of body "
        "citations versus bibliography annotations), the new empirical core E24\u2013E27 with a "
        "positive verdict, and persistent structural observations closing with five "
        "one-line summary statements. Its distinguishing strength is citation forensics and "
        "the \u201cthree different objects named \u03ba_V\u201d structural observation.", style_body))
    story.append(Paragraph(
        "Audit A2 (DeepSeek) is the longest checklist: eight sections of numbered flaws "
        "(33 items) covering global/abstract inconsistencies, definitional flaws, theorem-"
        "level issues, numerical inconsistencies, biological verdict inconsistencies, "
        "elevation-study versioning problems, referencing issues, and typographical items, "
        "followed by 28 mirrored \u201copportunity\u201d items and a seven-point highest-value "
        "summary. Its distinguishing strength is completeness of the tactical layer \u2014 it is "
        "the only audit that flags the abstract\u2019s stale \u201cconjectural upper envelope\u201d "
        "wording against the smooth-envelope theorem that closes the conjecture, the "
        "redundant conjecture-closure lists in \u00a721.5/\u00a721.6, the outdated Table 4, and the "
        "E25 +0.191/+0.187 reconciliation gap.", style_body))
    story.append(Paragraph(
        "Audit A3 (Editorial Assessment Unit) is the most systematic: a 19-page report with "
        "an executive summary, a scope/method statement, five finding categories (A textual "
        "and typesetting, B mathematical flaws, C internal inconsistencies, D provenance and "
        "integrity, E methodological weaknesses), a six-item prioritized de-construction "
        "plan, a consolidated ledger of 81 line-referenced findings graded Critical / Major / "
        "Moderate / Minor, and an editorial verdict. It explicitly distinguishes extraction "
        "artifacts from render-level defects and states that suspect passages were verified "
        "at the pixel level before a finding was recorded.", style_body))

    story.append(Paragraph("1.2 Verification method (five evidence layers)", style_h2))
    story.append(Paragraph(
        "Each audit claim was checked against the layer appropriate to its type. "
        "Textual and typesetting claims were checked in the compiled PDF\u2019s text layer with "
        "span-level coordinates (PyMuPDF), and every clipping claim was additionally "
        "rendered at 4\u00d7 zoom and inspected visually (VLM) \u2014 the span x-coordinates "
        "confirm the clipping physically (lines beginning at x &lt; 0 for the Definition "
        "3.18 labels; cells ending mid-word for Table 6). Citation claims were checked by "
        "parsing all <font face='DejaVuSansMono'>\\cite{...}</font> keys and all "
        "<font face='DejaVuSansMono'>\\bibitem{...}</font> entries in the LaTeX source and "
        "computing the set difference \u2014 this simultaneously confirms the never-cited "
        "entries, the false annotations, and the broken key. Numeric claims were checked "
        "against the deposited result JSONs (E15, E16, dep-ratio, closure-test CSVs), which "
        "settles which of two conflicting in-text values is ground truth. Methodological "
        "claims about implementation were checked by reading the analysis scripts themselves "
        "(for example <font face='DejaVuSansMono'>autopoiesis_ijO1366.py</font> and "
        "<font face='DejaVuSansMono'>novelty_structural_benchmark_e14.py</font>). Provenance "
        "claims were checked by full-text counts in both source and PDF (commit hashes, "
        "\u201cthe user\u201d, \u201cQwen\u201d, patch-script names, folder paths).", style_body))
    story.append(Paragraph(
        "This layered method is what allows the joint assessment to do more than "
        "triangulate: where the audits agree, the agreement is now evidence-backed; where "
        "they diverge, the divergence is resolved against ground truth; and where an audit "
        "over-claims, the over-claim is refuted with the specific evidence layer that "
        "exposes it. Two classes of audit error were found only because the right layer was "
        "consulted: extraction artifacts (visible only in the text layer, not on the rendered "
        "page) and code-inference errors (an audit guessing what the implementation must "
        "have done, when the implementation is directly readable).", style_body))

    # ===================== PART II: VERIFICATION LEDGER =====================
    story.append(part_divider("PART II", "Verification Ledger — Claim by Claim",
        "Every material claim from the three audits, graded VERIFIED (confirmed with "
        "evidence), CORRECTED (right finding, wrong detail or scope), or REFUTED (the "
        "claim fails verification). Line numbers refer to the LaTeX source unless "
        "stated otherwise; PDF page numbers are given for render-level findings."))

    story.append(Paragraph("2.1 Category A — Textual and typesetting defects", style_h2))
    story.append(Paragraph(
        "This is the category where verification was most literal: the claims describe "
        "what is physically on the page. Every clipping claim in the Editorial report "
        "survived pixel-level verification, and the citation-coverage audit confirms the "
        "broken key and the false annotations with exact set arithmetic. One DeepSeek item "
        "in this category (the \u201cstray Q\u201d) is an extraction artifact and is refuted "
        "below in Part III.", style_body))

    rows_a = [
        ("Definition 3.18 step labels (ii)\u2013(v) clipped mid-word; step numbers missing", "A3 (Critical)", VERIF,
         "Render-verified at 4\u00d7: spans begin at x = \u22122.3 to \u22120.4 (off-page); \u201cDrift\u201d, \u201cRecovery\u201d, \u201cDownstream\u201d, \u201cRestoration\u201d absent from PDF text layer; source lines 1204\u20131221 contain full labels. VLM confirms visible text starts \u201cunder dynamics\u201d, \u201cabove threshold\u201d, \u201cnstream cascade\u201d, \u201ctoration control\u201d."),
        ("Broken citation \u201c[\u003f]\u201d at the essentiality-threshold sentence", "A1, A3 (Major)", VERIF,
         "Source line 1299 cites <font face='DejaVuSansMono'>orth2011comprehensive</font>; no such bibitem exists (54 bibitems checked). Renders as [\u003f]. Correct key: <font face='DejaVuSansMono'>orth2011</font> or <font face='DejaVuSansMono'>orth2011ijo1366</font>."),
        ("Table 6 \u201clikely missing term\u201d cells clipped (\u201cgrowt\u201d \u00d73, \u201cregulat\u201d \u00d71)", "A3 (Major)", VERIF,
         "PDF p.119: four cells end mid-word at column x \u2248 435 (cell text literally truncated; no hyphenation)."),
        ("\u201cv10 main definition, indicator-weighted\u201d version metadata in body text", "A3 (Critical)", VERIF,
         "Source lines 1283, 1316, and the v9/v10 promotion narrative at 7628\u20137641; also \u201c(v10, E18; v11, E19)\u201d style labels throughout \u00a719."),
        ("Cross-references to nonexistent \u00a71.4 (Introduction has no subsections)", "A3 (Moderate)", VERIF,
         "Source lines 9898 and 9994: \u201cthe operational \u00a71.4 form\u201d; Introduction subsection scan returns empty. Dangling pointer, twice."),
        ("Authorship statement cites \u201c\u00a77 research-integrity notes\u201d; \u00a77 is the composition-theorem section", "A3 (Major)", VERIF,
         "Source line 10307; section list confirms \u00a77 = \u201cThe Single Composition Theorem\u201d; no research-integrity notes exist anywhere."),
        ("iML1515 Pearson \u22120.018 vs \u22120.018 in tables but \u22120.008 in E18 narrative (gaps 0.103/0.093)", "A2 #15, A3 (Moderate)", VERIF,
         "Source: \u22120.018 at lines 7429, 7502, 7543; \u22120.008 at lines 1321, 7730, 7741. Ground truth (E16 JSON): \u22120.0178. So \u22120.018 is correct; three \u22120.008 sites are wrong; gap 0.103 correct, 0.093 wrong."),
        ("Glycogen phosphorylase labeled EC 2.7.4.1 = polyphosphate kinase\u2019s number, 6 lines from correct PPK use", "A3 (Moderate)", VERIF,
         "Source line 4770 (GLYP1/2 phosphorylase EC 2.7.4.1) vs 4776\u201377 (PPK1/2 kinase EC 2.7.4.1). Glycogen phosphorylase is EC 2.4.1.1. Same EC on two enzymes, confirmed."),
        ("M11 / ALT aspartate\u2013pyruvate transaminase EC 2.6.1.12 attribution dubious", "A3 (Moderate)", VERIF,
         "Source lines 4631, 4701, 4720, 4769. EC 2.6.1.12 is aspartate\u2013prephenate aminotransferase; the described reaction is not that entry. Fair finding."),
        ("iJO1366 WT biomass 15.444 h\u207b\u00b9 on 10 mmol glucose (\u224816\u00d7 biologically possible); glossed as \u201cdifferent stoichiometry\u201d", "A3 (Moderate)", VERIF,
         "Source lines 6872, 7346. iML1515 0.9259 h\u207b\u00b9 same medium. The gloss hides a biomass-units convention difference (mmol-biomass vs gDW-normalized); the relative-threshold logic papers over it unstated."),
        ("\u201conly 3 compute \u03ba_V from FBA: E10, E12, E15 and E16\u201d (four items after \u201c3\u201d)", "A3 (Minor)", VERIF,
         "Source lines 7658\u20137661, verbatim. Count/list mismatch."),
        ("Table 6 caption \u201cthe author\u2019s hypothesis\u201d vs consistent \u201cwe\u201d", "A3 (Minor)", VERIF, "Source line 9574."),
        ("Table 3 (n=4) stray \u201c+0.99958\u201d in the c_comm fit-metric column", "A3 (Minor)", VERIF,
         "Source line 3026: second R\u00b2 for the commutator fit rendered as \u201c+0.99958\u201d in the wrong column slot."),
        ("Stray \u201cQ\u201d characters before product bounds (LaTeX artifact)", "A2 #31", REFUT,
         "Render-verified: the glyph is a correctly drawn \u220f (product symbol) from the math font; \u201cQ\u201d appears only in the PDF text-extraction layer (missing ToUnicode mapping). Not a page defect. See Part III."),
    ]
    story.append(ledger_table(rows_a, [0.34, 0.10, 0.10, 0.46],
        ["Finding", "Audit", "Verdict", "Evidence / note"]))

    story.append(Paragraph("2.2 Category B — Mathematical flaws and proof gaps", style_h2))
    story.append(Paragraph(
        "The mathematical claims were verified by reading each statement and proof in the "
        "source and re-deriving the contested steps. Every load-bearing criticism in the "
        "Editorial report\u2019s Category B is confirmed as mathematics, not rhetoric: the "
        "C\u00b2 smoothness claims are false at the threshold locus, the uniform Lipschitz "
        "lemma\u2019s denominator bound vanishes exactly as the audit says, the parameter "
        "family is uncountable where the proof calls it discrete-enumerable, and Corollary "
        "4.14\u2019s closing substitution is dimensionally incoherent. The two DeepSeek "
        "algebra items split: the gauge-matching-condition criticism is fair, while the "
        "CPTP \u201cpk/2\u207f\u00b7P/k\u201d item is algebraically correct as written (DeepSeek itself "
        "graded it \u201cacceptable\u201d).", style_body))

    rows_b = [
        ("Definition 4.6/Prop 4.7: C\u00b2 claims false \u2014 [d\u2212D]\u00b2\u208a is C\u00b9 at d = D; positive part, sup, max do not preserve smoothness", "A3 (Major)", VERIF,
         "Source lines 1455\u20131461, 1480\u20131488. t \u21a6 [t\u2212D]\u00b2\u208a has second derivative 0 / 2 across the threshold \u2014 discontinuous at d = D. \u00a74.2\u2019s own Clarke machinery concedes non-smoothness three pages later. Confirmed as stated."),
        ("Lemma 4.10 uniform Lipschitz bound vacuous: lower bound 2\u207b\u1d38/\u03c4 \u00b7 e\u207b\u03b2\u00b7diam\u00b2/\u03c4 \u2192 0 as \u03c4 \u2192 0; \u03b2 unbounded", "A3 (Major)", VERIF,
         "Source lines 1550\u20131568: denominator lower bound quoted verbatim; family parameters (\u03c4,\u03b2 > 0) unbounded. Pointwise bound only; no uniform bound established."),
        ("Theorem 4.11 calls the family \u201cdiscrete-enumerable\u201d while Definition 4.9 indexes it by \u03c4, \u03b2 \u2208 \u211d\u208a (uncountable); upper-semicomputability of an uncountable supremum asserted", "A2 #8/10, A3 (Major)", VERIF,
         "Source lines 1526\u20131531 vs 1600\u20131602 (\u201cdiscrete-enumerable\u201d) and 1588\u20131596 (part e). Internal contradiction plus an unproven enumerability claim."),
        ("Remark 4.12 \u201cE consistent with dist_D up to O(1)\u201d is one-sided (surrogate \u2264 R_L gives no upper bound on the envelope E); Levin\u2019s theorem uncited", "A3 (Major)", VERIF,
         "Source lines 1636\u20131648: only r\u2096 \u2264 R_L is derived; E = sup over the full (\u03c4,\u03b2,D) family is unbounded relative to dist_D (e.g. \u03b2 \u2192 \u221e blows up outside the D-ball). No Levin entry in the 54-item bibliography."),
        ("Corollary 4.14: asserts the D_V = \u03ba equality Definition 2.1 disclaims; proof computes only the radial average; \u201cF = \u03ba_V, area = \u03c0a\u00b2\u201d gives \u03ba_V\u00b7\u03c0a\u00b2 = \u03c0a\u2074, not \u03c0a\u00b2; V_max normalization silently dropped", "A1, A3 (Critical)", VERIF,
         "Definition 2.1 disclaimer at source line 452\u2013455; Corollary at 1675\u20131712; proof substitution at 1700\u20131704 (verbatim). H_geo = \u03c0\u00b7\u03ba = \u03c0\u00b7\u03b4\u0304V/V_max equals \u03c0a\u00b2 only if V_max = 1 \u2014 never stated. Dimensionally incoherent as the audits say."),
        ("Gluing matching condition (O3) is a BCH truncation presented as an exact gauge identity; sign/order inconsistent with the standard A_j = g\u207b\u00b9A_i g + g\u207b\u00b9dg", "A2 #8, A3 (Major)", VERIF,
         "Source lines 383, 665\u2013666: g\u2097\u209c*A_j = A_i + d(log g) \u2212 [A_i, log g] \u2014 exact-identity framing of a first-order expansion; commutator sign convention non-standard. Fair finding; both audits agree."),
        ("Theorem 3.5 small-loop formula: \u201ccrossing the boundary once\u201d impossible for a closed transverse loop (own numerics: ncross = 2); O(1) reset term inside an \u03b5\u00b2 expansion", "A2 #9, A3 (Major)", VERIF,
         "Source lines 453\u2013466 (eq. piecewise-F): R_b = log(g\u208a\u208b(p\u208a)) is O(1) beside \u03b5\u00b2[\u00b7] and O(\u03b5\u00b3); \u201ccrossing once\u201d stated verbatim. A closed loop crossing transversely crosses an even number of times."),
        ("Theorem 12.2: 3/2 exponent manufactured by the \u03c3\u00b2 = \u03bd\u00b7a ansatz (constant \u03c3\u00b2 gives a\u00b9); first-passage L\u00e9vy framing unused in proof; C_fat \u201corder-unity\u201d constant absorbs a 2.3\u00d7 gap; 95% CI [1.471, 1.493] excludes 1.5 yet summarized \u201cverified to 1.4%\u201d", "A1, A3 (Moderate)", VERIF,
         "Ansatz at source lines 307, 2862; CI and \u201c1.4%\u201d summary at \u00a712; constant C_fat = (\u221a\u03bd/2)\u03ba with \u03ba absorbing the factor. All four sub-claims verbatim-confirmed."),
        ("E13 Theorem A: \u03a6(S) \u2264 S false for the stated \u03a6 (r catalyzed by S need not lie in S); \u03a6 not polynomial (food-generation is reachability); full proof lives in a script header, not the manuscript", "A1, A3 (Major)", VERIF,
         "Source lines 6939\u20136975: \u03a6 defined with catalysis-by-S and food-generation conditions; \u201c(i) is by construction\u201d is not a proof of \u03a6(S) \u2286 S; \u201cFull proof in script novelty_terminal_coalgebra_e13.py\u201d verbatim."),
        ("E13 Theorem B: functor-uniqueness \u201cby Strachey\u2013Reynolds parametricity\u201d \u2014 parametricity is a property of polymorphic terms, not a functor-uniqueness theorem; Z/4 toy illustration", "A1, A3 (Major)", VERIF,
         "Source lines 6977+; parametricity invoked verbatim for uniqueness of a functor between categories. Inapplicable as stated."),
        ("Corollary 17.3 \u201cunivalence-identified fixed point\u201d incoherent; \u201ctype of contractible \u221e-groupoids equivalent to U\u201d false (that type is contractible)", "A3 (Critical)", VERIF,
         "Source lines 3894\u20133908 with the claimed equivalences; the HoTT claim is false under univalence exactly as the audit states."),
        ("Theorem 8.2 \u201cunconditional\u201d is conditional on the chosen instantiation; seven optics realized as six identical generic resnet blocks + one linear map; \u201cBregman-regularized\u201d is Euclidean projection", "A2 #11, A3 (Major)", VERIF,
         "Source lines 2130\u20132233: six maps share (\u03b1 = 0.40, s = 1.00, \u03c1 = 0.80); f\u2082 = 1.15\u00b7I; T_reg uses \u03a0_K with Moreau decomposition cited. \u201cUnconditional\u201d in the title overstates: theorem is instantiation-conditional (rhetorical, not fatal)."),
        ("\u201cRealization functor R\u201d invoked \u22656 times, called \u201cexplicit\u201d, never defined", "A1, A3 (Major)", VERIF,
         "Source lines 258, 2022, 2107, 5939, 5972, 9330; Theorem 7.4\u2019s own statement concedes the endofunctor semantics \u201cis not established here\u201d. The bridge is a name, not a construction."),
        ("Prop 18.26 HoTT verdict \u201ccontractible \u21d4 Phase I = 100%\u201d is true by construction, labeled falsifiable", "A3 (Major)", VERIF,
         "Source lines 5541\u20135562: witness triangle present iff PASS; equivalence declared and labeled \u201cfalsifiable higher-categorical verdict\u201d."),
        ("Claims F/G are deterministic simulations of textbook identities; R\u00b2 = 1.0000 defended as \u201cthe analytic law itself\u201d", "A3 (Moderate)", VERIF,
         "Remark 14.7 concedes the Zeno curve is the analytic law at machine precision; so(3) commutator norms are identities. Self-validation confirmed."),
        ("Eq. (37) three-term decomposition vs Claim C two-term fit; at a = 0.3 the omitted a\u00b3 term is 3.3\u00d7 the fatigue term; \u00a711 stress test uses the three-term mean", "A3 (Major)", VERIF,
         "Source line 2481\u20132484 (H_raw = \u03c0a\u00b2 + a\u00b7\u03ba(a) + C_fat\u00b7a^{3/2}); Claim C fits two terms; magnitudes at a = 0.3 check out (0.027 vs 0.0082)."),
        ("\u00a78.2 CPTP: \u201c(pk/2\u207f)P/k\u201d placement \u201cacceptable but could confuse\u201d", "A2 #12", CORR,
         "Algebra is exactly right (pk/2\u207f \u00d7 P/k = (p/2\u207f)P; the k cancels). Presentation-only note; DeepSeek self-graded it correctly. Not a defect."),
        ("Theorem 17.2 \u221e-categorical composition presented as theorem, proof is a sketch", "A2 #14/33", VERIF,
         "Proof-sketch level; no homotopy-coherence diagrams. Confirmed as over-labeled."),
    ]
    story.append(ledger_table(rows_b, [0.34, 0.10, 0.10, 0.46],
        ["Finding", "Audit", "Verdict", "Evidence / note"]))
    return story


def build_content2(story):
    # ---------- 2.3 Category C ----------
    story.append(Paragraph("2.3 Category C — Internal inconsistencies", style_h2))
    story.append(Paragraph(
        "The dominant cause, correctly identified by all three audits in different words, "
        "is structural: the manuscript grew by appending elevation rounds v1\u2013v20 without "
        "ever reconciling its framing layers. The six-way network-count contradiction is "
        "verified verbatim, and the limitations-versus-body contradiction over the fully "
        "autopoietic verdict is as stark as the Editorial report describes. Verification "
        "adds one item no audit stated precisely: the \u00a721.5 \u201cConjectures\u201d subsection opens "
        "by saying the conjectures are \u201cplausible but not currently provable\u201d while both "
        "of its entries are marked CLOSED in their own titles.", style_body))

    rows_c = [
        ("Network count stated six different ways: 2 / 4 (five listed) / 2 / 4 / 10 against ~13 actual (A\u2013K, K+, overlay)", "A1, A3 (Critical)", VERIF,
         "Abstract line 135 (\u201cfour\u201d, lists A\u2013E); contribution 12 line 329 (same); roadmap line 426 and \u00a718 opening line 4285 (\u201ctwo\u201d); limitations lines 9518\u20139527 (\u201cfour\u201d, \u201cno fully autopoietic verdict\u201d); conclusion line 10006 (\u201cten\u201d). Body contains A,B,C,D,E,F,G,H,I,J,K,K+,overlay."),
        ("Limitations deny the body\u2019s 52/52 = 100% headline", "A3 (Critical)", VERIF,
         "Limitations line 9522 (\u201cthe test does NOT produce a fully autopoietic verdict\u201d) vs \u00a718.11 lines 5288/5304/5358 (52/52, \u201cFULL AUTOPOIESIS\u201d) and abstract/conclusion usages."),
        ("D_V vs \u03ba_V separation drawn in Definition 2.1, collapsed by Corollary 4.14, Definition 6.1, Remark 10.1, conclusion", "A3 (Major)", VERIF,
         "Definition 2.1 lines 448\u2013455 disclaims identity; Corollary 4.14 reasserts it for radially symmetric V; later sections cite \u201c\u03ba_V of Definition 2.1 (viability depth)\u201d."),
        ("Inverse-limit vs filtered-colimit confusion resurfaces after \u00a716.1 corrects it", "A1, A3 (Major)", VERIF,
         "\u00a716.1 corrects the terminology; contribution 7, Proposition 16.7\u2019s title and \u201cprojection arrows ... described as the inclusions\u201d, the conclusion, and the script names keep \u201cinverse limit\u201d."),
        ("Intro claims \u201ca single endofunctor T on Optic(C)\u201d; Remark 7.8 / Theorem 7.4 concede not established; withdrawn form persists in \u00a717 and conclusion", "A3 (Major)", VERIF,
         "Source lines 2019\u20132026 concede; the endofunctor phrasing recurs at \u00a717 headline and conclusion (\u201crealization-to-contraction functor\u201d, itself never defined)."),
        ("Figure 7 caption says n=4 regime has structure group CO(3) while main text says SO(3)", "A2 #5/32", VERIF,
         "PDF p.37 caption verbatim \u201c(structure group CO(3), Lie algebra so(3))\u201d; main text \u00a713 (Remark at source line 798) = SO(3); CO(3) is a separate third regime (source line 837). Caption error confirmed; fix = SO(3) in caption."),
        ("SAVGS tuple notation (B, E, P, \u03b5, \u0393) vs five listed items where item 2 covers E and P and item 5 (2-categorical span) is absent from the tuple", "A2 #4", VERIF,
         "Source lines 582\u2013606: 5-tuple notation; list has (1) B, (2) E and P, (3) \u03b5, (4) \u0393, (5) span. The span is called \u201cthe fifth SAVGS component\u201d in Remark 2.5 \u2014 not in the tuple. Should be a 6-tuple or the span folded into \u0393."),
        ("Base manifold renamed \u0398 \u2192 B in Definition 3.1; \u0398 returns in Prop 4.4, Remark 4.15, Theorem 3.14", "A3 (Minor)", VERIF,
         "Definition 3.1 declares B (\u201cdenoted \u0398 in earlier drafts\u201d); later sections still use \u0398 with a differently shaped tuple."),
        ("Optic objects as triples (M, C, R) in Definition 2.5 vs pairs with morphism-residuals in Theorem 16.3", "A3 (Moderate)", VERIF,
         "Two formalisms coexist without reconciliation; Theorem 16.3\u2019s componentwise colimit is on the pair formalism."),
        ("Remark 3.2 defers the 2-categorical development to future work; \u00a73.1 immediately claims the full gluing theorem closing Conjecture 21.1", "A3 (Major)", VERIF,
         "Direct contradiction as quoted; \u00a73.1 claims closure \u201cin ALL THREE regimes\u201d while Remark 3.2 calls it future work."),
        ("T = 200 for Networks A/B/D but T = 500 for the designed-to-pass Network E; robustness sweep at T = 300 gives 51/52", "A2 #18, A3 (Moderate)", VERIF,
         "Source lines 4455/4505 (T = 200) vs 4534+ (T = 500) vs 5462 (\u201creduced T = 300 budget\u201d, 51/52). Recovery-horizon goalpost move verified; the T = 300 caveat never reaches the abstract."),
        ("Network A component g: HOMEOSTATIC with knockout final 0.37 (never below threshold 0.1) and recovery 164.2; narrative says repair pathway collapses", "A3 (Moderate)", CORR,
         "Table verbatim (line 4227). Verdict is defensible via the drop-condition reading (g never drops, so its production is not causally necessary); the NARRATIVE\u2019s collapse explanation contradicts the table\u2019s numbers. Audit\u2019s framing slightly overstates; the narrative-vs-table mismatch is real."),
        ("PYR \u201cbaseline 0.0, recover 5.7, causally internal\u201d \u2014 a component whose baseline is below threshold passes", "A3 (Moderate)", VERIF,
         "Source line 4830 verbatim. Drop-condition semantics break for zero-baseline components; never discussed."),
        ("Claim E acceptance criterion drifts between n = 3 (T_ctrl/T_loop \u2265 5) and n = 4 (T_loop &lt; 2, T_ctrl &gt; 1)", "A3 (Moderate)", VERIF,
         "Source line 1879 vs table line 3029. Criterion change between regimes unexplained."),
        ("Network J has no subsection; numbering skips I \u2192 K with J in passing", "A3 (Moderate)", VERIF,
         "Subsection scan of \u00a718: A, B, C, D, E, F, G, H, I, [no J], K. Network J appears parenthetically."),
        ("Abstract: \u201cserves only as a conjectural upper envelope\u201d \u2014 stale, Theorem 4.11 closes the conjecture and the abstract itself later says so", "A2 #1/2", VERIF,
         "Abstract lines 101\u2013106 vs line 130 (\u201cthe algorithmic upper envelope (smooth-envelope theorem ...)\u201d) and \u00a74.2\u2019s \u201cclosing Conjecture\u201d subtitle. Internal self-contradiction inside the abstract."),
        ("\u201cAll five previously open conjectures are now closed ... no open conjectures remain\u201d vs two in-text open statements", "A1", VERIF,
         "Conclusion line 10177 vs Theorem 7.4 (\u201cfull functorial construction is open\u201d, lines 2020\u20132023) and \u00a721.6 filtered-colimits closure (\u201cgeneralization to arbitrary lfp monoidal C remains open\u201d)."),
        ("\u00a721.5 subsection titled \u201cConjectures\u201d opens \u201cplausible but not currently provable\u201d while both entries are CLOSED; \u00a721.6 redundantly re-lists closures", "A2 #2/27 (strengthened here)", VERIF,
         "New precise finding from verification: the \u00a721.5 preamble contradicts its own [CLOSED] entries. The five-conjecture count itself is consistent (5 = 2 + 3); the redundancy and preamble are the defects."),
        ("E25: r = +0.191 at n = 241 (S2 cell) vs +0.187 at n = 240 (common-set matrix) \u2014 one-gene/one-set difference not stated", "A2 #17", VERIF,
         "Source lines 8793 vs 8822. The two numbers coexist without reconciliation; the explanation (241 \u2192 240 common set, possibly metric variant) is reconstructable but absent."),
        ("Table 4 (elevation summary) lists only E1\u2013E9; text claims three times \u201cTable 4 is updated to include ...\u201d", "A2 #24", VERIF,
         "Table source lines 5686\u20135700 contain E1\u2013E9 only; \u201cupdated\u201d claims at 6404, 6602, 7102. The update claims are false as rendered."),
    ]
    story.append(ledger_table(rows_c, [0.34, 0.10, 0.10, 0.46],
        ["Finding", "Audit", "Verdict", "Evidence / note"]))

    # ---------- 2.4 Category D ----------
    story.append(Paragraph("2.4 Category D — Provenance, citations, and integrity", style_h2))
    story.append(Paragraph(
        "This category carries the audits\u2019 most consequential publication-blocking "
        "findings, and every one of them is verified against the manuscript\u2019s own words. "
        "The citation-coverage audit is reproduced here in full because it is the "
        "highest-integrity-value item: the set arithmetic is exact, the false annotations "
        "quote verbatim, and the broken key resolves to a specific missing bibitem. "
        "The provenance counts are slightly corrected (twelve never-cited entries, not "
        "eleven; six \u201cthe user\u201d sites in the PDF text layer, not nine \u2014 the substance "
        "is unchanged).", style_body))

    story.append(Paragraph(
        "Citation-coverage audit (reproduced from the LaTeX source). The 54 bibitems "
        "yield exactly 43 cited keys and 12 never-cited entries: "
        "<font face='DejaVuSansMono'>baezschreiber2007higher</font>, "
        "<font face='DejaVuSansMono'>becker2021zeno</font>, "
        "<font face='DejaVuSansMono'>bravetti2023noether</font>, "
        "<font face='DejaVuSansMono'>breen1990bitorseurs</font>, "
        "<font face='DejaVuSansMono'>breenmessing2001combinatorial</font>, "
        "<font face='DejaVuSansMono'>brunerie2020</font>, "
        "<font face='DejaVuSansMono'>hirota2023alife</font>, "
        "<font face='DejaVuSansMono'>kirchhoff2018markov</font>, "
        "<font face='DejaVuSansMono'>lurie2017ha</font>, "
        "<font face='DejaVuSansMono'>schreiber2013thesis</font>, "
        "<font face='DejaVuSansMono'>segura2026topos</font>, and "
        "<font face='DejaVuSansMono'>vereshchagin2010rate</font>. Six of these carry "
        "annotations asserting citation sites that do not exist: Vereshchagin\u2013Vit\u00e1nyi "
        "(\u201cCited in \u00a74 for prior-art precedence\u201d \u2014 Definition 4.1 presents dist_D with no "
        "attribution at the point of definition), Hirota (\u201cCited in \u00a73\u201d), Segura "
        "(\u201cCited in \u00a73\u201d), Kirchhoff\u2013Friston (\u201cCited in \u00a721\u201d), Becker (\u201cCited in \u00a714\u201d), "
        "and Bravetti (\u201cCited in \u00a75\u201d). One cited key "
        "(<font face='DejaVuSansMono'>orth2011comprehensive</font>) has no bibitem and "
        "renders as \u201c[\u003f]\u201d. The audits\u2019 characterization \u2014 the bibliography performs "
        "attribution the text does not deliver \u2014 is verified exactly.", style_body))

    rows_d = [
        ("\u00a719 opens with \u201cnine elevation studies conducted in response to the Qwen novelty assessment (external audit)\u201d; commit 07e6d85 cited five times; Table 4 organized by the audit\u2019s own section numbers", "A3 (Critical)", VERIF,
         "Source lines 5665\u20135670 and 5670/5682/6197/6347/6406 (commit hash); PDF full-text count of \u201cQwen\u201d = 34. Session-transcript structure confirmed."),
        ("\u00a719.8 responds to \u201cthe Novelty Assessment Report (editorial-style external audit, 15 pages, see external_audits/ folder)\u201d and closes its three upgrades in-study", "A1, A3 (Critical)", VERIF,
         "Source lines 6836\u20136849 verbatim, including the folder path and the three upgrade paths (Keio anchor, terminal-coalgebra, COT/NE benchmark)."),
        ("v14b round corrects the manuscript\u2019s own prior false statements and retracts an interpretation in place", "A1, A3 (Critical)", VERIF,
         "The v14b round text corrects \u201ctwo false statements\u201d and retracts the MAPPED-only n = 15 finding; honest science, disqualifying as manuscript narrative."),
        ("\u201cThe user\u201d as driver of design/analysis decisions throughout; \u201cthe user deposited ... (folder raw tomoya baba supp/)\u201d; \u201c(user-directed)\u201d", "A1, A3 (Critical)", CORR,
         "Verified verbatim (source lines 5183, 7134\u20137137, 7322, 7479, 9872; PDF count of \u201cthe user\u201d = 6, not the audit\u2019s 9 \u2014 substance unchanged; the deposit path is quoted at line 7137)."),
        ("Definition shopping documented: indicator-weighted \u03ba_V promoted to MAIN definition at the user\u2019s request \u201cto test whether it strengthens the original findings\u201d; effects: E12 r +0.370 \u2192 +0.938; iML1515 \u22120.008 \u2192 +0.466", "A1, A3 (Critical)", VERIF,
         "Source lines 7637\u20137641 quote the request verbatim; the effects at lines 1316\u20131321 (note: the \u22120.008 there is itself the numeric error \u2014 true baseline \u22120.018). Post-data definition change confirmed in the authors\u2019 own words."),
        ("Label leakage: indicator mask \u1d9c[\u0394b &gt; 0.05\u00b7b_wt] embeds the in-silico essentiality criterion in the predictor; text concedes \u201cgiven that a gene is in-silico-essential, what is its \u03ba_V?\u201d", "A1, A3 (Critical)", VERIF,
         "Definition 3.21 (lines 1294\u20131303); concession at lines 7589\u20137590 verbatim. The predictor conditions on the in-silico version of the outcome label."),
        ("Unmasked metric below chance on iML1515: AUC 0.428, P@10 = 0.000, \u201cthe gap is now in the WRONG direction\u201d", "A1, A3 (Major)", VERIF,
         "Source lines 7431, 7463, 7553; E16 JSON confirms AUC 0.428. The standing null the masked variant was selected against."),
        ("Build log embedded in the body: dangling-\\ref audit (12 label namespaces, 321 labels, 704 references), patch scripts named (patch_manuscript_v12.py, patch_elevation_pdf_v12.py)", "A3 (Critical)", VERIF,
         "Source lines 8003\u20138047: label counts verbatim; patch-script names with escaped underscores at 8046\u20138047. Production-transcript content in the paper."),
        ("Referee-response negotiation in the body: \u201cthe audit\u2019s \u00a78.4 prescription ... is REJECTED in favor of elevation\u201d", "A3 (Moderate)", VERIF, "Source line 4297 verbatim."),
        ("Future-direction items implemented within the same document and marked [CLOSED] inside their own statements", "A2 #30, A3 (Critical)", VERIF,
         "Source lines 9764, 9790, 9862, 9880, 9891: items listed under \u201cFuture directions\u201d carrying [CLOSED] markers."),
        ("Authorship/AI statement contradicted by the documented workflow; \u201call citations were verified against primary sources\u201d vs the false annotations; repo name deepseek-highly-general vs stated drafting model", "A1, A3 (Critical)", VERIF,
         "Statement at lines 10293\u201310310; the workflow text attributes analyses and deposits to \u201cthe user\u201d and revision agenda to two external AI audits; 12 uncited + 6 false annotations + 1 broken key contradict the citation-verification claim; the repository name contradicts the named model."),
        ("Remark 20.6 cites \u201cthe source transcript\u2019s curvature-survival equivalence, acknowledged by the source\u201d", "A3 (Critical)", VERIF,
         "Source line 6940\u20136941 region; a source transcript cited as the origin of prior claims."),
        ("Session-environment details in the body: \u201cthe COLOMBOS host itself was unreachable from the analysis environment\u201d, deposit paths, \u201cinternet-access verification table\u201d", "A3 (Moderate)", VERIF,
         "PDF full-text: COLOMBOS \u00d73; the raw-data deposit narrative at lines 7134\u20137137 and the M3D provenance discussion."),
    ]
    story.append(ledger_table(rows_d, [0.34, 0.10, 0.10, 0.46],
        ["Finding", "Audit", "Verdict", "Evidence / note"]))

    # ---------- 2.5 Category E ----------
    story.append(Paragraph("2.5 Category E — Methodological weaknesses", style_h2))
    story.append(Paragraph(
        "The methodological findings are the deepest layer: they concern how evidence was "
        "produced and selected rather than whether any single number is right. All of the "
        "audits\u2019 structural patterns \u2014 definition shopping, label leakage, self-validation, "
        "threshold placement, and the uncorrected serial search \u2014 are documented in the "
        "manuscript\u2019s own text, which is why verification here mostly means confirming the "
        "quoted passages and checking the one claim that required reading the analysis "
        "code. That code check produced the single most consequential correction of this "
        "assessment (the \u00a718.4 finding, Part III).", style_body))

    rows_e = [
        ("E12 \u201cexternal validation\u201d is FBA-versus-FBA: \u03ba_V and the essentiality label are statistics of the same KO-FBA solutions; direct external anchor much weaker (AUC 0.713, specificity 0.180, MCC 0.085)", "A1, A3 (Major)", VERIF,
         "E15 JSON ground truth: Pearson 0.0847, Spearman 0.2284, AUC 0.7126, P@200 0.245 (2.27\u00d7); manuscript reports the same. The transitivity framing (r = 0.370 \u00d7 0.934) is model-internal."),
        ("E14 benchmark invalid as designed: NE scope of 45 metabolites on full iJO1366 is a cofactor-blocking artifact; COT on a 28-metabolite subnetwork; \u201cstrictly stronger\u201d compares instruments on different inputs", "A1 (concern), A3 (Moderate)", VERIF,
         "Script novelty_structural_benchmark_e14.py: seed = 18 extracellular uptake metabolites only; the all-reactants-in-scope rule blocks nearly every reaction (atp, h2o, pi, nad never seeded) \u2014 scope collapses to 45. NE finds ZERO of the 28 dynamically-internal metabolites, i.e. the comparison is against a broken NE. See Part V for the completed diagnosis."),
        ("\u00a718.4 written protocol (knock out ALL producers) cannot generate its own nprod-stratified results; implementation must have knocked out only active producers", "A3 (Major)", REFUT,
         "Code reading refutes the inference: autopoiesis_ijO1366.py knocks out ALL producers, matching the text. The real defect is deeper \u2014 protocol degeneracy (verdict \u21fa baseline production &gt; 10\u207b\u2076). See Part III and Part V."),
        ("Garden of forking paths: the abstract\u2019s r = +0.374 (n = 433, p \u2248 10\u207b\u00b9\u2075) is the survivor of seven documented restructurings (r = 0.010 \u2192 masks p = 0.33/0.43 \u2192 retraction \u2192 mapping inversion \u2192 n = 7, p = 0.18 \u2192 M3D); no multiplicity correction", "A3 (Major)", VERIF,
         "The full lineage is in \u00a719\u2019s rounds (E10 \u2192 E20 \u2192 v14b \u2192 E23 \u2192 E24). The round structure honestly discloses the search; the abstract reports only the survivor."),
        ("E5 self-refutation arc: c = 1.625 \u201ccloses the factor-of-2 gap\u201d \u2192 shape-dependent \u2192 NOT TRANSFERABLE (sign-flip, negative \u03ba_V on real FBA viability)", "A2 #25, A3 (Major)", VERIF,
         "Table 4 row E5 documents the arc; the v2 \u201ctransferable\u201d claim and the v4 \u201cNOT TRANSFERABLE\u201d verdict coexist in the appendix narrative."),
        ("Three objects named \u03ba_V: geometric curvature contraction (\u00a7\u00a72\u20135), indicator-masked FBA flux-rerouting statistic (Def 3.21), time-course squared flux change (E10/E22); the empirical program never touches the first; no theorem connects them", "A1, A3 (Critical)", VERIF,
         "Geometric \u03ba at Propositions 4.4/4.7 (ratio [Dh]\u208a/h); Def 3.21 (masked sum of squared flux changes, line 1301); time-course \u03ba_V(r,t) = (v_r(t) \u2212 v_r(T\u2081))\u00b2 (line 6635). Disjoint domains; the manuscript itself notes Def 3.21\u2019s object \u201cis the curvature \u03ba^alg of Theorem 4.11, not\u201d the synthetic one. Verified in the strongest form."),
        ("E2-v2/v3: dep-ratio and the essentiality label derive from the same FBA model; threshold \u03c4* swept on the evaluation data \u2014 internal consistency, not external validation", "A1", VERIF,
         "Source lines 5836\u20135885: threshold sweep on the same iJO1366 model whose essentiality is the label; \u03ba = 0.898/0.835 are same-model consistency numbers."),
        ("Endpoint-sampling problem: Phase I scores limit-cycle recoveries by oscillation phase at the sampling instant (AcCoA, ALA); the fix is one-line period-averaging, but the manuscript built an \u221e-categorical reinterpretation (2 perturbed reruns, 30% tolerance, no test statistic)", "A3 (Major)", VERIF,
         "Source line 4822 region (AcCoA caught at the low phase); Phase III operationalization = n = 2 reruns with 30% tolerance. The audits\u2019 diagnosis and the one-line fix are both correct."),
        ("Acceptance margins cluster at thresholds (0.498 vs 0.5; 0.401 vs 0.4; 0.853 vs 0.5); free parameters hand-set (\u03c6 = 0.4/0.5, \u03c4 = 0.30, n = 2, kcat overrides); recovery horizon doubled T = 200 \u2192 500 for Network E", "A3 (Major)", VERIF,
         "Margin values quoted at the cited sites; sensitivity analyzed only for a subset."),
        ("Prop 18.28 SO(3) holonomies hand-assigned (\u03b1 = 1.0 \u201ccanonical\u201d, axes by fiat); \u201cidentity holonomy\u201d = exp(\u03b1T)exp(\u2212\u03b1T) = I; Network K\u2019s actual dynamics never enter", "A3 (Moderate)", VERIF,
         "The SO(3) verdict section assigns canonical axes/amplitudes; the identity check is trivial matrix algebra; decorative use of Theorem 3.5."),
        ("Zero-\u03ba_V controls across layers: transcript control strong (p \u2248 10\u207b\u00b2\u00b2), protein control null (p \u2248 1) \u2014 layer-specificity not stated as a combined statement", "A2 #19", VERIF,
         "E24 transcript control vs E27 protein control; the dissociation is the paper\u2019s strongest honest finding and deserves an explicit combined statement."),
        ("\u201cE24\u2013E27 is genuinely competent experimental science with honest confound controls\u201d \u2014 the audits\u2019 positive verdict", "A1, A3", VERIF,
         "Verified: r = +0.374 / partial +0.251 / 2\u00d72 platform-class disambiguation with four significant Fisher-z contrasts / protein-layer null / confounders named. The strongest material in the manuscript."),
    ]
    story.append(ledger_table(rows_e, [0.34, 0.10, 0.10, 0.46],
        ["Finding", "Audit", "Verdict", "Evidence / note"]))
    return story


def build_content3(story):
    # ===================== PART III: AUDIT ERRORS =====================
    story.append(part_divider("PART III", "Audit Errors — Refuted and Corrected Claims",
        "Verification is bidirectional: an audit earns authority by being right, and the "
        "four failures below are what separate the three audits\u2019 reliability levels. One "
        "refutation replaces a mis-diagnosed finding with a sharper one; one refutes an "
        "extraction artifact; two correct counts and one numeric ground truth. None of "
        "these errors is fatal to the audit that made it, but all of them would have "
        "propagated into the repair plan if left uncorrected."))

    story.append(Paragraph("3.1 REFUTED — The \u00a718.4 \u201ctext vs code\u201d claim (Editorial report)", style_h2))
    story.append(Paragraph(
        "The Editorial report\u2019s Category C ledger states that \u00a718.4\u2019s written protocol "
        "\u201cknock out ALL producers of m\u201d \u201ccannot generate its own nprod-stratified results; "
        "implementation must have knocked out only active producers.\u201d This inference is "
        "wrong about the code. The function <font face='DejaVuSansMono'>producing_reactions</font> "
        "in <font face='DejaVuSansMono'>autopoiesis_ijO1366.py</font> (lines 106\u2013113) returns "
        "every reaction with a positive stoichiometric coefficient, and the knockout loop "
        "(lines 208\u2013216) sets the bounds of all of them to zero \u2014 the implementation "
        "matches the written protocol exactly. The nprod stratification is also directly "
        "recomputable from the deposited CSV: nprod \u2265 5 gives 10/11 causally internal, "
        "nprod \u2264 3 gives 18/39, totals 28/50 \u2014 the file carries the columns the "
        "manuscript\u2019s table reports.", style_body))
    story.append(Paragraph(
        "The correct diagnosis is worse than the audit\u2019s. Under an all-producers knockout, "
        "the production flux of m after knockout is structurally zero (every producing "
        "reaction is constrained to zero flux, and FBA stoichiometry cannot create new "
        "producers), so the \u201cdrop below threshold\u201d branch is satisfied whenever the "
        "baseline produced m at all. The \u201crecovery\u201d step re-solves the identical "
        "unconstrained model, so the recovery flux equals the baseline flux by "
        "determinism of the LP optimum returned. The verdict logic in the script "
        "(causally_internal = baseline_prod &gt; 10\u207b\u2076 AND knock_prod &lt; 10\u207b\u2076 AND "
        "rec_prod &gt; 10\u207b\u2076) therefore reduces to: baseline production flux exceeds "
        "10\u207b\u2076. The knockout and restoration \u2014 the entire operational content of the "
        "closure test at genome scale \u2014 add no discriminating power; the 28/50 \u201cpartially "
        "autopoietic\u201d verdict measures which metabolites the baseline FBA optimum happens "
        "to produce. The recorded knockout biomass is never used in the verdict. This "
        "degeneracy generalizes to the E2 dependency-ratio studies, which likewise never "
        "test a counterfactual the model has not already answered. The finding the audit "
        "wanted is real; its mechanism was not.", style_body))

    story.append(Paragraph("3.2 REFUTED — The \u201cstray Q characters\u201d (DeepSeek)", style_h2))
    story.append(Paragraph(
        "DeepSeek\u2019s item #31 reports \u201cNotation Q appears in several product bounds as a "
        "stray character ... likely a LaTeX rendering artifact.\u201d Pixel-level inspection of "
        "page 53 at 4\u00d7 zoom shows a correctly drawn large product symbol \u220f between "
        "\u201c[catalyst r]\u00b7\u201d and \u201cs \u2208 substrates(r)\u201d; the source is a normal "
        "<font face='DejaVuSansMono'>\\prod</font> at line 4181. The \u201cQ\u201d exists only in "
        "the PDF\u2019s text-extraction layer, where the math font\u2019s product glyph carries no "
        "ToUnicode mapping. This is precisely the class of artifact the Editorial report "
        "explicitly excluded (\u201cextraction artifacts ... were excluded from the ledger after "
        "pixel-level verification\u201d) \u2014 the contrast is a methodological data point between "
        "the two audits. No manuscript edit is required for this item; it is struck from "
        "the repair plan.", style_body))

    story.append(Paragraph("3.3 CORRECTED — Counts and ground truths", style_h2))
    story.append(Paragraph(
        "Four smaller corrections. First, the never-cited-reference count is twelve, not "
        "eleven: the audits\u2019 lists missed <font face='DejaVuSansMono'>breen1990bitorseurs</font> "
        "(both the Editorial report and GLM enumerate eleven entries; the set difference "
        "against the LaTeX source returns twelve). Second, the \u201cthe user (9 sites)\u201d count "
        "is six in the PDF text layer; the audits likely counted source-line matches "
        "including \u201cuser-suggested\u201d compounds \u2014 the substance (the user as the driver of "
        "design decisions) is unchanged, and the six sites are quoted in Part II. Third, "
        "the iML1515 baseline value is settled against ground truth: the E16 result file "
        "gives \u22120.0178, so the correct in-text value is \u22120.018 and the three \u22120.008 "
        "sites are transcription errors (the derived stability gap 0.103 is correct, 0.093 "
        "wrong) \u2014 the audits flagged the inconsistency but could not say which side was "
        "right. Fourth, a new discrepancy found during verification: the manuscript states "
        "the nprod \u2265 5 stratum as \u201c9/10\u201d but the deposited CSV gives 10/11 (one "
        "metabolite, not a rounding difference); the nprod \u2264 3 stratum (18/39) and the "
        "totals (28/50) match exactly.", style_body))
    story.append(Paragraph(
        "A fifth, softer correction concerns GLM\u2019s E15 numbers: they are all exactly right "
        "(raw Pearson +0.085, Spearman +0.228, AUC 0.713, P@200 = 0.245, specificity "
        "0.180, MCC 0.085), which is worth stating because GLM presented them without "
        "source. DeepSeek\u2019s claim that the E2-v3 value \u201c\u03ba = 0.835, AUC 0.968\u201d involves "
        "threshold selection on the evaluation data is likewise confirmed verbatim from "
        "the threshold-sweep text. Where the audits supplied numbers, the deposited files "
        "agreeed in every checked case except the two count items above \u2014 an "
        "encouraging reliability result for all three documents.", style_body))

    # ===================== PART IV: TRIANGULATION =====================
    story.append(part_divider("PART IV", "Cross-Audit Triangulation",
        "Where the three audits agree (and are now jointly evidence-backed), where they "
        "diverge, and what each contributes that the others cannot. The three-audits "
        "convergence on the integrity items is itself a finding: no reviewer perspective "
        "dissents on the false bibliography annotations, the provenance leakage, or the "
        "three-\u03ba_V problem."))

    story.append(Paragraph("4.1 Points of full three-way agreement (all verified)", style_h2))
    story.append(simple_table(
        ["Convergent finding", "A1 GLM", "A2 DeepSeek", "A3 Editorial", "Verification"],
        [
            ("Bibliography: never-cited entries with false \u201cCited in \u00a7X\u201d annotations; V-V attribution missing at Definition 4.1", "\u2713 (11/54)", "\u2713", "\u2713 (11/54)", "12/54; 6 false; + broken key [\u003f]"),
            ("Numeric inconsistency iML1515 \u22120.018 vs \u22120.008", "\u2014", "\u2713", "\u2713", "Ground truth \u22120.018; 3 wrong sites"),
            ("Framing layers stale vs body (network counts; abstract stops at E; limitations vs 52/52)", "\u2713", "\u2713", "\u2713", "Six-way count contradiction verbatim"),
            ("Session provenance throughout (\u201cthe user\u201d, audits, commits, build logs)", "\u2713", "\u2713 (implicit)", "\u2713 (9 sites)", "6 sites + 34 \u201cQwen\u201d + 5 commit hashes"),
            ("Three (or more) distinct objects named \u03ba_V, never connected", "\u2713 (core point)", "\u2713 #6", "\u2713", "Disjoint definitions quoted"),
            ("Definition shopping + label leakage documented in-text", "\u2713", "\u2014", "\u2713", "Verbatim quotes at lines 7637\u20137641, 7589\u20137590"),
            ("E24\u2013E27 transcript/protein chain = strongest material, honestly caveated", "\u2713 (explicit)", "\u2713 (implicit)", "\u2713 (explicit)", "All statistics match deposited JSONs"),
            ("E13 terminal-coalgebra: genuine candidate but proof not in manuscript", "\u2713", "\u2014", "\u2713", "\u03a6(S) \u2264 S false as stated; proof in script header"),
            ("Conjecture-closure bookkeeping is inconsistent/redundant", "\u2713 (no-open tension)", "\u2713 #2/#27", "\u2713 (D category)", "\u00a721.5 preamble vs [CLOSED] labels"),
        ],
        [0.40, 0.11, 0.13, 0.13, 0.23]))

    story.append(Paragraph("4.2 Where the audits diverge", style_h2))
    story.append(Paragraph(
        "The strategic divergence is real but reconcilable. The Editorial report concludes "
        "the manuscript is \u201cfurther from publishable than v2\u201d and recommends deconstruction "
        "into three papers; DeepSeek implicitly treats the manuscript as repairable in "
        "place, offering a 28-item improvement checklist; GLM diagnoses structure without "
        "prescribing a plan. These are not incompatible: GLM\u2019s diagnosis \u2014 append-only "
        "growth without framing reconciliation \u2014 explains why DeepSeek-style in-place "
        "checklists keep being overtaken by the next round, and the Editorial report\u2019s "
        "deconstruction is the strategic exit from that loop. On severity, the Editorial "
        "report grades hardest (its four Critical provenance items would each block "
        "publication alone), DeepSeek grades most generously (several of its \u201cflaws\u201d are "
        "presentation notes, including the refuted Q item and the self-graded \u201cacceptable\u201d "
        "CPTP item), and GLM sits between. On E14, GLM alone flagged the 45-metabolite NE "
        "scope as a likely implementation artifact \u2014 confirmed by code reading here \u2014 "
        "while the Editorial report criticized only the input mismatch; GLM\u2019s version is "
        "the stronger half and both halves are completed in Part V.", style_body))

    story.append(Paragraph("4.3 Reliability scorecard", style_h2))
    story.append(simple_table(
        ["Audit", "Claims checked", "Verified", "Corrected", "Refuted", "Distinctive reliability profile"],
        [
            ("A3 Editorial (81 findings)", "~60 material", "all but 1", "2 (counts)", "1 (\u00a718.4 mechanism)",
             "Only audit that excluded extraction artifacts after pixel verification; line references accurate; the one diagnostic error is an inference beyond its evidence layer."),
            ("A1 GLM (5 sections)", "~25 material", "all but 1", "1 (11/54 count)", "0",
             "Highest signal density; citation forensics and the three-\u03ba_V diagnosis are its own; no independent numeric errors; supplied E15 numbers that all check out."),
            ("A2 DeepSeek (33 + 28)", "~40 material", "most", "1 (self-graded CPTP)", "1 (stray Q)",
             "Most complete tactical checklist; abstract-staleness and section-redundancy items are unique and correct; weakest on render-vs-extraction distinction."),
        ],
        [0.17, 0.11, 0.10, 0.10, 0.12, 0.40]))
    story.append(Paragraph(
        "Net reliability is high for all three, and the failure modes are complementary "
        "rather than correlated: the Editorial report\u2019s single error was an over-reach "
        "into code behavior it had not read; DeepSeek\u2019s error was trusting a text-layer "
        "extraction; GLM\u2019s only misses were count arithmetic. No finding was contradicted "
        "by another audit, and no audit\u2019s Critical item failed verification \u2014 which is "
        "the strongest reason to treat the merged repair plan below as "
        "implementation-ready rather than aspirational.", style_body))
    return story


def build_content4(story):
    # ===================== PART V: STRENGTHENED FINDINGS =====================
    story.append(part_divider("PART V", "Strengthened, Augmented, and Completed Findings",
        "The instruction to strengthen, augment, improve, correct, and complete weaker "
        "suggestions before implementation is executed here: six findings that entered "
        "the audits as fragments or mis-diagnoses leave this section as complete, "
        "actionable defect statements with named repairs. These are the joint "
        "assessment\u2019s own contributions beyond the sum of its sources."))

    story.append(Paragraph("5.1 The Network-C closure test is degenerate (replaces the \u00a718.4 finding)", style_h3))
    story.append(Paragraph(
        "Completed statement: at genome scale the operational centerpiece reduces to a "
        "one-line property of the baseline FBA solution. Under the written protocol, "
        "knocking out all producers of m makes m\u2019s production identically zero, so the "
        "drop condition is equivalent to \u201cm is produced at baseline\u201d; the restoration step "
        "re-solves the same unconstrained LP, so recovery equals baseline; the verdict "
        "therefore reads causally_internal \u21fa baseline_prod &gt; 10\u207b\u2076. The knockout biomass "
        "the script records is never consulted. Consequences: (i) the 28/50 verdict "
        "measures which metabolites the baseline optimum produces, not organizational "
        "closure; (ii) the nprod stratification is an artifact of pathway redundancy "
        "correlating with nonzero production; (iii) the same critique applies mutatis "
        "mutandis to the E2 dependency-ratio studies, whose \u201cvalidation\u201d target is the "
        "same model\u2019s own essentiality calls. Named repair: either knock out one producer "
        "at a time (or the k-th fraction), making the drop non-trivial and the recovery "
        "informative, or re-define the genome-scale verdict as \u201cproduction essentiality "
        "under producer-set deletion\u201d and stop calling it autopoiesis. The fixed-model "
        "confusion matrices (E15/E16) are unaffected \u2014 they never claimed dynamical "
        "closure \u2014 which cleanly separates what survives this repair from what does not.",
        style_body))

    story.append(Paragraph("5.2 The E14 network-expansion benchmark is broken at the seed, not the comparison", style_h3))
    story.append(Paragraph(
        "Completed statement: GLM suspected the 45-metabolite scope was \u201can implementation "
        "artifact\u201d; the Editorial report attacked the input mismatch (full model versus "
        "28-metabolite subnetwork). Code reading settles it: the seed contains only the 18 "
        "extracellular uptake metabolites, and the expansion rule requires every reactant "
        "of a reaction to be in scope before it fires. Since essentially every iJO1366 "
        "reaction consumes currency metabolites (protons, water, ATP, NAD, phosphate, "
        "coenzyme A) that are never seeded, almost nothing fires \u2014 the scope collapses to "
        "45 metabolites and finds ZERO of the 28 dynamically-internal metabolites. "
        "Standard network-expansion methodology seeds the intracellular forms of the "
        "medium components plus the currency cofactors (or uses reaction-activation "
        "variants); with a correct seed the scope covers hundreds of metabolites and the "
        "\u201cstrictly stronger\u201d claim would face a real instrument instead of a broken one. "
        "Named repair: re-run NE with cofactor-bootstrapped seed; re-run COT on the full "
        "model (or the same 50-metabolite test universe); only then report the comparison. "
        "Until then, E14\u2019s verdict should be marked not-yet-established rather than "
        "\u201cclosed\u201d.", style_body))

    story.append(Paragraph("5.3 The three \u03ba_V objects need a naming divorce, not a reconciliation theorem", style_h3))
    story.append(Paragraph(
        "Completed statement: the audits agree that \u03ba_V names three incompatible objects "
        "\u2014 the geometric curvature contraction of Propositions 4.4/4.7 (a derivative ratio "
        "on the SAVGS base), the indicator-masked FBA flux-rerouting statistic of "
        "Definition 3.21, and the time-course squared flux change of E10/E22 \u2014 and that no "
        "theorem connects them. The GLM report\u2019s closing line (\u201cthe theory\u2019s object never "
        "touches the data\u2019s object\u201d) is the manuscript\u2019s central structural fact. The "
        "completed repair is terminological before it is mathematical: rename now, "
        "reconcile later if a bridge is ever proven. Concrete proposal: keep \u03ba_V (or a "
        "better name) for the geometric object; call the FBA statistic \u03ba_flux or a "
        "\u201crerouting index\u201d; call the time-course statistic by its formula\u2019s name. Every "
        "cross-reference in the abstract, Definition 6.1, Remark 10.1, the E24\u2013E27 "
        "narrative, and the conclusion must then be re-scoped to the object actually "
        "measured. This single edit dissolves the \u201cunification\u201d overclaim at every level "
        "and is the highest-leverage non-provenance edit available. A genuine reconciliation "
        "theorem (FBA-flux curvature bounding the geometric object under a declared "
        "embedding) is a legitimate open problem \u2014 to be stated as one, not implied.",
        style_body))

    story.append(Paragraph("5.4 The conjecture bookkeeping contradicts itself inside one subsection", style_h3))
    story.append(Paragraph(
        "Completed statement: DeepSeek\u2019s \u201cconjecture labeling duplication\u201d and the "
        "Editorial report\u2019s \u201cfuture-direction items marked CLOSED\u201d understate a sharper "
        "local contradiction: \u00a721.5\u2019s subsection \u201cConjectures\u201d opens \u201cThe following "
        "conjectures are precise, falsifiable statements that are plausible but not "
        "currently provable from the manuscript\u2019s assumptions\u201d \u2014 and then presents two "
        "conjectures whose titles both end in \u201c(CLOSED)\u201d, closed by theorems stated in "
        "the same document. \u00a721.6 then re-opens the theme with \u201cFormerly open "
        "conjectures, now closed\u201d and three more CLOSED entries, while the conclusion "
        "claims \u201cno open conjectures remain\u201d against two in-text openness concessions "
        "(the endofunctor semantics and the lfp-generalization). Named repair: one "
        "subsection \u201cConjectures and closures\u201d with a five-row closure table (conjecture, "
        "status, closed by, verification), the preamble rewritten to past tense, the "
        "genuinely open items (endofunctor semantics; lfp generalization; the global "
        "cross-stratum bound that Remark 20.2 itself calls \u201ca separate, well-defined open "
        "problem\u201d) listed under Future directions \u2014 and the conclusion\u2019s \u201cno open "
        "conjectures remain\u201d deleted or replaced by the true count.", style_body))

    story.append(Paragraph("5.5 The Corollary 4.14 cluster: a three-line repair the audits each saw a third of", style_h3))
    story.append(Paragraph(
        "Completed statement: three audits each caught a different face of the same "
        "passage. GLM called the proof dimensionally incoherent; the Editorial report "
        "added the D_V = \u03ba equality contradiction with Definition 2.1 and the "
        "\u201cradial average\u201d non-proof; DeepSeek did not itemize it but its Definition 6.1 "
        "criticism is downstream of the same collapse. The complete defect: (i) the "
        "statement asserts, for all radially symmetric V, an equality that Definition 2.1 "
        "scopes to one radial prototype with a specific connection; (ii) the proof\u2019s final "
        "substitution \u201cF = \u03ba_V and area = \u03c0a\u00b2 gives H_geo = \u03c0a\u00b2\u201d is false as algebra "
        "(it gives \u03ba_V\u00b7\u03c0a\u00b2 = \u03c0a\u2074) unless \u03ba_V \u2261 1; (iii) the V_max normalization "
        "required to make H_geo = \u03c0\u00b7\u03ba = \u03c0a\u00b2 is silently dropped. Named repair: delete the "
        "corollary or restate it as a model-specific computation \u2014 for the radial "
        "prototype with V_max = 1 and the connection A = \u00bd(x dy \u2212 y dx), Stokes gives "
        "H_geo = \u03c0a\u00b2 directly (this is already done correctly in \u00a75\u2019s eq:alpha-form "
        "derivation) \u2014 and reconcile the statement with Definition 2.1\u2019s disclaimer by "
        "citing the prototype explicitly.", style_body))

    story.append(Paragraph("5.6 The Theorem 4.11 computability claim: the exact weakening that makes it true", style_h3))
    story.append(Paragraph(
        "Completed statement: the audits correctly reject \u201cupper-semicomputable\u201d for a "
        "supremum over an uncountable family and the proof\u2019s \u201cdiscrete-enumerable\u201d "
        "self-contradiction. The completed repair, so that implementation does not have to "
        "re-derive it: restrict the envelope to a countable dense parameter subfamily "
        "\u2014 rational \u03c4, \u03b2, D from a fixed enumeration, L \u2208 \u2115 \u2014 and add a continuity "
        "argument (the surrogate family is continuous in its parameters on compact "
        "parameter boxes, so the countable sup equals the continuum sup pointwise; this "
        "also repairs Lemma 4.10 by bounding the family: compact \u03c4 \u2208 [\u03c4_min, \u03c4_max], "
        "\u03b2 \u2264 \u03b2_max, L \u2264 L_max, which makes the uniform Lipschitz bound and the "
        "upper-semicomputability claim simultaneously provable). The C\u00b2 claims should be "
        "weakened to C\u00b9 plus Clarke differentiability everywhere in \u00a74.1 (or the kernel "
        "replaced by a logistic soft-threshold, making C\u00b2 true); \u00a74.2 already uses the "
        "Clarke machinery, so the honest weakening costs nothing downstream. Remark 4.12 "
        "needs a Levin citation added to the bibliography and its one-sided bound "
        "restated as such, or an actual upper bound on E relative to dist_D derived.",
        style_body))

    # ===================== PART VI: REPAIR PLAN =====================
    story.append(part_divider("PART VI", "Unified, Prioritized Repair Plan (Implementation-Ready)",
        "Every surviving audit recommendation, merged, de-duplicated, corrected, and "
        "ranked. P0\u2013P1 are mechanical (hours); P2\u2013P3 are editorial rewrites (1\u20132 days "
        "each); P4 is the mathematical repair tier; P5 is the strategic tier. Items "
        "refuted in Part III are struck. Every item names the exact edit site."))

    rows_p0 = [
        ("Broken cite key: replace <font face='DejaVuSansMono'>orth2011comprehensive</font> with <font face='DejaVuSansMono'>orth2011</font> (line 1299)", "all 3", "5 min"),
        ("Fix \u22120.008 \u2192 \u22120.018 at lines 1321, 7730, 7741; gap 0.093 \u2192 0.103 where derived", "A2/A3", "10 min"),
        ("Delete the six false \u201cCited in \u00a7X\u201d annotations; add real in-text citations at point of use (V\u2013V at Definition 4.1; Hirota + Segura in \u00a73 related-work paragraph; Kirchhoff in \u00a721; Becker in \u00a714; Bravetti in \u00a75) or remove the 12 uncited entries", "all 3", "1\u20132 h"),
        ("EC number: glycogen phosphorylase 2.7.4.1 \u2192 2.4.1.1 (line 4770); re-check 2.6.1.12 attributions (lines 4631, 4701, 4720, 4769)", "A3", "10 min"),
        ("Figure 7 caption: CO(3) \u2192 SO(3) (PDF p.37; keep the separate CO(3) third regime as text)", "A2", "5 min"),
        ("Fix \u201c\u00a77 research-integrity notes\u201d (line 10307) and \u201c\u00a71.4 form\u201d (lines 9898, 9994) dangling pointers", "A3", "15 min"),
        ("\u201conly 3 compute \u03ba_V ... E10, E12, E15 and E16\u201d \u2192 four (lines 7658\u20137661)", "A3", "2 min"),
        ("Add biomass-units note for 15.444 vs 0.9259 (lines 6872, 7346)", "A3", "15 min"),
        ("nprod \u2265 5 stratum: 9/10 \u2192 10/11 per deposited CSV", "this assessment", "2 min"),
        ("E25: add one sentence reconciling +0.191 (n = 241) vs +0.187 (n = 240 common set)", "A2", "5 min"),
    ]
    story.append(Paragraph("P0 — Mechanical integrity fixes (total: one afternoon)", style_h3))
    story.append(simple_table(["Edit", "Source", "Effort"], rows_p0, [0.72, 0.13, 0.15]))

    rows_p1 = [
        ("Definition 3.18 step labels: restructure the enumerate (short labels + description run-in) so (ii)\u2013(v) render fully; same fix for Table 6 column widths (Paragraph-wrapped cells)", "A3 (Critical)", "1\u20132 h"),
        ("Remove version metadata from formal statements: \u201cv10 main definition\u201d \u2192 \u201cindicator-weighted definition\u201d; strip \u201c(v10, E18; v11, E19)\u201d-style labels from body math", "A3 (Critical)", "1 h"),
        ("Fix \u201c+0.99958\u201d stray in the n = 4 table\u2019s c_comm row (line 3026); fix Table 6 caption \u201cthe author\u2019s\u201d \u2192 \u201cour\u201d (line 9574)", "A3", "10 min"),
        ("Update Table 4 to E1\u2013E27 (or delete the three false \u201cTable 4 is updated\u201d claims at lines 6404, 6602, 7102)", "A2", "2 h"),
        ("Add the missing Levin reference for Remark 4.12 or restate the bound as one-sided", "A3", "20 min"),
    ]
    story.append(Paragraph("P1 — Typesetting and bookkeeping (total: half a day)", style_h3))
    story.append(simple_table(["Edit", "Source", "Effort"], rows_p1, [0.72, 0.13, 0.15]))

    rows_p2 = [
        ("Rewrite abstract: final biological state (E\u2192K lineage summarized in one line as engineering; E24\u2013E27 as the empirical core), drop \u201cconjectural upper envelope\u201d staleness, carry the honest external numbers (r = +0.374 / partial +0.251 / protein null / raw-Keio AUC 0.713)", "A2/A3", "0.5 day"),
        ("Network-count reconciliation across all six sites (abstract 135, contribution 329, roadmap 426, \u00a718 opening 4285, limitations 9518, conclusion 10006): one canonical count with designed-vs-fixed distinction (~13: A\u2013K, K+, overlay; 2 fixed external models)", "all 3", "0.5 day"),
        ("Limitations rewrite: reconcile \u201cno fully autopoietic verdict\u201d with 52/52 (either demote the 100% headline as endpoint-only with T-caveat, or upgrade the limitation to the v20 state)", "A2/A3", "0.5 day"),
        ("Conjecture section: single \u201cConjectures and closures\u201d subsection, five-row closure table, open items to Future directions, delete \u201cno open conjectures remain\u201d (line 10177)", "A2/A3 + this", "0.5 day"),
        ("\u03ba_V naming divorce (\u03ba_geom / \u03ba_flux / time-course name) at all cross-referencing sites; re-scope the unification claim to the object actually measured", "A1/A3 + this", "1 day"),
    ]
    story.append(Paragraph("P2 — Framing-layer rewrite (total: 2\u20133 days)", style_h3))
    story.append(simple_table(["Edit", "Source", "Effort"], rows_p2, [0.72, 0.13, 0.15]))

    rows_p3 = [
        ("Excise session provenance: rewrite \u00a719 as Methods (remove \u201cthe user\u201d, Qwen, Novelty Assessment Report, commit hashes, build log with patch-script names, folder paths, \u201csource transcript\u201d, COLOMBOS narrative); disclose the variant search in a methods paragraph instead", "all 3", "1\u20132 days"),
        ("Authorship/AI statement: replace with a true account of the workflow (LLM-executed analyses, user-directed round structure, external audits as revision drivers) consistent with the repository name and AI-use policies", "A1/A3", "0.5 day"),
        ("Multiplicity disclosure for the E10\u2192E24 search lineage (or pre-registration language for future rounds); report unmasked \u03ba_flux alongside the masked variant wherever the masked statistic is headlined", "A3 + this", "0.5 day"),
    ]
    story.append(Paragraph("P3 — Provenance excision and honest disclosure (total: 2\u20133 days)", style_h3))
    story.append(simple_table(["Edit", "Source", "Effort"], rows_p3, [0.72, 0.13, 0.15]))

    rows_p4 = [
        ("\u00a74 smoothness: weaken to C\u00b9 + Clarke consistently (or logistic soft-threshold kernel); fix Prop 4.7 \u201cpreserve smoothness\u201d", "A3", "0.5 day"),
        ("Lemma 4.10 + Theorem 4.11: compact parameter box (\u03c4, \u03b2, D, L bounded), countable dense subfamily + continuity \u2192 both the uniform bound and upper-semicomputability become provable; delete \u201cdiscrete-enumerable\u201d contradiction", "A2/A3 + this", "1 day"),
        ("Corollary 4.14: delete or restate as model-specific computation (see 5.5)", "A1/A3 + this", "0.5 day"),
        ("Theorem 3.4/3.5: standard gauge form for the matching condition; two-crossing small-loop formula with the boundary term at its true order", "A2/A3", "1 day"),
        ("E13 Theorem A: correct \u03a6 to the deflationary operator (S \u21a4 S \u2229 {catalyzed + food-generated}), cite finite-lattice fixed-point literature; move the proof from the script header into an appendix; demote Theorem B to a conjecture", "A1/A3", "1 day"),
        ("Define the realization functor R or remove every claim depending on it (six sites); demote Theorem 17.2 to \u201cTheorem (sketch)\u201d; delete or prove Corollary 17.3", "A1/A3", "1 day"),
        ("Network-C closure test: re-implement with single-producer (or fractional-producer) knockout so drop and recovery are non-trivial; re-scope E2 accordingly (see 5.1)", "this assessment", "1 day"),
        ("E14: re-run NE with cofactor-bootstrapped seed and COT on matched inputs; re-word \u201cstrictly stronger\u201d (see 5.2)", "A1/A3 + this", "1 day"),
        ("Phase I endpoint sampling: period-average (or multi-offset median) scoring, replacing the \u221e-categorical two-rerun patch; retain persistent homology as a descriptor", "A3", "0.5 day"),
    ]
    story.append(Paragraph("P4 — Mathematical and methodological repairs (total: ~1 week)", style_h3))
    story.append(simple_table(["Edit", "Source", "Effort"], rows_p4, [0.72, 0.13, 0.15]))

    story.append(Paragraph("P5 — Strategic tier (the Editorial report\u2019s de-construction)", style_h3))
    story.append(Paragraph(
        "The Editorial report\u2019s recommendation to split the manuscript into three papers "
        "is adopted as the strategic end-state, now with the verification-backed content "
        "map. Paper 1 (methods): the repaired closure test on fixed genome-scale models "
        "(Definition 3.18 re-typeset, the 5.1 re-implementation, E15/E16 fixed-model "
        "confusion matrices, a correctly seeded E14). Paper 2 (empirical report): the "
        "\u03ba_flux\u2013transcript association (E22, E24\u2013E27) with the metric renamed, the search "
        "path disclosed, the 2\u00d72 disambiguation and protein-layer null as headline "
        "honesty. Paper 3 (theory): the categorical framework after the P4 mathematical "
        "repairs. Each paper is reviewable on its own merits; none is reviewable while "
        "embedded in the current compilation. The designed-network lineage E\u2192K+ becomes "
        "a calibration appendix for the closure-test instrument (engineering, declared "
        "parameters, changelog as data), and the in-silico AUC 0.953 is reported as a "
        "calibration diagnostic rather than validation. If the authors choose in-place "
        "repair instead of de-construction, P0\u2013P4 is the honest maximum: after P4, the "
        "manuscript\u2019s remaining overclaims are strategic (unification, \u201cno open "
        "conjectures\u201d, 100% autopoiesis) and are cleared by P2\u2019s framing rewrite.", style_body))

    # ===================== PART VII: VERDICT =====================
    story.append(part_divider("PART VII", "Joint Verdict",
        "The three audits, verified, are one audit with three voices. The verdict below "
        "is the merged judgment, stated as findings about the manuscript and about the "
        "audits themselves."))

    story.append(Paragraph(
        "On the manuscript: the v20 document is not publishable as a single submission, "
        "and the reasons are now fully evidence-backed rather than asserted. Four "
        "integrity items alone would end any competent refereeing round \u2014 the "
        "bibliography\u2019s six false attribution annotations plus twelve never-cited entries "
        "plus one broken key; the authorship statement contradicted by the body\u2019s own "
        "documented workflow; the in-text record of a definition change made after "
        "seeing the data with the winning mask embedding the outcome label; and the "
        "session-transcript provenance spanning \u00a719 (50 of 131 pages). The mathematical "
        "core has five load-bearing statements that are wrong or unproven as written "
        "(Corollary 4.14, the Theorem 4.11 computability claim, the Lemma 4.10 uniform "
        "bound, the matching-condition and small-loop formulas, and the E13 terminal-"
        "coalgebra statement), all repairable with bounded effort per Part 5.6\u2019s "
        "prescriptions. The strongest genuinely new material \u2014 the E24\u2013E27 "
        "transcript/protein dissociation chain with the 2\u00d72 platform-by-class "
        "disambiguation, and the E15/E16 fixed-model analyses \u2014 is real, honestly "
        "caveated, and publishable once extracted and renamed. The salvageable core is "
        "at least one good paper; it is currently buried under the machinery of its own "
        "production.", style_body))
    story.append(Paragraph(
        "On the audits: all three earn adoption, with corrections. The Editorial "
        "line-level review is the strategic backbone (de-construction plan adopted in "
        "P5; ledger adopted with the \u00a718.4 mechanism corrected in 5.1); DeepSeek\u2019s "
        "checklist is the tactical backbone (P0\u2013P2 are largely its items, with the "
        "stray-Q item struck and the CPTP item closed as presentation-only); GLM\u2019s "
        "structural diagnosis is the explanatory backbone (the three-\u03ba_V naming divorce "
        "in 5.3 is its core observation, completed). The audits\u2019 positive verdict on "
        "E24\u2013E27 is confirmed against the deposited result files in every checked "
        "number. Where the audits disagreed with each other, the verification resolved "
        "the disagreement; where they agreed, the agreement survived verification in "
        "every instance. The merged P0\u2013P5 plan is the implementation-ready output of "
        "this assessment: 10 mechanical edits, 5 bookkeeping edits, 5 framing rewrites, "
        "3 provenance excisions, 9 mathematical/methodological repairs, and one "
        "strategic split, in that order.", style_body))
    story.append(Paragraph(
        "Recommended immediate next step: execute P0 (one afternoon of mechanical "
        "integrity fixes, including the citation repairs that close the highest-value "
        "integrity item), then P1, then decide between in-place repair (P2\u2013P4) and "
        "de-construction (P5) \u2014 a decision that belongs to the authors, but which the "
        "verification here has made fully informed: the honest maximum of in-place "
        "repair is a correctly-scoped, correctly-cited, provenance-clean 131-page "
        "monograph whose headline empirical claim (a genome-scale, platform-robust, "
        "transcript-layer-specific correlational association of a flux-rerouting "
        "sensitivity with carbon-depletion transcriptional response) is defensible "
        "exactly as caveated; de-construction additionally buys reviewability, at the "
        "cost of three submission processes instead of one.", style_body))
    return story


# =============================================================================
# BUILD
# =============================================================================
def build():
    out_path = "/home/z/my-project/download/joint_assessment_2nd_wave.pdf"
    doc = SimpleDocTemplate(
        out_path, pagesize=A4,
        leftMargin=2.2*cm, rightMargin=2.2*cm,
        topMargin=2.0*cm, bottomMargin=1.9*cm,
        title="Joint Assessment of Three Second-Wave Audits of the v20 Manuscript",
        author="Z.ai",
        subject="Claim-level verification, audit-error refutation, and unified repair plan",
        creator="Z.ai PDF skill (ReportLab)",
    )

    story = []
    story.append(CoverPage())
    story.append(PageBreak())

    doc.onFirstPage = draw_cover
    def noop(canv, d):
        pass
    doc.onLaterPages = noop

    build_content(story)
    build_content2(story)
    build_content3(story)
    build_content4(story)

    doc.build(story)
    print(f"built: {out_path}")


if __name__ == "__main__":
    build()
