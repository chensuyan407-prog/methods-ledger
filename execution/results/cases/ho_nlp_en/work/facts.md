# Facts for case `ho_nlp_sst2` (methods-ledger 0.2.0)
profile: **ml** · target language: **en** · 83 facts from 8 files · 2 conflicts · 6 gaps/questions
Cite a fact in the draft as `[[F12]]` right after the sentence part it supports (several: `[[F12,F30]]`).

## Files
- `README.md` — doc, 4 lines, 6 facts
- `case.json` — case, 4 lines, 0 facts
- `launch.sh` — code, 6 lines, 11 facts
- `results.csv` — table, 8 lines, 13 facts
- `run_glue.py` — code, 12 lines, 4 facts
- `train_lora_s1.log` — log, 7 lines, 25 facts
- `conf/full_ft.yaml` — config, 11 lines, 6 facts
- `conf/lora.yaml` — config, 24 lines, 18 facts

## Task (excerpt)
Draft Section 4 'Experimental Setup' (English, NeurIPS style) for our LoRA fine-tuning study from the configs, launch script, logs and results. Report datasets and splits, hyperparameters, baselines, compute, seeds/repetitions and reproducibility. Flag anything missing.

## Experimental setup / 实验设置
| id | key (canonical) | value | source | kind | flags |
|---|---|---|---|---|---|
| F56 | version.cuda (cuda) | `12.1` | train_lora_s1.log:1 | log |  |
| F57 | gpu (hardware) | `NVIDIA A100-SXM4-40GB` | train_lora_s1.log:2 | log |  |
| F36 | world_size (num_gpus) | `4` | train_lora_s1.log:2 | log |  |
| F9 | nproc_per_node (num_gpus) | `4` | launch.sh:3 | cli |  |
| F14 | nproc_per_node (num_gpus) | `4` | launch.sh:4 | cli |  |
| F7 | num_gpus (num_gpus) | `4` | launch.sh:3 | code |  |
| F81 | training.bf16 (precision) | `true` | conf/lora.yaml:20 | config |  |
| F52 | version.python (python) | `3.10.13` | train_lora_s1.log:1 | log |  |
| F54 | version.transformers (software) | `4.40.0` | train_lora_s1.log:1 | log |  |
| F55 | version.peft (software) | `0.10.0` | train_lora_s1.log:1 | log |  |
| F53 | version.torch (torch) | `2.2.1` | train_lora_s1.log:1 | log |  |

## Parameters / 参数
| id | key (canonical) | value | source | kind | flags |
|---|---|---|---|---|---|
| F41 | per_device_train_batch_size (batch_size) | `32` | train_lora_s1.log:5 | log | CONFLICT C1 |
| F63 | training.per_device_train_batch_size (batch_size) | `16` | conf/full_ft.yaml:8 | config | CONFLICT C1 |
| F77 | training.per_device_train_batch_size (batch_size) | `16` | conf/lora.yaml:16 | config | CONFLICT C1 |
| F70 | lora.dropout (dropout) | `0.05` | conf/lora.yaml:7 | config |  |
| F44 | num_train_epochs (epochs) | `20` | train_lora_s1.log:5 | log |  |
| F64 | training.num_train_epochs (epochs) | `10` | conf/full_ft.yaml:9 | config |  |
| F79 | training.num_train_epochs (epochs) | `20` | conf/lora.yaml:18 | config |  |
| F42 | gradient_accumulation_steps (grad_accum) | `1` | train_lora_s1.log:5 | log | CONFLICT C2 |
| F78 | training.gradient_accumulation_steps (grad_accum) | `2` | conf/lora.yaml:17 | config | CONFLICT C2 |
| F43 | learning_rate (learning_rate) | `4e-4` | train_lora_s1.log:5 | log |  |
| F61 | optim.learning_rate (learning_rate) | `1.0e-5` | conf/full_ft.yaml:5 | config |  |
| F73 | optim.learning_rate (learning_rate) | `4.0e-4` | conf/lora.yaml:11 | config |  |
| F69 | lora.alpha (lora_alpha) | `16` | conf/lora.yaml:6 | config |  |
| F68 | lora.r (lora_r) | `8` | conf/lora.yaml:5 | config |  |
| F65 | training.max_seq_length (max_length) | `128` | conf/full_ft.yaml:10 | config |  |
| F80 | training.max_seq_length (max_length) | `128` | conf/lora.yaml:19 | config |  |
| F72 | optim.optimizer (optimizer) | `adamw_torch` | conf/lora.yaml:10 | config |  |
| F75 | optim.lr_scheduler_type (scheduler) | `linear` | conf/lora.yaml:13 | config |  |
| F76 | optim.warmup_ratio (warmup) | `0.06` | conf/lora.yaml:14 | config |  |
| F62 | optim.weight_decay (weight_decay) | `0.1` | conf/full_ft.yaml:6 | config |  |
| F74 | optim.weight_decay (weight_decay) | `0.1` | conf/lora.yaml:12 | config |  |

