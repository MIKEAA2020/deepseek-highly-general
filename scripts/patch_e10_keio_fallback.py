#!/usr/bin/env python3
"""
Patcher: adds Keio MOESM5 b-number fallback to novelty_real_time_series_e10.py.

Three patches:
  P1: OUT_DIR redirect to /tmp/my-project/download (where v10 expects outputs)
  P2: Add Keio MOESM5 loader function (KEIO_MAP global)
  P3: Add b-number fallback in the gene-matching loop (lines ~161-185)

The patcher is idempotent: if the patches are already present, it's a no-op.
"""
from pathlib import Path

TARGET = Path("/tmp/my-project/scripts/novelty_real_time_series_e10.py")


def patch(content: str) -> str:
    # P1: OUT_DIR
    old_p1 = 'OUT_DIR = "/home/z/my-project/download"\nos.makedirs(OUT_DIR, exist_ok=True)'
    new_p1 = (
        'OUT_DIR = "/tmp/my-project/download"\n'
        'os.makedirs(OUT_DIR, exist_ok=True)\n\n'
        '# ----------------------------------------------------------------------\n'
        '# 1a. Keio b-number fallback map (Baba et al. 2006, MSB4100050, MOESM5\n'
        '#     Sup. Table 3 - gene-name -> b-number for E. coli K-12 W3110).\n'
        '#     Loaded once at script start; used as a fallback when a Lemuth gene\n'
        '#     name does not directly match an iJO1366 gene ID.\n'
        '# ----------------------------------------------------------------------\n'
        'KEIO_MOESM5_PATH = "/tmp/my-project/raw tomoya baba supp/44320_2006_BFMSB4100050_MOESM5_ESM.xls"\n'
        '\n'
        'def load_keio_bnumber_map(path=KEIO_MOESM5_PATH):\n'
        '    """Return {gene_name_lower: b_number_str} from Keio Sup. Table 3.\n'
        '    The Excel file has a 4-row header block. After skipping with header=3:\n'
        '      col 0 = ECK number, col 1 = gene name, col 8 = "b number".\n'
        '    First occurrence of each gene name wins (canonical Keio ordering).\n'
        '    """\n'
        '    import pandas as pd\n'
        '    df = pd.read_excel(path, sheet_name=0, header=3)\n'
        '    df_clean = df.dropna(subset=[df.columns[1], "b number"]).copy()\n'
        '    df_clean["_gene_lc"] = df_clean[df.columns[1]].astype(str).str.strip().str.lower()\n'
        '    df_clean["_b"] = df_clean["b number"].astype(str).str.strip()\n'
        '    mapping = {}\n'
        '    for _, row in df_clean.iterrows():\n'
        '        g = row["_gene_lc"]\n'
        '        if g and g not in mapping:\n'
        '            mapping[g] = row["_b"]\n'
        '    return mapping\n'
        '\n'
        'print("Loading Keio MOESM5 Sup Table 3 (b-number fallback map)...")\n'
        'KEIO_MAP = load_keio_bnumber_map()\n'
        'print(f"  Keio gene-name -> b-number map: {len(KEIO_MAP)} entries")\n'
    )
    if old_p1 in content:
        content = content.replace(old_p1, new_p1)
        print("P1 (OUT_DIR + Keio loader): APPLIED")
    elif "KEIO_MOESM5_PATH" in content:
        print("P1 (OUT_DIR + Keio loader): already applied (idempotent)")
    else:
        print("P1: target string not found — ABORT")
        raise SystemExit(1)

    # P2: Add b-number fallback in the gene-matching loop.
    # Original block (lines 161-185):
    #     for rec in lemuth_data:
    #         gene = rec['gene']
    #         matched_gene = None
    #         if gene in iJO_genes_set:
    #             matched_gene = gene
    #         else:
    #             for alt in [gene, gene.upper(), gene.capitalize()]:
    #                 if alt in iJO_genes_set:
    #                     matched_gene = alt
    #                     break
    #     if matched_gene:
    #         rxns = iJO_gene_to_rxns[matched_gene]
    #         ...
    #
    # Patched block: insert Keio b-number fallback AFTER the alt-match loop,
    # BEFORE the `if matched_gene:` check.
    old_p2 = (
        '    if matched_gene:\n'
        '        rxns = iJO_gene_to_rxns[matched_gene]\n'
        '        gene_kappa_V_per_T[gene] = {}\n'
        '        for t_label in [f"T{i+1}" for i in range(8)]:\n'
        '            kv_t = max((kappa_V_per_rxn_per_T.get(rid, {}).get(t_label, 0.0)\n'
        '                        for rid in rxns), default=0.0)\n'
        '            gene_kappa_V_per_T[gene][t_label] = kv_t\n'
        '        gene_kappa_V_max[gene] = max(gene_kappa_V_per_T[gene].values())\n'
        '        gene_mapping_status[gene] = f"MAPPED to {matched_gene} -> {rxns[:3]}"\n'
        '    else:\n'
        '        # No direct mapping: use GLOBAL κ_V time-series (biomass-deficit proxy)\n'
        '        gene_kappa_V_per_T[gene] = dict(kappa_V_global_per_T)\n'
        '        gene_kappa_V_max[gene] = kappa_V_global\n'
        '        gene_mapping_status[gene] = "GLOBAL (uses biomass-deficit curvature time-series)"'
    )
    new_p2 = (
        '    # --- Keio b-number fallback (added v2): if no direct/alt match in iJO1366,\n'
        '    #     look up the gene name in the Keio Sup Table 3 map. If the\n'
        '    #     recovered b-number IS in iJO1366\'s gene set, use it as the matched gene.\n'
        '    #     This expands the MAPPED set from 1 (just b2097=fbaA) to 15, recovering\n'
        '    #     14 metabolic/transport genes (galT, sodA, narJ, otsB, treA, ugpC, ...).\n'
        '    if not matched_gene:\n'
        '        keio_b = KEIO_MAP.get(str(gene).strip().lower())\n'
        '        if keio_b and keio_b in iJO_genes_set:\n'
        '            matched_gene = keio_b\n'
        '            gene_mapping_status_extra = f" (via Keio fallback: {gene} -> {keio_b})"\n'
        '        else:\n'
        '            gene_mapping_status_extra = ""\n'
        '    else:\n'
        '        gene_mapping_status_extra = ""\n'
        '    if matched_gene:\n'
        '        rxns = iJO_gene_to_rxns[matched_gene]\n'
        '        gene_kappa_V_per_T[gene] = {}\n'
        '        for t_label in [f"T{i+1}" for i in range(8)]:\n'
        '            kv_t = max((kappa_V_per_rxn_per_T.get(rid, {}).get(t_label, 0.0)\n'
        '                        for rid in rxns), default=0.0)\n'
        '            gene_kappa_V_per_T[gene][t_label] = kv_t\n'
        '        gene_kappa_V_max[gene] = max(gene_kappa_V_per_T[gene].values())\n'
        '        gene_mapping_status[gene] = (f"MAPPED to {matched_gene} -> {rxns[:3]}"\n'
        '                                     + gene_mapping_status_extra)\n'
        '    else:\n'
        '        # No direct mapping: use GLOBAL κ_V time-series (biomass-deficit proxy)\n'
        '        gene_kappa_V_per_T[gene] = dict(kappa_V_global_per_T)\n'
        '        gene_kappa_V_max[gene] = kappa_V_global\n'
        '        gene_mapping_status[gene] = "GLOBAL (uses biomass-deficit curvature time-series)"'
    )
    if old_p2 in content:
        content = content.replace(old_p2, new_p2)
        print("P2 (Keio fallback in matching loop): APPLIED")
    elif "Keio b-number fallback" in content:
        print("P2 (Keio fallback in matching loop): already applied (idempotent)")
    else:
        print("P2: target string not found — ABORT")
        raise SystemExit(1)

    return content


def main():
    if not TARGET.exists():
        print(f"ERROR: target file not found at {TARGET}", flush=True)
        raise SystemExit(1)
    content = TARGET.read_text(encoding="utf-8")
    print(f"Original file: {len(content)} bytes, {content.count(chr(10))+1} lines")
    patched = patch(content)
    if patched == content:
        print("No changes — patches were already present.")
        return
    TARGET.write_text(patched, encoding="utf-8")
    print(f"Patched file: {len(patched)} bytes, {patched.count(chr(10))+1} lines")
    # Verify patches are in place
    reloaded = TARGET.read_text(encoding="utf-8")
    assert "KEIO_MOESM5_PATH" in reloaded
    assert "load_keio_bnumber_map" in reloaded
    assert "Keio b-number fallback" in reloaded
    assert 'OUT_DIR = "/tmp/my-project/download"' in reloaded
    print("VERIFICATION: all three patches present in reloaded file.")


if __name__ == "__main__":
    main()
