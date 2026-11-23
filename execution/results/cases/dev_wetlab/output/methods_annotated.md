# Materials and Methods

## Procedure

1. Cell seeding: HeLa cells (ATCC CCL-2, passage 12) <sup>[F8: notebook_2024-05.txt:1; F13: notebook_2024-05.txt:1]</sup> were seeded at 5,000 cells per well in 96-well plates in 100 µL DMEM with 10% FBS <sup>[F17: protocol.md:3]</sup>; output: plates P1–P3 <sup>[F8: notebook_2024-05.txt:1; F13: notebook_2024-05.txt:1]</sup>.
2. Attachment: plates were incubated for 24 h at 37 °C and 5% CO2 <sup>[F18: protocol.md:4; F26: protocol.md:4]</sup>.
3. Treatment: cells were treated with compound K-17 (lot KX-0412) <sup>[F9: notebook_2024-05.txt:2; F14: notebook_2024-05.txt:2]</sup> at 0, 1, 5, 10, 50 and 100 µM with a final DMSO concentration of 0.1% <sup>[F19: protocol.md:5]</sup>, then incubated for 48 h <sup>[F20: protocol.md:6; F27: protocol.md:6]</sup>.
4. MTT labelling: 10 µL MTT (5 mg/mL) was added per well and incubated at 37 °C <sup>[protocol.md:7]</sup> for 45 min <sup>[F10: notebook_2024-05.txt:3; F15: notebook_2024-05.txt:3]</sup> [AUTHOR TO CONFIRM: C1 the SOP specifies 30 min; the notebook records 45 min for this run because the reader was booked. Text uses the notebook value].
5. Solubilisation: the medium was removed, 100 µL DMSO was added and the plates were shaken for 10 min <sup>[F22: protocol.md:8; F29: protocol.md:8]</sup> [AUTHOR TO CONFIRM: C2 the reader additionally shakes 5 s before reading (reader_settings.txt:8)].
6. Readout: absorbance was read at 570 nm with a 630 nm reference <sup>[F23: protocol.md:9]</sup> (decision rule for exclusion: wells with visible contamination were excluded; well H12 on plate P2 was excluded <sup>[F12: notebook_2024-05.txt:5]</sup>).

## Instrument settings

Absorbance was measured on a BioTek Synergy H1 <sup>[F30: reader_settings.txt:1]</sup> with Gen5 3.11 <sup>[F31: reader_settings.txt:2; F32: reader_settings.txt:2]</sup> as an endpoint read <sup>[reader_settings.txt:3]</sup> at 570 nm <sup>[F33: reader_settings.txt:4; F34: reader_settings.txt:4; F35: reader_settings.txt:4]</sup> with a 630 nm reference wavelength <sup>[F36: reader_settings.txt:5; F37: reader_settings.txt:5; F38: reader_settings.txt:5]</sup>, a read height of 8.5 mm <sup>[reader_settings.txt:6]</sup> and a chamber temperature of 25 °C <sup>[F41: reader_settings.txt:7; F42: reader_settings.txt:7; F43: reader_settings.txt:7]</sup>.

## Controls, replicates and statistics

Each plate included vehicle wells (0.1% DMSO), blank wells (medium only) and a doxorubicin 1 µM positive control <sup>[protocol.md:11]</sup>. Plates P1–P3 were three independent experiments <sup>[F11: notebook_2024-05.txt:4; F16: notebook_2024-05.txt:4]</sup>; viability is reported as mean ± SD with n = 3 per concentration <sup>[F48: viability_summary.csv:2; F49: viability_summary.csv:2; F50: viability_summary.csv:2]</sup>. Concentration–response curves were fitted with a four-parameter log-logistic model (LL.4) <sup>[analysis.R:5]</sup> to estimate the IC50 with delta-method intervals <sup>[analysis.R:6]</sup>. Treatment groups were compared with the vehicle by one-way ANOVA with Dunnett's post hoc test <sup>[F6: analysis.R:7; F7: analysis.R:7]</sup> at alpha = 0.05 <sup>[F2: analysis.R:9]</sup>. Analyses used R 4.3.1 <sup>[F3: analysis.R:1]</sup> and drc 3.0-1 <sup>[F4: analysis.R:2]</sup> with set.seed(7) <sup>[F5: analysis.R:3]</sup>.

## Data availability and reproducibility

The plate-reader export and analysis script are part of the study materials [TO CONFIRM: Where will raw absorbance data and analysis.R be deposited (repository/DOI)?]. Background subtraction and normalisation to vehicle [TO CONFIRM: How were blank subtraction and normalisation to vehicle computed?].

## Limitations

- Only one cell line (HeLa, passage 12) was tested <sup>[F8: notebook_2024-05.txt:1; F13: notebook_2024-05.txt:1]</sup>; responses of other cell types are unknown.
- The MTT incubation (45 min) deviated from the SOP (30 min) in all three experiments <sup>[F10: notebook_2024-05.txt:3; F15: notebook_2024-05.txt:3; F21: protocol.md:7; F28: protocol.md:7]</sup> [AUTHOR TO CONFIRM: C1 confirm the deviation applied to all plates], so absolute absorbance values may not be comparable with SOP runs.
- Each concentration rests on n = 3 independent experiments <sup>[F48: viability_summary.csv:2; F49: viability_summary.csv:2; F50: viability_summary.csv:2]</sup>; one well was lost to contamination <sup>[F12: notebook_2024-05.txt:5]</sup>.


**Table. Parameters and their sources**



| Parameter | Value | Unit | Applies to | Source | Status |
|---|---|---|---|---|---|
| duration | 45 min | - | text/duration | notebook_2024-05.txt:3 (F15) | CONFLICT C1 - author to confirm |
| temperature | 25 °C | - | - | reader_settings.txt:7 (F41) | cited in text; other values: reader_settings.txt:7=25 |
| wavelength | 570 nm | - | - | reader_settings.txt:4 (F33) | cited in text; other values: reader_settings.txt:4=570; reader_settings.txt:5=630 |
| lot / catalogue number | KX-0412 | - | - | notebook_2024-05.txt:2 (F14) | cited in text |
| reagent / material | ATCC CCL-2 | - | - | notebook_2024-05.txt:1 (F13) | cited in text |
| instrument | BioTek Synergy H1 | - | - | reader_settings.txt:1 (F30) | cited in text |
| software (Software) | Gen5 3.11 | - | - | reader_settings.txt:2 (F31) | cited in text |
| statistics software (r) | 4.3.1 | - | - | analysis.R:1 (F3) | cited in text |
| statistics software (drc) | 3.0-1 | - | - | analysis.R:2 (F4) | cited in text |
| significance level | 0.05 | - | - | analysis.R:9 (F2) | cited in text |
| repetitions / replicates | 3 | - | - | notebook_2024-05.txt:4 (F16) | cited in text |
| statistical test | one-way ANOVA | - | - | analysis.R:7 (F6) | cited in text; other values: analysis.R:7=Dunnett; analysis.R:8=aov |
| random seed | 7 | - | set | analysis.R:3 (F5) | cited in text |
