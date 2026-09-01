#!/usr/bin/env python3
"""
Restore /tmp/lemuth_ts_clean.json from the v1-backup E10 CSV (the original
run's per-(gene, time) log2 fold-changes). The JSON is required by
novelty_real_time_series_e10.py but was lost from /tmp.

The v1 backup CSV contains the ORIGINAL (pre-Keio-fallback) run, whose
gene/log2_FC columns are identical to the patched run (the patch only
changes kappa_V_predicted and mapping_status, never the Lemuth data).
"""
import json
from pathlib import Path
import pandas as pd

SRC = Path("/tmp/my-project/download/novelty_real_time_series_e10_v1_backup.csv")
DST = Path("/tmp/lemuth_ts_clean.json")

df = pd.read_csv(SRC)
# Rebuild records: one per gene, with table + T1..T8
records = []
for gene, sub in df.groupby("gene", sort=False):
    sub = sub.sort_values("time_point")
    rec = {"gene": gene, "table": str(int(sub.iloc[0]["table"]))}
    for _, row in sub.iterrows():
        rec[row["time_point"]] = float(row["log2_fold_change"])
    # sanity: 8 timepoints
    assert all(f"T{i}" in rec for i in range(1, 9)), f"missing timepoints for {gene}"
    records.append(rec)

DST.parent.mkdir(parents=True, exist_ok=True)
DST.write_text(json.dumps(records, indent=1))
print(f"Restored {len(records)} gene records -> {DST}")

# Cross-check against the patched CSV's log2 values
df2 = pd.read_csv("/tmp/my-project/download/novelty_real_time_series_e10.csv")
mism = 0
for _, row in df2.iterrows():
    rec = next(r for r in records if r["gene"] == row["gene"])
    if abs(rec[row["time_point"]] - row["log2_fold_change"]) > 1e-9:
        mism += 1
print(f"Cross-check vs patched CSV: {mism} mismatches out of {len(df2)} rows "
      f"({'OK' if mism == 0 else 'MISMATCH!'})")
