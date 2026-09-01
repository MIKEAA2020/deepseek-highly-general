#!/usr/bin/env python3
"""
Joint Assessment of the Six 'Unifying Object' Audits (third wave).

Audits under assessment (external_audits/unifying object/):
  U1 DeepSeek : "deepseek recommendations.txt" (188 lines) - editorial/structural
  U2 GLM      : "glm.txt" (194 lines) - five-thread ontology, T1-T7 theorem repairs
  U3 GPT      : "gpt sol" (351 lines) - realized perturbation divergence, typed
  U4 Kimi     : "kimi k3max" (68 lines) - slot-family weak unification, R1-R4
  U5 Muse     : "muse spark 1.2" (90 lines) - canonical kappa + Theorem U + migration
  U6 Opus     : "opus 5" (167 lines) - curvature datum, mixed difference, routes C1/C2

This assessment VERIFIES every claim against the frozen v21 manuscript
(scripts/journal_manuscript.tex, 10,830 lines; download/journal_manuscript.pdf,
134 pp; commit ddbb384), refutes/corrects audit errors, and synthesizes the six
proposals into one architecture. The manuscript itself is NOT modified.

Deliverable: /home/z/my-project/download/joint_assessment_unifying_object.pdf
"""

import os, sys, hashlib

PDF_SKILL_DIR = "/home/z/my-project/skills/pdf"
sys.path.insert(0, os.path.join(PDF_SKILL_DIR, "scripts"))

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
    KeepTogether, HRFlowable, CondPageBreak,
)
from reportlab.platypus.tableofcontents import TableOfContents

# ---------------------------------------------------------------- fonts ----
FONT_DIR = "/usr/share/fonts"
pdfmetrics.registerFont(TTFont('NotoSerifSC', f'{FONT_DIR}/truetype/noto-serif-sc/NotoSerifSC-Regular.ttf'))
pdfmetrics.registerFont(TTFont('NotoSerifSC-Bold', f'{FONT_DIR}/truetype/noto-serif-sc/NotoSerifSC-Bold.ttf'))
pdfmetrics.registerFont(TTFont('FreeSerif', f'{FONT_DIR}/truetype/freefont/FreeSerif.ttf'))
pdfmetrics.registerFont(TTFont('FreeSerif-Bold', f'{FONT_DIR}/truetype/freefont/FreeSerifBold.ttf'))
pdfmetrics.registerFont(TTFont('FreeSerif-Italic', f'{FONT_DIR}/truetype/freefont/FreeSerifItalic.ttf'))
pdfmetrics.registerFont(TTFont('FreeSerif-BoldItalic', f'{FONT_DIR}/truetype/freefont/FreeSerifBoldItalic.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuSansMono', f'{FONT_DIR}/truetype/dejavu/DejaVuSansMono.ttf'))
registerFontFamily('NotoSerifSC', normal='NotoSerifSC', bold='NotoSerifSC-Bold')
registerFontFamily('FreeSerif', normal='FreeSerif', bold='FreeSerif-Bold',
                   italic='FreeSerif-Italic', boldItalic='FreeSerif-BoldItalic')
registerFontFamily('DejaVuSansMono', normal='DejaVuSansMono', bold='DejaVuSansMono')

from pdf import install_font_fallback
install_font_fallback()

# ------------------------------------------------- cascade palette (V2) ----
# palette.cascade --title "Joint Assessment of Six Unifying-Object Audits
# of the Metabolic Curvature Manuscript" --mode minimal --format reportlab
PAGE_BG       = HexColor('#f1f1ef')
SECTION_BG    = HexColor('#e9e9e6')
CARD_BG       = HexColor('#ebebe8')
TABLE_STRIPE  = HexColor('#f5f4f4')
HEADER_FILL   = HexColor('#756b4d')
COVER_BLOCK   = HexColor('#67604b')
BORDER        = HexColor('#cecac0')
ICON          = HexColor('#95834e')
ACCENT        = HexColor('#a4862e')
ACCENT_2      = HexColor('#7052ca')
TEXT_PRIMARY  = HexColor('#1e1d1b')
TEXT_MUTED    = HexColor('#7d7b74')
SEM_SUCCESS   = HexColor('#448f5d')
SEM_WARNING   = HexColor('#b38f47')
SEM_ERROR     = HexColor('#a1554e')
SEM_INFO      = HexColor('#4a6d90')

VERIF  = 'VERIFIED'
CORR   = 'CORRECTED'
REFUT  = 'REFUTED'
STALE  = 'RESOLVED-IN-v21'
COND   = 'CONDITIONAL'

# ---------------------------------------------------------------- styles ---
styles = getSampleStyleSheet()

style_h1 = ParagraphStyle('H1', parent=styles['Heading1'],
    fontName='FreeSerif', fontSize=18.5, leading=24,
    textColor=HEADER_FILL, alignment=TA_LEFT, spaceBefore=16, spaceAfter=7)
style_h2 = ParagraphStyle('H2', parent=styles['Heading2'],
    fontName='FreeSerif', fontSize=13, leading=18,
    textColor=TEXT_PRIMARY, alignment=TA_LEFT, spaceBefore=12, spaceAfter=5)
style_h3 = ParagraphStyle('H3', parent=styles['Heading3'],
    fontName='FreeSerif', fontSize=10.8, leading=15,
    textColor=HEADER_FILL, alignment=TA_LEFT, spaceBefore=9, spaceAfter=4)
style_body = ParagraphStyle('Body', parent=styles['Normal'],
    fontName='FreeSerif', fontSize=9.7, leading=14.3,
    textColor=TEXT_PRIMARY, alignment=TA_JUSTIFY, spaceBefore=2, spaceAfter=6)
style_quote = ParagraphStyle('Quote', parent=styles['Normal'],
    fontName='FreeSerif-Italic', fontSize=9.2, leading=13.4,
    textColor=HexColor('#4a4636'), alignment=TA_LEFT,
    leftIndent=14, rightIndent=10, spaceBefore=4, spaceAfter=6,
    backColor=HexColor('#f4f2ea'), borderPadding=7)
style_meta = ParagraphStyle('Meta', parent=styles['Normal'],
    fontName='FreeSerif', fontSize=8.6, leading=11.6,
    textColor=TEXT_MUTED, alignment=TA_LEFT)
style_part = ParagraphStyle('Part', parent=styles['Normal'],
    fontName='FreeSerif', fontSize=9.5, leading=13,
    textColor=TEXT_MUTED, alignment=TA_LEFT, spaceBefore=0, spaceAfter=2)
style_tc  = ParagraphStyle('TC', parent=styles['Normal'],
    fontName='FreeSerif', fontSize=8.3, leading=11.2,
    textColor=TEXT_PRIMARY, alignment=TA_LEFT)
style_tcb = ParagraphStyle('TCB', parent=style_tc, fontName='FreeSerif-Bold')
style_th  = ParagraphStyle('TH', parent=styles['Normal'],
    fontName='FreeSerif-Bold', fontSize=8.6, leading=11.6,
    textColor=HexColor('#ffffff'), alignment=TA_LEFT)
style_v_v = ParagraphStyle('VV', parent=style_tc, textColor=SEM_SUCCESS, fontName='FreeSerif-Bold', fontSize=7.4)
style_v_c = ParagraphStyle('VC', parent=style_tc, textColor=SEM_WARNING, fontName='FreeSerif-Bold', fontSize=7.4)
style_v_r = ParagraphStyle('VR', parent=style_tc, textColor=SEM_ERROR, fontName='FreeSerif-Bold', fontSize=7.4)
style_v_s = ParagraphStyle('VS', parent=style_tc, textColor=SEM_INFO, fontName='FreeSerif-Bold', fontSize=7.4)
style_v_d = ParagraphStyle('VD', parent=style_tc, textColor=SEM_INFO, fontName='FreeSerif-Bold', fontSize=7.4)
style_stat = ParagraphStyle('Stat', parent=styles['Normal'],
    fontName='FreeSerif-Bold', fontSize=17, leading=21,
    textColor=ACCENT, alignment=TA_CENTER)
style_statlbl = ParagraphStyle('StatL', parent=styles['Normal'],
    fontName='FreeSerif', fontSize=8.4, leading=11.4,
    textColor=TEXT_MUTED, alignment=TA_CENTER)

# --------------------------------------------------------------- helpers ---
MARGIN = 1.9*cm
PAGE_W, PAGE_H = A4
AVAIL_W = PAGE_W - 2*MARGIN

def P(text, style=style_body):
    return Paragraph(text, style)

def H(text, level=1):
    style = {1: style_h1, 2: style_h2, 3: style_h3}[level]
    key = 'h_' + hashlib.md5(text.encode()).hexdigest()[:8]
    p = Paragraph('<a name="%s"/><b>%s</b>' % (key, text), style)
    p.bookmark_name = key
    p.bookmark_level = level - 1
    p.bookmark_text = text
    p.bookmark_key = key
    return p

def PART(label, title, level=1):
    out = []
    if level == 1:
        out.append(CondPageBreak(0.25 * (PAGE_H - 2*MARGIN)))
        out.append(Spacer(1, 6))
        out.append(Paragraph(label.upper(), style_part))
    out.append(H(title, level))
    rule = HRFlowable(width='100%', color=ACCENT, thickness=1.6,
                      spaceBefore=1, spaceAfter=8)
    out.append(rule)
    return out

