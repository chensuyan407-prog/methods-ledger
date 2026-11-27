# Methods

## Procedure

1. Data split: the credit table credit_2019.csv <sup>[model.ipynb:4]</sup> was split into training and test sets with test_size = 0.25, stratified by the label <sup>[F9: model.ipynb:5; F10: model.ipynb:5; F11: model.ipynb:5]</sup>, giving 22500 training and 7500 test rows <sup>[F5: model.ipynb:8]</sup>.
2. Model selection: an XGBoost classifier was evaluated by stratified 5-fold cross-validation with shuffling <sup>[F12: model.ipynb:6; F13: model.ipynb:6; F14: model.ipynb:6]</sup> on the training set.
3. Final model and test: the classifier was refit with the parameters below <sup>[model.ipynb:11]</sup> and evaluated once on the test set by ROC AUC <sup>[F15: model.ipynb:12]</sup>.

## Data

The dataset name and source of credit_2019.csv are not documented [TO CONFIRM: Name, source/URL and version of the credit default dataset; preprocessing of features].

## Parameters

The model used 400 trees <sup>[F16: xgb_params.json:2]</sup> of maximum depth 5 <sup>[F17: xgb_params.json:3]</sup>, a learning rate of 0.05 <sup>[F18: xgb_params.json:4]</sup>, row subsampling 0.8 <sup>[F19: xgb_params.json:5]</sup> and column subsampling 0.8 per tree <sup>[F20: xgb_params.json:6]</sup>.



| Parameter | Value | Unit | Applies to | Source | Status |
|---|---|---|---|---|---|
| learning rate | 0.05 | - | - | xgb_params.json:4 (F18) | cited in text |
| maximum depth | 5 | - | - | xgb_params.json:3 (F17) | cited in text |
| number of estimators | 400 | - | - | xgb_params.json:2 (F16) | cited in text |
| cross-validation folds | 5 | - | - | model.ipynb:6 (F12) | cited in text |
| shuffling | True | - | - | model.ipynb:6 (F13) | cited in text |
| data-split seed | 11 | - | - | model.ipynb:5 (F10) | cited in text |
| stratification | y | - | - | model.ipynb:5 (F11) | cited in text |
| test fraction | 0.25 | - | test | model.ipynb:5 (F9) | cited in text |
| software (xgboost) | 2.0.3 | - | - | model.ipynb:14 (F7) | cited in text |
| evaluation metric | roc_auc_score | - | - | model.ipynb:12 (F15) | cited in text |
| random seed | 11 | - | - | xgb_params.json:7 (F21) | cited in text |



## Evaluation and controls

Cross-validated AUC was 0.776 ± 0.006 (mean ± SD over folds) <sup>[F2: metrics.csv:2; F3: metrics.csv:3]</sup> and test AUC 0.781 <sup>[F4: metrics.csv:4]</sup>. No baseline model was reported [TO CONFIRM: Which baseline (e.g. logistic regression) and under which tuning budget?]. A single random seed (11) was used for splitting and the model <sup>[F9: model.ipynb:5; F10: model.ipynb:5; F11: model.ipynb:5; F21: xgb_params.json:7]</sup> [TO CONFIRM: Repeat with several seeds?]; no statistical test was run [TO CONFIRM: Uncertainty estimate for the test AUC (e.g. bootstrap CI)?].

## Reproducibility

Software: xgboost 2.0.3 <sup>[F6: model.ipynb:14; F7: model.ipynb:14]</sup> [TO CONFIRM: Python, scikit-learn and pandas versions; hardware]. Code version and run command [TO CONFIRM: Commit of the notebook and how it is executed].

## Limitations

- Results rest on one split seed (11) <sup>[F9: model.ipynb:5; F10: model.ipynb:5; F11: model.ipynb:5]</sup> and one test set of 7500 rows <sup>[F5: model.ipynb:8]</sup>; variance across splits is unknown.
- Hyperparameters were not reported as tuned; only the fixed values in xgb_params.json were evaluated <sup>[F16: xgb_params.json:2]</sup>.
