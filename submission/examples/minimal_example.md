# Minimal example (illustrative output — not a platform case)

## Input (`/input`)

```
case.json        {"case_id": "fresh_xgb_credit", "task": "Write the Methods section (English) for the credit-default model ...",
                  "output_contract": {"methods": "...", "parameters": "...", "sources": "...", "open_questions": "..."}}
model.ipynb      train_test_split(..., test_size=0.25, random_state=11, stratify=y); StratifiedKFold(n_splits=5, shuffle=True, random_state=11)
                 outputs: "train rows: 22500, test rows: 7500", "xgboost 2.0.3", "test AUC 0.781"
xgb_params.json  {"n_estimators": 400, "max_depth": 5, "learning_rate": 0.05, "subsample": 0.8, "colsample_bytree": 0.8, "random_state": 11}
metrics.csv      auc_cv_mean 0.776, auc_cv_sd 0.006, auc_test 0.781
```

## Calls

```bash
python $SKILL_DIR/scripts/ml_extract.py --case /input/case.json --out /app/output --work /app/work
# -> language en, profile generic, 24 facts, 0 conflicts, 11 gaps; read /app/work/facts.md
# write /app/work/draft.md, e.g.
#   1. Data split: ... test_size = 0.25, stratified by the label [[@model.ipynb:5]], giving 22500 training and 7500 test rows [[@model.ipynb:8]].
#   The model used 400 trees [[@xgb_params.json:2]] of maximum depth 5 [[@xgb_params.json:3]] ...
#   No baseline model was reported [[GAP: Which baseline (e.g. logistic regression) and under which tuning budget?]].
python $SKILL_DIR/scripts/ml_build.py --work /app/work --out /app/output
# -> status: success - all checks pass; 17 items await author confirmation
```

If the draft had said "a learning rate of 0.8 [[@xgb_params.json:4]]", the build prints
`FLAG T02 l.15: 0.8 is not the value of the fact(s) tagged on this clause (F21=0.05); it is the value of F22 (subsample), tagged on another clause - move the tag or correct the value`;
an added sentence "Early stopping after 50 rounds was used." prints
`FLAG N01 l.23: number 50 has no source in the materials - remove it, replace it with the sourced value, or write [[GAP: ...]]`
(both verified on this case; since 0.3.0 neither blocks: the build exits 0, lists the T02 item for the author and marks 50 as
【待核实】/[UNVERIFIED] in methods.md).

## Output excerpt (`/app/output/methods.md`)

```
## Parameters

The model used 400 trees of maximum depth 5, a learning rate of 0.05, row subsampling 0.8 and column subsampling 0.8 per tree.

| Parameter | Value | Unit | Applies to | Source | Status |
|---|---|---|---|---|---|
| learning rate | 0.05 | - | - | xgb_params.json:4 (F21) | cited in text |
| maximum depth | 5 | - | - | xgb_params.json:3 (F20) | cited in text |
| number of estimators | 400 | - | - | xgb_params.json:2 (F19) | cited in text |
| data-split seed | 11 | - | - | model.ipynb:5 (F13) | cited in text |
...
## Evaluation and controls
... No baseline model was reported [TO CONFIRM: Which baseline (e.g. logistic regression) and under which tuning budget?].
```

`questions.md` (excerpt): `- [ ] G2 (gap, data) Name the dataset and where it was obtained (URL/DOI/accession).`

`result.json` (abridged): `{"case_id": "fresh_xgb_credit", "methods": "<chapter>", "parameters": [...rows...],
"sources": [...per-sentence fact map...], "open_questions": [...], "status": "success", "status_reason": "all checks pass;
17 items await author confirmation", "checks": {"fail": 0, "warn": 5, "coverage": [...]}, ...}`

The full run is in the bundle under `execution/results/fresh_run/`.
