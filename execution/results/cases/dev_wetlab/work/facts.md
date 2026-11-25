# Facts for case `dev_wetlab_mtt` (methods-ledger 0.2.0)
profile: **wetlab** · target language: **en** · 65 facts from 6 files · 2 conflicts · 4 gaps/questions
Cite a fact in the draft as `[[F12]]` right after the sentence part it supports (several: `[[F12,F30]]`).

## Files
- `analysis.R` — code, 10 lines, 7 facts
- `case.json` — case, 4 lines, 0 facts
- `notebook_2024-05.txt` — doc, 6 lines, 9 facts
- `protocol.md` — doc, 12 lines, 13 facts
- `reader_settings.txt` — doc, 9 lines, 17 facts
- `viability_summary.csv` — table, 8 lines, 19 facts

## Task (excerpt)
Write the Materials and Methods section (English, for a cell-biology journal) for the cytotoxicity experiment, from the protocol, notebook, plate-reader export and analysis script. Include materials, procedure, instrument settings, controls, replicates, statistics, and reproducibility notes. Do not invent values.

## Experimental setup / 实验设置
| id | key (canonical) | value | source | kind | flags |
|---|---|---|---|---|---|
| F30 | Instrument (instrument) | `BioTek Synergy H1` | reader_settings.txt:1 | doc_kv |  |
| F31 | Software (software) | `Gen5 3.11` | reader_settings.txt:2 | doc_kv |  |
| F3 | version.r (software_stats) | `4.3.1` | analysis.R:1 | code |  |
| F4 | version.drc (software_stats) | `3.0-1` | analysis.R:2 | code |  |

## Parameters / 参数
| id | key (canonical) | value | source | kind | flags |
|---|---|---|---|---|---|
| F15 | text.duration.MTT (duration) | `45 min` | notebook_2024-05.txt:3 | doc_kv | CONFLICT C1 |
| F26 | text.duration.incubat (duration) | `24 h` | protocol.md:4 | doc_kv |  |
| F27 | text.duration.incubat (duration) | `48 h` | protocol.md:6 | doc_kv |  |
| F28 | text.duration.MTT (duration) | `30 min` | protocol.md:7 | doc_kv | CONFLICT C1 |
| F29 | text.duration.shak (duration) | `10 min` | protocol.md:8 | doc_kv | CONFLICT C2 |
| F46 | text.duration.shak (duration) | `5 s` | reader_settings.txt:8 | doc_kv | CONFLICT C2 |
| F41 | Temperature (temperature) | `25 °C` | reader_settings.txt:7 | doc_kv |  |
| F42 | text.Temperature (temperature) | `25` | reader_settings.txt:7 | doc_kv |  |
| F33 | Wavelength (wavelength) | `570 nm` | reader_settings.txt:4 | doc_kv |  |
| F34 | text.Wavelength (wavelength) | `570` | reader_settings.txt:4 | doc_kv |  |
| F37 | text.wavelength (wavelength) | `630` | reader_settings.txt:5 | doc_kv |  |

## Datasets and splits / 数据集与划分
| id | key (canonical) | value | source | kind | flags |
|---|---|---|---|---|---|
| F14 | lot (lot) | `KX-0412` | notebook_2024-05.txt:2 | doc_kv |  |
| F13 | lot (reagent) | `ATCC CCL-2` | notebook_2024-05.txt:1 | doc_kv |  |

## Baselines / controls and evaluation / 对照与评价
| id | key (canonical) | value | source | kind | flags |
|---|---|---|---|---|---|
| F2 | alpha (alpha_level) | `0.05` | analysis.R:9 | code | assignment |
| F16 | n_runs (n_runs) | `3` | notebook_2024-05.txt:4 | doc_kv |  |
| F1 | statistical_test (statistical_test) | `aov` | analysis.R:8 | code |  |
| F6 | statistical_test (statistical_test) | `one-way ANOVA` | analysis.R:7 | code |  |
| F7 | statistical_test (statistical_test) | `Dunnett` | analysis.R:7 | code |  |

## Reproducibility and limitations / 可复现性与限制
| id | key (canonical) | value | source | kind | flags |
|---|---|---|---|---|---|
| F5 | set.seed (seed) | `7` | analysis.R:3 | code |  |

