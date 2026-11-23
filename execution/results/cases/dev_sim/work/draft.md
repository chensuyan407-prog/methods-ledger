# 2 计算方法

## 2.1 计算流程

1. 体系构建：读入数据文件 water_4096.data [[SRC: in.npt:4]]，体系含 4096 个 TIP4P/2005 水分子 [[@log.lammps:5]]，共 12288 个原子 [[@log.lammps:4]]，置于立方盒子中 [[SRC: notes_gbk.txt:1]]。
2. 初始化：按 298.0 K 的高斯分布生成初始速度 [[@in.npt:7]]。
3. 平衡：先进行 100 ps 的 NVT 平衡 [[@notes_gbk.txt:2]] [[GAP: NVT 平衡的输入文件未提供，请补充其控温方式与参数]]。
4. 生产：在 NPT 系综下运行 500000 步 [[@in.npt:12,@in.npt:10#fix]]，输出每 1000 步的热力学量 [[SRC: in.npt:11]]。
5. 分析：密度取生产段后 500 ps 的平均值 [[SRC: notes_gbk.txt:4]]。

## 2.2 力场与模拟参数

采用 TIP4P/2005 水模型 [[SRC: in.npt:1]]，非键相互作用为 lj/cut/tip4p/long，截断 12.0 Å [[@in.npt:5]]，长程静电用 PPPM（精度 1.0e-5）[[SRC: in.npt:6]]，并用 SHAKE 约束水分子几何（容差 0.0001）[[SRC: in.npt:9]]。时间步长为 2.0 fs [[@in.npt:8]] [[CONFIRM: C1 输入文件为 2.0 fs，笔记写 1 fs（与 Vega 2005 一致）；正文按实际输入文件写 2.0 fs]]，因此 500000 步对应 1 ns [[CALC: 500000*2.0/1000000 = 1 | @in.npt:12,@in.npt:8]]，与笔记中的 1 ns 生产时长一致 [[@notes_gbk.txt:2]]。温度控制在 298.0 K（阻尼 100.0）[[@in.npt:10#temp]]，压强 1.0 atm（阻尼 1000.0）各向同性耦合 [[@in.npt:10#press]]；LAMMPS 采用 real 单位制 [[SRC: in.npt:2]]。

[[PARAM_TABLE]]

## 2.3 软硬件环境

模拟使用 LAMMPS（2 Aug 2023 - Update 1）[[@log.lammps:1]]，在 1 个节点 [[@job.slurm:3]] 的 32 个 MPI 进程上运行 [[@job.slurm:4]]，处理器为 Intel(R) Xeon(R) Gold 6248R [[@log.lammps:6]]；生产段总墙钟时间 11:27:15 [[@log.lammps:11]]。

## 2.4 重复与统计

仅模拟了一条轨迹 [[@notes_gbk.txt:5]]，初始速度随机种子为 4928459 [[@in.npt:7#seed]]，因此未给出轨迹间的统计误差 [[GAP: 是否补充不同速度种子的独立轨迹，或用分块平均给出密度的标准误？]]。

## 2.5 可复现性

运行命令为 `lmp -in in.npt -log log.lammps` [[@job.slurm:8]]，作业脚本见 job.slurm [[SRC: job.slurm:1]]。数据文件 water_4096.data 未包含在材料中 [[GAP: 请说明 water_4096.data 的生成方式或公开获取方式]]。

## 2.6 局限

- 结果仅基于单条轨迹 [[@notes_gbk.txt:5]]，未估计初始条件带来的涨落。
- 仅在 298.0 K、1.0 atm 单一状态点模拟 [[@in.npt:10#temp,@in.npt:10#press]]，其他温度压强下的密度未验证。
- 时间步长 2.0 fs 与笔记中 1 fs 的说法不一致 [[@in.npt:8,@notes_gbk.txt:3]] [[CONFIRM: C1 若作者实际意图为 1 fs，则生产时长仅为 0.5 ns]]。
