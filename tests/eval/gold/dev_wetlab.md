# Materials and Methods

## Procedure

1. Cell seeding: HeLa cells (ATCC CCL-2, passage 12) [[@notebook_2024-05.txt:1]] were seeded at 5,000 cells per well in 96-well plates in 100 µL DMEM with 10% FBS [[@protocol.md:3]]; output: plates P1–P3 [[@notebook_2024-05.txt:1]].
2. Attachment: plates were incubated for 24 h at 37 °C and 5% CO2 [[@protocol.md:4]].
3. Treatment: cells were treated with compound K-17 (lot KX-0412) [[@notebook_2024-05.txt:2]] at 0, 1, 5, 10, 50 and 100 µM with a final DMSO concentration of 0.1% [[@protocol.md:5]], then incubated for 48 h [[@protocol.md:6]].
4. MTT labelling: 10 µL MTT (5 mg/mL) was added per well and incubated at 37 °C [[SRC: protocol.md:7]] for 45 min [[@notebook_2024-05.txt:3]] [[CONFIRM: C1 the SOP specifies 30 min; the notebook records 45 min for this run because the reader was booked. Text uses the notebook value]].
5. Solubilisation: the medium was removed, 100 µL DMSO was added and the plates were shaken for 10 min [[@protocol.md:8]] [[CONFIRM: C2 the reader additionally shakes 5 s before reading (reader_settings.txt:8)]].
6. Readout: absorbance was read at 570 nm with a 630 nm reference [[@protocol.md:9]] (decision rule for exclusion: wells with visible contamination were excluded; well H12 on plate P2 was excluded [[@notebook_2024-05.txt:5]]).

## Instrument settings

Absorbance was measured on a BioTek Synergy H1 [[@reader_settings.txt:1]] with Gen5 3.11 [[@reader_settings.txt:2]] as an endpoint read [[SRC: reader_settings.txt:3]] at 570 nm [[@reader_settings.txt:4]] with a 630 nm reference wavelength [[@reader_settings.txt:5]], a read height of 8.5 mm [[SRC: reader_settings.txt:6]] and a chamber temperature of 25 °C [[@reader_settings.txt:7]].

## Controls, replicates and statistics

Each plate included vehicle wells (0.1% DMSO), blank wells (medium only) and a doxorubicin 1 µM positive control [[SRC: protocol.md:11]]. Plates P1–P3 were three independent experiments [[@notebook_2024-05.txt:4]]; viability is reported as mean ± SD with n = 3 per concentration [[@viability_summary.csv:2]]. Concentration–response curves were fitted with a four-parameter log-logistic model (LL.4) [[SRC: analysis.R:5]] to estimate the IC50 with delta-method intervals [[SRC: analysis.R:6]]. Treatment groups were compared with the vehicle by one-way ANOVA with Dunnett's post hoc test [[@analysis.R:7]] at alpha = 0.05 [[@analysis.R:9]]. Analyses used R 4.3.1 [[@analysis.R:1]] and drc 3.0-1 [[@analysis.R:2]] with set.seed(7) [[@analysis.R:3]].

## Data availability and reproducibility

The plate-reader export and analysis script are part of the study materials [[GAP: Where will raw absorbance data and analysis.R be deposited (repository/DOI)?]]. Background subtraction and normalisation to vehicle [[GAP: How were blank subtraction and normalisation to vehicle computed?]].

## Limitations

- Only one cell line (HeLa, passage 12) was tested [[@notebook_2024-05.txt:1]]; responses of other cell types are unknown.
- The MTT incubation (45 min) deviated from the SOP (30 min) in all three experiments [[@notebook_2024-05.txt:3,@protocol.md:7]] [[CONFIRM: C1 confirm the deviation applied to all plates]], so absolute absorbance values may not be comparable with SOP runs.
- Each concentration rests on n = 3 independent experiments [[@viability_summary.csv:2]]; one well was lost to contamination [[@notebook_2024-05.txt:5]].
