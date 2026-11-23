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

## Check items
- WARN T05 l.9: cited F24 (baseline.name = tfidf_logreg) but its value is not in the sentence
- WARN T05 l.21: cited F44 (train.scheduler = linear) but its value is not in the sentence
- WARN T05 l.43: cited F98 (gpu = NVIDIA A100-SXM4-80GB) but its value is not in the sentence
- WARN K03 l.None: facts in the materials never used in the chapter: dataset (F33); validation file (F35); test file (F36); cuDNN version (F97); training steps / iterations (F103)
