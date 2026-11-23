# Questions for the author

- [ ] **G1** (gap, steps) Confirm the order of the processing stages and the output of each stage.
- [ ] **G2** (gap, control) Define each metric (and on which split / at which checkpoint it is computed).
- [ ] **G3** (gap, repro) How can readers obtain the data (URL/DOI, license, access restrictions)?
- [ ] **G4** (gap, repro) Which conditions were not tested (data, scale, hardware, settings) and where is the method expected to fail?
- [ ] **C1** (conflict, params) duration (MTT) differs between sources: 45 min (notebook_2024-05.txt:3); 30 min (protocol.md:7). Which value did the reported run use? — facts F15, F28
- [ ] **C2** (conflict, params) duration (shak) differs between sources: 10 min (protocol.md:8); 5 s (reader_settings.txt:8). Which value did the reported run use? — facts F29, F46
- [ ] **Q-u10c** (draft_confirm) C1 the SOP specifies 30 min; the notebook records 45 min for this run because the reader was booked. Text uses the notebook value
- [ ] **Q-u12c** (draft_confirm) C2 the reader additionally shakes 5 s before reading (reader_settings.txt:8)
- [ ] **Q-u24** (draft_gap) Where will raw absorbance data and analysis.R be deposited (repository/DOI)?
- [ ] **Q-u25** (draft_gap) How were blank subtraction and normalisation to vehicle computed?
- [ ] **Q-u27c** (draft_confirm) C1 confirm the deviation applied to all plates
