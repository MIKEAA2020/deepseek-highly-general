#!/usr/bin/env python3
"""
Reconstruct /tmp/lemuth_ts_clean.json from the existing E10 CSV output.
The cached JSON was cleaned from /tmp, but the E10 CSV preserves all 92 genes
x 8 time points x signed log2 fold-change values, plus the 'table' column
(which Lemuth paper Table 1-4 the gene came from).

Output format (matches original lemuth_data):
    [{"gene": "flhD", "table": 1, "T1": 0.18, "T2": -0.20, ..., "T8": ...}, ...]
"""
import json
import pandas as pd
from pathlib import Path

CSV = Path("/tmp/my-project/download/novelty_real_time_series_e10.csv")
OUT = Path("/tmp/lemuth_ts_clean.json")

df = pd.read_csv(CSV)
# Group by gene, build a record per gene with T1..T8 signed log2 fold-change + table
records = []
for gene, sub in df.groupby("gene", sort=False):
    rec = {"gene": gene, "table": int(sub["table"].iloc[0])}
    for _, row in sub.iterrows():
        rec[row["time_point"]] = float(row["log2_fold_change"])
    records.append(rec)
OUT.write_text(json.dumps(records, indent=2))
print(f"Wrote {OUT} ({len(records)} genes)")
print(f"Sample record: {records[0]}")
assert len(records) == 92, f"Expected 92 genes, got {len(records)}"
sample = records[0]
assert all(f"T{i}" in sample for i in range(1, 9)), "Missing T1-T8 keys"
assert "table" in sample, "Missing 'table' field"
print("Sanity: 92 genes x T1-T8 keys + 'table' field confirmed.")
