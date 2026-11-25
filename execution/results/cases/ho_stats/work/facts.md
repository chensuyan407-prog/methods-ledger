# Facts for case `ho_stats_sleep` (methods-ledger 0.2.0)
profile: **stats** · target language: **zh** · 31 facts from 5 files · 1 conflicts · 8 gaps/questions
Cite a fact in the draft as `[[F12]]` right after the sentence part it supports (several: `[[F12,F30]]`).

## Files
- `analysis.R` — code, 10 lines, 8 facts
- `case.json` — case, 4 lines, 0 facts
- `cleaning_log.txt` — log, 6 lines, 8 facts
- `notes.txt` — doc, 4 lines, 5 facts
- `问卷说明.md` — doc, 9 lines, 10 facts

## Task (excerpt)
撰写“2 研究方法”一节（中文，面向公共卫生期刊），基于问卷说明、数据清洗日志和 R 分析脚本。需写清研究对象与纳排标准、样本量、变量、统计方法、软件版本与复现，以及局限。

## Experimental setup / 实验设置
| id | key (canonical) | value | source | kind | flags |
|---|---|---|---|---|---|
| F4 | version.r (software_stats) | `4.3.2` | analysis.R:1 | code |  |
| F5 | version.mice (software_stats) | `3.16.0` | analysis.R:2 | code |  |
| F6 | version.lme4 (software_stats) | `1.1-35` | analysis.R:3 | code |  |

## Datasets and splits / 数据集与划分
| id | key (canonical) | value | source | kind | flags |
|---|---|---|---|---|---|
| F22 | 调查时间 (dataset_version) | `2023-10-09 至 2023-10-27` | 问卷说明.md:2 | doc_kv |  |
| F27 | 纳入标准 (inclusion) | `在校本科生、知情同意` | 问卷说明.md:6 | doc_kv |  |
| F28 | 排除标准 (inclusion) | `问卷作答时间 < 120 秒或缺失项 > 20%` | 问卷说明.md:7 | doc_kv |  |
| F31 | lot (lot) | `XJ-2023-118` | 问卷说明.md:8 | doc_kv |  |
| F16 | m (n_imputations) | `20` | cleaning_log.txt:5 | log | CONFLICT C1 |
| F8 | m (n_imputations) | `20` | analysis.R:5 | code | CONFLICT C1 |
| F21 | m (n_imputations) | `10` | notes.txt:2 | doc_kv | CONFLICT C1 |
| F9 | responses (n_samples) | `2846` | cleaning_log.txt:1 | log |  |
| F10 | sample (n_samples) | `2638` | cleaning_log.txt:4 | log |  |
| F17 | text.样本量 (n_samples) | `2500` | notes.txt:1 | doc_kv |  |
| F24 | 对象 (sample_source) | `某综合性大学本科一至四年级学生` | 问卷说明.md:3 | doc_kv |  |

## Baselines / controls and evaluation / 对照与评价
| id | key (canonical) | value | source | kind | flags |
|---|---|---|---|---|---|
| F3 | alpha (alpha_level) | `0.05` | analysis.R:8 | code | assignment |
| F2 | statistical_test (statistical_test) | `glmer` | analysis.R:6 | code |  |

## Reproducibility and limitations / 可复现性与限制
| id | key (canonical) | value | source | kind | flags |
|---|---|---|---|---|---|
| F1 | seed (seed) | `2023` | analysis.R:5 | code | keyword argument |
| F7 | set.seed (seed) | `2023` | analysis.R:4 | code |  |

## Lines with numbers in notes / data cards / drafts (cite them like any fact)
- F11 `cleaning_log.txt:1` 2023-11-02 raw responses: 2846
- F12 `cleaning_log.txt:2` 2023-11-02 excluded completion time < 120 s: 131
- F13 `cleaning_log.txt:3` 2023-11-02 excluded missing > 20%: 77
- F14 `cleaning_log.txt:4` 2023-11-02 analytic sample: 2638
- F15 `cleaning_log.txt:5` 2023-11-03 missing covariates imputed with mice (m = 20)
- F18 `notes.txt:1` 样本量按 2500 份有效问卷设计（预期患病率 30%，容许误差 2%）。
- F19 `notes.txt:2` 多重插补 m=10 就够了，脚本里写的是 20。
- F20 `notes.txt:3` GPA 后 25% 定义为学业表现差。
- F23 `问卷说明.md:2` - 调查时间：2023-10-09 至 2023-10-27
- F26 `问卷说明.md:5` - 量表：匹兹堡睡眠质量指数（PSQI），PSQI > 7 判为睡眠质量差
- F29 `问卷说明.md:7` - 排除标准：问卷作答时间 < 120 秒或缺失项 > 20%

## Conflicts (must be marked [[CONFIRM: ...]] or resolved in agent.json)
- **C1** 插补次数: `20` (F16, F8; cleaning_log.txt:5, analysis.R:5; code/log); `10` (F21; notes.txt:2; doc_kv) — precedence guess F16

## Gaps / author questions (write [[GAP: ...]] in the draft where the information belongs)
- **G1** [steps, required, missing] 有序步骤（每步输入→操作→输出）: 请确认各处理阶段的先后顺序及每一步的产出。
- **G2** [data, required, missing] 划分规模/比例与划分方式: 请给出训练/验证/测试集规模（或比例）、划分方式（随机/分层/官方）及划分种子。
- **G3** [control, required, missing] 对照组（阳性/阴性/溶剂对照）: 每个条件同时设置了哪些对照组？
- **G4** [control, required, only_mentioned_in_text] 评价指标/测量结局: 请定义各评价指标（在哪个数据子集、哪个检查点上计算）。
- **G5** [repro, required, only_mentioned_in_text] 代码版本与运行命令: 请给出代码提交号/标签及复现报告数值的确切命令。
- **G6** [repro, recommended, missing] 数据获取方式: 读者如何获取数据（URL/DOI、许可、访问限制）？
- **G7** [repro, required, author_input] 落到具体失效场景的限制条件: 哪些条件未测试（数据、规模、硬件、设置）？方法在哪些具体场景下可能失效？
- **G8** [control, required, ambiguous] 是否仅单个种子？: 材料中只出现一个随机种子取值：报告结果是否来自单次运行？若有多次运行，请列出各次种子。