## Datasets and splits / 数据集与划分
| id | key (canonical) | value | source | kind | flags |
|---|---|---|---|---|---|
| F82 | data.dataset (dataset) | `glue` | conf/lora.yaml:22 | config |  |
| F33 | dataset (dataset) | `glue` | run_glue.py:10 | code |  |
| F34 | dataset_config (dataset_version) | `sst2` | run_glue.py:10 | code |  |
| F58 | n_train (n_train) | `67349,` | train_lora_s1.log:3 | log |  |
| F59 | n_val (n_val) | `872` | train_lora_s1.log:3 | log |  |

## Baselines / controls and evaluation / 对照与评价
| id | key (canonical) | value | source | kind | flags |
|---|---|---|---|---|---|
| F60 | model.name_or_path (model) | `roberta-large` | conf/full_ft.yaml:3 | config |  |
| F66 | model.name_or_path (model) | `roberta-large` | conf/lora.yaml:2 | config |  |

## Reproducibility and limitations / 可复现性与限制
| id | key (canonical) | value | source | kind | flags |
|---|---|---|---|---|---|
| F67 | model.revision (code_version) | `main` | conf/lora.yaml:3 | config |  |
| F32 | revision (code_version) | `bcdcba79d07bc864c1c254ccfcedcce55bcc9a8c` | run_glue.py:10 | code | keyword argument |
| F6 | commit (code_version) | `4be1d0e` | README.md:2 | doc_kv |  |
| F8 | command (command) | `torchrun --nproc_per_node 4 run_glue.py --config conf/lora.yaml --seed $SEED --o` | launch.sh:3 | cli |  |
| F13 | command (command) | `torchrun --nproc_per_node 4 run_glue.py --config conf/full_ft.yaml --seed $SEED ` | launch.sh:4 | cli |  |
| F12 | output_dir (output_dir) | `out/lora_s$SEED` | launch.sh:3 | cli |  |
| F17 | output_dir (output_dir) | `out/full_s$SEED` | launch.sh:4 | cli |  |
| F11 | seed (seed) | `$SEED` | launch.sh:3 | cli |  |
| F16 | seed (seed) | `$SEED` | launch.sh:4 | cli |  |
| F31 | seed (seed) | `0` | run_glue.py:6 | code | argparse default |
| F19 | lora.seed (seed) | `1` | results.csv:2 | table |  |
| F21 | lora.seed (seed) | `2` | results.csv:3 | table |  |
| F23 | lora.seed (seed) | `3` | results.csv:4 | table |  |
| F25 | full_ft.seed (seed) | `1` | results.csv:5 | table |  |
| F27 | full_ft.seed (seed) | `2` | results.csv:6 | table |  |
| F29 | full_ft.seed (seed) | `3` | results.csv:7 | table |  |
| F2 | text.seeds (seed) | `1` | README.md:2 | doc_kv | scope val |

