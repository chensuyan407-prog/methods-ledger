# Materials and Methods

## Procedure

1. Cell seeding: HeLa cells (ATCC CCL-2, passage 12) were seeded at 5,000 cells per well in 96-well plates in 100 µL DMEM with 10% FBS; output: plates P1–P3.
2. Attachment: plates were incubated for 24 h at 37 °C and 5% CO2.
3. Treatment: cells were treated with compound K-17 (lot KX-0412) at 0, 1, 5, 10, 50 and 100 µM with a final DMSO concentration of 0.1%, then incubated for 48 h.
4. MTT labelling: 10 µL MTT (5 mg/mL) was added per well and incubated at 37 °C for 45 min [AUTHOR TO CONFIRM: C1 the SOP specifies 30 min; the notebook records 45 min for this run because the reader was booked. Text uses the notebook value].
5. Solubilisation: the medium was removed, 100 µL DMSO was added and the plates were shaken for 10 min [AUTHOR TO CONFIRM: C2 the reader additionally shakes 5 s before reading (reader_settings.txt:8)].
6. Readout: absorbance was read at 570 nm with a 630 nm reference (decision rule for exclusion: wells with visible contamination were excluded; well H12 on plate P2 was excluded ).

## Instrument settings

Absorbance was measured on a BioTek Synergy H1 with Gen5 3.11 as an endpoint read at 570 nm with a 630 nm reference wavelength, a read height of 8.5 mm and a chamber temperature of 25 °C.

## Controls, replicates and statistics

Each plate included vehicle wells (0.1% DMSO), blank wells (medium only) and a doxorubicin 1 µM positive control. Plates P1–P3 were three independent experiments; viability is reported as mean ± SD with n = 3 per concentration. Concentration–response curves were fitted with a four-parameter log-logistic model (LL.4) to estimate the IC50 with delta-method intervals. Treatment groups were compared with the vehicle by one-way ANOVA with Dunnett's post hoc test at alpha = 0.05. Analyses used R 4.3.1 and drc 3.0-1 with set.seed(7).

## Data availability and reproducibility

The plate-reader export and analysis script are part of the study materials [TO CONFIRM: Where will raw absorbance data and analysis.R be deposited (repository/DOI)?]. Background subtraction and normalisation to vehicle [TO CONFIRM: How were blank subtraction and normalisation to vehicle computed?].

## Limitations

- Only one cell line (HeLa, passage 12) was tested; responses of other cell types are unknown.
- The MTT incubation (45 min) deviated from the SOP (30 min) in all three experiments [AUTHOR TO CONFIRM: C1 confirm the deviation applied to all plates], so absolute absorbance values may not be comparable with SOP runs.
- Each concentration rests on n = 3 independent experiments; one well was lost to contamination.


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
