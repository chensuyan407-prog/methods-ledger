# Facts for case `dev_ml_textcls` (methods-ledger 0.2.0)
profile: **ml** · target language: **zh** · 119 facts from 13 files · 1 conflicts · 5 gaps/questions
Cite a fact in the draft as `[[F12]]` right after the sentence part it supports (several: `[[F12,F30]]`).

## Files
- `case.json` — case, 12 lines, 0 facts
- `data_card.md` — datacard, 8 lines, 12 facts
- `notes.md` — doc, 6 lines, 6 facts
- `requirements.txt` — env, 6 lines, 5 facts
- `task.md` — task, 4 lines, 0 facts
- `configs/baseline_tfidf.yaml` — config, 8 lines, 6 facts
- `configs/train.yaml` — config, 26 lines, 20 facts
- `logs/baseline.log` — log, 3 lines, 5 facts
- `logs/preprocess.log` — log, 6 lines, 10 facts
- `logs/train_bert_seed42.log` — log, 13 lines, 36 facts
- `src/baseline.py` — code, 8 lines, 3 facts
- `src/preprocess.py` — code, 13 lines, 6 facts
- `src/train.py` — code, 19 lines, 10 facts

## Task (excerpt)
# 任务
为一篇中文期刊论文撰写“3 方法与实验”一节。读者为领域审稿人。材料位于本目录：训练配置、代码、训练/评测日志、依赖文件、数据说明和实验笔记。
要求：参数取值必须与配置/日志一致；数据集版本与划分写清；基线与对照条件写清；给出复现所需命令与环境；材料缺失处标注待确认。

根据实验材料撰写论文第3节“方法与实验”（中文，面向期刊审稿人），需包含方法步骤、实验设置、数据集与划分、参数表、对照实验、可复现性与限制。不得补造材料中没有的数值。

## Experimental setup / 实验设置
| id | key (canonical) | value | source | kind | flags |
|---|---|---|---|---|---|
| F96 | version.cuda (cuda) | `12.1` | logs/train_bert_seed42.log:2 | log |  |
| F97 | version.cudnn (cudnn) | `8902` | logs/train_bert_seed42.log:2 | log |  |
| F98 | gpu (hardware) | `NVIDIA A100-SXM4-80GB` | logs/train_bert_seed42.log:3 | log |  |
| F99 | num_gpus (num_gpus) | `1` | logs/train_bert_seed42.log:3 | log |  |
| F46 | train.fp16 (precision) | `true` | configs/train.yaml:21 | config |  |
| F20 | version.transformers (software) | `4.36.2` | requirements.txt:2 | env |  |
| F21 | version.scikit-learn (software) | `1.3.2` | requirements.txt:3 | env |  |
| F22 | version.numpy (software) | `>=1.24` | requirements.txt:4 | env |  |
| F23 | version.jieba (software) | `0.42.1` | requirements.txt:5 | env |  |
| F95 | version.torch (torch) | `2.1.2+cu121` | logs/train_bert_seed42.log:2 | log |  |
| F19 | version.torch (torch) | `2.1.2` | requirements.txt:1 | env |  |

