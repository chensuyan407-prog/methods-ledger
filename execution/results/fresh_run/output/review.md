# Review — fresh_xgb_credit

status: **success** — all checks pass; 17 items await author confirmation

facts extracted 24, cited 22; conflicts 0; questions 17; preview: pymupdf story, 2 pages

## Coverage
- E_steps (steps, required): **covered** — ordered procedure (input -> operation -> output per step)
- E_dataset (data, required): **marked_gap** — dataset name and source
- E_dataset_version (data, required): **marked_gap** — dataset version / release / snapshot date
- E_split (data, required): **covered** — split sizes/ratios and how they were drawn
- E_preproc (data, recommended): **marked_gap** — preprocessing / filtering
- E_software (setup, required): **covered** — software and versions
- E_seed (repro, required): **covered** — random seed(s)
- E_repeats (control, required): **covered** — number of repetitions / replicates and how results are aggregated
- E_baseline (control, required): **marked_gap** — baselines with versions and same-budget conditions
- E_metric (control, required): **covered** — evaluation metrics / measured outcomes
- E_stats (control, recommended): **covered** — statistical test / uncertainty estimate
- E_code (repro, required): **marked_gap** — code version and run commands
- E_data_access (repro, recommended): **marked_gap** — data availability / access
- E_limits (repro, required): **covered** — limitations tied to concrete failure scenarios

## Check items
- WARN T05 l.7: cited F18 (metric = roc_auc_score) but its value is not in the sentence
- WARN T05 l.21: cited F2 (auc_cv_mean.metric = auc_cv_mean) but its value is not in the sentence
- WARN T05 l.21: cited F4 (auc_cv_sd.metric = auc_cv_sd) but its value is not in the sentence
- WARN T05 l.21: cited F6 (auc_test.metric = auc_test) but its value is not in the sentence
- WARN T05 l.21: cited F14 (stratify = y) but its value is not in the sentence