## Other structured values (not mapped to a known key)
| id | key | value | source | kind |
|---|---|---|---|---|
| F47 | n_rows | `6` | viability_summary.csv:1 | table |
| F48 | 0.mean_viability_pct | `100.0` | viability_summary.csv:2 | table |
| F49 | 0.sd_pct | `4.1` | viability_summary.csv:2 | table |
| F50 | 0.n | `3` | viability_summary.csv:2 | table |
| F51 | 1.mean_viability_pct | `97.2` | viability_summary.csv:3 | table |
| F52 | 1.sd_pct | `5.0` | viability_summary.csv:3 | table |
| F53 | 1.n | `3` | viability_summary.csv:3 | table |
| F54 | 5.mean_viability_pct | `88.4` | viability_summary.csv:4 | table |
| F55 | 5.sd_pct | `6.2` | viability_summary.csv:4 | table |
| F56 | 5.n | `3` | viability_summary.csv:4 | table |
| F57 | 10.mean_viability_pct | `71.9` | viability_summary.csv:5 | table |
| F58 | 10.sd_pct | `5.5` | viability_summary.csv:5 | table |
| F59 | 10.n | `3` | viability_summary.csv:5 | table |
| F60 | 50.mean_viability_pct | `32.6` | viability_summary.csv:6 | table |
| F61 | 50.sd_pct | `4.8` | viability_summary.csv:6 | table |
| F62 | 50.n | `3` | viability_summary.csv:6 | table |
| F63 | 100.mean_viability_pct | `12.3` | viability_summary.csv:7 | table |
| F64 | 100.sd_pct | `2.9` | viability_summary.csv:7 | table |
| F65 | 100.n | `3` | viability_summary.csv:7 | table |

## Lines with numbers in notes / data cards / drafts (cite them like any fact)
- F8 `notebook_2024-05.txt:1` 2024-05-06 seeded plates P1-P3, HeLa passage 12 (ATCC CCL-2)
- F9 `notebook_2024-05.txt:2` 2024-05-07 treatment K-17 lot KX-0412, dilution series as SOP
- F10 `notebook_2024-05.txt:3` 2024-05-09 MTT added; incubation 45 min this time (reader booked)
- F11 `notebook_2024-05.txt:4` 2024-05-09 read on Synergy H1 (BioTek), plates P1-P3 = three independent experiments
- F17 `protocol.md:3` 1. Seed HeLa cells at 5,000 cells per well in 96-well plates (100 µL DMEM + 10% FBS).
- F18 `protocol.md:4` 2. Incubate 24 h at 37 °C, 5% CO2.
- F19 `protocol.md:5` 3. Treat with compound K-17 at 0, 1, 5, 10, 50 and 100 µM (final DMSO 0.1%).
- F20 `protocol.md:6` 4. Incubate 48 h.
- F21 `protocol.md:7` 5. Add 10 µL MTT (5 mg/mL) per well and incubate 30 min at 37 °C.
- F22 `protocol.md:8` 6. Remove medium, add 100 µL DMSO, shake 10 min.
- F23 `protocol.md:9` 7. Read absorbance at 570 nm (reference 630 nm).
- F25 `protocol.md:11` Controls: vehicle (0.1% DMSO), blank wells (medium only), positive control doxorubicin 1 µM.
- F32 `reader_settings.txt:2` Software: Gen5 3.11
- F35 `reader_settings.txt:4` Wavelength: 570 nm
- F38 `reader_settings.txt:5` Reference wavelength: 630 nm
- F40 `reader_settings.txt:6` Read height: 8.5 mm
- F43 `reader_settings.txt:7` Temperature: 25 °C
- F45 `reader_settings.txt:8` Shake: 5 s linear before read

## Conflicts (must be marked [[CONFIRM: ...]] or resolved in agent.json)
- **C1** duration (MTT): `45 min` (F15; notebook_2024-05.txt:3; doc_kv); `30 min` (F28; protocol.md:7; doc_kv) — precedence guess F15
- **C2** duration (shak): `10 min` (F29; protocol.md:8; doc_kv); `5 s` (F46; reader_settings.txt:8; doc_kv) — precedence guess F29

## Gaps / author questions (write [[GAP: ...]] in the draft where the information belongs)
- **G1** [steps, required, only_mentioned_in_text] ordered procedure (input -> operation -> output per step): Confirm the order of the processing stages and the output of each stage.
- **G2** [control, required, only_mentioned_in_text] evaluation metrics / measured outcomes: Define each metric (and on which split / at which checkpoint it is computed).
- **G3** [repro, recommended, missing] data availability / access: How can readers obtain the data (URL/DOI, license, access restrictions)?
- **G4** [repro, required, author_input] limitations tied to concrete failure scenarios: Which conditions were not tested (data, scale, hardware, settings) and where is the method expected to fail?
