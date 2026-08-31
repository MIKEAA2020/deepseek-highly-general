#!/usr/bin/env python3
"""
b-number re-audit for the 91 E10 unmapped genes, using Keio collection
Supplementary Table 3 (MOESM5: Baba et al. 2006, MSB4100050).

Goal:
  - For each of the 91 unmapped genes (originally flagged "GLOBAL" by E10's
    script — no direct iJO1366 reaction match), look up its b-number in the
    Keio master table.
  - Cross-reference against iJO1366's gene set (loaded via cobra.io.load_model)
    to determine whether any of those recovered b-numbers would actually map
    to iJO1366 reactions — i.e., would they become "MAPPED" if E10's lookup
    logic tried the b-number fallback?

Inputs:
  /tmp/my-project/download/novelty_real_time_series_e10.csv   (92 genes, mapping_status)
  /tmp/my-project/raw tomoya baba supp/44320_2006_BFMSB4100050_MOESM5_ESM.xls
  (Keio Sup. Table 3: 4378 rows × 29 cols; col 1 = gene name, col 8 = b number)

Outputs:
  /home/z/my-project/download/bnumber_reamudit_keio_e10.csv
  /home/z/my-project/download/bnumber_reamudit_keio_e10.txt
  /home/z/my-project/download/bnumber_reamudit_keio_e10.json
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pandas as pd

CSV_IN = Path("/tmp/my-project/download/novelty_real_time_series_e10.csv")
MOESM5 = Path("/tmp/my-project/raw tomoya baba supp/44320_2006_BFMSB4100050_MOESM5_ESM.xls")
OUT_DIR = Path("/home/z/my-project/download")


def load_keio_bnumber_map() -> dict[str, str]:
    """Return {gene_name_lower: b_number} from MOESM5 Sup Table 3."""
    df = pd.read_excel(MOESM5, sheet_name=0, header=3)
    df.columns = [str(c).strip() for c in df.columns]
    # Identify columns: index 0 = ECK, index 1 = gene, index 8 = b number
    gene_col = df.columns[1]  # 'Unnamed: 1' — header is on a different row but col 1 holds gene
    bnum_col = "b number"
    # Rename for clarity
    df = df.rename(columns={df.columns[0]: "ECK", gene_col: "gene", bnum_col: "b_number"})
    # Build mapping — drop rows where gene is NaN
    df_clean = df.dropna(subset=["gene", "b_number"]).copy()
    df_clean["gene_lc"] = df_clean["gene"].astype(str).str.strip().str.lower()
    df_clean["b_number"] = df_clean["b_number"].astype(str).str.strip()
    mapping = {}
    for _, row in df_clean.iterrows():
        g = row["gene_lc"]
        b = row["b_number"]
        # First occurrence wins (canonical)
        if g not in mapping:
            mapping[g] = b
    return mapping


def load_ijo1366_genes() -> set[str] | None:
    """Try to load iJO1366 via cobrapy. Return set of gene IDs or None on failure."""
    try:
        from cobra.io import load_model
    except ImportError:
        print("WARN: cobrapy not available; cannot load iJO1366 gene set", file=sys.stderr)
        return None
    for attempt in range(2):
        try:
            m = load_model("iJO1366")
            return {g.id for g in m.genes}
        except Exception as e:
            print(f"  cobrapy load_model attempt {attempt+1} failed: {e}", file=sys.stderr)
    return None


def main() -> int:
    # --- Load E10 gene list with mapping_status ---
    df = pd.read_csv(CSV_IN)
    gene_status = df.groupby("gene")["mapping_status"].first().to_dict()
    n_total = len(gene_status)
    unmapped_genes = [g for g, s in gene_status.items() if str(s).startswith("GLOBAL")]
    mapped_genes = [g for g, s in gene_status.items() if str(s).startswith("MAPPED")]
    print(f"E10 gene counts: total = {n_total}; MAPPED = {len(mapped_genes)}; UNMAPPED = {len(unmapped_genes)}")
    if mapped_genes:
        print(f"  MAPPED: {mapped_genes}")
    print(f"  UNMAPPED (first 10): {unmapped_genes[:10]}")

    # --- Load Keio b-number map ---
    print(f"\nLoading Keio Sup Table 3 (MOESM5): {MOESM5}")
    keio_map = load_keio_bnumber_map()
    print(f"  Keio gene→b-number map: {len(keio_map)} entries (after dedup, lowercase gene names)")
    # Sanity sample
    sample = list(keio_map.items())[:5]
    print(f"  Sample: {sample}")

    # --- Load iJO1366 gene set (for cross-ref) ---
    print("\nLoading iJO1366 gene set via cobrapy (may take 30-60 s for first download)...")
    ijo_genes = load_ijo1366_genes()
    if ijo_genes is not None:
        print(f"  iJO1366 gene set: {len(ijo_genes)} gene IDs (b-numbers)")
    else:
        print("  iJO1366 gene set: unavailable — will skip the 'would-be-MAPPED' cross-ref")

    # --- For each UNMAPPED gene, look up b-number ---
    rows = []
    for g in unmapped_genes:
        g_lc = str(g).strip().lower()
        b_found = keio_map.get(g_lc)
        in_ijo = None
        if b_found is not None and ijo_genes is not None:
            in_ijo = b_found in ijo_genes
        rows.append({
            "gene": g,
            "gene_lowercase": g_lc,
            "b_number_in_keio": b_found if b_found else "",
            "already_b_number_format": g_lc.startswith("b") and g_lc[1:].isdigit(),
            "would_map_to_iJO1366": in_ijo if in_ijo is not None else None,
            "status_now": "MAPPED-NEW" if (b_found and in_ijo) else
                          ("B-NUMBER-RECOVERED" if b_found else
                           ("ALREADY-B-NUMBER" if (g_lc.startswith("b") and g_lc[1:].isdigit()) else "NO-MATCH")),
        })

    out_df = pd.DataFrame(rows)

    # Also check the MAPPED genes for sanity (b2097 → should already be in iJO1366)
    sanity = []
    for g in mapped_genes:
        g_lc = str(g).strip().lower()
        # If gene is already a b-number (e.g., "b2097"), check it directly against iJO1366
        if g_lc.startswith("b") and g_lc[1:].isdigit():
            in_ijo = (g in ijo_genes) if ijo_genes else None
            sanity.append({
                "gene": g, "b_number_in_keio": g,  # gene IS the b-number
                "in_iJO1366": in_ijo, "mapping_status_in_E10": "MAPPED",
            })
            continue
        # Otherwise look up via gene name in Keio
        b_found = keio_map.get(g_lc)
        in_ijo = (b_found in ijo_genes) if (b_found and ijo_genes) else None
        sanity.append({
            "gene": g, "b_number_in_keio": b_found or "",
            "in_iJO1366": in_ijo, "mapping_status_in_E10": "MAPPED",
        })

    # --- Report ---
    print("\n" + "=" * 78)
    print("b-NUMBER RE-AUDIT (UNMAPPED → Keio lookup → iJO1366 cross-ref)")
    print("=" * 78)
    print(f"\nUNMAPPED genes (n={len(unmapped_genes)}):")
    print(f"  {'gene':12s} {'b-number (Keio)':18s} {'in_iJO1366':12s} {'new_status':25s}")
    print(f"  {'-'*12} {'-'*18} {'-'*12} {'-'*25}")
    for r in rows:
        in_ijo_str = ("YES" if r["would_map_to_iJO1366"] is True else
                      "no" if r["would_map_to_iJO1366"] is False else "?")
        print(f"  {r['gene']:12s} {r['b_number_in_keio']:18s} "
              f"{in_ijo_str:12s} {r['status_now']:25s}")

    n_recovered = sum(1 for r in rows if r["b_number_in_keio"])
    n_already_bnum = sum(1 for r in rows if r["already_b_number_format"])
    n_nomatch = len(rows) - n_recovered - n_already_bnum
    n_would_map_to_ijo = sum(1 for r in rows if r["would_map_to_iJO1366"] is True)

    print(f"\nSummary:")
    print(f"  Unmapped genes total:                 {len(unmapped_genes)}")
    print(f"  Of which already in b-number format:   {n_already_bnum}")
    print(f"  Recovered b-number from Keio (gene name lookup): {n_recovered}")
    print(f"  NO MATCH in Keio (gene name not found): {n_nomatch}")
    print(f"  Of recovered b-numbers, those IN iJO1366 (would be MAPPED-NEW): {n_would_map_to_ijo}")

    print(f"\nMAPPED sanity check (n={len(mapped_genes)}):")
    for s in sanity:
        in_str = ("YES" if s["in_iJO1366"] is True else "no" if s["in_iJO1366"] is False else "?")
        print(f"  gene={s['gene']:10s} keio_b={s['b_number_in_keio']:10s} in_iJO1366={in_str}")

    # --- Save outputs ---
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(OUT_DIR / "bnumber_reamudit_keio_e10.csv", index=False)
    # TXT
    with (OUT_DIR / "bnumber_reamudit_keio_e10.txt").open("w") as f:
        f.write("b-number Re-audit: 91 UNMAPPED E10 genes vs Keio Sup Table 3 (MOESM5)\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"E10 total genes: {n_total}\n")
        f.write(f"E10 MAPPED (already): {len(mapped_genes)}\n")
        f.write(f"E10 UNMAPPED (this audit's target): {len(unmapped_genes)}\n")
        f.write(f"Keio MOESM5 b-number map size: {len(keio_map)}\n")
        if ijo_genes is not None:
            f.write(f"iJO1366 gene set size: {len(ijo_genes)}\n")
        else:
            f.write("iJO1366 gene set: unavailable (cobrapy load failed)\n")
        f.write("\nPer-gene results (UNMAPPED):\n")
        f.write(f"  {'gene':14s} {'b_number':12s} {'already_bnum':14s} "
                f"{'in_iJO1366':12s} {'status':25s}\n")
        for r in rows:
            in_ijo_str = ("YES" if r["would_map_to_iJO1366"] is True else
                          "no" if r["would_map_to_iJO1366"] is False else "?")
            f.write(f"  {r['gene']:14s} {r['b_number_in_keio']:12s} "
                    f"{str(r['already_b_number_format']):14s} "
                    f"{in_ijo_str:12s} {r['status_now']:25s}\n")
        f.write("\nSummary counts:\n")
        f.write(f"  already_b_number_format:  {n_already_bnum}\n")
        f.write(f"  b_number_recovered:       {n_recovered}\n")
        f.write(f"  no_match_in_keio:          {n_nomatch}\n")
        f.write(f"  would_map_to_iJO1366_NEW: {n_would_map_to_ijo}\n")
        f.write("\nMAPPED sanity:\n")
        for s in sanity:
            in_str = ("YES" if s["in_iJO1366"] is True else "no" if s["in_iJO1366"] is False else "?")
            f.write(f"  gene={s['gene']:10s} keio_b={s['b_number_in_keio']:10s} in_iJO1366={in_str}\n")
    # JSON
    (OUT_DIR / "bnumber_reamudit_keio_e10.json").write_text(json.dumps({
        "e10_total_genes": n_total,
        "e10_mapped_genes": len(mapped_genes),
        "e10_unmapped_genes": len(unmapped_genes),
        "keio_map_size": len(keio_map),
        "iJO1366_gene_count": len(ijo_genes) if ijo_genes else None,
        "iJO1366_gene_set_loaded": ijo_genes is not None,
        "summary_counts": {
            "already_b_number_format": n_already_bnum,
            "b_number_recovered_from_keio": n_recovered,
            "no_match_in_keio": n_nomatch,
            "would_map_to_iJO1366_NEW": n_would_map_to_ijo,
        },
        "unmapped_genes_per_gene": rows,
        "mapped_genes_sanity": sanity,
    }, indent=2))
    print(f"\nWrote: {OUT_DIR}/bnumber_reamudit_keio_e10.{{csv,txt,json}}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
