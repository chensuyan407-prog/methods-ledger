# Methods

## Procedure

1. Data split: the credit table credit_2019.csv was split into training and test sets with test_size = 0.25, stratified by the label, giving 22500 training and 7500 test rows.
2. Model selection: an XGBoost classifier was evaluated by stratified 5-fold cross-validation with shuffling on the training set.
3. Final model and test: the classifier was refit with the parameters below and evaluated once on the test set by ROC AUC.

## Data

The dataset name and source of credit_2019.csv are not documented [TO CONFIRM: Name, source/URL and version of the credit default dataset; preprocessing of features].

## Parameters

The model used 400 trees of maximum depth 5, a learning rate of 0.05, row subsampling 0.8 and column subsampling 0.8 per tree.



| Parameter | Value | Unit | Applies to | Source | Status |
|---|---|---|---|---|---|
| learning rate | 0.05 | - | - | xgb_params.json:4 (F21) | cited in text |
| maximum depth | 5 | - | - | xgb_params.json:3 (F20) | cited in text |
| number of estimators | 400 | - | - | xgb_params.json:2 (F19) | cited in text |
| cross-validation folds | 5 | - | - | model.ipynb:6 (F15) | cited in text |
| shuffling | True | - | - | model.ipynb:6 (F16) | cited in text |
| data-split seed | 11 | - | - | model.ipynb:5 (F13) | cited in text |
| stratification | y | - | - | model.ipynb:5 (F14) | cited in text |
| test fraction | 0.25 | - | test | model.ipynb:5 (F12) | cited in text |
| software (xgboost) | 2.0.3 | - | - | model.ipynb:14 (F10) | cited in text |
| evaluation metric | roc_auc_score | - | - | model.ipynb:12 (F18) | cited in text; other values: metrics.csv:2=auc_cv_mean; metrics.csv:3=auc_cv_sd; metrics.csv:4=auc_test |
| random seed | 11 | - | - | xgb_params.json:7 (F24) | cited in text |



## Evaluation and controls

Cross-validated AUC was 0.776 ± 0.006 (mean ± SD over folds) and test AUC 0.781. No baseline model was reported [TO CONFIRM: Which baseline (e.g. logistic regression) and under which tuning budget?]. A single random seed (11) was used for splitting and the model [TO CONFIRM: Repeat with several seeds?]; no statistical test was run [TO CONFIRM: Uncertainty estimate for the test AUC (e.g. bootstrap CI)?].

## Reproducibility

Software: xgboost 2.0.3 [TO CONFIRM: Python, scikit-learn and pandas versions; hardware]. Code version and run command [TO CONFIRM: Commit of the notebook and how it is executed].

## Limitations

- Results rest on one split seed (11) and one test set of 7500 rows; variance across splits is unknown.
- Hyperparameters were not reported as tuned; only the fixed values in xgb_params.json were evaluated.