## Parameters / 参数
| id | key (canonical) | value | source | kind | flags |
|---|---|---|---|---|---|
| F67 | batch_size (batch_size) | `32` | logs/train_bert_seed42.log:5 | log |  |
| F41 | train.batch_size (batch_size) | `32` | configs/train.yaml:16 | config |  |
| F32 | model.dropout (dropout) | `0.1` | configs/train.yaml:5 | config |  |
| F68 | epochs (epochs) | `5` | logs/train_bert_seed42.log:5 | log |  |
| F100 | epoch_total (epochs) | `5` | logs/train_bert_seed42.log:6 | log |  |
| F93 | epochs (epochs) | `5` | logs/train_bert_seed42.log:1 | cli |  |
| F42 | train.epochs (epochs) | `5` | configs/train.yaml:17 | config |  |
| F112 | epochs (epochs) | `3` | src/train.py:10 | code | argparse default |
| F49 | eval.batch_size (eval_batch_size) | `64` | configs/train.yaml:25 | config | scope test |
| F45 | train.max_grad_norm (grad_clip) | `1.0` | configs/train.yaml:20 | config |  |
| F66 | lr (learning_rate) | `2e-05` | logs/train_bert_seed42.log:5 | log | CONFLICT C1 |
| F92 | lr (learning_rate) | `2e-5` | logs/train_bert_seed42.log:1 | cli | CONFLICT C1 |
| F39 | train.lr (learning_rate) | `3.0e-5` | configs/train.yaml:14 | config | CONFLICT C1 |
| F111 | lr (learning_rate) | `2e-5` | src/train.py:9 | code | argparse default |
| F13 | text.学习率 (learning_rate) | `2e-5` | notes.md:2 | doc_kv | CONFLICT C1 |
| F70 | max_length (max_length) | `256` | logs/train_bert_seed42.log:5 | log |  |
| F31 | model.max_length (max_length) | `256` | configs/train.yaml:4 | config |  |
| F103 | max_iter (max_steps) | `1000` | src/baseline.py:6 | code | scope baseline; keyword argument |
| F28 | baseline.solver (optimizer) | `liblinear` | configs/baseline_tfidf.yaml:6 | config | scope baseline |
| F38 | train.optimizer (optimizer) | `AdamW` | configs/train.yaml:13 | config |  |
| F102 | solver (optimizer) | `liblinear` | src/baseline.py:6 | code | scope baseline; keyword argument |
| F119 | optimizer (optimizer) | `AdamW` | src/train.py:17 | code |  |
| F44 | train.scheduler (scheduler) | `linear` | configs/train.yaml:19 | config |  |
| F115 | scheduler (scheduler) | `get_linear_schedule_with_warmup` | src/train.py:4 | code |  |
| F71 | warmup_ratio (warmup) | `0.1` | logs/train_bert_seed42.log:5 | log |  |
| F43 | train.warmup_ratio (warmup) | `0.1` | configs/train.yaml:18 | config |  |
| F40 | train.weight_decay (weight_decay) | `0.01` | configs/train.yaml:15 | config |  |
| F118 | weight_decay (weight_decay) | `0.01` | src/train.py:17 | code | keyword argument |

## Datasets and splits / 数据集与划分
| id | key (canonical) | value | source | kind | flags |
|---|---|---|---|---|---|
| F34 | data.train_file (data_path) | `data/train.jsonl` | configs/train.yaml:8 | config |  |
| F33 | data.dataset (dataset) | `THUCNews-subset` | configs/train.yaml:7 | config |  |
| F11 | snapshot (dataset_version) | `downloaded 2024-02-28` | data_card.md:5 | doc_kv |  |
| F4 | License (license) | `research use only` | data_card.md:4 | doc_kv |  |
| F64 | n_test (n_test) | `7200` | logs/preprocess.log:5 | log |  |
| F62 | n_train (n_train) | `57600` | logs/preprocess.log:5 | log |  |
| F63 | n_val (n_val) | `7200` | logs/preprocess.log:5 | log |  |
| F37 | data.num_classes (num_classes) | `10` | configs/train.yaml:11 | config |  |
| F117 | num_labels (num_classes) | `10` | src/train.py:16 | code | keyword argument |
| F3 | Source (source_url) | `http://thuctc.thunlp.org/` | data_card.md:3 | doc_kv |  |
| F9 | Split (split_ratio) | `8:1:1, stratified by label for the train/rest split` | data_card.md:7 | doc_kv |  |
| F12 | split_ratio (split_ratio) | `8:1:1` | data_card.md:7 | doc_kv |  |
| F107 | random_state (split_seed) | `2023` | src/preprocess.py:10 | code | keyword argument |
| F109 | random_state (split_seed) | `2023` | src/preprocess.py:11 | code | keyword argument |
| F36 | data.test_file (test_file) | `data/test.jsonl` | configs/train.yaml:10 | config | scope test |
| F106 | test_size (test_size) | `0.2` | src/preprocess.py:10 | code | scope test; keyword argument |
| F108 | test_size (test_size) | `0.5` | src/preprocess.py:11 | code | scope test; keyword argument |
| F35 | data.val_file (val_file) | `data/val.jsonl` | configs/train.yaml:9 | config | scope val |

