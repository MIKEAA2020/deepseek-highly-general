#!/usr/bin/env python3
"""Builds download/Root_Cause_Evaluation_report.pdf
(body: ReportLab TocDocTemplate + multiBuild; cover: Template 03 via
html2poster.js; merge: pypdf). Follows the pdf skill report brief;
series-consistent with Active_Set_Bridge_v2_solution_report.pdf."""
import hashlib
import os
import subprocess
import sys

PDF_SKILL = "/home/z/my-project/skills/pdf"
sys.path.insert(0, os.path.join(PDF_SKILL, "scripts"))
sys.path.insert(0, "/home/z/my-project/scripts")

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (CondPageBreak, HRFlowable, Image,
                                KeepTogether, PageBreak, Paragraph,
                                SimpleDocTemplate, Spacer, Table,
                                TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents
from PIL import Image as PILImage

from root_cause_report_content import CONTENT

# ---------------------------------------------------------------- fonts
FONT_DIR = "/usr/share/fonts"
pdfmetrics.registerFont(TTFont(
    "NotoSerifSC", f"{FONT_DIR}/truetype/noto-serif-sc/"
    "NotoSerifSC-Regular.ttf"))
pdfmetrics.registerFont(TTFont(
    "NotoSerifSC-Bold", f"{FONT_DIR}/truetype/noto-serif-sc/"
    "NotoSerifSC-Bold.ttf"))
pdfmetrics.registerFont(TTFont(
    "FreeSerif", f"{FONT_DIR}/truetype/freefont/FreeSerif.ttf"))
pdfmetrics.registerFont(TTFont(
    "FreeSerif-Bold", f"{FONT_DIR}/truetype/freefont/FreeSerifBold.ttf"))
pdfmetrics.registerFont(TTFont(
    "FreeSerif-Italic", f"{FONT_DIR}/truetype/freefont/"
    "FreeSerifItalic.ttf"))
pdfmetrics.registerFont(TTFont(
    "FreeSerif-BoldItalic", f"{FONT_DIR}/truetype/freefont/"
    "FreeSerifBoldItalic.ttf"))
pdfmetrics.registerFont(TTFont(
    "DejaVuSansMono", f"{FONT_DIR}/truetype/dejavu/DejaVuSansMono.ttf"))
registerFontFamily("NotoSerifSC", normal="NotoSerifSC",
                   bold="NotoSerifSC-Bold")
registerFontFamily("FreeSerif", normal="FreeSerif", bold="FreeSerif-Bold",
                   italic="FreeSerif-Italic",
                   boldItalic="FreeSerif-BoldItalic")
registerFontFamily("DejaVuSansMono", normal="DejaVuSansMono",
                   bold="DejaVuSansMono")

from pdf import install_font_fallback  # noqa: E402
install_font_fallback()

# ━━ Cascade Palette (series seed 20260901, steel-blue family; matches the
#    Active-Set Bridge v2 report in the same delivery series) ━━
PAGE_BG = colors.HexColor("#f1f2f2")
SECTION_BG = colors.HexColor("#e8eaea")
CARD_BG = colors.HexColor("#e6e9ea")
TABLE_STRIPE = colors.HexColor("#f2f3f4")
HEADER_FILL = colors.HexColor("#3c535f")
COVER_BLOCK = colors.HexColor("#405560")
BORDER = colors.HexColor("#a2b7c2")
ICON = colors.HexColor("#437d9a")
ACCENT = colors.HexColor("#266a8c")
ACCENT_2 = colors.HexColor("#c65f70")
TEXT_PRIMARY = colors.HexColor("#212325")
TEXT_MUTED = colors.HexColor("#80868a")
TABLE_HEADER_COLOR = HEADER_FILL
TABLE_ROW_ODD = TABLE_STRIPE

OUT_DIR = "/home/z/my-project/download/m4"
BODY_PDF = os.path.join(OUT_DIR, "_rce_body.pdf")
COVER_HTML = os.path.join(OUT_DIR, "rce_cover.html")
COVER_PDF = os.path.join(OUT_DIR, "_rce_cover.pdf")
FINAL_PDF = os.path.join(
    "/home/z/my-project/download",
    "Root_Cause_Evaluation_report.pdf")

MARGIN = 0.9 * inch
PAGE_W, PAGE_H = A4
AVAIL_W = PAGE_W - 2 * MARGIN

# ---------------------------------------------------------------- styles
S_H1 = ParagraphStyle("H1", fontName="FreeSerif", fontSize=17, leading=22,
                      textColor=HEADER_FILL, spaceBefore=18, spaceAfter=8)
S_H2 = ParagraphStyle("H2", fontName="FreeSerif", fontSize=12.5,
                      leading=16, textColor=TEXT_PRIMARY, spaceBefore=12,
                      spaceAfter=6)
S_BODY = ParagraphStyle("Body", fontName="FreeSerif", fontSize=10.2,
                        leading=15.5, textColor=TEXT_PRIMARY,
                        alignment=TA_JUSTIFY, spaceAfter=8)
S_QUOTE = ParagraphStyle("Quote", fontName="FreeSerif-Italic",
                         fontSize=10.2, leading=15.2, textColor=TEXT_PRIMARY,
                         leftIndent=24, rightIndent=12, spaceBefore=6,
                         spaceAfter=10, borderPadding=(2, 0, 2, 0))
S_CAPTION = ParagraphStyle("Caption", fontName="FreeSerif", fontSize=8.5,
                           leading=11, textColor=TEXT_MUTED,
                           alignment=TA_CENTER, spaceBefore=3,
                           spaceAfter=6)
S_BULLET = ParagraphStyle("Bullet", fontName="FreeSerif", fontSize=10.2,
                          leading=15, textColor=TEXT_PRIMARY,
                          alignment=TA_LEFT, leftIndent=14,
                          bulletIndent=2, spaceAfter=5)
S_STAT = ParagraphStyle("StatBig", fontName="FreeSerif", fontSize=19,
                        leading=23, textColor=ACCENT,
                        alignment=TA_CENTER)
S_STATLBL = ParagraphStyle("StatLabel", fontName="FreeSerif", fontSize=8.3,
                           leading=11, textColor=TEXT_MUTED,
                           alignment=TA_CENTER)
S_TH = ParagraphStyle("TH", fontName="FreeSerif", fontSize=9,
                      leading=11.5, textColor=colors.white,
                      alignment=TA_CENTER)
S_TD = ParagraphStyle("TD", fontName="FreeSerif", fontSize=8.6,
                      leading=11, textColor=TEXT_PRIMARY,
                      alignment=TA_LEFT)
S_TDC = ParagraphStyle("TDC", parent=S_TD, alignment=TA_CENTER)
S_TOC_TITLE = ParagraphStyle("TOCTitle", fontName="FreeSerif",
                             fontSize=17, leading=22,
                             textColor=HEADER_FILL, spaceAfter=10)

H1_ORPHAN = (PAGE_H - 2 * MARGIN) * 0.18


class TocDocTemplate(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if hasattr(flowable, "bookmark_name"):
            level = getattr(flowable, "bookmark_level", 0)
            text = getattr(flowable, "bookmark_text", "")
            key = getattr(flowable, "bookmark_key", "")
            self.notify("TOCEntry", (level, text, self.page, key))


def add_heading(text, style, level=0):
    key = "h_%s" % hashlib.md5(text.encode()).hexdigest()[:8]
    p = Paragraph('<a name="%s"/><b>%s</b>' % (key, text), style)
    p.bookmark_name = key
    p.bookmark_level = level
    p.bookmark_text = text
    p.bookmark_key = key
    return p


def fit_image(path, max_w, max_h):
    pil = PILImage.open(path)
    ow, oh = pil.size
    ratio = min(max_w / ow if ow > max_w else 1.0,
                max_h / oh if oh > max_h else 1.0)
    return Image(path, width=ow * ratio, height=oh * ratio)


def callout(big, label):
    t = Table([[Paragraph("<b>%s</b>" % big, S_STAT)],
               [Paragraph(label, S_STATLBL)]],
              colWidths=[AVAIL_W * 0.72], hAlign="CENTER")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CARD_BG),
        ("BOX", (0, 0), (-1, -1), 1, ACCENT),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    return t


def make_table(spec):
    ratios = spec["ratios"]
    widths = [r * AVAIL_W for r in ratios]
    data = [[Paragraph("<b>%s</b>" % h, S_TH) for h in spec["header"]]]
    for row in spec["rows"]:
        cells = []
        for j, cell in enumerate(row):
            st = S_TD if j == 0 or len(str(cell)) > 24 else S_TDC
            cells.append(Paragraph(str(cell), st))
        data.append(cells)
    t = Table(data, colWidths=widths, hAlign="CENTER", repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), TABLE_HEADER_COLOR),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]
    for i in range(1, len(data)):
        style.append(("BACKGROUND", (0, i), (-1, i),
                      colors.white if i % 2 else TABLE_ROW_ODD))
    t.setStyle(TableStyle(style))
    parts = [Spacer(1, 10), t]
    if spec.get("note"):
        parts.append(Paragraph(spec["note"], S_CAPTION))
    parts.append(Spacer(1, 8))
    return parts


