# Facts for case `fresh_xgb_credit` (methods-ledger 0.3.0)
profile: **generic** · target language: **en** · 21 facts from 4 files · 0 conflicts · 11 gaps/questions
Cite a fact in the draft as `[[F12]]` right after the sentence part it supports (several: `[[F12,F30]]`).

## Files
- `case.json` — case, 2 lines, 0 facts
- `metrics.csv` — table, 5 lines, 4 facts
- `model.ipynb` — code, 40 lines, 11 facts
- `xgb_params.json` — config, 8 lines, 6 facts

## Task (excerpt)
Write the Methods section (English) for the credit-default model from the notebook, params file and metrics.

## Experimental setup / 实验设置
| id | key (canonical) | value | source | kind | flags |
|---|---|---|---|---|---|
| F7 | version.xgboost (software) | `2.0.3` | model.ipynb:14 | log |  |

## Parameters / 参数
| id | key (canonical) | value | source | kind | flags |
|---|---|---|---|---|---|
| F18 | learning_rate (learning_rate) | `0.05` | xgb_params.json:4 | config |  |
| F17 | max_depth (max_depth) | `5` | xgb_params.json:3 | config |  |
| F16 | n_estimators (n_estimators) | `400` | xgb_params.json:2 | config |  |

## Datasets and splits / 数据集与划分
| id | key (canonical) | value | source | kind | flags |
|---|---|---|---|---|---|
| F12 | n_splits (k_folds) | `5` | model.ipynb:6 | code | keyword argument |
| F13 | shuffle (shuffle) | `True` | model.ipynb:6 | code | keyword argument |
| F10 | random_state (split_seed) | `11` | model.ipynb:5 | code | keyword argument |
| F14 | random_state (split_seed) | `11` | model.ipynb:6 | code | keyword argument |
| F11 | stratify (stratify) | `y` | model.ipynb:5 | code | keyword argument |
| F9 | test_size (test_size) | `0.25` | model.ipynb:5 | code | scope test; keyword argument |

## Baselines / controls and evaluation / 对照与评价
| id | key (canonical) | value | source | kind | flags |
|---|---|---|---|---|---|
| F15 | metric (metric) | `roc_auc_score` | model.ipynb:12 | code |  |

## Reproducibility and limitations / 可复现性与限制
| id | key (canonical) | value | source | kind | flags |
|---|---|---|---|---|---|
| F21 | random_state (seed) | `11` | xgb_params.json:7 | config |  |

## Other structured values (not mapped to a known key)
| id | key | value | source | kind |
|---|---|---|---|---|
| F1 | n_rows | `3` | metrics.csv:1 | table |
| F2 | auc_cv_mean | `0.776` | metrics.csv:2 | table |
| F3 | auc_cv_sd | `0.006` | metrics.csv:3 | table |
| F4 | auc_test | `0.781` | metrics.csv:4 | table |
| F19 | subsample | `0.8` | xgb_params.json:5 | config |
| F20 | colsample_bytree | `0.8` | xgb_params.json:6 | config |

## Lines with numbers in notes / data cards / drafts (cite them like any fact)
- F5 `model.ipynb:8` train rows: 22500, test rows: 7500
- F6 `model.ipynb:14` xgboost 2.0.3
- F8 `model.ipynb:15` test AUC 0.781

## Conflicts (must be marked [[CONFIRM: ...]] or resolved in agent.json)
none found

## Gaps / author questions (write [[GAP: ...]] in the draft where the information belongs)
- **G1** [steps, required, missing] ordered procedure (input -> operation -> output per step): Confirm the order of the processing stages and the output of each stage.
- **G2** [data, required, missing] dataset name and source: Name the dataset and where it was obtained (URL/DOI/accession).
- **G3** [data, required, missing] dataset version / release / snapshot date: Which dataset version/release (or download date) was used? Different versions change sample counts and splits.
- **G4** [data, recommended, missing] preprocessing / filtering: Describe preprocessing and filtering (what was removed and how many items).
- **G5** [control, required, missing] number of repetitions / replicates and how results are aggregated: How many independent runs/replicates per condition, and is mean ± SD/SE or a single run reported?
- **G6** [control, required, missing] baselines with versions and same-budget conditions: Which baselines (implementation + version) were compared, and were they trained/tuned under the same budget and data?
- **G7** [control, recommended, missing] statistical test / uncertainty estimate: Which statistical test or uncertainty estimate supports comparisons (test, alpha, correction)?
- **G8** [repro, required, missing] code version and run commands: Give the code commit/tag and the exact commands to reproduce the reported numbers.
- **G9** [repro, recommended, missing] data availability / access: How can readers obtain the data (URL/DOI, license, access restrictions)?
- **G10** [repro, required, author_input] limitations tied to concrete failure scenarios: Which conditions were not tested (data, scale, hardware, settings) and where is the method expected to fail?
- **G11** [control, required, ambiguous] single seed only?: Only one seed value appears in the materials: were results from a single run? If several runs, list their seeds.