## Baselines / controls and evaluation / 对照与评价
| id | key (canonical) | value | source | kind | flags |
|---|---|---|---|---|---|
| F48 | eval.metric (metric) | `macro_f1` | configs/train.yaml:24 | config | scope test |
| F101 | metric (metric) | `f1_score` | src/baseline.py:3 | code | scope baseline |
| F30 | model.name (model) | `bert-base-chinese` | configs/train.yaml:3 | config |  |
| F116 | model (model) | `bert-base-chinese` | src/train.py:15 | code |  |

## Reproducibility and limitations / 可复现性与限制
| id | key (canonical) | value | source | kind | flags |
|---|---|---|---|---|---|
| F76 | checkpoint (checkpoint) | `epoch 4` | logs/train_bert_seed42.log:11 | log | scope val |
| F65 | commit (code_version) | `9f3c2ab` | logs/train_bert_seed42.log:4 | log |  |
| F53 | command (command) | `python src/baseline.py --config configs/baseline_tfidf.yaml` | logs/baseline.log:1 | cli | scope baseline |
| F59 | command (command) | `python src/preprocess.py --raw data/raw/thucnews_2016.zip --out data/` | logs/preprocess.log:1 | cli |  |
| F90 | command (command) | `python src/train.py --config configs/train.yaml --lr 2e-5 --epochs 5 --seed 42` | logs/train_bert_seed42.log:1 | cli |  |
| F114 | output_dir (output_dir) | `runs/bert` | src/train.py:12 | code | argparse default |
| F69 | seed (seed) | `42` | logs/train_bert_seed42.log:5 | log |  |
| F94 | seed (seed) | `42` | logs/train_bert_seed42.log:1 | cli |  |
| F29 | seed (seed) | `42` | configs/baseline_tfidf.yaml:7 | config | scope baseline |
| F47 | seed (seed) | `42` | configs/train.yaml:22 | config |  |
| F113 | seed (seed) | `42` | src/train.py:11 | code | argparse default |
| F15 | text.seed (seed) | `42` | notes.md:3 | doc_kv |  |

## Other structured values (not mapped to a known key)
| id | key | value | source | kind |
|---|---|---|---|---|
| F24 | baseline.name | `tfidf_logreg` | configs/baseline_tfidf.yaml:2 | config |
| F25 | baseline.ngram_range | `[1, 2]` | configs/baseline_tfidf.yaml:3 | config |
| F26 | baseline.max_features | `50000` | configs/baseline_tfidf.yaml:4 | config |
| F27 | baseline.C | `1.0` | configs/baseline_tfidf.yaml:5 | config |
| F54 | config | `configs/baseline_tfidf.yaml` | logs/baseline.log:1 | cli |
| F60 | raw | `data/raw/thucnews_2016.zip` | logs/preprocess.log:1 | cli |
| F61 | out | `data/` | logs/preprocess.log:1 | cli |
| F91 | config | `configs/train.yaml` | logs/train_bert_seed42.log:1 | cli |

## Logged series (values that change during a run; not conflicts)
- `logs/baseline.log` accuracy: 1 values, first 0.882 (l.2), last 0.882 (l.2), range 0.882–0.882
- `logs/train_bert_seed42.log` train_loss: 5 values, first 0.412 (l.6), last 0.081 (l.10), range 0.081–0.412
- `logs/train_bert_seed42.log` val_macro_f1: 6 values, first 0.912 (l.6), last 0.940 (l.11), range 0.912–0.94
- `logs/train_bert_seed42.log` accuracy: 1 values, first 0.941 (l.12), last 0.941 (l.12), range 0.941–0.941

