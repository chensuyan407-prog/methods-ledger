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