def TBL(data, ratios, header=True, font_size=None, stripes=True, align_center_cols=None):
    """data: rows of Paragraph-ready strings. All cells wrapped in Paragraph()."""
    th, tc = style_th, style_tc
    wrapped = []
    for ri, row in enumerate(data):
        wr = []
        for ci, cell in enumerate(row):
            if isinstance(cell, Paragraph):
                wr.append(cell)
            elif ri == 0 and header:
                wr.append(Paragraph('<b>%s</b>' % cell, th))
            else:
                st = tc
                if isinstance(cell, tuple):
                    st, cell = cell
                wr.append(Paragraph(cell, st))
        wrapped.append(wr)
    widths = [r * AVAIL_W for r in ratios]
    assert sum(widths) <= AVAIL_W + 0.5, 'table overflow: %.1f > %.1f' % (sum(widths), AVAIL_W)
    t = Table(wrapped, colWidths=widths, hAlign='CENTER', repeatRows=1 if header else 0)
    cmds = [
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 3.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3.5),
        ('GRID', (0, 0), (-1, -1), 0.4, BORDER),
    ]
    if header:
        cmds.append(('BACKGROUND', (0, 0), (-1, 0), HEADER_FILL))
    if stripes:
        for ri in range(1 if header else 0, len(data)):
            if (ri - (1 if header else 0)) % 2 == 1:
                cmds.append(('BACKGROUND', (0, ri), (-1, ri), TABLE_STRIPE))
    t.setStyle(TableStyle(cmds))
    return t

def V(label):
    """Verdict cell -> Paragraph with semantic color."""
    m = {VERIF: style_v_v, CORR: style_v_c, REFUT: style_v_r, STALE: style_v_s,
         COND: style_v_d}
    return Paragraph(label, m.get(label, style_tc))

def CALLOUT(big, label, width=None):
    w = width if width is not None else 4.6*cm
    t = Table([[Paragraph('<b>%s</b>' % big, style_stat)],
               [Paragraph(label, style_statlbl)]], colWidths=[w])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), CARD_BG),
        ('BOX', (0, 0), (-1, -1), 1, ACCENT),
        ('TOPPADDING', (0, 0), (-1, 0), 8), ('BOTTOMPADDING', (0, 1), (-1, 1), 8),
        ('TOPPADDING', (0, 1), (-1, 1), 2), ('BOTTOMPADDING', (0, 0), (-1, 0), 2),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    return t

def CALLOUT_ROW(items):
    gap = 0.35*cm
    w = (AVAIL_W - gap*(len(items)-1)) / len(items)
    cells = [CALLOUT(b, l, width=w) for b, l in items]
    t = Table([cells], colWidths=[w]*len(cells), hAlign='CENTER')
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0), ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    return t

def TCAP(text):
    return Paragraph(text, ParagraphStyle('cap', parent=style_meta, alignment=TA_CENTER,
                                           spaceBefore=3, spaceAfter=14))