## Other structured values (not mapped to a known key)
| id | key | value | source | kind |
|---|---|---|---|---|
| F10 | config | `conf/lora.yaml` | launch.sh:3 | cli |
| F15 | config | `conf/full_ft.yaml` | launch.sh:4 | cli |
| F18 | n_rows | `6` | results.csv:1 | table |
| F20 | lora.eval_accuracy | `0.9622` | results.csv:2 | table |
| F22 | lora.eval_accuracy | `0.9576` | results.csv:3 | table |
| F24 | lora.eval_accuracy | `0.9599` | results.csv:4 | table |
| F26 | full_ft.eval_accuracy | `0.9633` | results.csv:5 | table |
| F28 | full_ft.eval_accuracy | `0.9587` | results.csv:6 | table |
| F30 | full_ft.eval_accuracy | `0.9610` | results.csv:7 | table |
| F71 | lora.target_modules | `[query, value]` | conf/lora.yaml:8 | config |
| F83 | data.subset | `sst2` | conf/lora.yaml:23 | config |

## Logged series (values that change during a run; not conflicts)
- `train_lora_s1.log` eval_accuracy: 1 values, first 0.9622 (l.6), last 0.9622 (l.6), range 0.9622–0.9622

## Lines with numbers in notes / data cards / drafts (cite them like any fact)
- F3 `README.md:2` Code commit: 4be1d0e. Results: mean over seeds 1-3 on the GLUE SST-2 validation set (872 sentences).
- F5 `README.md:3` Total compute: about 40 GPU-hours.
- F46 `train_lora_s1.log:1` env: python 3.10.13, torch 2.2.1, transformers 4.40.0, peft 0.10.0, CUDA 12.1
- F47 `train_lora_s1.log:2` world_size=4, GPU: NVIDIA A100-SXM4-40GB
- F48 `train_lora_s1.log:3` train examples: 67349, validation examples: 872
- F49 `train_lora_s1.log:4` trainable params: 1,838,082 || all params: 357,199,876 || trainable%: 0.5146
- F50 `train_lora_s1.log:5` per_device_train_batch_size=32 gradient_accumulation_steps=1 learning_rate=4e-4 num_train_epochs=20
- F51 `train_lora_s1.log:6` best eval_accuracy=0.9622 at epoch 14

## Pipeline stages / commands found (method steps should cover each)
- `launch.sh:3` `torchrun --nproc_per_node 4 run_glue.py --config conf/lora.yaml --seed $SEED --output_dir out/lora_s$SEED`
- `launch.sh:4` `torchrun --nproc_per_node 4 run_glue.py --config conf/full_ft.yaml --seed $SEED --output_dir out/full_s$SEED`

## Conflicts (must be marked [[CONFIRM: ...]] or resolved in agent.json)
- **C1** batch size: `32` (F41; train_lora_s1.log:5; log); `16` (F63, F77; conf/full_ft.yaml:8, conf/lora.yaml:16; config) — precedence guess F41
- **C2** gradient accumulation steps: `1` (F42; train_lora_s1.log:5; log); `2` (F78; conf/lora.yaml:17; config) — precedence guess F42

## Gaps / author questions (write [[GAP: ...]] in the draft where the information belongs)
- **G1** [control, required, missing] number of repetitions / replicates and how results are aggregated: How many independent runs/replicates per condition, and is mean ± SD/SE or a single run reported?
- **G2** [control, required, only_mentioned_in_text] baselines with versions and same-budget conditions: Which baselines (implementation + version) were compared, and were they trained/tuned under the same budget and data?
- **G3** [control, required, only_mentioned_in_text] evaluation metrics / measured outcomes: Define each metric (and on which split / at which checkpoint it is computed).
- **G4** [control, recommended, only_mentioned_in_text] statistical test / uncertainty estimate: Which statistical test or uncertainty estimate supports comparisons (test, alpha, correction)?
- **G5** [repro, recommended, missing] data availability / access: How can readers obtain the data (URL/DOI, license, access restrictions)?
- **G6** [repro, required, author_input] limitations tied to concrete failure scenarios: Which conditions were not tested (data, scale, hardware, settings) and where is the method expected to fail?