# ------------------------------------------------------------- header/foot
def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFont("FreeSerif", 7.5)
    canvas.setFillColor(TEXT_MUTED)
    canvas.drawString(MARGIN, PAGE_H - 0.55 * inch,
                      "Root Cause Evaluation \u00b7 The Order of "
                      "Smoothness and the Regime Dial")
    canvas.setStrokeColor(ACCENT)
    canvas.setLineWidth(1.1)
    canvas.line(MARGIN, PAGE_H - 0.62 * inch, PAGE_W - MARGIN,
                PAGE_H - 0.62 * inch)
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, 0.62 * inch, PAGE_W - MARGIN, 0.62 * inch)
    canvas.drawString(MARGIN, 0.45 * inch,
                      "iML1515 \u00b7 lexicographic pFBA \u00b7 M4a/M4b/M4c "
                      "\u00b7 root-cause analysis")
    canvas.drawRightString(PAGE_W - MARGIN, 0.45 * inch,
                           "page %d" % doc.page)
    canvas.restoreState()


# ------------------------------------------------------------------- build
def build_body():
    doc = TocDocTemplate(
        BODY_PDF, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=0.95 * inch, bottomMargin=0.85 * inch,
        title="Root Cause Evaluation: The Order of Smoothness and the "
              "Regime Dial",
        author="Z.ai", creator="Z.ai",
        subject="Evaluation, verification, and exploration of the "
                "root-cause analysis of the active-set bridge, with the "
                "M4c regime-dial measurement")
    story = []
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle("TOC0", fontName="FreeSerif", fontSize=11,
                       leading=15, leftIndent=16, spaceBefore=4,
                       textColor=TEXT_PRIMARY),
        ParagraphStyle("TOC1", fontName="FreeSerif", fontSize=9.5,
                       leading=13, leftIndent=32,
                       textColor=TEXT_MUTED)]
    story.append(Paragraph("<b>Table of Contents</b>", S_TOC_TITLE))
    story.append(HRFlowable(width="100%", color=ACCENT, thickness=1.1,
                            spaceAfter=10))
    story.append(toc)
    story.append(PageBreak())

    for item in CONTENT:
        kind, payload = item[0], item[1]
        if isinstance(payload, str):
            payload = payload.replace(" \u2014", "\u00a0\u2014")
        if kind == "h1":
            story.append(CondPageBreak(H1_ORPHAN))
            story.append(add_heading(payload, S_H1, level=0))
            story.append(HRFlowable(width="100%", color=BORDER,
                                    thickness=0.6, spaceAfter=6))
        elif kind == "h2":
            story.append(CondPageBreak(60))
            story.append(add_heading(payload, S_H2, level=1))
        elif kind == "body":
            story.append(Paragraph(payload, S_BODY))
        elif kind == "quote":
            q = Table([[Paragraph(payload, S_QUOTE)]],
                      colWidths=[AVAIL_W * 0.92], hAlign="CENTER")
            q.setStyle(TableStyle([
                ("LINEBEFORE", (0, 0), (0, -1), 2, ACCENT),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
            story.append(q)
        elif kind == "callout":
            story.append(Spacer(1, 4))
            story.append(callout(payload[0], payload[1]))
            story.append(Spacer(1, 6))
        elif kind == "table":
            parts = make_table(payload)
            title = Paragraph("<b>%s</b>" % payload["title"], S_CAPTION)
            if len(payload["rows"]) <= 8:
                story.append(KeepTogether([parts[1], title]))
                story.append(Spacer(1, 8))
            else:
                story.append(parts[1])
                story.append(title)
                story.append(Spacer(1, 8))
        elif kind == "figure":
            path, caption, maxh = payload
            img = fit_image(path, AVAIL_W, maxh)
            cap = Paragraph("<b>%s</b>" % caption, S_CAPTION)
            story.append(Spacer(1, 6))
            if img.drawHeight <= 210:
                story.append(KeepTogether([img, cap]))
            else:
                story.append(img)
                story.append(cap)
            story.append(Spacer(1, 6))
        elif kind == "bullet_list":
            for head, text in payload:
                story.append(Paragraph(
                    "<b>\u2022 %s</b> %s" % (head, text), S_BULLET,
                    bulletText=None))
            story.append(Spacer(1, 4))
    doc.multiBuild(story, onFirstPage=on_page, onLaterPages=on_page)
    print("body built:", BODY_PDF)


# ------------------------------------------------------------------- cover
COVER = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Noto+Serif+SC:wght@400;700;900&family=Inter:wght@300;400;500&family=Noto+Sans+SC:wght@300;400;500&display=swap" rel="stylesheet">
  <style>
    @page { size: 794px 1123px; margin: 0; }
    :root {
      --c-bg: #1d2d38;
      --c-accent: #7fb3c8;
      --c-text: #edf1f3;
      --c-muted: #8fa3ad;
      --c-footer: #8fa3ad;
    }
    html, body { margin: 0; padding: 0; width: 794px; height: 1123px; background: var(--c-bg); color: var(--c-text); font-family: 'Inter', 'Noto Sans SC', sans-serif; }
    @media screen {
      html { height: auto; display: flex; justify-content: center; min-height: 100vh; background: var(--c-bg); }
      body { transform-origin: top center; scale: min(1, calc(100vw / 794), calc(100vh / 1123)); margin: 0 auto; box-shadow: 0 0 60px rgba(0,0,0,0.3); }
    }
    .cover { width: 794px; height: 1123px; position: relative; box-sizing: border-box; border: none; outline: none; box-shadow: none; }
    .vline { position: absolute; left: 57px; top: 76px; bottom: 76px; width: 2.5px; background: var(--c-accent); }
    .content { position: absolute; left: 102px; right: 76px; top: 0; bottom: 0; }
    .label { position: absolute; top: 128px; font-size: 9pt; color: var(--c-accent); letter-spacing: 3px; text-transform: uppercase; font-family: 'Inter', 'Noto Sans SC', sans-serif; }
    .title { position: absolute; top: 210px; font-size: 33pt; font-weight: 700; line-height: 1.28; font-family: 'Playfair Display', 'Noto Serif SC', serif; color: var(--c-text); max-width: 600px; }
    .subtitle { position: absolute; top: 520px; font-size: 12pt; line-height: 1.6; color: var(--c-muted); max-width: 540px; }
    .authors { position: absolute; top: 690px; font-size: 12pt; color: var(--c-text); }
    .institution { position: absolute; top: 732px; font-size: 10pt; color: var(--c-muted); line-height: 1.5; max-width: 540px; }
    .summary { position: absolute; top: 812px; font-size: 10.5pt; line-height: 1.7; color: var(--c-muted); max-width: 560px; }
    .footer { position: absolute; bottom: 76px; left: 0; right: 0; display: flex; justify-content: space-between; font-size: 9pt; color: var(--c-footer); }
  </style>
</head>
<body>
  <div class="cover">
    <div class="vline"></div>
    <div class="content">
      <div class="label">Evaluation Report · Unifying Object Wave</div>
      <div class="title">The Root Cause,<br>Verified: Smoothness<br>and the Regime Dial</div>
      <div class="subtitle">The root-cause analysis of the active-set
        bridge - "the wrong order of smoothness" - evaluated claim by
        claim against the executed M1/M3/M4a/M4b record, corrected where
        it misdescribes the measured objects, and extended by a new
        measurement, M4c, which gives its "separate regime" a mechanism
        and a law: one curvature measure, multiple resolutions, a
        measurable crossover.</div>
      <div class="authors">Computational Verification Unit</div>
      <div class="institution">Source: the root-cause analysis under
        evaluation · verdicts grounded in the v2 theorem set
        (S/G/N1/N/D), the committed M4a/M4b artifacts, and 858 new
        lexicographic solves at the M4b codim-2 vertex · frozen v21
        untouched</div>
      <div class="summary">The diagnosis is correct and theorem-backed;
        three misdescriptions are corrected (no O(eps) holonomy exists -
        the scalings form a trichotomy; the slope-1.00 statistic is the
        9-of-76 interacting stratum; the slope-1 law belongs to the
        dynamic layer). Theorem R closes the gap: the smoothed map's
        curvature is the same measure, its epsilon-squared law measures
        at slope 1.9991-1.9995, and the crossover scales linearly,
        epsilon-star approximately 3 sigma. The unification is a
        resolution statement, not a limit statement.</div>
      <div class="footer">
        <span>download/Root_Cause_Evaluation.md · download/m4/</span>
        <span>September 2026</span>
      </div>
    </div>
  </div>
</body>
</html>
"""


def build_cover():
    with open(COVER_HTML, "w") as fh:
        fh.write(COVER)
    r = subprocess.run(["node", os.path.join(PDF_SKILL, "scripts",
                                              "html2poster.js"),
                        COVER_HTML, "--output", COVER_PDF,
                        "--width", "794px"], capture_output=True, text=True,
                       timeout=240)
    print(r.stdout[-500:] if r.stdout else "", r.stderr[-500:] if r.stderr
          else "")
    assert os.path.exists(COVER_PDF), "cover render failed"


def merge():
    from pypdf import PdfReader, PdfWriter
    A4_W, A4_H = 595.28, 841.89
    writer = PdfWriter()
    cover_page = PdfReader(COVER_PDF).pages[0]
    w, h = float(cover_page.mediabox.width), float(cover_page.mediabox.height)
    if abs(w - A4_W) > 0.1 or abs(h - A4_H) > 0.1:
        cover_page.scale_to(A4_W, A4_H)
        cover_page.mediabox.lower_left = (0, 0)
        cover_page.mediabox.upper_right = (A4_W, A4_H)
    writer.add_page(cover_page)
    for page in PdfReader(BODY_PDF).pages:
        writer.add_page(page)
    writer.add_metadata({
        "/Title": "Root Cause Evaluation: The Order of Smoothness and "
                  "the Regime Dial",
        "/Author": "Z.ai", "/Creator": "Z.ai",
        "/Subject": "Evaluation, verification, and exploration of the "
                    "root-cause analysis of the active-set bridge, with "
                    "the M4c regime-dial measurement"})
    with open(FINAL_PDF, "wb") as f:
        writer.write(f)
    print("final:", FINAL_PDF)


if __name__ == "__main__":
    build_body()
    build_cover()
    merge()
