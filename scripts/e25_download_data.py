#!/usr/bin/env python3
"""
Study E25 data acquisition (manuscript round v18).

Purpose: resolve the platform-vs-class ambiguity of the E24 dissociation
  - E24 found  r = +0.374 (microarray, carbon EXHAUSTION, positive)
  - E24 found  r = -0.054 (RNA-seq,    carbon SWITCH,     null)
  Platform and perturbation class changed together, so the null has two
  readings.  E25 completes the 2x2 matrix by obtaining:
  (a) RNA-seq carbon DEPLETION (GSE64021, Su lab UNCC: MG1655 resuspended
      in MOPS WITHOUT glucose = "M-C" vs MOPS+glucose control, 1/2/4/6 h;
      same series also has phosphorus starvation "M-P" and heat shock
      "HS" -- non-carbon stress controls on the same platform), and
  (b) PaxDB E. coli K-12 MG1655 integrated whole-organism proteome
      (v6.1; 3,759 rows, 91% coverage, gene_name + b-number + ppm)
      for the v19/E26 protein-abundance round.

Files downloaded
----------------
- 22 x GSM1562980..GSM1563001 processed_genes.csv.gz  (~2 MB total)
  from ftp.ncbi.nlm.nih.gov/geo/samples/GSM1562nnn/.../suppl/
- 1 x 511145-WHOLE_ORGANISM-integrated.txt from
  https://pax-db.org/downloads/latest/datasets/511145/

Provenance: sha256 of every file is recorded in data/gse64021/README.md
and data/paxdb/README.md (same convention as data/m3d/README.md).
"""
import gzip
import hashlib
import shutil
from pathlib import Path
from urllib.request import Request, urlopen

BASE = Path("/home/z/my-project/data")
GSE_DIR = BASE / "gse64021"
PAX_DIR = BASE / "paxdb"
GSE_DIR.mkdir(parents=True, exist_ok=True)
PAX_DIR.mkdir(parents=True, exist_ok=True)

GEO_SAMPLES = {
    # GSM accession : (short name, cluster file stem)
    "GSM1562980": ("LB_od0.5", "GSM1562980_cluster_5_processed_genes"),
    "GSM1562981": ("LB_od1.0", "GSM1562981_cluster_7_processed_genes"),
    "GSM1562982": ("LB_od3.0", "GSM1562982_cluster_10_processed_genes"),
    "GSM1562983": ("HS_15min", "GSM1562983_cluster_12_processed_genes"),
    "GSM1562984": ("HS_30min", "GSM1562984_cluster_13_processed_genes"),
    "GSM1562985": ("HS_1h", "GSM1562985_cluster_14_processed_genes"),
    "GSM1562986": ("HS_2h", "GSM1562986_cluster_15_processed_genes"),
    "GSM1562987": ("HS_4h", "GSM1562987_cluster_16_processed_genes"),
    "GSM1562988": ("MOPS_1h", "GSM1562988_cluster_17_processed_genes"),
    "GSM1562989": ("MOPS_2h", "GSM1562989_cluster_18_processed_genes"),
    "GSM1562990": ("MOPS_4h", "GSM1562990_cluster_19_processed_genes"),
    "GSM1562991": ("MOPS_6h", "GSM1562991_cluster_20_processed_genes"),
    "GSM1562992": ("MC_1h", "GSM1562992_cluster_25_processed_genes"),
    "GSM1562993": ("MC_1h_PE", "GSM1562993_cluster_25_processed_genes"),
    "GSM1562994": ("MC_2h", "GSM1562994_cluster_26_processed_genes"),
    "GSM1562995": ("MC_2h_PE", "GSM1562995_cluster_26_processed_genes"),
    "GSM1562996": ("MC_4h", "GSM1562996_cluster_27_processed_genes"),
    "GSM1562997": ("MC_6h", "GSM1562997_cluster_28_processed_genes"),
    "GSM1562998": ("MP_1h", "GSM1562998_cluster_29_processed_genes"),
    "GSM1562999": ("MP_2h", "GSM1562999_cluster_30_processed_genes"),
    "GSM1563000": ("MP_4h", "GSM1563000_cluster_31_processed_genes"),
    "GSM1563001": ("MP_6h", "GSM1563001_cluster_32_processed_genes"),
}


def fetch(url: str, tries: int = 5) -> bytes:
    """curl with retries; verifies gzip magic when the URL ends .gz."""
    import subprocess
    import time
    last = b""
    for i in range(tries):
        r = subprocess.run(["curl", "-s", "--max-time", "120", url],
                           capture_output=True)
        raw = r.stdout
        if r.returncode == 0 and raw and (
                not url.endswith(".gz") or raw[:2] == b"\x1f\x8b"):
            return raw
        last = raw[:200]
        print(f"  [retry {i+1}] {url.rsplit('/', 1)[-1]}: rc={r.returncode} "
              f"len={len(raw)} head={last[:60]!r}")
        time.sleep(3 + 4 * i)
    raise RuntimeError(f"fetch failed after {tries} tries: {url} -> {last!r}")


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


