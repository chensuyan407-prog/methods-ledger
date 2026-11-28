| 参数 | 取值 | 单位 | 作用对象 | 来源 | 状态 |
|---|---|---|---|---|---|
| 批大小 | 32 | - | - | logs/train_bert_seed42.log:5 (F67) | 正文已引用 |
| dropout | 0.1 | - | model | configs/train.yaml:5 (F32) | 正文已引用 |
| 训练轮数 | 5 | - | - | logs/train_bert_seed42.log:5 (F68) | 正文已引用; 其他取值：src/train.py:10=3 |
| 评测批大小 | 64 | - | test/eval | configs/train.yaml:25 (F49) | 正文未使用 |
| 梯度裁剪阈值 | 1.0 | - | train | configs/train.yaml:20 (F45) | 正文已引用 |
| 学习率 | 2e-05 | - | - | logs/train_bert_seed42.log:5 (F66) | 冲突 C1，待作者确认 |
| 最大迭代次数（求解器） | 1000 | - | baseline | src/baseline.py:6 (F103) | 正文未使用 |
| 最大序列长度 | 256 | - | - | logs/train_bert_seed42.log:5 (F70) | 正文已引用 |
| 优化器 | AdamW | - | train | configs/train.yaml:13 (F38) | 正文已引用 |
| 学习率调度 | linear | - | train | configs/train.yaml:19 (F44) | 正文已引用; 其他取值：src/train.py:4=get_linear_schedule_with_warmu |
| 求解器 | liblinear | - | baseline | configs/baseline_tfidf.yaml:6 (F28) | 正文已引用 |
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
| 硬件 (gpu) | NVIDIA A100-SXM4-80GB | - | - | logs/train_bert_seed42.log:3 (F98) | 正文已引用 |
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
