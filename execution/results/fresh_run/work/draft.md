# Methods

## Procedure

1. Data split: the credit table credit_2019.csv [[SRC: model.ipynb:4]] was split into training and test sets with test_size = 0.25, stratified by the label [[@model.ipynb:5]], giving 22500 training and 7500 test rows [[@model.ipynb:8]].
2. Model selection: an XGBoost classifier was evaluated by stratified 5-fold cross-validation with shuffling [[@model.ipynb:6]] on the training set.
3. Final model and test: the classifier was refit with the parameters below [[SRC: model.ipynb:11]] and evaluated once on the test set by ROC AUC [[@model.ipynb:12]].

## Data

The dataset name and source of credit_2019.csv are not documented [[GAP: Name, source/URL and version of the credit default dataset; preprocessing of features]].

## Parameters

The model used 400 trees [[@xgb_params.json:2]] of maximum depth 5 [[@xgb_params.json:3]], a learning rate of 0.05 [[@xgb_params.json:4]], row subsampling 0.8 [[@xgb_params.json:5]] and column subsampling 0.8 per tree [[@xgb_params.json:6]].

[[PARAM_TABLE]]

## Evaluation and controls

Cross-validated AUC was 0.776 ± 0.006 (mean ± SD over folds) [[@metrics.csv:2,@metrics.csv:3]] and test AUC 0.781 [[@metrics.csv:4]]. No baseline model was reported [[GAP: Which baseline (e.g. logistic regression) and under which tuning budget?]]. A single random seed (11) was used for splitting and the model [[@model.ipynb:5,@xgb_params.json:7]] [[GAP: Repeat with several seeds?]]; no statistical test was run [[GAP: Uncertainty estimate for the test AUC (e.g. bootstrap CI)?]].

## Reproducibility

Software: xgboost 2.0.3 [[@model.ipynb:14]] [[GAP: Python, scikit-learn and pandas versions; hardware]]. Code version and run command [[GAP: Commit of the notebook and how it is executed]].

## Limitations

- Results rest on one split seed (11) [[@model.ipynb:5]] and one test set of 7500 rows [[@model.ipynb:8]]; variance across splits is unknown.
- Hyperparameters were not reported as tuned; only the fixed values in xgb_params.json were evaluated [[@xgb_params.json:2]].
