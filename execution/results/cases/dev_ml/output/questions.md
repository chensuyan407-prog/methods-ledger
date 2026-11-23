# 待作者确认清单

- [ ] **G1** (gap, control) 每个条件独立运行/平行样多少次？报告的是均值±标准差/标准误还是单次结果？
- [ ] **G2** (gap, control) 比较结论基于何种统计检验或不确定度估计（检验方法、显著性水平、多重校正）？
- [ ] **G3** (gap, repro) 哪些条件未测试（数据、规模、硬件、设置）？方法在哪些具体场景下可能失效？
- [ ] **G4** (gap, control) 材料中只出现一个随机种子取值：报告结果是否来自单次运行？若有多次运行，请列出各次种子。 — facts F15, F29, F47, F69, F94
- [ ] **G5** (gap, setup) 部分依赖只写了版本范围（>=、~=）：请给出报告运行时实际安装的精确版本（pip freeze）。 — facts F22
- [ ] **C1** (conflict, params) 学习率 在材料中取值不一致：2e-05 (logs/train_bert_seed42.log:5); 3.0e-5 (configs/train.yaml:14)。正文采用哪一个？ — facts F66, F92, F39, F13
- [ ] **Q-u18** (draft_gap) 请提供实际安装的 numpy 版本（pip freeze）
- [ ] **Q-u22** (draft_gap) 请确认所用 THUCNews 发布版本或在论文中以下载日期作为版本标识
- [ ] **Q-u25c** (draft_confirm) C1 配置文件 train.yaml 中为 3.0e-5，训练命令与日志为 2e-5，作者笔记称最终采用 2e-5；正文按日志写 2e-5
- [ ] **Q-u32** (draft_gap) 是否补充多种子重复实验并报告均值±标准差？
- [ ] **Q-u33** (draft_gap) 是否需要对 BERT 与基线的差异做显著性检验（如配对 bootstrap）？
