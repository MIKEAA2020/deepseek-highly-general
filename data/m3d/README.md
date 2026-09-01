# E24 (v17 / Option A) external expression data

## M3D E. coli compendium v4 Build 6

- Source: http://m3d.mssm.edu/norm/E_coli_v4_Build_6.tar.gz
  (retrieved 2026-08-31; direct download, host alive)
- File: E_coli_v4_Build_6.tar.gz, 117,091,420 bytes
  sha256 e73088f7b9318dd592a9790683fa1255c0dfc38f7813ff2a744ee2dd73fa976e
  (gzip -t verified; tar fully extracted)
- Reference: Faith et al. 2008, Nucleic Acids Res 36(Database issue):
  D866-D870 (PMID 17932051)
- Used by scripts/novelty_v17_option_a_e24.py:
  - E_coli_v4_Build_6_chips907probes4297.tab  (4,297 gene probes x 907
    arrays, log2 uniformly normalized)  [NOT in git: 30.8 MB]
  - E_coli_v4_Build_6.probe_set_descriptions  (probe -> locus/b-number)
  - E_coli_v4_Build_6.experiment_descriptions [in git]
  - E_coli_v4_Build_6.experiment_feature_descriptions [in git]
- The tarball and the large .tab matrices are intentionally NOT committed
  (GitHub 100 MB/file limit and repo bloat); re-download from the URL
  above and verify the sha256, or re-derive from the committed
  description files.

## PRECISE RNA-seq compendium

- Source: https://github.com/SBRG/precise-db (master tarball,
  retrieved 2026-08-31), 41,909,684 bytes
  sha256 17a607ed76464a120a8bcd665953dc30e53e4ac106434a2343f0292eef75666e
- Reference: Sastry et al. 2019, bioRxiv 10.1101/080929
  (metadata.csv DOIs; GEO GSE65643 for control/omics samples)
- Used by scripts/novelty_v17_option_a_e24.py:
  - data/log_tpm.csv (3,923 genes x 278 samples, b-number index,
    log2 TPM)  [NOT in git: 18.3 MB]
  - data/metadata.csv [in git]
  - data/gene_info.csv [in git]
- COLOMBOS (colombos.net) was unreachable from this environment
  (connection hangs); M3D + PRECISE close the same coverage gap.
