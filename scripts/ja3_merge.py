#!/usr/bin/env python3
"""Merge cover + body for the third-wave joint assessment, normalize to A4."""
from pypdf import PdfReader, PdfWriter

A4_W, A4_H = 595.28, 841.89

def normalize_page_to_a4(page):
    box = page.mediabox
    w, h = float(box.width), float(box.height)
    if abs(w - A4_W) > 0.3 or abs(h - A4_H) > 0.3:
        page.scale_to(A4_W, A4_H)
    return page

cover_pdf = '/home/z/my-project/scripts/ja3_cover.pdf'
body_pdf = '/home/z/my-project/download/joint_assessment_unifying_object.pdf'
output_pdf = '/home/z/my-project/download/joint_assessment_unifying_object_final.pdf'

writer = PdfWriter()
writer.add_page(normalize_page_to_a4(PdfReader(cover_pdf).pages[0]))
for page in PdfReader(body_pdf).pages:
    writer.add_page(normalize_page_to_a4(page))
writer.add_metadata({
    '/Title': 'Joint Assessment of Six Unifying-Object Audits',
    '/Author': 'Z.ai',
    '/Creator': 'Z.ai',
    '/Subject': 'Third-wave audit verification and synthesis',
})
with open(output_pdf, 'wb') as f:
    writer.write(f)
print('MERGED ->', output_pdf, 'pages:', len(writer.pages))
