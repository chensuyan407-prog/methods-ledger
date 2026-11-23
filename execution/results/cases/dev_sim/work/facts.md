# Facts for case `dev_sim_water` (methods-ledger 0.1.0)
profile: **simulation** · target language: **zh** · 44 facts from 5 files · 1 conflicts · 4 gaps/questions
Cite a fact in the draft as `[[F12]]` right after the sentence part it supports (several: `[[F12,F30]]`).

## Files
- `case.json` — case, 4 lines, 0 facts
- `in.npt` — config, 13 lines, 13 facts
- `job.slurm` — code, 9 lines, 9 facts
- `log.lammps` — log, 12 lines, 14 facts
- `notes_gbk.txt` — doc, 6 lines, 8 facts

## Task (excerpt)
根据模拟输入文件、作业脚本、日志和笔记，撰写论文“2 计算方法”一节（中文）。需写清体系、力场、系综与控温控压、步长与模拟时长、平衡与采样、软硬件、重复与统计、复现方式和局限。

## Experimental setup / 实验设置
| id | key (canonical) | value | source | kind | flags |
|---|---|---|---|---|---|
| F35 | cpu (hardware) | `Intel(R) Xeon(R) Gold 6248R` | log.lammps:6 | log |  |
| F15 | nodes (num_nodes) | `1` | job.slurm:3 | cli |  |
| F16 | ntasks (num_workers) | `32` | job.slurm:4 | cli |  |
| F32 | version.lammps (software) | `2 Aug 2023 - Update 1` | log.lammps:1 | log |  |
| F19 | version.lammps (software) | `2Aug2023` | job.slurm:7 | code |  |
| F36 | wall_time (wall_time) | `11:27:15` | log.lammps:11 | log |  |

## Parameters / 参数
| id | key (canonical) | value | source | kind | flags |
|---|---|---|---|---|---|
| F43 | text.duration.平衡 (duration) | `100 ps` | notes_gbk.txt:2 | doc_kv |  |
| F9 | fix (ensemble) | `npt` | in.npt:10 | config |  |
| F4 | pair_style (force_field) | `lj/cut/tip4p/long 1 2 1 1 0.1546 12.0` | in.npt:5 | config |  |
| F13 | run (nsteps) | `500000` | in.npt:12 | config |  |
| F11 | press (pressure) | `1.0 1.0 1000.0` | in.npt:10 | config |  |
| F6 | velocity.initial_temperature (temperature) | `298.0` | in.npt:7 | config |  |
| F10 | temp (temperature) | `298.0 298.0 100.0` | in.npt:10 | config |  |
| F8 | timestep (timestep) | `2.0` | in.npt:8 | config | CONFLICT C1 |
| F40 | text.步长 (timestep) | `1` | notes_gbk.txt:3 | doc_kv | CONFLICT C1 |

## Datasets and splits / 数据集与划分
| id | key (canonical) | value | source | kind | flags |
|---|---|---|---|---|---|
| F33 | text.system_size.atoms (system_size) | `12288 atoms` | log.lammps:4 | log |  |
| F34 | text.system_size.molecules (system_size) | `4096 molecules` | log.lammps:5 | log |  |

## Baselines / controls and evaluation / 对照与评价
| id | key (canonical) | value | source | kind | flags |
|---|---|---|---|---|---|
| F44 | n_runs (n_runs) | `1` | notes_gbk.txt:5 | doc_kv |  |

## Reproducibility and limitations / 可复现性与限制
| id | key (canonical) | value | source | kind | flags |
|---|---|---|---|---|---|
| F20 | command (command) | `lmp -in in.npt -log log.lammps` | job.slurm:8 | cli |  |
| F7 | velocity.seed (seed) | `4928459` | in.npt:7 | config |  |

## Other structured values (not mapped to a known key)
| id | key | value | source | kind |
|---|---|---|---|---|
| F1 | units | `real` | in.npt:2 | config |
| F2 | atom_style | `full` | in.npt:3 | config |
| F3 | read_data | `water_4096.data` | in.npt:4 | config |
| F5 | kspace_style | `pppm/tip4p 1.0e-5` | in.npt:6 | config |
| F12 | thermo | `1000` | in.npt:11 | config |
| F14 | job-name | `water_npt` | job.slurm:2 | cli |
| F17 | time | `24:00:00` | job.slurm:5 | cli |
| F18 | partition | `cpu` | job.slurm:6 | cli |
| F21 | in | `in.npt` | job.slurm:8 | cli |
| F22 | log | `log.lammps` | job.slurm:8 | cli |

## Lines with numbers in notes / data cards / drafts (cite them like any fact)
- F23 `log.lammps:1` LAMMPS (2 Aug 2023 - Update 1)
- F24 `log.lammps:2` OMP_NUM_THREADS environment is not set. Defaulting to 1 thread.
- F25 `log.lammps:4` 12288 atoms
- F26 `log.lammps:5` 4096 molecules
- F27 `log.lammps:6` Running on 32 MPI tasks, Intel(R) Xeon(R) Gold 6248R CPU @ 3.00GHz
- F28 `log.lammps:8` 0          298   -120.4   0.9921
- F29 `log.lammps:9` 500000    298.3     2.1   0.9973
- F30 `log.lammps:10` Loop time of 41235.2 on 32 procs for 500000 steps with 12288 atoms
- F31 `log.lammps:11` Total wall time: 11:27:15
- F38 `notes_gbk.txt:1` 体系：4096 个 TIP4P/2005 水分子，立方盒子。
- F39 `notes_gbk.txt:2` 先 NVT 平衡 100 ps，再 NPT 生产 1 ns。
- F41 `notes_gbk.txt:3` 步长 1 fs（与 Vega 2005 一致）。
- F42 `notes_gbk.txt:4` 密度取后 500 ps 平均。

## Pipeline stages / commands found (method steps should cover each)
- `job.slurm:8` `lmp -in in.npt -log log.lammps`

## Conflicts (must be marked [[CONFIRM: ...]] or resolved in agent.json)
- **C1** 时间步长: `2.0` (F8; in.npt:8; config); `1` (F40; notes_gbk.txt:3; doc_kv) — precedence guess F8

## Gaps / author questions (write [[GAP: ...]] in the draft where the information belongs)
- **G1** [control, required, only_mentioned_in_text] 评价指标/测量结局: 请定义各评价指标（在哪个数据子集、哪个检查点上计算）。
- **G2** [control, recommended, missing] 统计检验/不确定度估计: 比较结论基于何种统计检验或不确定度估计（检验方法、显著性水平、多重校正）？
- **G3** [repro, recommended, missing] 数据获取方式: 读者如何获取数据（URL/DOI、许可、访问限制）？
- **G4** [repro, required, author_input] 落到具体失效场景的限制条件: 哪些条件未测试（数据、规模、硬件、设置）？方法在哪些具体场景下可能失效？