## Lines with numbers in notes / data cards / drafts (cite them like any fact)
- F2 `data_card.md:2` - Name: THUCNews (subset of 10 categories)
- F6 `data_card.md:5` - Raw dump: thucnews_2016.zip (downloaded 2024-02-28)
- F8 `data_card.md:6` - Categories: 10
- F10 `data_card.md:7` - Split: 8:1:1, stratified by label for the train/rest split
- F14 `notes.md:2` - BERT 微调学习率最终用 2e-5，比配置里的 3e-5 稳定。
- F16 `notes.md:3` - 只跑了 seed 42 一次，时间不够。
- F17 `notes.md:4` - TF-IDF 基线没有调参，直接用默认 C=1.0。
- F18 `notes.md:5` - 测试集只评一次，按验证集 macro-F1 选 epoch 4 的检查点。
- F52 `logs/baseline.log:2` test macro_f1=0.874 accuracy=0.882
- F55 `logs/preprocess.log:2` loaded 74000 raw documents
- F56 `logs/preprocess.log:3` removed 1210 documents outside length range [20, 2000]
- F57 `logs/preprocess.log:4` removed 790 exact duplicates
- F58 `logs/preprocess.log:5` 57600 train samples, 7200 val samples, 7200 test samples
- F79 `logs/train_bert_seed42.log:2` torch 2.1.2+cu121 | CUDA 12.1 | cuDNN 8902
- F80 `logs/train_bert_seed42.log:3` device: NVIDIA A100-SXM4-80GB x 1
- F81 `logs/train_bert_seed42.log:4` git commit: 9f3c2ab
- F82 `logs/train_bert_seed42.log:5` Namespace(lr=2e-05, batch_size=32, epochs=5, seed=42, max_length=256, warmup_ratio=0.1)
- F83 `logs/train_bert_seed42.log:6` Epoch 1/5 train_loss=0.412 val_macro_f1=0.912
- F84 `logs/train_bert_seed42.log:7` Epoch 2/5 train_loss=0.221 val_macro_f1=0.931
- F85 `logs/train_bert_seed42.log:8` Epoch 3/5 train_loss=0.150 val_macro_f1=0.938
- F86 `logs/train_bert_seed42.log:9` Epoch 4/5 train_loss=0.102 val_macro_f1=0.940
- F87 `logs/train_bert_seed42.log:10` Epoch 5/5 train_loss=0.081 val_macro_f1=0.939
- F88 `logs/train_bert_seed42.log:11` best checkpoint: epoch 4 (val_macro_f1=0.940)
- F89 `logs/train_bert_seed42.log:12` test macro_f1=0.936 accuracy=0.941

## Pipeline stages / commands found (method steps should cover each)
- `logs/baseline.log:1` `python src/baseline.py --config configs/baseline_tfidf.yaml`
- `logs/preprocess.log:1` `python src/preprocess.py --raw data/raw/thucnews_2016.zip --out data/`
- `logs/train_bert_seed42.log:1` `python src/train.py --config configs/train.yaml --lr 2e-5 --epochs 5 --seed 42`

## Conflicts (must be marked [[CONFIRM: ...]] or resolved in agent.json)
- **C1** 学习率: `2e-05` (F66, F92, F13; logs/train_bert_seed42.log:5, logs/train_bert_seed42.log:1, notes.md:2; cli/doc_kv/log); `3.0e-5` (F39; configs/train.yaml:14; config) — precedence guess F66

## Gaps / author questions (write [[GAP: ...]] in the draft where the information belongs)
- **G1** [control, required, missing] 重复次数/平行样数及结果汇总方式: 每个条件独立运行/平行样多少次？报告的是均值±标准差/标准误还是单次结果？
- **G2** [control, recommended, missing] 统计检验/不确定度估计: 比较结论基于何种统计检验或不确定度估计（检验方法、显著性水平、多重校正）？
- **G3** [repro, required, author_input] 落到具体失效场景的限制条件: 哪些条件未测试（数据、规模、硬件、设置）？方法在哪些具体场景下可能失效？
- **G4** [control, required, ambiguous] 是否仅单个种子？: 材料中只出现一个随机种子取值：报告结果是否来自单次运行？若有多次运行，请列出各次种子。
- **G5** [setup, recommended, ambiguous] 未锁定的版本: 部分依赖只写了版本范围（>=、~=）：请给出报告运行时实际安装的精确版本（pip freeze）。
