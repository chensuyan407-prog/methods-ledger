# 3 方法与实验

## 3.1 方法步骤

1. 数据清洗：输入为原始数据包 thucnews_2016.zip（共 74000 篇文档）；运行 `src/preprocess.py`，剔除长度不在 [20, 2000] 字符范围内的文档 1210 篇，再按全文精确去重剔除 790 篇；输出为保留的 72000 篇文档。
2. 数据划分：先以 test_size=0.2 分层抽取，再将剩余部分按 test_size=0.5 等分为验证集与测试集，两次划分的随机种子均为 2023；输出训练集 57600 条、验证集 7200 条、测试集 7200 条，与数据说明中的 8:1:1 划分一致。
3. 模型微调：以 `src/train.py` 加载预训练模型 bert-base-chinese，在训练集上微调 5 个 epoch，每个 epoch 结束后在验证集上计算 macro-F1。
4. 检查点选择与测试：按验证集 macro-F1 选择第 4 个 epoch 的检查点，测试集只评测一次。
5. 基线：以 `src/baseline.py` 训练 TF-IDF + 逻辑回归基线，在同一测试集上评测。

## 3.2 实验设置

微调在 1 块 NVIDIA A100-SXM4-80GB 上完成，软件环境为 PyTorch 2.1.2+cu121、CUDA 12.1 、transformers 4.36.2 与 scikit-learn 1.3.2，训练启用 fp16 混合精度。numpy 仅给出版本下限 >=1.24 【待确认：请提供实际安装的 numpy 版本（pip freeze）】。

## 3.3 数据集与划分

实验使用 THUCNews 的 10 类子集，数据来源为 http://thuctc.thunlp.org/，许可为仅限研究使用。原始数据包下载于 2024-02-28；THUCNews 本身未给出版本号 【待确认：请确认所用 THUCNews 发布版本或在论文中以下载日期作为版本标识】。划分方式见 3.1 第 2 步。

## 3.4 参数设置

BERT 微调使用 AdamW 优化器，学习率 2e-5 【待作者确认：C1 配置文件 train.yaml 中为 3.0e-5，训练命令与日志为 2e-5，作者笔记称最终采用 2e-5；正文按日志写 2e-5】，权重衰减 0.01，批大小 32，最大序列长度 256，dropout 0.1，线性学习率调度并以 0.1 的比例预热，梯度裁剪阈值 1.0。基线的 TF-IDF 取 1–2 元语法 、最多 50000 个特征，逻辑回归 C=1.0、求解器 liblinear，未调参。



