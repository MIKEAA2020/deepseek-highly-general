#!/usr/bin/env python3
"""Verify that all submission-package file paths resolve on GitHub main branch.

Uses anonymous API access (the repository is public). Optionally set the
GITHUB_TOKEN environment variable to raise the rate limit.
"""
import json
import os
import urllib.request

REPO = "MIKEAA2020/deepseek-highly-general"
API = f"https://api.github.com/repos/{REPO}/contents/"
TOKEN = os.environ.get("GITHUB_TOKEN", "")

MAIN_PAPER = [
    "download/journal_manuscript_v2.pdf",
    "download/cover_letter_bmb.md",
    "scripts/journal_manuscript_v2.tex",
    "scripts/journal_manuscript_v2_bmb_refs.tex",
    "scripts/journal_manuscript_v2_refs.bib",
    "scripts/build_bmb_refs.py",
    "download/m1_m3/fig_m1_summary.png",
    "download/alexandrov_bridge/coupling_figures.png",
    "download/deepseek_bridge/v5_e24_recalibration.png",
    "download/deepseek_bridge/v7_path_robustness.png",
    "download/deepseek_bridge/v8_tiebreak_robustness.png",
    "download/deepseek_bridge/e32_event_measure_stabilization.png",
]
COMPANION = [
    "download/companion_categorical.pdf",
    "download/cover_letter_tac.md",
    "scripts/companion_categorical.tex",
    "download/lipschitz_constants_per_optic.png",
    "download/cptc_zeno_contraction.png",
    "download/inverse_limit_raf_hasse.png",
    "download/inverse_limit_raf_extended_hasse.png",
]
SUPPORTING = [
    "download/Two_Paper_Submission_Package_Evaluation.md",
    "download/Declarations_and_Final_Scan_Evaluation.md",
    "download/Journal_Submission_Pass_Evaluation.md",
]


def check(path):
    headers = {"User-Agent": "link-check"}
    if TOKEN:
        headers["Authorization"] = f"token {TOKEN}"
    req = urllib.request.Request(
        API + urllib.request.quote(path) + "?ref=main", headers=headers
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode())
            return r.status, data.get("size", "?")
    except urllib.error.HTTPError as e:
        return e.code, 0


def run(label, paths):
    print(f"===== {label} =====")
    ok = True
    for p in paths:
        status, size = check(p)
        mark = "OK " if status == 200 else "FAIL"
        if status != 200:
            ok = False
        print(f"[{mark}] {status}  {size:>9} B  {p}")
    return ok


all_ok = True
all_ok &= run("MAIN PAPER (Bulletin of Mathematical Biology)", MAIN_PAPER)
all_ok &= run("COMPANION PAPER (Theory and Applications of Categories)", COMPANION)
all_ok &= run("SUPPORTING DOCS", SUPPORTING)
print("\nRESULT:", "ALL LINKS RESOLVE" if all_ok else "SOME LINKS BROKEN")
