# Review — dev_ml_textcls

status: **success** — all checks pass; 11 items await author confirmation

facts extracted 119, cited 56; conflicts 1; questions 11; preview: pymupdf story, 4 pages

## Coverage
- E_steps (steps, required): **covered** — 有序步骤（每步输入→操作→输出）
- E_dataset (data, required): **covered** — 数据集名称与来源
- E_dataset_version (data, required): **covered** — 数据集版本/发布号/快照日期
- E_split (data, required): **covered** — 划分规模/比例与划分方式
- E_preproc (data, recommended): **covered** — 预处理/筛选
- E_model (control, recommended): **covered** — 模型/结构及初始化
- E_hparams (params, required): **covered** — 优化器、学习率、批大小、训练长度
- E_hardware (setup, required): **covered** — 硬件（设备型号与数量）
- E_software (setup, required): **covered** — 软件及版本
- E_seed (repro, required): **covered** — 随机种子
- E_repeats (control, required): **covered** — 重复次数/平行样数及结果汇总方式
- E_baseline (control, required): **covered** — 基线（含版本）及同预算对照条件
- E_metric (control, required): **covered** — 评价指标/测量结局
- E_stats (control, recommended): **covered** — 统计检验/不确定度估计
- E_code (repro, required): **covered** — 代码版本与运行命令
- E_data_access (repro, recommended): **covered** — 数据获取方式
- E_limits (repro, required): **covered** — 落到具体失效场景的限制条件

## 审核说明（自动映射）

- numbers/versions in the text: 44; matched by tag 40, auto-mapped 0, CALC/SRC 1, unsourced 0

| line | token | fact | source | how |
|---|---|---|---|---|
| 5 | `74000` | F55 |  | tag |
| 5 | `1210` | F56 |  | tag |
| 5 | `790` | F57 |  | tag |
| 5 | `72000` | CALC |  | calc |
| 6 | `0.2` | F106 |  | tag |
| 6 | `0.5` | F108 |  | tag |
| 6 | `2023` | F107 |  | tag |
| 6 | `57600` | F62 |  | tag |
| 6 | `7200` | F63 |  | tag |
| 6 | `7200` | F63 |  | tag |
| 6 | `8` | F9 |  | tag |
| 6 | `1` | F9 |  | tag |
| 6 | `1` | F9 |  | tag |
| 7 | `5` | F68 |  | tag |
| 13 | `1` | F99 |  | tag |
| 13 | `12.1` | F96 |  | tag |
| 13 | `2.1.2+cu121` | F95 |  | version-tag |
| 13 | `4.36.2` | F20 |  | version-tag |
| 13 | `1.3.2` | F21 |  | version-tag |
| 13 | `1.24` | F22 |  | tag |
| 17 | `10` | F1 |  | tag |
| 17 | `2024` | F11 |  | tag |
| 17 | `02` | F11 |  | tag |
| 17 | `28` | F11 |  | tag |
| 21 | `2e-5` | F66 |  | tag |
| 21 | `0.01` | F40 |  | tag |
| 21 | `32` | F67 |  | tag |
| 21 | `256` | F70 |  | tag |
| 21 | `0.1` | F32 |  | tag |
| 21 | `0.1` | F71 |  | tag |
| 21 | `1.0` | F45 |  | tag |
| 21 | `1` | F25 |  | tag |
| 21 | `2` | F25 |  | tag |
| 21 | `50000` | F26 |  | tag |
| 21 | `1.0` | F27 |  | tag |
| 27 | `42` | F16 |  | tag |
| 31 | `9` | F65 |  | tag |
| 39 | `42` | F69 |  | tag |
| 39 | `2023` | F107 |  | tag |
| 43 | `42` | F16 |  | tag |
| 43 | `10` | F37 |  | tag |
| 43 | `20` | F104 |  | tag |
| 43 | `2000` | F105 |  | tag |
| 43 | `256` | F70 |  | tag |

## Check items
- WARN T05 l.9: cited F24 (baseline.name = tfidf_logreg) but its value is not in the sentence
- WARN T05 l.21: cited F44 (train.scheduler = linear) but its value is not in the sentence
- WARN T05 l.43: cited F98 (gpu = NVIDIA A100-SXM4-80GB) but its value is not in the sentence
- WARN K03 l.None: facts in the materials never used in the chapter: dataset (F33); validation file (F35); test file (F36); cuDNN version (F97); max iterations (solver) (F103)