| 参数 | 取值 | 单位 | 作用对象 | 来源 | 状态 |
|---|---|---|---|---|---|
| 批大小 | 32 | - | - | logs/train_bert_seed42.log:5 (F67) | 正文已引用 |
| dropout | 0.1 | - | model | configs/train.yaml:5 (F32) | 正文已引用 |
| 训练轮数 | 5 | - | - | logs/train_bert_seed42.log:5 (F68) | 正文已引用; 其他取值：src/train.py:10=3 |
| 评测批大小 | 64 | - | test/eval | configs/train.yaml:25 (F49) | 正文未使用 |
| 梯度裁剪阈值 | 1.0 | - | train | configs/train.yaml:20 (F45) | 正文已引用 |
| 学习率 | 2e-05 | - | - | logs/train_bert_seed42.log:5 (F66) | 冲突 C1，待作者确认 |
| 最大序列长度 | 256 | - | - | logs/train_bert_seed42.log:5 (F70) | 正文已引用 |
| 训练步数/迭代次数 | 1000 | - | baseline | src/baseline.py:6 (F103) | 正文未使用 |
| 优化器 | liblinear | - | baseline | configs/baseline_tfidf.yaml:6 (F28) | 正文已引用 |
| 优化器 | AdamW | - | train | configs/train.yaml:13 (F38) | 正文已引用 |
| 学习率调度 | linear | - | train | configs/train.yaml:19 (F44) | 正文已引用; 其他取值：src/train.py:4=get_linear_schedule_with_warmu |
| 预热 | 0.1 | - | - | logs/train_bert_seed42.log:5 (F71) | 正文已引用 |
| 权重衰减 | 0.01 | - | train | configs/train.yaml:15 (F40) | 正文已引用 |
| 数据集 | THUCNews-subset | - | data | configs/train.yaml:7 (F33) | 正文未使用 |
| 数据集版本 | downloaded 2024-02-28 | - | - | data_card.md:5 (F11) | 正文已引用 |
| 许可 | research use only | - | - | data_card.md:4 (F4) | 正文已引用 |
| 测试集样本数 | 7200 | - | - | logs/preprocess.log:5 (F64) | 正文已引用 |
| 训练集样本数 | 57600 | - | - | logs/preprocess.log:5 (F62) | 正文已引用 |
| 验证集样本数 | 7200 | - | - | logs/preprocess.log:5 (F63) | 正文已引用 |
| 类别数 | 10 | - | data | configs/train.yaml:11 (F37) | 正文已引用 |
| 数据来源 | http://thuctc.thunlp.org/ | - | - | data_card.md:3 (F3) | 正文已引用 |
| 划分比例 | 8:1:1, stratified by label for the train/rest split | - | - | data_card.md:7 (F9) | 正文已引用; 其他取值：data_card.md:7=8:1:1 |
| 数据划分种子 | 2023 | - | - | src/preprocess.py:10 (F107) | 正文已引用 |
| 测试集文件 | data/test.jsonl | - | test/data | configs/train.yaml:10 (F36) | 正文未使用 |
| 测试集比例 | 0.2 | - | test | src/preprocess.py:10 (F106) | 正文已引用; 其他取值：src/preprocess.py:11=0.5 |
| 验证集文件 | data/val.jsonl | - | val/data | configs/train.yaml:9 (F35) | 正文未使用 |
| CUDA 版本 | 12.1 | - | - | logs/train_bert_seed42.log:2 (F96) | 正文已引用 |
| cuDNN 版本 | 8902 | - | - | logs/train_bert_seed42.log:2 (F97) | 正文未使用 |
| 硬件 | NVIDIA A100-SXM4-80GB | - | - | logs/train_bert_seed42.log:3 (F98) | 正文已引用 |
| GPU/设备数 | 1 | - | - | logs/train_bert_seed42.log:3 (F99) | 正文已引用 |
| 数值精度 | true | - | train | configs/train.yaml:21 (F46) | 正文已引用 |
| 软件 (transformers) | 4.36.2 | - | - | requirements.txt:2 (F20) | 正文已引用 |
| 软件 (scikit-learn) | 1.3.2 | - | - | requirements.txt:3 (F21) | 正文已引用 |
| 软件 (numpy) | >=1.24 | - | - | requirements.txt:4 (F22) | 正文已引用 |
| 软件 (jieba) | 0.42.1 | - | - | requirements.txt:5 (F23) | 正文未使用 |
| PyTorch 版本 | 2.1.2+cu121 | - | - | logs/train_bert_seed42.log:2 (F95) | 正文已引用; 其他取值：requirements.txt:1=2.1.2 |
| 评价指标 | macro_f1 | - | test/eval | configs/train.yaml:24 (F48) | 正文已引用 |
| 评价指标 | f1_score | - | baseline | src/baseline.py:3 (F101) | 正文未使用 |
| 模型/结构 | bert-base-chinese | - | model | configs/train.yaml:3 (F30) | 正文已引用 |
| 检查点/权重 | epoch 4 | - | val | logs/train_bert_seed42.log:11 (F76) | 正文已引用 |
| 代码版本 | 9f3c2ab | - | - | logs/train_bert_seed42.log:4 (F65) | 正文已引用 |
| 随机种子 | 42 | - | - | logs/train_bert_seed42.log:5 (F69) | 正文已引用 |
| 随机种子 | 42 | - | baseline | configs/baseline_tfidf.yaml:7 (F29) | 正文未使用 |



## 3.5 对照实验与评价

主要评价指标为测试集 macro-F1，同时报告准确率。BERT 与 TF-IDF 基线使用同一划分的训练集与测试集；基线未做超参数搜索，因此两者的调参预算不同。每个模型只运行了一次（BERT 种子 42） 【待确认：是否补充多种子重复实验并报告均值±标准差？】；未进行统计检验 【待确认：是否需要对 BERT 与基线的差异做显著性检验（如配对 bootstrap）？】。

## 3.6 可复现性

代码版本为提交 9f3c2ab。依次运行以下命令可复现数据划分、BERT 微调和基线：

```
python src/preprocess.py --raw data/raw/thucnews_2016.zip --out data/
python src/train.py --config configs/train.yaml --lr 2e-5 --epochs 5 --seed 42
python src/baseline.py --config configs/baseline_tfidf.yaml
```

训练随机种子为 42，数据划分种子为 2023。

## 3.7 限制条件

- 所有结果来自单一种子（42）的单次运行，未估计随机初始化带来的方差。
- 基线未调参而 BERT 使用了经调整的学习率，比较不在相同调参预算下进行。
- 仅在 THUCNews 10 类子集、长度 20–2000 字符的文档上评测，更长文档会被 256 的最大序列长度截断，其效果未测试。
- 仅在单块 A100 上训练，未验证其他硬件与 fp16 关闭时的结果。
