# 3 方法与实验

## 3.1 方法步骤

1. 数据清洗：输入为原始数据包 thucnews_2016.zip（共 74000 篇文档）[[@logs/preprocess.log:1#raw,@logs/preprocess.log:2#log_line]]；运行 `src/preprocess.py`，剔除长度不在 [20, 2000] 字符范围内的文档 1210 篇 [[@src/preprocess.py:4#MIN_CHARS,@src/preprocess.py:5#MAX_CHARS,@logs/preprocess.log:3#log_line]]，再按全文精确去重剔除 790 篇 [[@logs/preprocess.log:4#log_line]]；输出为保留的 72000 篇文档 [[CALC: 74000-1210-790 = 72000 | @logs/preprocess.log:2#log_line,@logs/preprocess.log:3#log_line,@logs/preprocess.log:4#log_line]]。
2. 数据划分：先以 test_size=0.2 分层抽取 [[@src/preprocess.py:10#test_size]]，再将剩余部分按 test_size=0.5 等分为验证集与测试集 [[@src/preprocess.py:11#test_size]]，两次划分的随机种子均为 2023 [[@src/preprocess.py:10#random_state,@src/preprocess.py:11#random_state]]；输出训练集 57600 条、验证集 7200 条、测试集 7200 条 [[@logs/preprocess.log:5#n_train,@logs/preprocess.log:5#n_val,@logs/preprocess.log:5#n_test]]，与数据说明中的 8:1:1 划分一致 [[@data_card.md:7#split_ratio]]。
3. 模型微调：以 `src/train.py` 加载预训练模型 bert-base-chinese [[@configs/train.yaml:3#model.name]]，在训练集上微调 5 个 epoch [[@logs/train_bert_seed42.log:5#epochs]]，每个 epoch 结束后在验证集上计算 macro-F1 [[@configs/train.yaml:24#eval.metric]]。
4. 检查点选择与测试：按验证集 macro-F1 选择第 4 个 epoch 的检查点 [[@logs/train_bert_seed42.log:11#checkpoint]]，测试集只评测一次 [[@notes.md:5#sentence]]。
5. 基线：以 `src/baseline.py` 训练 TF-IDF + 逻辑回归基线 [[@configs/baseline_tfidf.yaml:2#baseline.name]]，在同一测试集上评测 [[@logs/baseline.log:1#command]]。

## 3.2 实验设置

微调在 1 块 NVIDIA A100-SXM4-80GB 上完成 [[@logs/train_bert_seed42.log:3#gpu,@logs/train_bert_seed42.log:3#num_gpus]]，软件环境为 PyTorch 2.1.2+cu121、CUDA 12.1 [[@logs/train_bert_seed42.log:2#version.torch,@logs/train_bert_seed42.log:2#version.cuda]]、transformers 4.36.2 与 scikit-learn 1.3.2 [[@requirements.txt:2#version.transformers,@requirements.txt:3#version.scikit-learn]]，训练启用 fp16 混合精度 [[@configs/train.yaml:21#train.fp16]]。numpy 仅给出版本下限 >=1.24 [[@requirements.txt:4#version.numpy]] [[GAP: 请提供实际安装的 numpy 版本（pip freeze）]]。

## 3.3 数据集与划分

实验使用 THUCNews 的 10 类子集 [[@data_card.md:2#Name,@configs/train.yaml:11#data.num_classes]]，数据来源为 http://thuctc.thunlp.org/ [[@data_card.md:3#Source]]，许可为仅限研究使用 [[@data_card.md:4#License]]。原始数据包下载于 2024-02-28 [[@data_card.md:5#snapshot]]；THUCNews 本身未给出版本号 [[GAP: 请确认所用 THUCNews 发布版本或在论文中以下载日期作为版本标识]]。划分方式见 3.1 第 2 步。

## 3.4 参数设置

BERT 微调使用 AdamW 优化器 [[@configs/train.yaml:13#train.optimizer]]，学习率 2e-5 [[@logs/train_bert_seed42.log:5#lr,@logs/train_bert_seed42.log:1#lr]] [[CONFIRM: C1 配置文件 train.yaml 中为 3.0e-5，训练命令与日志为 2e-5，作者笔记称最终采用 2e-5；正文按日志写 2e-5]]，权重衰减 0.01 [[@configs/train.yaml:15#train.weight_decay]]，批大小 32 [[@logs/train_bert_seed42.log:5#batch_size]]，最大序列长度 256 [[@logs/train_bert_seed42.log:5#max_length]]，dropout 0.1 [[@configs/train.yaml:5#model.dropout]]，线性学习率调度并以 0.1 的比例预热 [[@configs/train.yaml:19#train.scheduler,@logs/train_bert_seed42.log:5#warmup_ratio]]，梯度裁剪阈值 1.0 [[@configs/train.yaml:20#train.max_grad_norm]]。基线的 TF-IDF 取 1–2 元语法 [[@configs/baseline_tfidf.yaml:3#baseline.ngram_range]]、最多 50000 个特征 [[@configs/baseline_tfidf.yaml:4#baseline.max_features]]，逻辑回归 C=1.0、求解器 liblinear [[@configs/baseline_tfidf.yaml:5#baseline.C,@configs/baseline_tfidf.yaml:6#baseline.solver]]，未调参 [[@notes.md:4#sentence]]。

[[PARAM_TABLE]]

## 3.5 对照实验与评价

主要评价指标为测试集 macro-F1，同时报告准确率 [[@configs/train.yaml:24#eval.metric,@logs/train_bert_seed42.log:12#accuracy]]。BERT 与 TF-IDF 基线使用同一划分的训练集与测试集 [[@logs/baseline.log:1#command,@logs/train_bert_seed42.log:1#command]]；基线未做超参数搜索 [[@notes.md:4#sentence]]，因此两者的调参预算不同。每个模型只运行了一次（BERT 种子 42）[[@notes.md:3#sentence,@logs/train_bert_seed42.log:5#seed]] [[GAP: 是否补充多种子重复实验并报告均值±标准差？]]；未进行统计检验 [[GAP: 是否需要对 BERT 与基线的差异做显著性检验（如配对 bootstrap）？]]。

## 3.6 可复现性

代码版本为提交 9f3c2ab [[@logs/train_bert_seed42.log:4#commit]]。依次运行以下命令可复现数据划分、BERT 微调和基线：

```
python src/preprocess.py --raw data/raw/thucnews_2016.zip --out data/
python src/train.py --config configs/train.yaml --lr 2e-5 --epochs 5 --seed 42
python src/baseline.py --config configs/baseline_tfidf.yaml
```

训练随机种子为 42 [[@logs/train_bert_seed42.log:5#seed]]，数据划分种子为 2023 [[@src/preprocess.py:10#random_state]]。

## 3.7 限制条件

- 所有结果来自单一种子（42）的单次运行 [[@notes.md:3#sentence]]，未估计随机初始化带来的方差。
- 基线未调参而 BERT 使用了经调整的学习率 [[@notes.md:2#sentence,@notes.md:4#sentence]]，比较不在相同调参预算下进行。
- 仅在 THUCNews 10 类子集、长度 20–2000 字符的文档上评测 [[@configs/train.yaml:11#data.num_classes,@src/preprocess.py:4#MIN_CHARS,@src/preprocess.py:5#MAX_CHARS]]，更长文档会被 256 的最大序列长度截断 [[@logs/train_bert_seed42.log:5#max_length]]，其效果未测试。
- 仅在单块 A100 上训练 [[@logs/train_bert_seed42.log:3#gpu]]，未验证其他硬件与 fp16 关闭时的结果。
