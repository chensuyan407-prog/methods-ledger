# Questions for the author

- [ ] **G1** (gap, steps) Confirm the order of the processing stages and the output of each stage.
- [ ] **G2** (gap, data) Name the dataset and where it was obtained (URL/DOI/accession).
- [ ] **G3** (gap, data) Which dataset version/release (or download date) was used? Different versions change sample counts and splits.
- [ ] **G4** (gap, data) Describe preprocessing and filtering (what was removed and how many items).
- [ ] **G5** (gap, control) How many independent runs/replicates per condition, and is mean ± SD/SE or a single run reported?
- [ ] **G6** (gap, control) Which baselines (implementation + version) were compared, and were they trained/tuned under the same budget and data?
- [ ] **G7** (gap, control) Which statistical test or uncertainty estimate supports comparisons (test, alpha, correction)?
- [ ] **G8** (gap, repro) Give the code commit/tag and the exact commands to reproduce the reported numbers.
- [ ] **G9** (gap, repro) How can readers obtain the data (URL/DOI, license, access restrictions)?
- [ ] **G10** (gap, repro) Which conditions were not tested (data, scale, hardware, settings) and where is the method expected to fail?
- [ ] **G11** (gap, control) Only one seed value appears in the materials: were results from a single run? If several runs, list their seeds. — facts F24
- [ ] **Q-u10** (draft_gap) Name, source/URL and version of the credit default dataset; preprocessing of features
- [ ] **Q-u16** (draft_gap) Which baseline (e.g. logistic regression) and under which tuning budget?
- [ ] **Q-u17** (draft_gap) Repeat with several seeds?
- [ ] **Q-u17** (draft_gap) Uncertainty estimate for the test AUC (e.g. bootstrap CI)?
- [ ] **Q-u19** (draft_gap) Python, scikit-learn and pandas versions; hardware
- [ ] **Q-u20** (draft_gap) Commit of the notebook and how it is executed
