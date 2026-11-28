# Review — dev_sim_water

status: **success** — all checks pass; 10 items await author confirmation

facts extracted 44, cited 29; conflicts 1; questions 10; preview: pymupdf story, 2 pages

## Coverage
- E_steps (steps, required): **covered** — 有序步骤（每步输入→操作→输出）
- E_system (data, required): **covered** — 模拟体系与模型（规模、力场/泛函）
- E_conditions (params, required): **covered** — 操作条件（含单位）
- E_hardware (setup, required): **covered** — 硬件（设备型号与数量）
- E_software (setup, required): **covered** — 软件及版本
- E_seed (repro, required): **covered** — 随机种子
- E_repeats (control, required): **covered** — 重复次数/平行样数及结果汇总方式
- E_metric (control, required): **covered** — 评价指标/测量结局
- E_stats (control, recommended): **covered** — 统计检验/不确定度估计
- E_code (repro, required): **covered** — 代码版本与运行命令
- E_data_access (repro, recommended): **marked_gap** — 数据获取方式
- E_limits (repro, required): **covered** — 落到具体失效场景的限制条件

## 审核说明（自动映射）

- numbers/versions in the text: 28; matched by tag 24, auto-mapped 0, CALC/SRC 4, unsourced 0

| line | token | fact | source | how |
|---|---|---|---|---|
| 5 | `4096` | F26 |  | tag |
| 5 | `12288` | F25 |  | tag |
| 6 | `298.0` | F6 |  | tag |
| 9 | `500` | SRC |  | source-line |
| 13 | `12.0` | F4 |  | tag |
| 13 | `1.0e-5` | SRC |  | source-line |
| 13 | `0.0001` | SRC |  | source-line |
| 13 | `2.0` | F8 |  | tag |
| 13 | `1` | CALC |  | calc |
| 13 | `1` | F39 |  | tag |
| 13 | `298.0` | F10 |  | tag |
| 13 | `100.0` | F10 |  | tag |
| 13 | `1.0` | F11 |  | tag |
| 13 | `1000.0` | F11 |  | tag |
| 19 | `2` | F23 |  | tag |
| 19 | `2023` | F23 |  | tag |
| 19 | `1` | F23 |  | tag |
| 19 | `1` | F15 |  | tag |
| 19 | `32` | F16 |  | tag |
| 19 | `6248` | F27 |  | tag |
| 19 | `11` | F31 |  | tag |
| 19 | `27` | F31 |  | tag |
| 19 | `15` | F31 |  | tag |
| 23 | `4928459` | F7 |  | tag |
| 31 | `298.0` | F10 |  | tag |
| 31 | `1.0` | F11 |  | tag |
| 31 | `2.0` | F8 |  | tag |
| 31 | `1` | F40 |  | tag |

## Check items