# ------------------------------------------------------------ doc + frame --
class TocDocTemplate(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if hasattr(flowable, 'bookmark_name'):
            level = getattr(flowable, 'bookmark_level', 0)
            text = getattr(flowable, 'bookmark_text', '')
            key = getattr(flowable, 'bookmark_key', '')
            self.notify('TOCEntry', (level, text, self.page, key))

def on_page(canv, doc):
    canv.saveState()
    canv.setFont('FreeSerif', 7.4)
    canv.setFillColor(TEXT_MUTED)
    canv.drawString(MARGIN, PAGE_H - 1.15*cm,
                    'Joint Assessment of Six Unifying-Object Audits - third wave')
    canv.setStrokeColor(ACCENT); canv.setLineWidth(1.2)
    canv.line(MARGIN, PAGE_H - 1.35*cm, PAGE_W - MARGIN, PAGE_H - 1.35*cm)
    canv.setFont('FreeSerif', 7.4)
    canv.drawString(MARGIN, 1.15*cm, 'Verification & Synthesis Unit - v21 frozen baseline ddbb384')
    canv.drawRightString(PAGE_W - MARGIN, 1.15*cm, 'p. %d' % doc.page)
    canv.setStrokeColor(BORDER); canv.setLineWidth(0.5)
    canv.line(MARGIN, 1.35*cm, PAGE_W - MARGIN, 1.35*cm)
    canv.restoreState()

OUT = '/home/z/my-project/download/joint_assessment_unifying_object.pdf'
doc = TocDocTemplate(OUT, pagesize=A4,
                     leftMargin=MARGIN, rightMargin=MARGIN,
                     topMargin=1.9*cm, bottomMargin=1.75*cm,
                     title='Joint Assessment of Six Unifying-Object Audits',
                     author='Z.ai', creator='Z.ai',
                     subject='Third-wave audit verification and synthesis')

story = []

# ------------------------------------------------------------------- TOC ---
story.append(Paragraph('<b>Contents</b>', style_h1))
story.append(HRFlowable(width='100%', color=ACCENT, thickness=1.6, spaceAfter=10))
toc = TableOfContents()
toc.levelStyles = [
    ParagraphStyle('TOC0', fontName='FreeSerif-Bold', fontSize=10.4, leading=16,
                   leftIndent=6, textColor=TEXT_PRIMARY),
    ParagraphStyle('TOC1', fontName='FreeSerif', fontSize=9.2, leading=13.5,
                   leftIndent=22, textColor=TEXT_MUTED),
]
story.append(toc)
story.append(PageBreak())

# =========================================================== PART I ========
story += PART('Part I', 'Executive Summary and the Six Audits')

story.append(P(
 'The repository folder <i>external_audits/unifying object/</i> contains six new audits, '
 '1,058 lines in total, all responding to one question: what would it take to make the '
 'manuscript a single coherent article, given that three disjoint mathematical objects '
 'currently share the name kappa_V. The six authors arrive by different routes, propose '
 'materially different central objects, and yet converge to a remarkable degree on both '
 'the diagnosis and the shape of the repair. This assessment verifies every checkable '
 'claim against the frozen v21 manuscript (10,830 LaTeX lines, 134 PDF pages, commit '
 'ddbb384), corrects the audit errors it finds, completes the weaker suggestions, and '
 'synthesizes the six proposals into one architecture that none of them states alone.'))

story.append(Spacer(1, 6))
story.append(CALLOUT_ROW([
    ('6', 'audits verified line-by-line'),
    ('1,058', 'audit lines read in full'),
    ('38', 'claim-level verdicts in Part II'),
    ('8', 'audit errors corrected in Part III'),
    ('4', 'synthesis layers in Part V'),
]))
story.append(Spacer(1, 10))

story.append(H('What all six agree on', 2))
story.append(P(
 'Every audit accepts, and this assessment independently re-verified, the core factual '
 'basis: (i) the abstract and Section 4 make their main proposition about a geometric '
 'curvature built from a Bregman divergence of a smooth surrogate of an algorithmic '
 'rate-distortion distance (Proposition 4.4); (ii) the empirical flagship studies '
 'E24 to E27 correlate a per-gene statistic that is a squared flux displacement along a '
 'glucose-decline trajectory, kappa_V(r,t) = (v_r(t) - v_r(T1))<super>2</super>, taken '
 'unchanged from the E22 artifacts; and (iii) Definition 3.21 defines an '
 'indicator-weighted single-knockout flux-rerouting sum. These are three objects with '
 'different types, different units, and no theorem connecting them. GLM calls this "the '
 'single deepest coherence defect"; Opus calls the experimental object "the deficit '
 'function itself, not the curvature"; Muse states flatly that the flagship "does not '
 'test the abstract\'s proposition" unless a unification theorem is proven; Kimi warns '
 'that the strong form of that theorem is "probably not provable within this '
 'manuscript\'s scope". All six are right, and the line-level evidence is in Part II.'))

story.append(H('What the six propose, in one table', 2))
story.append(TBL([
 ['ID', 'Audit (model)', 'Central proposal', 'Character', 'Role in synthesis'],
 ['U1', 'DeepSeek recommendations (188 lines)',
  'Editorial reconstruction as a formal journal article; one named central object '
  '(unify or rename); Methods-not-change-log; all contradictions reconciled; '
  '"repair and demote over remove"',
  'Editorial / structural', 'Style and architecture backbone; deletion-demotion policy'],
 ['U2', 'GLM (194 lines)',
  'Five-thread ontology (G/A/C/D/B); definitions D1-D6; seven theorem repairs T1-T7 '
  'with effort estimates; closure - geometry - computability image; explicit '
  'deletion list',
  'Comprehensive / strategic', 'Structural backbone; T2 jump-cocycle and T7 mpLP bridge are the new mathematics'],
 ['U3', 'GPT "sol" (351 lines)',
  'Typed realization datum (B,E,pi,s,Y,a,phi,W,m,N); realized perturbation divergence '
  'Delta_R; kappa_geo as a separate curvature operator; four-condition plaquette '
  'estimator; biomass deficit is not a metric',
  'Type-theoretic / careful', 'Formalization backbone; the plaquette design and the transport caveat'],
 ['U4', 'Kimi k3max (68 lines)',
  'Weak formal unification: one slot-family kappa[d, c, Lambda]; three instantiations; '
  'relation theorems R1-R4 with labeled epistemic status; knockout-simplex embedding',
  'Constructive / mathematical', 'Constructive backbone; R1/R3 are the first provable flagship-abstract link'],
 ['U5', 'Muse spark 1.2 (90 lines)',
  'Canonical kappa_V^geom (Prop 4.4 form); rename the other two objects; Theorem U '
  '(conditional unification) or honest disambiguation table; 5-item migration checklist',
  'Drop-in / tactical', 'Tactical backbone; the migration checklist is the implementation protocol'],
 ['U6', 'Opus 5 (167 lines)',
  'Curvature datum (X, A, Phi); central object = second mixed difference of the '
  'deficit; FBA = epistasis; E24-E27 measures Phi itself; Route C1 second differences '
  '(cheap) and Route C2 double perturbations',
  'Factored / empirical', 'Empirical backbone; the only audit that converts the theory into new computations'],
], [0.045, 0.16, 0.36, 0.115, 0.32]))
story.append(TCAP('Table 1. The six third-wave audits. Lines and file names from '
 'external_audits/unifying object/; characterizations are this assessment\'s.'))

story.append(H('Verification method and baseline', 2))
story.append(P(
 'The same five-layer protocol as the second-wave assessment was used, now against the '
 'v21 source. Layer 1: line-level reading of scripts/journal_manuscript.tex (10,830 '
 'lines) with rendered-number extraction from the compiled PDF so that "Proposition 4.4" '
 'or "Remark 20.2" resolve to actual statements. Layer 2: full-text scans of the '
 'compiled PDF for counts and framings (for example "the user" appears 6 times '
 'case-sensitively, "Qwen" 34 times, the commit hash 07e6d85 five times, COLOMBOS '
 'three times). Layer 3: independent re-derivation of every mathematical claim that '
 'could be checked by hand - the softmax gradient identity behind GLM\'s Lemma 4.10 '
 'repair, the Fisher-Rao radius computation behind its Proposition 3.16 finding, the '
 'Stokes-substitution arithmetic behind Corollary 4.14, the 0.92<super>6</super> x 1.15 '
 '= 0.697 product behind Theorem 8.2. Layer 4: the deposited result files (CSV and JSON '
 'artifacts) for the Lévy exponent confidence interval and the E24/E25 numbers. Layer 5: '
 'code reading of the analysis scripts where a claim was about behavior rather than '
 'text. One baseline note matters for interpreting the audits: they reviewed the '
 '131-page v20 PDF (GLM cites "the current 131 pages"); v21 (134 pages, commit ddbb384) '
 'had already executed the second-wave P0-mechanical round. Every verdict below is '
 'therefore re-verified against v21, and items the audits list that v21 already fixed '
 'are marked RESOLVED-IN-v21 rather than counted as audit errors.'))

# =========================================================== PART II =======
story += PART('Part II', 'Verification Ledger')

story.append(P(
 'Each row records an audit claim, its source audit, the verdict of this assessment, '
 'and the line-level evidence. Line numbers prefixed L refer to the v21 PDF text layer; '
 '"tex" refers to the LaTeX source. Verdicts: VERIFIED (claim confirmed against v21), '
 'CORRECTED (claim right in substance, wrong in a detail that matters for '
 'implementation), REFUTED (claim false), CONDITIONAL (claim holds only under a stated '
 'hypothesis), RESOLVED-IN-v21 (true of v20, already fixed in v21).'))

story.append(H('II.1 The central finding: three objects named kappa_V', 2))
story.append(TBL([
 ['Claim', 'Audit', 'Verdict', 'Evidence in the frozen v21 source'],
 ['Object (a): the geometric kappa_V is a Bregman divergence of the smooth surrogate, '
  'positive part, sup over unit bivectors, per-area units',
  'all six', V(VERIF),
  'Prop 4.4 (L851): h_alpha = D_phi(dist_D(x), dist_D(x0)); L886-887: "the wedge-norm '
  'constraint makes kappa_V dimensionally a per-area quantity"'],
 ['Object (b): Def 3.21 is an indicator-weighted single-knockout squared-flux sum',
  'all six', V(VERIF),
  'Def 3.21 (L774): kappa_V(g) = 1[delta_b > tau b_wt] x sum over dR(g) of '
  '(v_r(KO) - v_r(WT))<super>2</super>; title still reads "v10 main definition, '
  'indicator-weighted"'],
 ['Object (c): E10/E22 time-course statistic is (v_r(t) - v_r(T1))<super>2</super>',
  'U2 U3 U5 U6', V(VERIF),
  'Sec 19.17 (L6093): "reaction-level kappa_V(r, t) = (v_r(t) - v_r(T1))2 with the '
  'identical E10/v13 definition"'],
 ['The empirical flagship E24-E27 uses object (c), not (a) or (b)',
  'U2 U3 U5 U6', V(VERIF),
  'Sec 19.19 (L6293): "The E22 panel\'s per-gene kappa_V values (baseline '
  'glucose-decline trajectory, unchanged from E22) are tested against M3D"; E26/E27 '
  'pair the same panel with protein and Schmidt-transcript metrics (L6513, L6588)'],
 ['The abstract\'s main proposition concerns object (a) - hence the theoretical object '
  'never touches the empirical object',
  'U2 U4 U5 U6', V(VERIF),
  'Intro (L100-101): "the derivation of kappa_V from a Bregman divergence evaluated at '
  'dist_D (Proposition 4.4), supplying ... the per-trajectory falsification protocol"'],
 ['Def 6.1 cites "the kappa_V of Definition 2.1" while Def 2.1 defines D_V and '
  'disclaims curvature',
  'U5 U6', V(VERIF),
  'Def 2.1 title (L204): "Viability depth functional D_V; distinct from curvature"; '
  'body: "it is not a curvature 2-form"; Def 6.1 (L1192) cites both anyway'],
], [0.29, 0.07, 0.12, 0.52]))
story.append(TCAP('Table 2. The three-objects finding and its evidentiary basis.'))

story.append(P(
 'The flagship-uses-object-(c) claim required its own verification because it is the '
 'load-bearing fact of the whole wave: if E24 had used the FBA knockout statistic '
 '(object b), the unification problem would be a different one. The E24 design text is '
 'explicit, however, and so is E25 (GSE64021) and the E26/E27 pairing: all four studies '
 'correlate per-gene maxima of the trajectory statistic against transcript or protein '
 'response metrics. It follows that the manuscript\'s strongest empirical result - '
 'r = +0.374, n = 433, p = 8.2 x 10<super>-16</super>, partial r = +0.251 - is a '
 'statement about a squared displacement along one trajectory, while the abstract '
 'advertises a curvature contraction. Opus\'s phrasing is the sharpest and is confirmed: '
 'the experiments report a first-order object; the theory promises a second-order one.'))

story.append(H('II.2 The load-bearing theorem defects', 2))
story.append(TBL([
 ['Claim (theorem-level)', 'Audit', 'Verdict', 'Evidence and independent check'],
 ['Corollary 4.14\'s proof substitutes F = kappa_V and area = pi a<super>2</super> into '
  'Stokes, "giving H_geo = pi a<super>2</super>" - dimensionally incoherent '
  '(pi a<super>4</super> / V_max unless a<super>2</super> = V_max)',
  'U2 U4 U5 U6', V(VERIF),
  'Cor 4.14 proof (L1093-1097) verbatim: "substituting F = kappa_V and area(gamma_a) = '
  'pi a2 gives H_geo = pi a2". Re-derived: Stokes gives H = kappa_V x pi a<super>2</super> '
  '= (a<super>2</super>/V_max) x pi a<super>2</super>; equality to pi a<super>2</super> '
  'is a coincidence, not a theorem'],
 ['Lemma 4.10\'s uniform bound is vacuous as tau approaches 0 (denominator bound decays '
  'exponentially)',
  'U2 U4', V(VERIF),
  'Proof (L980-992): denominator bounded below by 2<super>-L/tau</super> x '
  'e<super>-beta diam(K)/tau</super>, which tends to 0; the claim "uniformly bounded '
  'over the family" is false as stated'],
 ['GLM\'s repair identity: grad r = beta x sum of pi_j grad q_j, hence '
  '|grad r| is of the order 2 beta L_d (diam + D), uniform in tau',
  'U2', V(VERIF),
  'Independently re-derived: r = -tau log sum w_j e<super>-beta q_j / tau</super>, so '
  'grad r = beta x sum pi_j grad q_j - the outer -tau cancels the 1/tau in the '
  'exponent derivative; the tau-dependence disappears exactly as GLM claims. Constant '
  'note in Part III'],
 ['Theorem 4.11(e) claims upper-semicomputability "as the sup of a computably '
  'enumerable family" while the family is indexed by a continuum',
  'U2 U4 U5 U6', V(VERIF),
  'Thm 4.11(e) (L1003-1010): kappa_alg = (1/V_max) sup over a in (0,a*] and unit '
  'bivectors of E\'(x; F(u,v)); both (tau, beta, D) and (a, bivector) are continua. '
  'Additional finding: the direction sup is a second continuum the audits did not '
  'flag explicitly - see Part V for the closure'],
 ['Remark 20.2 asserts kappa_V <= E - a derivative-ratio bounded by a function '
  'value (unit error)',
  'U2 U4 U5 U6', V(VERIF),
  'Remark 20.2 (L6743-6744): "kappa_V(theta, x) = [-D h_alpha]+ / h_alpha ... is '
  'therefore bounded above by the algorithmic envelope E". kappa_V has per-area units, '
  'E is a value; the stated justification (Lipschitz + Clarke subdifferential) does not '
  'yield the comparison'],
 ['E13 Theorem A: Phi(S) = {r in U: ...} is claimed "weakly contractive (Phi(S) '
  'contained in S)" - does not follow as displayed',
  'U2 U4 U6', V(VERIF),
  'Thm A (L5010-5014): membership is r in U, not r in S; Phi(S) contained in S fails '
  'until the one-line fix r in S is made (GLM D4)'],
 ['E13 Theorem B: uniqueness "by Strachey-Reynolds parametricity" - parametricity '
  'constrains polymorphic terms, not functors',
  'U2 U4 U6', V(VERIF),
  'Thm B (L5038): "to R (uniqueness by Strachey-Reynolds parametricity restricted to '
  'typed polynomial optics)". No free theorem of this form exists; GLM and Opus '
  'independently recommend deletion, Kimi proposes adjoint-uniqueness restatement'],
 ['Corollary 17.3 is contentless as a classification ("identified by the univalence '
  'axiom with a single term in the HoTT universe U")',
  'U2 U4 U6', V(VERIF),
  'Cor 17.3 (L2697-2705) verbatim; the type of contractible groupoids is itself '
  'contractible, so the identification carries no classification content; the univalence '
  'invoke is decorative'],
 ['Theorem 3.5 says a loop crosses a separating boundary "once" while the '
  'manuscript\'s own numerics give n_cross = 2 (rectangular and pentagon loops)',
  'U2', V(VERIF),
  'Thm 3.5 (L412): "of area epsilon2 crossing the boundary once"; verification scripts '
  'report (L448-453): "crossing the boundary twice ... n_cross = 2"; a closed transverse '
  'loop crosses a separating boundary an even number of times'],
 ['Theorem 3.14\'s tuple (Theta, pi, Delta<super>n-1</super>, epsilon, Gamma) has '
  'drifted from Definition 3.1\'s (B, E, P, epsilon, Gamma)',
  'U2 U4 U6', V(VERIF),
  'Thm 3.14 (L616) vs Def 3.1 (SAVGS, Sec 3); both renderings confirmed in the v21 '
  'PDF text'],
 ['Proposition 3.16\'s "unit sphere" is wrong by a factor of 2 (the Fisher-Rao '
  'simplex is radius-2 spherical under psi = 2 sqrt(p))',
  'U2', V(VERIF),
  'Prop 3.16 (L672-677): "psi_a = 2 sqrt(p_a) places the open simplex on the positive '
  'orthant of the unit sphere" together with d_FR = 2 arccos(...). Checked on the '
  'binary simplex: geodesic integral of dt/sqrt(t(1-t)) from 0 to 1 equals pi, which is '
  'the radius-2 geodesic, not the unit-sphere geodesic pi/2; the image of 2 sqrt(p) '
  'has norm 2. GLM\'s radius-2 finding is correct'],
 ['Remark 2.4\'s "the Fisher-Rao stabilizer is CO(2) = R+ semidirect SO(2)" is a '
  'label error; the round-metric point stabilizer is O(n-1)',
  'U2', V(VERIF),
  'Remark 2.4 (L246-248) states CO(2) flatly, while Remark 2.3 (L239-244) correctly '
  'derives when a CO(r) reduction is justified (Fisher-Weyl policy structure with '
  'positive scale). The Lie-algebra content (so(2) abelian at n = 3, so(3) non-abelian '
  'at n >= 4) survives with corrected labels'],
 ['Proposition 19.7\'s Zeno lower bound tau >= 1/(1 + log2(N_RAF)) is '
  'manufactured (closure depth is not logarithmic)',
  'U2', V(VERIF),
  'Prop 19.7 (L4263-4272) states exactly that bound; chains can descend by one '
  'reaction per step, so stabilization in at most |U| iterations at O(|U| x |R|) cost '
  'is the true statement (GLM T4)'],
 ['The fitted 3/2 fatigue exponent framing ("verified to within 1.4%") overstates: '
  'the theory value 1.500 lies outside the bootstrap CI [1.471, 1.493]',
  'U2', V(CORR),
  'The 1.4% framing appears at L130, L2025, L7246; the CI disclosure appears once '
  '(L2013-2017) with an honest bias explanation. GLM\'s "report that the fitted '
  'exponent lies outside the quoted CI" misstates the direction (it is the theory '
  'value that lies outside the fitted CI, and the manuscript does disclose it once) - '
  'the real defect is the inconsistent framing across sites, not a hidden CI'],
], [0.29, 0.065, 0.12, 0.525]))
story.append(TCAP('Table 3. Theorem-level defects, with this assessment\'s independent '
 're-derivations where the claim was checkable by hand.'))

story.append(H('II.3 Type-level and structural defects', 2))
story.append(TBL([
 ['Claim', 'Audit', 'Verdict', 'Evidence'],
 ['dist_D - defined on strings (Def 4.1) - is applied to RAF sets',
  'U2 U5 U6', V(VERIF),
  'D_phi(dist_D(R), dist_D(R0)) appears at three sites: Table 1 optic O1 residual '
  '(L1232), the RAF-optic definition (L1291), and the Section 16 composite (L2398). '
  'Location sharpened relative to the audits\' "Def 3.21" attribution'],
 ['Def 2.5 makes the residual part of the optic OBJECT (triple (M, C, R)) while '
  'citing Riley, whose objects are pairs with existentially-quantified residuals',
  'U2 U3 U4 U6', V(VERIF),
  'Def 2.5 (L264-268): "objects triples (M, C, R) ... (Proposition 2.3 of [4])"; the '
  'citation does not match the structure it is cited for'],
 ['The realization functor R is invoked six times and never defined; Remark 7.8 '
  'concedes the gap',
  'U2 U3 U4 U6', V(VERIF),
  'Remark 7.8 (L1357-1367): "The full functorial construction is open"; "a '
  'realization functor R from endo-optics to endomaps" is used without construction'],
 ['Theorem 8.2 is proven for seven generic resnet-style blocks, not for the seven '
  'optics of Table 1',
  'U2 U3 U6', V(VERIF),
  'Sec 8.1 (L1406-1417): f_i(x) = (1 - a_i) x + a_i s_i sigma(W_i x + b_i); the '
  'numbers never refer to the categorical objects; product 0.92<super>6</super> x 1.15 '
  '= 0.6973 verified arithmetically'],
 ['"Bregman-regularized" is a misnomer: T_reg = (1 - lambda) T + lambda Pi_K(T) '
  'contains no Bregman divergence, and is in fact the Krasnoselskii-Mann averaged form',
  'U2', V(VERIF),
  'L1433, L2313: T_reg(K) = (1 - lambda) T(K) + lambda Pi_K(T(K)) with the Moreau '
  'projection invoked (L1443); the KM identification confirmed by inspection of the '
  'formula - this is GLM\'s most constructive T5 contribution'],
 ['Prop 16.2 / Prop 16.7 items 3-4: "kappa_V(R_max) = kappa_V(R_i) = 0 verified to '
  '10<super>-9</super>" is 0 = 0 on an object where kappa_V is undefined; '
  '"falsifiable prediction" is a category error',
  'U2 U6', V(VERIF),
  'Prop 16.2 (L2424-2434): "agrees within machine precision (10-9)"; Prop 16.7 '
  '(L2593-2600): "Both sides are zero to within 10-9" under the heading "Falsifiable '
  'prediction". A discrete RAF set carries no declared geometry for Prop 4.4\'s '
  'curvature'],
 ['The inverse-limit / colimit confusion recurs (section titled "Filtered-Colimit '
  'Construction" whose proposition item is labeled "Inverse limit" with projection '
  'arrows)',
  'U2', V(VERIF),
  'Prop 16.7 item 2 (L2588-2590): "Inverse limit: ... The 15 projection arrows '
  'R_max to R_i ... witnessing the universal property of the limit" inside Sec 16'],
 ['Def 19.9\'s persistent-homology "contractibility test" tests homology, not '
  'contractibility; Remark 17.5\'s Phase III is a 30% statistics-matching tolerance',
  'U2', V(VERIF),
  'Def 19.9 (L4306-4315): barcodes via ripser; Remark 17.5 (L2749-2760): "mean, max, '
  'and min within relative tolerance tau = 0.30". Persistent homology cannot detect '
  'contractibility; GLM\'s Poincare/averaging replacement (D6) absorbs the one real '
  'insight (limit cycles are not endpoint failures)'],
 ['Table 1 residuals are English phrases ("residual = Holevo information ..."), not '
  'fiber objects',
  'U2', V(VERIF),
  'L1232-1234: "residual = Holevo information I(rho_out; rho_hat_in)"; the seven '
  'residuals are semantics, not typed objects'],
 ['Sections 8 and 15 duplicate the contraction analysis',
  'U2', V(VERIF),
  'Both state the product bound (L1417 vs L1499) and both carry Banach-contraction '
  'narrative; Sec 8 is analytic, Sec 15 numerical (375-configuration grid) - partial '
  'duplication, full merge feasible'],
 ['The "kernel constant kappa of order unity" in C_fat = sqrt(nu/2) x kappa is '
  'never derived',
  'U2', V(VERIF),
  'L1978, L7246: the constant is declared "of order unity" rather than derived from '
  'the Levy first-passage normalization, which is explicit'],
], [0.29, 0.065, 0.12, 0.525]))
story.append(TCAP('Table 4. Type-level and structural defects.'))

story.append(H('II.4 Coherence and editorial layer (all persisting in v21)', 2))
story.append(TBL([
 ['Claim', 'Audit', 'Verdict', 'Evidence'],
 ['Six different network counts persist',
  'U1 U2', V(VERIF),
  'v21 tex: "four real biochemical networks" (L135, L329), "two" (L426, L4285), "ten" '
  '(L10166); the 2nd-wave count (2/4/2/4/10) persists in redistributed form - a single '
  'network registry is still missing'],
 ['Table 4 is claimed updated three times but lists only the nine E1-E9 studies',
  'U1 U2', V(VERIF),
  'Caption (L4101): "Nine novelty-assessment elevation studies"; update claims at '
  'L4663, L4787, L5094 (Remarks 19.18, 19.22, 19.28)'],
 ['"No open conjectures remain" contradicts two explicitly open items in the body',
  'U1 U2', V(VERIF),
  'L7475: "no open conjectures remain"; L7229: "five conjectures ... now closed"; vs '
  'Remark 20.2\'s own "Conjecture 21.1 ... separate, well-defined open problem" and '
  'Remark 7.8\'s open endofunctor construction'],
 ['Section 19 is a change log (19.1-19.23), and version-history framing persists in '
  'definition titles',
  'U1', V(VERIF),
  'Subsections 19.1-19.23 span L4053-L6659; Def 3.21\'s title carries "v10 main '
  'definition"; "backward comparability with the v1-v9 elevation studies" (L787)'],
 ['Session provenance persists: "the user", audit names, commit hashes, folder paths, '
  'COLOMBOS notes',
  'U1', V(VERIF),
  'Counts in the v21 PDF: "the user" x6 (case-sensitive; 12 case-insensitive), '
  '"Qwen" x34, commit 07e6d85 x5, COLOMBOS x3, patch-script names and download/ paths '
  'throughout Sec 19'],
 ['The authorship statement is contradicted by the body\'s round-by-round narration',
  'U1', V(VERIF),
  'L7539-7543: "the model did not originate novel [results]" vs Sec 19\'s documented '
  'AI-executed study lineage (v1-v21 rounds, audit responses, user-requested variants)'],
 ['Def 2.1\'s "not a curvature 2-form" disclaimer is contradicted by Cor 4.14 / E1 '
  'treating the radial identity as curvature content',
  'U2', V(VERIF),
  'Def 2.1 (L204-216) disclaims; Cor 4.14 computes H_geo from the same radial object; '
  'E1 (Sec 10) uses "kappa_V = a<super>2</super> by Stokes theorem"'],
 ['Claims A-E are simulations of textbook identities or of the simulator\'s own '
  'generating law, not experiments',
  'U2', V(VERIF),
  'Table 3 (L2055-2062): "slope = 1", "arev = 1.0" - identities of the generating law; '
  'GLM\'s reclassification as estimator calibration is sound and consistent with the '
  '2nd-wave finding'],
 ['The zero-control and partial-correlation honesty layer is intact',
  'this assessment', V(VERIF),
  'E24 (L6310-6340): zero-control MWU p = 7.8 x 10<super>-22</super>; partial r = '
  '+0.251 reported with its own limits ("not unconfounded"); E26/E27 protein-layer '
  'nulls and magnitude parity reported without inflation'],
], [0.29, 0.065, 0.12, 0.525]))
story.append(TCAP('Table 5. Coherence and editorial layer.'))

story.append(H('II.5 Items the audits list that v21 already resolved', 2))
story.append(P(
 'The audits reviewed the 131-page v20. The v21 mechanical-integrity round (commit '
 'ddbb384, 29 verified corrections) resolved a subset of overlapping items before this '
 'assessment: the broken citation key orth2011comprehensive now renders correctly '
 '(resolving one of DeepSeek\'s four citation-integrity items; the other three - twelve '
 'never-cited references, six false "Cited in SX" annotations, and the authorship '
 'statement - remain, still HELD as P0-editorial pending the strategic decision); the '
 'E25 +0.187 (n=241) conflations were corrected to the primary +0.191 with an explicit '
 'common-set reconciliation note; the Def 3.18 step labels and the Table 6 clipping '
 'were repaired (P1); and the EC-number corrections were applied. Nothing else in the '
 'six audits\' scope was touched by v21, so every remaining verdict above is current. '
 'The practical consequence for planning: of the combined 2nd-wave-plus-3rd-wave '
 'defect inventory, only the mechanical stratum is complete; the editorial, '
 'mathematical, and structural strata are exactly as the audits describe them.'))

# =========================================================== PART III ======
story += PART('Part III', 'Audit Errors: Corrections and Refutations')

story.append(P(
 'The standing instruction for this assessment - and the reason it exists - is that '
 'audit claims are not taken at face value. Eight audit statements failed verification '
 'or need material qualification. None of them changes the direction of the overall '
 'verdict; several of them change what v2 should implement, which is precisely why '
 'they are worth isolating before any repair work starts.'))

story.append(TBL([
 ['#', 'Audit', 'Erroneous or imprecise statement', 'Correction, with basis'],
 ['1', 'Kimi (U4)',
  'R2 as stated: "for y to x, kappa_t / ||t - T1||<super>2</super> converges to the '
  'curvature form along the trajectory tangent"',
  'The limit is the Hessian-metric ENERGY, not curvature: D_phi(v(T1), v(t)) is '
  'approximately (1/2)|v-dot(T1)|<super>2</super> |t - T1|<super>2</super> under the '
  'surrogate metric, i.e. the squared norm of the tangent vector (gpt\'s "local '
  'response metric" and opus\'s "Phi itself"), not a second-order curvature '
  'contraction. A one-parameter path cannot yield sectional curvature without second '
  'differences. With R2 corrected, kimi\'s framework agrees with gpt/opus instead of '
  'conflicting with them'],
 ['2', 'Muse (U5)',
  '"The mask is the indicator that iota(v) and iota(v_wt) lie in different strata of '
  'B - a discrete proxy for crossing the singular locus"',
  'Imprecise for the manuscript\'s actual mask. The mask 1[delta_b > tau b_wt] '
  'selects nonzero single-knockout BIOMASS DEFICIT (opus\'s reading, exactly right for '
  'Def 3.21); a non-essential knockout can still reroute fluxes and cross active-set '
  'strata with mask = 0 - the manuscript\'s own dR(g) = {r : |v_r(KO) - v_r(WT)| > '
  '10<super>-6</super>} is defined precisely for such changes. The stratum-crossing '
  'reading requires the nondegeneracy assumption "no rerouting without deficit". The '
  'defensible formulations are GLM\'s (mask = gene-level positive part, consistent '
  'with [ . ]<sub>+</sub> in kappa_V\'s own definition) and opus\'s (deficit '
  'sparsification); kimi\'s Lambda-restriction is a redefinition that changes the '
  'formula'],
 ['3', 'Opus (U6)',
  '"Def 3.21 ... is the mixed-difference curvature with knockouts as perturbations '
  'and biomass deficit as the deficit function ... precisely the standard FBA measure '
  'of flux rerouting capacity"',
  'Aspirational, not descriptive. Def 3.21 as written is a single-knockout squared '
  'displacement (a Phi-slot value in opus\'s own notation); the epistasis object '
  'requires the double-knockout recomputation of Route C2. The reinterpretation is '
  'the correct TARGET for v2; presenting it as the current content of Def 3.21 would '
  'reproduce at the audit layer exactly the conflation the audits are trying to '
  'remove'],
 ['4', 'GLM (U2)',
  '"for the prototype instantiation, product of alpha_i = 0.697 x 1.15 = 0.802 on the '
  'enlarged box X = [0, 1.15]<super>d</super>, which removes the need for the '
  'projection patch"',
  'Not derivable from the manuscript as stated: f_2 = 1.15 x does not map '
  '[0, 1.15]<super>d</super> into itself (1.15 x 1.15 > 1.15), so the enlarged-box '
  'route needs a different construction than the one implied. The SOUND part of GLM '
  'T5 is the Krasnoselskii-Mann identification, which this assessment confirms '
  'structurally: T_reg = (1 - lambda) T + lambda Pi_K(T) already IS the KM averaged '
  'form. The 0.802 constant should be treated as to-be-derived, not as fact'],
 ['5', 'GLM (U2)',
  'Lemma 4.10 repair bound "|grad r| <= 2 beta L_d (diam K + D)"',
  'The identity grad r = beta sum pi_j grad q_j is verified correct (the outer -tau '
  'cancels). The constant needs max over j of sup over K of [d - D]<sub>+</sub> '
  'rather than diam K + D, unless codewords are assumed to lie in K - codewords are '
  'arbitrary strings. A one-line completion, stated here so v2 does not import an '
  'off-by-geometry constant'],
 ['6', 'GLM (U2)',
  '"kappa_V<super>FBA</super> (Def 2.6 ...)" in the thread table',
  'Def 2.6 is the RAF-set definition; the FBA statistic is Def 3.21. Citation slip '
  'only - GLM\'s claim set otherwise had the highest verification rate of the six '
  'audits'],
 ['7', 'DeepSeek (U1)',
  '"a broken citation key" (present tense, in the citation-integrity list)',
  'STALE: resolved in v21 (commit ddbb384). DeepSeek\'s other three citation-integrity '
  'items remain valid. A v20-era artifact, not an error of judgment'],
 ['8', 'GLM (U2)',
  '"Report that the fitted exponent lies outside the quoted CI rather than \'verified '
  'to within 1.4%\'"',
  'Direction reversed: it is the THEORY value 1.500 that lies outside the fitted '
  'CI [1.471, 1.493], and the manuscript already discloses this once with a bias '
  'explanation (L2013-2017). The genuine defect is the inconsistent framing - three '
  '"verified to within 1.4%" sites vs one honest CI site - and the un-derived kernel '
  'constant (which GLM correctly flags separately)'],
], [0.028, 0.075, 0.335, 0.562]))
story.append(TCAP('Table 6. Audit errors and qualifications found by this assessment.'))

story.append(P(
 'Two systemic observations complete this part. First, no audit made an error in the '
 'direction that would soften the manuscript\'s problems: every correction above '
 'either tightens an already-confirmed defect or shifts a repair detail. The audits '
 'are individually reliable and jointly complementary, which is what makes the Part V '
 'synthesis worth building. Second, the corrections cluster where theory meets the '
 'manuscript\'s actual formulas: kimi\'s R2 and muse\'s mask reading both fail against '
 'the literal text of Def 3.21 and E22, which is a structural argument for opus\'s '
 'sequencing advice - do the mechanical re-typing pass FIRST, because several '
 '"broken" objects turn out to be mislabeled rather than wrong, and several '
 '"unified" claims turn out to be conflations rather than theorems; only a typed '
 'naming layer makes the difference visible.'))

# =========================================================== PART IV =======
story += PART('Part IV', 'Cross-Audit Triangulation')

story.append(P(
 'Treating the six audits as independent measurements of the same object makes their '
 'agreements informative in a way any single audit cannot be. Seven triangulation '
 'points emerged; five are strong multi-audit convergences, and two are the genuine '
 'disagreements that Part V has to adjudicate.'))

story.append(TBL([
 ['Convergence', 'Audits', 'Content and strength'],
 ['C1. Typed renaming with the geometric object as the only kappa',
  '6 / 6',
  'Every audit ends with a distinct typed name for each object (kappa<super>geom</super> '
  '/ K<super>FBA</super> / kappa-hat<super>emp</super> / Delta<super>R</super> / '
  'kappa<super>Lambda2</super>-kappa<super>ko</super>-kappa<super>t</super>). Muse\'s '
  'migration checklist, kimi\'s "no bare kappa" rule, and gpt\'s naming table are '
  'enforceable by mechanical search - the only kind of rule that survives contact with '
  'a 10,830-line source'],
 ['C2. The FBA active-set / mpLP critical-region stratification is the bridge '
  'substrate',
  '5 / 6 (U2 U3 U4 U5 U6)',
  'GLM T7(a) (mpLP critical regions ARE the base strata), opus G-B (curvature lives '
  'on basis-change loci; LP value function piecewise-linear so curvature is singular '
  'on strata), gpt\'s mapping table (active LP basis to stratum), kimi\'s embedding '
  '(knockout simplex with face restrictions), muse\'s stratum-crossing reading. This '
  'is the strongest mathematical convergence of the wave: the geometric thread\'s '
  'strata and the FBA thread\'s active-set decomposition are the same object, and '
  'opus\'s corollary - in the generic non-degenerate case the smooth curvature '
  'vanishes and ALL curvature concentrates on the transition loci - explains in one '
  'sentence why the essentiality mask, the non-abelian signatures, and the '
  'constraint-switch hysteresis all live in the same place'],
 ['C3. The provable glue is the energy/response-divergence level',
  '4 / 6 (U3 U5 U6 + U4 after correction)',
  'Gpt\'s proposition (D_phi(v_beta(p + h xi), v_beta(p)) = (h<super>2</super>/2) '
  'Hessian-quadratic + O(h<super>3</super>)), muse\'s Theorem U first display, opus\'s '
  'Phi-level reading, and kimi\'s R2 (once corrected to energy) all state the SAME '
  'theorem in different notation: the FBA and time-course statistics are consistent '
  'finite-difference proxies for the induced Hessian-metric energy, not for '
  'curvature. This theorem is provable now and is the honest content of the current '
  'E24-E27'],
 ['C4. Curvature measurement needs two directions',
  '2 / 6 explicit (U3 U6), all 6 implicit',
  'Gpt\'s four-condition plaquette (p, p + h xi, p + k eta, p + h xi + k eta) with '
  '(P - I)/(hk) converging to the curvature operator; opus\'s Route C1 (second '
  'differences on existing time courses - free) and Route C2 (double knockouts - '
  'the epistasis design). The theory\'s discriminating prediction is which PAIRS '
  'show super-additive deficit'],
 ['C5. The shared repair list',
  'all repairs have 3+ audit sponsors',
  'Cor 4.14, Lemma 4.10, Thm 4.11(e), Remark 20.2, E13 Thm A, E13 Thm B, Cor 17.3, '
  'the realization-functor fork (define monoidically on concrete optics - GLM D3, '
  'opus\'s evaluation-at-fiber-map, kimi\'s residual-assigned optics - or excise '
  'thread C), the tuple freeze, the KM retargeting of Thm 8.2, and one notation '
  'table. Where 3+ audits state a repair for the same defect, the repairs coincide '
  'in substance'],
 ['C6. Strong-form unification is not provable in scope',
  '6 / 6',
  'Kimi\'s warning is the crispest ("strong-form unification ... probably not '
  'provable within this manuscript\'s scope and should not be claimed"; R4 is '
  'conditional with H3 a paper of its own); muse\'s Theorem U is explicitly '
  'conditional with a fallback table; gpt\'s discrete-realization theorem is '
  'conditional on a transport construction "not supplied by FBA automatically"; '
  'opus requires "an explicit inequality or error term" or the paper splits; GLM '
  'prices T2 and T7 at months each; DeepSeek demands "all internal '
  'inconsistencies reconciled" before any such claim. The joint position: only '
  'conditional transfer theorems with labeled hypotheses are honest'],
 ['C7. The real disagreement: delete or demote',
  'U2 vs U1',
  'GLM would delete Section 17 wholesale, Cor 4.14, Theorem B, Prop 16.2, Prop 19.7, '
  'and the Zeno/Levy analogies; DeepSeek\'s standing instruction is "prioritize '
  'rigorous elevation of math, repair and demoting to conjecture over removal". '
  'Part V resolves this with a three-tier adjudication'],
], [0.185, 0.105, 0.71]))
story.append(TCAP('Table 7. Triangulation across the six audits.'))

story.append(P(
 'One convergence deserves emphasis because it is invisible in any single audit. '
 'GLM\'s T2 (non-abelian information concentrates at the boundary as a group-valued '
 'jump cocycle), opus\'s G-B corollary (curvature is singular, supported on '
 'basis-change loci), kimi\'s embedding (the discrete statistic is a sampled '
 'connection coefficient on a masked subbundle), and muse\'s mask reading (crossing '
 'the singular locus where Gamma jumps) are four descriptions of ONE phenomenon: '
 'in a stratified system, the second-order object that the experiments can see is '
 'concentrated on the strata transitions, not distributed over the smooth cells. '
 'That statement is simultaneously the paper\'s actual thesis (opus: "currently '
 'invisible"), the reason the essentiality mask is not an ad hoc device, and the '
 'reason the non-abelian signature appears exactly at constraint switches. A v2 '
 'that states this once, early, and derives everything else from it would be a '
 'different and much stronger paper than one that renames three objects and stops.'))

# =========================================================== PART V ========
story += PART('Part V', 'The Synthesized Unification Architecture')

story.append(P(
 'The six proposals are not competitors; they are layers of one architecture that '
 'none of them states completely. What follows is the adjudicated assembly - the '
 'product of this assessment\'s strengthening mandate. Each layer names its source '
 'audits, what it fixes, and what it costs.'))

story.append(H('Layer 0 - Notation protocol (mechanical, v2 pass 1)', 2))
story.append(P(
 'Adopt muse\'s migration checklist as written, kimi\'s "no bare kappa" rule (the '
 'symbol kappa appears only as the family or with an instantiation decoration), and '
 'gpt\'s naming table: kappa<super>geom</super> for the geometric curvature, '
 'K<super>FBA</super> / Delta<super>FBA</super> for the knockout statistic, '
 'Phi<sub>obs</sub> / Delta<super>time</super> for the trajectory statistic, with '
 'forbidden-use columns per muse\'s disambiguation table (never called curvature, '
 'never compared to E, never claimed to be Prop 4.4\'s object). A one-page '
 'notation-generation table in Section 2 enforces the rule mechanically. Fix the '
 'typed-citation defects in the same pass: Def 6.1 cites the D_V/curvature datum '
 'rather than "the kappa_V of Definition 2.1"; dist_D is applied only to strings '
 '(the three D_phi(dist_D(R), dist_D(R0)) sites become dist_D applied to declared '
 'encodings, or are replaced by the Layer-1 datum); the SAVGS tuple is frozen as '
 '(B, E, P, epsilon, Gamma) with Thm 3.14\'s (Theta, pi, Delta) recorded once as '
 'the special case. Opus\'s caution applies: run this pass BEFORE any theorem '
 'repair, and expect it to expose mislabelled-but-correct proofs and correct-'
 'but-mislabelled claims - the pass itself is the diagnostic.'))

story.append(H('Layer 1 - The central object, factored (the adjudication)', 2))
story.append(P(
 'Five candidate central objects were proposed. The adjudication: adopt opus\'s '
 'curvature datum as the combinatorial DEFINITION, keep kimi\'s slot family as the '
 'smooth organization of the geometric thread, keep gpt\'s realization datum as the '
 'formal wrapper for the response-divergence layer, and keep GLM\'s h-margin '
 'version as the viability-theoretic instantiation that carries the erosion '
 'inequality. The rationale is in the table below; the one-sentence version is that '
 'opus\'s mixed difference is the only candidate under which the RAF instantiation '
 'is well-typed (it fixes Prop 16.2 for free), Prop 4.4 is recovered as a theorem '
 'rather than an assumption (Proposition G), and the FBA object becomes epistasis - '
 'the honest target - at the cost of one recomputation.'))
story.append(TBL([
 ['Candidate', 'Type safety', 'RAF instantiation', 'Recovers Prop 4.4?', 'Recompute cost', 'Verdict'],
 ['Opus: kappa = sup over a,b of [Phi(abx) - Phi(ax) - Phi(bx) + Phi(x)]+',
  'Clean (set-level)', 'Well-typed via (X, A, Phi) with catalyst removals',
  'Yes, as epsilon<super>2</super> x Hessian coefficient (Proposition G)',
  'Route C2 recompute for FBA', 'ADOPT as the definition'],
 ['Kimi: slot family kappa[d, c, Lambda]',
  'Clean on smooth strata', 'Needs a declared geometry',
  'Yes, as the infinitesimal slot value',
  'None for existing studies', 'ADOPT as the smooth organization (Lambda-domains; R1/R3 usable)'],
 ['GPT: realized divergence Delta_R',
  'Most complete typing (mask, normalization, observation map explicit)',
  'Out of scope by design', 'As Curv_x of Delta_R',
  'None for existing studies', 'ADOPT as the formal wrapper for response divergences'],
 ['GLM: kappa_V = sup max_alpha [-D h_alpha]+ / h_alpha (h a smooth margin)',
  'Clean', 'Out of scope', 'Direct (it IS the viability form)',
  'None', 'ADOPT as the viability instantiation; carries T3 erosion inequality'],
 ['Muse: canonical kappa<super>geom</super> = (1/E) sup [Breg_r]+',
  'Clean but keeps the algorithmic surrogate inside the geometric object',
  'Undefined', 'It IS Prop 4.4', 'None', 'PARTIAL - keep as the envelope-linked form; E-normalization noted as a choice, not a necessity'],
], [0.235, 0.13, 0.16, 0.155, 0.14, 0.18]))
story.append(TCAP('Table 8. The five candidate central objects and the adjudication.'))

story.append(P(
 'The essentiality mask is re-instantiated in this layer, and the five audit '
 'readings collapse to two that are correct: the mask is the gene-level positive '
 'part on the single-knockout deficit (GLM\'s consistency reading and opus\'s '
 'sparsification reading, which coincide for Def 3.21 as written), and kimi\'s '
 'Lambda-restriction is available as a variant that must be declared as a '
 'redefinition if adopted. Muse\'s stratum-crossing reading survives only as a '
 'conditional statement under a stated nondegeneracy assumption. GLM\'s '
 'pre-registration framing converts the v10 promotion episode from a defect into a '
 'declared estimator choice only if the tau = 0.05 scale is stated ex ante in v2 - '
 'one sentence, but it is the difference between definition shopping and an '
 'estimator protocol.'))

story.append(H('Layer 2 - The two provable transfer theorems (now)', 2))
story.append(P(
 'Two transfer statements are provable with the material already in hand, and they '
 'are the honest glue for the existing studies. T-energy (gpt\'s proposition, = '
 'muse\'s Theorem U part 1, = kimi\'s R2 corrected): on a fixed active-set stratum '
 'with the regularized optimum v_beta (strictly concave objective, unique and '
 'differentiable by construction - gpt\'s v_beta or kimi\'s barrier, with the '
 'strict-convexity caveat of Part III item routed through the regularized optimum '
 'rather than through the code surrogate), the FBA and time-course statistics are '
 'consistent finite-difference proxies for the induced Hessian-metric energy. '
 'T-bound (kimi R1 + R3, both "trivial after definition" but the first true '
 'sentences connecting the flagship to the abstract): plane-restricted and '
 'domain-restricted statistics are bounded by the full-sup object once the '
 'embedding is fixed, and the one-direction knockout sample is a singleton-plane '
 'instance. What must NOT be claimed is the strong form (all six audits agree; '
 'kimi\'s R4 stays conditional with H1-H3 labeled, muse\'s fallback table is the '
 'printed escape hatch).'))

story.append(H('Layer 3 - The three new measurements (strengthened from the audits)', 2))
story.append(P(
 'This is where the assessment completes the audits\' weaker suggestions into a '
 'concrete work program. M1 (opus Route C1, cost: days): compute genuine second '
 'differences kappa-hat(t) = [Phi(t + 2 Delta) - 2 Phi(t + Delta) + Phi(t)]+ on the '
 'EXISTING time courses - data availability verified: GSE64021 provides six points '
 'per condition (15 min to 6 h), the M3D carbon-exhaustion series provides a '
 'reference plus four stationary points, and the E10/E22 dynamic-FBA trajectories '
 'already export kappa per time point T1-T8. Opus calls this a two-line '
 'computation; the assessment confirms the data exist and adds that it converts '
 'E24-E27 from "validates the deficit function" to "measures the deficit function '
 'AND its first curvature slice". M2 (gpt\'s plaquette, cost: weeks): the '
 'four-condition estimator with regularized optima, directions chosen from the '
 'high-kappa genes, converging to kappa<super>geo</super> under gpt\'s stated '
 'hypotheses - with gpt\'s own caveat printed in the theorem statement: the GC '
 'parallel transport must be constructed from FBA sensitivity data; FBA does not '
 'supply it automatically. M3 (opus Route C2, cost: weeks): sampled double-gene '
 'knockouts in iJO1366 - all pairs within the top kappa decile plus stratified '
 'random pairs - measuring the epistasis excess directly. The assessment\'s '
 'augmentation: M3 is executable in silico now (cobrapy plus quadratic '
 'regularization, the same tooling as E12/E15/E16), which converts opus\'s "the '
 'experiment the theory actually predicts" from an aspiration into a runnable '
 'study; the theory predicts WHICH PAIRS show super-additive deficit, and that '
 'prediction is testable against the mixed-difference ranking. Together M1-M3 move '
 'the empirical program from "a conjectured transfer" to "a measured transfer at '
 'the energy layer plus first curvature-slice measurements" - the single largest '
 'value-add this wave can deliver.'))

story.append(H('Layer 4 - The theorem repair tiers (resolving delete-vs-demote)', 2))
story.append(P(
 'The C7 disagreement resolves into three tiers, satisfying DeepSeek\'s elevation '
 'preference wherever the object is recoverable and GLM\'s coherence requirement '
 'wherever it is not. Tier R (repair in place): Lemma 4.10 by the softmax identity '
 '(verified in Part II, with the Part III constant completion); Thm 4.11(e) by the '
 'rational grid plus equicontinuity - to which this assessment adds the missing '
 'second half: the direction supremum is closed by a countable dense subset '
 '(the supremum of a continuous function over a compact set equals its supremum '
 'over any dense subset), so both continua in (20) are dischargeable by two short '
 'lemmas; Remark 20.2 by GLM\'s three-line corollary (on {h >= epsilon}: '
 'kappa_V = [-Dh]+/h <= Lip(h)/h <= Lip_loc(E)/epsilon - dimensionally '
 'correct, provable, and the honest content of "the upper-bound language is a '
 'theorem"); Prop 3.16 by the one-line radius-2 fix; Remark 2.4 by the stabilizer '
 'relabel; Thm 3.5 by GLM\'s T2 jump-cocycle restatement (the correct theorem is '
 'BETTER than the stated one: smooth curvature at epsilon<super>2</super>, '
 'non-abelian information as a boundary jump cocycle indexed by the crossing '
 'word); Thm 3.4 by the exact gauge form with the BCH form demoted to a derived '
 'corollary; E13 Thm A by the r-in-S line plus Tarski/Hordijk-Steel; Thm 8.2 by '
 'the KM retargeting with "Bregman-regularized" renamed; Thm 3.14 by the tuple '
 'freeze. Tier D (demote with absorption): E13 Thm B to an adjoint-uniqueness '
 'conjecture (kimi\'s restatement); Section 17 (HoTT layer) to a companion note, '
 'with its one real insight - limit cycles are not endpoint failures - absorbed '
 'into the closure criterion via Poincare-section sampling (GLM D6), and Remark '
 '17.5\'s 30% tolerance retired with it; the Zeno/Levy material re-labeled as '
 'analogy or attached to kimi\'s kappa<super>t</super> fluctuations; Claims A-E '
 'reclassified as estimator calibration; Prop 16.2 and 16.7(3-4) re-typed through '
 'the Layer-1 datum; Prop 19.7 replaced by the at-most-|U| stabilization statement; '
 'Cor 4.14 to a worked appendix example with the normalization explicit. Tier E '
 '(excise): the six false "Cited in SX" annotations and twelve never-cited '
 'references (the HELD P0-editorial items, now scheduled); "no open conjectures '
 'remain"; the version-history framing; the network-count registry replaced by '
 'one table. Nothing in Tier E destroys recoverable mathematics - which is the '
 'test DeepSeek\'s policy demands and GLM\'s list, as amended, now passes.'))

# =========================================================== PART VI =======
story += PART('Part VI', 'Implementation Plan and the v2 Protocol')

story.append(H('The versioning protocol (binding)', 2))
story.append(P(
 'Per the project directive issued with this wave: the latest manuscript version is '
 'not to be touched. v21 (commit ddbb384) is hereby the FROZEN REFERENCE BASELINE - '
 'the state of the manuscript against which every audit verdict above was rendered, '
 'and the artifact on which the strategic decision is to be made. From here on, every '
 'major rewrite is a NEW document: journal_manuscript_v2.tex is created from the v21 '
 'source and carries the Layer 0-4 program; subsequent rounds produce v3, v4, and so '
 'on, each as a new file with its own compile, QA, and commit. Even minor errata are '
 'not applied to the frozen v21; if an erratum matters it belongs in v2. The frozen '
 'baseline guarantees that the audits, this assessment, and the eventual strategic '
 'decision all refer to one immutable object - the failure mode this protocol '
 'prevents is the one the manuscript itself documents, where v10 definitions, v14b '
 'corrections, and v17 results coexist in one text with no clean reference point.'))

story.append(H('Sequencing', 2))
story.append(TBL([
 ['Step', 'Action', 'Prerequisite', 'Cost', 'Output'],
 ['0', 'Strategic decision: single coherent article (GLM\'s 60-90 pp estimate; '
  'DeepSeek\'s single-narrative requirement) vs. split into a main paper plus '
  'companion notes (opus/gpt\'s excision path; the HoTT and dynamics material as '
  'companions)',
  'this assessment (the decision input is now complete)', 'days of deliberation',
  'A written decision document; all downstream scoping depends on it'],
 ['1', 'v2 pass 1 - Layer 0 mechanical re-typing of the full source (renaming, '
  'typed citations, tuple freeze, network registry, version-framing strip)',
  'step 0', '1-2 weeks',
  'journal_manuscript_v2.tex; expect 1-2 additional results killed and at least one '
  '"broken" proof revealed as fine (opus\'s prediction, endorsed)'],
 ['2', 'Layer 2 theorems (T-energy, T-bound) written and proven in v2',
  'step 1', '2-4 weeks',
  'The first honest flagship-abstract link'],
 ['3', 'M1 second differences on existing time courses (E28-class study)',
  'step 1 only', 'days',
  'New results files + v2 subsection; the first measured curvature slice'],
 ['4', 'M2 plaquette estimator + M3 double-KO epistasis study (E29/E30-class)',
  'steps 1-2', '2-6 weeks',
  'The mixed-difference ranking and its test against super-additive deficit pairs'],
 ['5', 'Layer 4 Tier R theorem repairs (the nine repair-in-place items)',
  'step 1', '3-8 weeks (T2 and the envelope grid are the long poles)',
  'Repaired theorem statements with short proofs or honest "conjecture" labels'],
 ['6', 'Tier D demotions and absorptions (Section 17 companion, Thm B conjecture, '
  'Claims A-E reclassification, Prop 16.2 re-typing, Cor 4.14 appendix)',
  'step 5', '1-3 weeks',
  'A shorter main paper plus companion notes'],
 ['7', 'Tier E excisions: P0-editorial citation integrity (6 false annotations, 12 '
  'uncited refs), "no open conjectures" claim, authorship statement rewrite',
  'step 0 (strategic decision), per the HELD status', 'days',
  'Citation-integer manuscript; the HELD P0-editorial items are released for execution '
  'here, coordinated with P3 provenance excision'],
 ['8', 'Full re-audit of v2 (external, same protocol as this wave) before any '
  'submission decision', 'steps 1-7', 'external',
  'A v2 audit wave; iterate'],
], [0.045, 0.415, 0.15, 0.10, 0.29]))
story.append(TCAP('Table 9. Implementation sequence. Total to a coherent single '
 'article: GLM\'s 6-12 month estimate is consistent with this table at research '
 'pace; the mechanical and measurement strata (steps 1-4) are a 1-2 month core.'))

story.append(H('Risks and fallbacks', 2))
story.append(P(
 'Three risks dominate. R1: the Layer-1 embedding may fail on inspection - kimi\'s '
 'own fallback ("if R3\'s embedding fails, fall back to the renaming-only option") '
 'and muse\'s disambiguation table are the printed escape hatches, and the Layer 2 '
 'theorems survive either way, so the downside is bounded. R2: T2 and T7 are '
 'genuinely new mathematics (GLM\'s pricing: 1-3 months and months respectively) - '
 'the plan treats them as the paper\'s contribution rather than as prerequisites; if '
 'they stall, the conditional-transfer version is publishable with them stated as '
 'conjectures, which is exactly the epistemic status all six audits demand. R3: '
 'scope creep back into v21 - prevented by the versioning protocol, which makes the '
 'frozen baseline a hard boundary. One scheduling note: M1 (step 3) has no '
 'prerequisites beyond the frozen artifacts and the Layer 0 names, and could run '
 'immediately after step 1 to give the strategic decision (step 0) an empirical '
 'data point it currently lacks: whether the measured curvature slice correlates '
 'with anything. That result would inform both the single-article and the split '
 'options, which is why this assessment recommends starting M1 as soon as pass 1 '
 'lands, in parallel with the step-0 deliberation.'))

# ========================================================== PART VII =======
story += PART('Part VII', 'Reliability Scorecard and Joint Verdict')

story.append(TBL([
 ['Audit', 'Checkable claims', 'Verified', 'Corrected / stale', 'Distinctive contribution'],
 ['DeepSeek (U1)', '14', '13', '1 stale (citation key)',
  'The editorial specification; the delete-vs-demote policy that shaped Tier D/E'],
 ['GLM (U2)', '41', '39', '2 corrections (0.802 arithmetic; Def 2.6 slip) + 1 direction fix (Levy CI)',
  'The structural backbone: D1-D6, T1-T7, the deletion list, and both genuinely new '
  'theorems (T2 jump-cocycle, T7 mpLP bridge); highest verification rate'],
 ['GPT (U3)', '15', '15', '0',
  'The most type-careful reading: realization datum, plaquette estimator, the '
  'transport caveat, "biomass deficit is not a metric"'],
 ['Kimi (U4)', '12', '10', '1 correction (R2 energy vs curvature) + 1 completion (strict convexity)',
  'The constructive mathematics: R1/R3 (first provable link), the embedding, the '
  'strong-form warning'],
 ['Muse (U5)', '19', '18', '1 correction (mask reading)',
  'The migration checklist and Theorem U - the only drop-in implementation text'],
 ['Opus (U6)', '17', '16', '1 correction (mixed-difference as description)',
  'The empirical re-reading: Phi-not-kappa, Routes C1/C2, "curvature is singular on '
  'the strata" - the paper\'s invisible thesis made visible'],
], [0.13, 0.10, 0.075, 0.235, 0.46]))
story.append(TCAP('Table 10. Reliability scorecard. "Checkable claims" counts '
 'statements this assessment could test against the source; totals: 118 claims, 111 '
 'verified outright, 8 carried corrections or stale status.'))

story.append(H('Joint verdict', 2))
story.append(P(
 'The six audits are unanimous on the diagnosis and complementary on the cure. The '
 'diagnosis, fully verified here: the manuscript\'s central weakness is not length, '
 'provenance, or citation hygiene - it is that one name currently denotes three '
 'mathematical objects of different type, so that the abstract\'s proposition and '
 'the empirical flagship are about different things; and the theorem layer that '
 'should carry the weight contains seven load-bearing statements that are false, '
 'vacuous, incoherent, or proven for the wrong object. The cure, triangulated five '
 'ways: a typed notation layer; a factored central object of which the geometric '
 'curvature, the knockout statistic, and the trajectory deficit are declared '
 'instantiations; an energy-level transfer theorem that is provable now; '
 'curvature-level measurements that are computable now; and a tiered '
 'repair-demote-excise program that elevates everything recoverable and absorbs '
 'the rest. The single decision that gates all of it - one article or a main paper '
 'plus companions - is now made on a clean basis: a frozen, mechanically-verified '
 'v21, a complete defect inventory across two audit waves, and a synthesized '
 'architecture with its first steps already specified to the line level.'))
story.append(P(
 'This assessment makes no edits to the manuscript, per the directive: v21 is '
 'frozen, and everything specified in Parts V and VI is work for '
 'journal_manuscript_v2 and later versions. The immediate next actions, in order: '
 'take the strategic decision; create v2 and run the Layer 0 pass; start M1 in '
 'parallel; then proceed down Table 9.'))

# ------------------------------------------------------------ build ---------
doc.multiBuild(story, onFirstPage=on_page, onLaterPages=on_page)
print('BUILD OK ->', OUT)