manifest = []

# ----------------------------------------------------------- GSE64021 files
def bucket(gsm: str) -> str:
    """GEO FTP bucket: first 7 chars + 'nnn' (GSM1562980 -> GSM1562nnn)."""
    return gsm[:7] + "nnn"

for gsm, (name, stem) in GEO_SAMPLES.items():
    url = (f"https://ftp.ncbi.nlm.nih.gov/geo/samples/"
           f"{bucket(gsm)}/{gsm}/suppl/{stem}.csv.gz")
    raw = fetch(url)
    out = GSE_DIR / f"{name}.csv.gz"
    out.write_bytes(raw)
    # decompress a copy for grepping
    with gzip.open(out, "rb") as fin, open(GSE_DIR / f"{name}.csv", "wb") as fout:
        shutil.copyfileobj(fin, fout)
    manifest.append((f"{name}.csv.gz", len(raw), sha256(raw), url))
    print(f"[gse64021] {name:10s} {len(raw):7,d} B  sha256 {manifest[-1][2][:16]}...")

# ------------------------------------------------------------ PaxDB file
pax_url = ("https://pax-db.org/downloads/latest/datasets/511145/"
           "511145-WHOLE_ORGANISM-integrated.txt")
raw = fetch(pax_url)
out = PAX_DIR / "511145-WHOLE_ORGANISM-integrated.txt"
out.write_bytes(raw)
print(f"[paxdb]    integrated  {len(raw):,d} B  sha256 {sha256(raw)[:16]}...")

# --------------------------------------------------------- provenance docs
n_files = len(manifest)
doc = f"""# E25/E26 (v18/v19) external data

## GSE64021 -- RNA-seq (+ tandem-MS proteome) carbon-starvation series

- Source: GEO Series GSE64021, "Antisense transcription and its roles in
  response to environmental changes in E. coli K12"
  (contributors: E. Tabari, S. Li, X. Dong, H. Lee, S. Hwang, Z. Su;
  UNC Charlotte; series public 2023-12-15, submitted 2014-12-09;
  SRA study SRP050994; no linked journal publication at retrieval date
  -- cited by accession).
- Design (verbatim from the GEO overall design): MG1655 grown in LB to
  OD600 1.0, pelleted, resuspended in MOPS minimal medium either
  + glucose (MOPS control), WITHOUT glucose (carbon starvation, "M-C"),
  WITHOUT KH2PO4 (phosphorus starvation, "M-P"), or + glucose at 48 C
  (heat shock, "HS"); sampled at 1/2/4/6 h (M-C, M-P, MOPS) and
  15 min-4 h (HS). Directional RNA-seq; per-gene processed tables
  (mRNARaw, mRNATPM, asRNA..., PeptideRaw) produced by the depositors.
- Retrieved 2026-08-31 via https://ftp.ncbi.nlm.nih.gov/geo/samples/...
- {n_files} per-sample files, ~2 MB total; format:
  columns RegDbId, Gene (gene name), Strand, Start, End, Length, Sample,
  mRNARaw, mRNATPM, asRNARaw, asRNALen, asRNARPK, mRNACoverage, Gamma,
  TrMode, PeptideRaw, NPPH.
- Sample map: LB_od0.5/1.0/3.0; HS_15min/30min/1h/2h/4h; MOPS_1h/2h/4h/6h;
  MC_1h/2h/4h/6h (+ MC_1h_PE, MC_2h_PE paired-end re-sequencing of the
  same libraries); MP_1h/2h/4h/6h.
- sha256 per file (compressed .csv.gz):
"""
for fname, size, digest, url in manifest:
    doc += f"  - {fname}: {size:,d} B, sha256 {digest}\n"
doc += """  (decompressed .csv copies are generated by the fetch script and are
   not checksummed separately.)

## PaxDB -- E. coli K-12 MG1655 integrated whole-organism proteome

- Source: https://pax-db.org/downloads/latest/datasets/511145/
  511145-WHOLE_ORGANISM-integrated.txt (PaxDb v6.1 dataset id 3740039012;
  "integrated dataset: weighted average of all E.coli str. K-12 substr.
  MG1655 WHOLE_ORGANISM; score 23.3; coverage 91%").
- 3,759 lines; columns gene_name, string_external_id (511145.bNNNN --
  the b-number), abundance (ppm).
- License: CC BY 4.0 (PaxDb, von Mering lab, SIB/UZH).
- Retrieved 2026-08-31; sha256 of the file:
"""
doc += f"  {sha256(raw)}\n"
(GSE_DIR.parent / "gse64021" / "README.md").write_text(doc)
(PAX_DIR / "README.md").write_text(
    "See ../gse64021/README.md (section PaxDB) for provenance details.\n"
    f"sha256 511145-WHOLE_ORGANISM-integrated.txt: {sha256(raw)}\n")
print("\n[done] provenance READMEs written to data/gse64021/ and data/paxdb/")
