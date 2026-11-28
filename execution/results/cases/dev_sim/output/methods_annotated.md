# 2 计算方法

## 2.1 计算流程

1. 体系构建：读入数据文件 water_4096.data <sup>[in.npt:4]</sup>，体系含 4096 个 TIP4P/2005 水分子 <sup>[F26: log.lammps:5; F34: log.lammps:5]</sup>，共 12288 个原子 <sup>[F25: log.lammps:4; F33: log.lammps:4]</sup>，置于立方盒子中 <sup>[notes_gbk.txt:1]</sup>。
2. 初始化：按 298.0 K 的高斯分布生成初始速度 <sup>[F6: in.npt:7; F7: in.npt:7]</sup>。
3. 平衡：先进行 100 ps 的 NVT 平衡 <sup>[F39: notes_gbk.txt:2; F43: notes_gbk.txt:2]</sup> 【待确认：NVT 平衡的输入文件未提供，请补充其控温方式与参数】。
4. 生产：在 NPT 系综下运行 500000 步 <sup>[F13: in.npt:12; F9: in.npt:10]</sup>，输出每 1000 步的热力学量 <sup>[in.npt:11]</sup>。
5. 分析：密度取生产段后 500 ps 的平均值 <sup>[notes_gbk.txt:4]</sup>。

## 2.2 力场与模拟参数

采用 TIP4P/2005 水模型 <sup>[in.npt:1]</sup>，非键相互作用为 lj/cut/tip4p/long，截断 12.0 Å <sup>[F4: in.npt:5]</sup>，长程静电用 PPPM（精度 1.0e-5）<sup>[in.npt:6]</sup>，并用 SHAKE 约束水分子几何（容差 0.0001）<sup>[in.npt:9]</sup>。时间步长为 2.0 fs <sup>[F8: in.npt:8]</sup> 【待作者确认：C1 输入文件为 2.0 fs，笔记写 1 fs（与 Vega 2005 一致）；正文按实际输入文件写 2.0 fs】，因此 500000 步对应 1 ns <sup>[calc: 500000*2.0/1000000]</sup>，与笔记中的 1 ns 生产时长一致 <sup>[F39: notes_gbk.txt:2; F43: notes_gbk.txt:2]</sup>。温度控制在 298.0 K（阻尼 100.0）<sup>[F10: in.npt:10]</sup>，压强 1.0 atm（阻尼 1000.0）各向同性耦合 <sup>[F11: in.npt:10]</sup>；LAMMPS 采用 real 单位制 <sup>[in.npt:2]</sup>。



| 参数 | 取值 | 单位 | 作用对象 | 来源 | 状态 |
|---|---|---|---|---|---|
| 时长 | 100 ps | - | text/duration | notes_gbk.txt:2 (F43) | 正文已引用 |
| 系综/积分器 | npt | - | - | in.npt:10 (F9) | 正文已引用 |
| 力场/势函数 | lj/cut/tip4p/long 1 2 1 1 0.1546 12.0 | - | - | in.npt:5 (F4) | 正文已引用 |
| 模拟步数 | 500000 | - | - | in.npt:12 (F13) | 正文已引用 |
| 压强 | 1.0 1.0 1000.0 | - | - | in.npt:10 (F11) | 正文已引用 |
| 温度 | 298.0 | - | velocity | in.npt:7 (F6) | 正文已引用; 其他取值：in.npt:10=298.0 298.0 100.0 |
| 时间步长 | 2.0 | - | - | in.npt:8 (F8) | 冲突 C1，待作者确认 |
| 体系规模 | 12288 atoms | - | text/system_size | log.lammps:4 (F33) | 正文已引用; 其他取值：log.lammps:5=4096 molecules |
| 硬件 (cpu) | Intel(R) Xeon(R) Gold 6248R | - | - | log.lammps:6 (F35) | 正文已引用 |
| 节点数 | 1 | - | - | job.slurm:3 (F15) | 正文已引用 |
| 进程/线程数 | 32 | - | - | job.slurm:4 (F16) | 正文已引用 |
| 软件 (lammps) | 2 Aug 2023 - Update 1 | - | - | log.lammps:1 (F32) | 正文已引用; 其他取值：job.slurm:7=2Aug2023 |
| 运行时间 | 11:27:15 | - | - | log.lammps:11 (F36) | 正文已引用 |
| 重复次数 | 1 | - | - | notes_gbk.txt:5 (F44) | 正文已引用 |
| 随机种子 | 4928459 | - | velocity | in.npt:7 (F7) | 正文已引用 |



## 2.3 软硬件环境

模拟使用 LAMMPS（2 Aug 2023 - Update 1）<sup>[F23: log.lammps:1; F32: log.lammps:1]</sup>，在 1 个节点 <sup>[F15: job.slurm:3]</sup> 的 32 个 MPI 进程上运行 <sup>[F16: job.slurm:4]</sup>，处理器为 Intel(R) Xeon(R) Gold 6248R <sup>[F27: log.lammps:6; F35: log.lammps:6]</sup>；生产段总墙钟时间 11:27:15 <sup>[F31: log.lammps:11; F36: log.lammps:11]</sup>。

## 2.4 重复与统计

仅模拟了一条轨迹 <sup>[F44: notes_gbk.txt:5]</sup>，初始速度随机种子为 4928459 <sup>[F7: in.npt:7]</sup>，因此未给出轨迹间的统计误差 【待确认：是否补充不同速度种子的独立轨迹，或用分块平均给出密度的标准误？】。

## 2.5 可复现性

运行命令为 `lmp -in in.npt -log log.lammps` <sup>[F20: job.slurm:8; F21: job.slurm:8; F22: job.slurm:8]</sup>，作业脚本见 job.slurm <sup>[job.slurm:1]</sup>。数据文件 water_4096.data 未包含在材料中 【待确认：请说明 water_4096.data 的生成方式或公开获取方式】。

## 2.6 局限

- 结果仅基于单条轨迹 <sup>[F44: notes_gbk.txt:5]</sup>，未估计初始条件带来的涨落。
- 仅在 298.0 K、1.0 atm 单一状态点模拟 <sup>[F10: in.npt:10; F11: in.npt:10]</sup>，其他温度压强下的密度未验证。
- 时间步长 2.0 fs 与笔记中 1 fs 的说法不一致 <sup>[F8: in.npt:8; F40: notes_gbk.txt:3; F41: notes_gbk.txt:3]</sup> 【待作者确认：C1 若作者实际意图为 1 fs，则生产时长仅为 0.5 ns】。

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
