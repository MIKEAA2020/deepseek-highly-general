# E27 (v20) external data: Schmidt et al. 2016 condition-dependent proteome

## Source

- Paper: Schmidt A., Kochanowski K., Vedelaar S., Ahrne E., Volkmer B.,
  Callipo L., Knoops K., Bauer M., Aebersold R., Heinemann M.,
  "The quantitative and condition-dependent Escherichia coli proteome",
  Nature Biotechnology 34:104-110 (2016); doi:10.1038/nbt.3418.
- Raw MS data: PRIDE PXD000498 (not used here; the processed
  supplementary tables were used instead).
- Processed supplementary tables: NIHMS65833-supplement-
  Supplementary_tables.xlsx, obtained via the Europe PMC REST
  supplementary-files endpoint for PMC4888949:
  https://www.ebi.ac.uk/europepmc/webservices/rest/PMC4888949/supplementaryFiles
  (direct PMC download is captcha-gated for curl; the REST endpoint
  returns the same files as a zip).
- Retrieved 2026-08-31.

## Files

- NIHMS65833-supplement-Supplementary_tables.xlsx -- 17,128,596 B,
  sha256 3280a13ff67a73f25440cff6ee73fb99b5ce3ef57854213dbbf6272be241912f
  (NOT committed; re-download per the URL above).
- epmc_suppl.zip -- 24,061,832 B (the REST endpoint's zip; NOT
  committed).
- schmidt2016_s8_fc.csv -- extracted Table S8 (dataset 2, BW25113,
  biological triplicates, SafeQuant label-free quantification):
  2,058 proteins x 22 conditions, per-protein fold-change
  (medianRatio) vs the glucose reference + q-values + per-condition
  triplicate CVs + peptide counts and confidence scores.
  sha256 f479d0c5d42fb77361a0439d3889417ee5b6e036f94d6edbf4ff3f915758dd8f
- schmidt2016_s6_map.csv -- extracted Table S6 final-table mapping:
  Uniprot accession -> gene name -> b-number (2,284 of 2,350 rows
  carry b-numbers; spot checks aceA=b4015, rpoB=b3987,
  gapA=P0A9B2=b1779, groL=b4143) + COG class.
- schmidt2016_s7_fc.csv -- extracted Table S7 (dataset 1, no
  replicates): 2,039 proteins x 18 conditions, fold-changes vs
  glucose; used only as a cross-dataset sensitivity.
- precise1k_metadata_qc_scan.csv -- metadata of all 1,035 PRECISE-1K
  (a.k.a. PRECISE 2.0, SBRG) samples, retrieved from
  https://raw.githubusercontent.com/SBRG/precise1k/main/data/precise1k/metadata_qc.csv
  (retrieved 2026-08-31; NOT committed upstream). Documents that the
  compendium contains no carbon-depletion condition (only Fe- and
  N-starvation), hence the Schmidt proteome was chosen for the E27
  replication.

## Extraction

scripts/e27_prepare_schmidt.py performs the extraction (Table S8
columns medianRatio_*/qvalue_*/cv_*/Peptides/Confidence; Table S6
positional columns 0/2/74/77 because "Gene" appears twice; Table S7
medianRatio_*). 4 duplicate-b-number rows in S8 (clpB listed twice,
bioD under two accessions P13000/P0A6E9) are averaged in the E27
analysis script.
