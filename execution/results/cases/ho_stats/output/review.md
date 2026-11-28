# Review — ho_stats_sleep

status: **success** — all checks pass; 15 items await author confirmation

facts extracted 31, cited 26; conflicts 1; questions 15; preview: pymupdf story, 2 pages

## Coverage
- E_steps (steps, required): **covered** — 有序步骤（每步输入→操作→输出）
- E_dataset (data, required): **covered** — 数据集名称与来源
- E_dataset_version (data, required): **covered** — 数据集版本/发布号/快照日期
- E_split (data, required): **marked_gap** — 划分规模/比例与划分方式
- E_preproc (data, recommended): **covered** — 预处理/筛选
- E_software (setup, required): **covered** — 软件及版本
- E_seed (repro, required): **covered** — 随机种子
- E_controls (control, required): **marked_gap** — 对照组（阳性/阴性/溶剂对照）
- E_metric (control, required): **covered** — 评价指标/测量结局
- E_stats (control, recommended): **covered** — 统计检验/不确定度估计
- E_code (repro, required): **covered** — 代码版本与运行命令
- E_data_access (repro, recommended): **marked_gap** — 数据获取方式
- E_limits (repro, required): **covered** — 落到具体失效场景的限制条件

## 审核说明（自动映射）

- numbers/versions in the text: 34; matched by tag 32, auto-mapped 0, CALC/SRC 0, unsourced 0

| line | token | fact | source | how |
|---|---|---|---|---|
| 5 | `2023` | F22 |  | tag |
| 5 | `10` | F22 |  | tag |
| 5 | `09` | F22 |  | tag |
| 5 | `2023` | F22 |  | tag |
| 5 | `10` | F22 |  | tag |
| 5 | `27` | F22 |  | tag |
| 5 | `120` | F28 |  | tag |
| 5 | `20%` | F28 |  | tag |
| 9 | `2846` | F9 |  | tag |
| 10 | `120` | F12 |  | tag |
| 10 | `131` | F12 |  | tag |
| 11 | `20%` | F13 |  | tag |
| 11 | `77` | F13 |  | tag |
| 12 | `2638` | F10 |  | tag |
| 13 | `20` | F15 |  | tag |
| 15 | `2500` | F17 |  | tag |
| 15 | `30%` | F18 |  | tag |
| 15 | `2%` | F18 |  | tag |
| 19 | `7` | F25 |  | tag |
| 19 | `25%` | F20 |  | tag |
| 23 | `0.05` | F3 |  | tag |
| 23 | `2023` | F7 |  | tag |
| 27 | `1.1` | F6 |  | tag |
| 27 | `35` | F6 |  | tag |
| 27 | `4.3.2` | F4 |  | version-tag |
| 27 | `3.16.0` | F5 |  | version-tag |
| 31 | `2023` | F22 |  | tag |
| 31 | `10` | F22 |  | tag |
| 31 | `09` | F22 |  | tag |
| 31 | `2023` | F22 |  | tag |
| 31 | `10` | F22 |  | tag |
| 31 | `27` | F22 |  | tag |
| 31 | `120` | F12 |  | tag |
| 31 | `131` | F12 |  | tag |

## Check items
- WARN T05 l.5: cited F27 (纳入标准 = 在校本科生、知情同意) but its value is not in the sentence
