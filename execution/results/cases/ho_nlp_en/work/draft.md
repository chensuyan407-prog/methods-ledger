# 4 Experimental Setup

## 4.1 Procedure

1. Data loading: GLUE SST-2 was loaded with `load_dataset("glue", "sst2")` at dataset revision bcdcba79d07bc864c1c254ccfcedcce55bcc9a8c [[@run_glue.py:10]]; output: 67349 training and 872 validation sentences [[@train_lora_s1.log:3]].
2. LoRA fine-tuning: roberta-large [[@conf/lora.yaml:2]] was adapted with LoRA on the query and value projections [[@conf/lora.yaml:8]], training 1,838,082 of 357,199,876 parameters [[@train_lora_s1.log:4]].
3. Baseline: full fine-tuning of the same roberta-large model [[@conf/full_ft.yaml:3]] with its own configuration [[@launch.sh:4]].
4. Evaluation: accuracy on the official SST-2 validation split, because GLUE test labels are hidden [[SRC: run_glue.py:11]]; the best epoch was selected on the same split (epoch 14 in the logged LoRA run) [[@train_lora_s1.log:6]].

## 4.2 Hyperparameters

LoRA used rank r = 8 [[@conf/lora.yaml:5]], alpha = 16 [[@conf/lora.yaml:6]] and dropout 0.05 [[@conf/lora.yaml:7]]. Optimisation used adamw_torch [[@conf/lora.yaml:10]] with learning rate 4e-4 [[@train_lora_s1.log:5#learning_rate]], weight decay 0.1 [[@conf/lora.yaml:12]], a linear schedule with warm-up ratio 0.06 [[@conf/lora.yaml:13,@conf/lora.yaml:14]], 20 epochs [[@train_lora_s1.log:5#num_train_epochs]], maximum sequence length 128 [[@conf/lora.yaml:19]] and bf16 [[@conf/lora.yaml:20]]. The logged run used a per-device batch size of 32 without gradient accumulation [[@train_lora_s1.log:5]] [[CONFIRM: conf/lora.yaml sets per-device batch 16 with accumulation 2; the log shows 32 and 1. Both give an effective batch of 128 on 4 GPUs, but which setting was used for seeds 2 and 3?]].
The full fine-tuning baseline used learning rate 1.0e-5 [[@conf/full_ft.yaml:5]] , weight decay 0.1 [[@conf/full_ft.yaml:6]], per-device batch size 16 [[@conf/full_ft.yaml:8]] [[CONFIRM: batch size 16 here is the baseline config value; the LoRA log shows 32, the LoRA config 16]] for 10 epochs [[@conf/full_ft.yaml:9]] at sequence length 128 [[@conf/full_ft.yaml:10]].

[[PARAM_TABLE]]

## 4.3 Compute and software

Each run used 4 GPUs (torchrun, 4 processes per node) [[@launch.sh:3]] of type NVIDIA A100-SXM4-40GB [[@train_lora_s1.log:2]], with Python 3.10.13, PyTorch 2.2.1, transformers 4.40.0, peft 0.10.0 and CUDA 12.1 [[@train_lora_s1.log:1]]. Total compute was about 40 GPU-hours [[@README.md:3]].

## 4.4 Seeds, repetitions and statistics

Every method was run with seeds 1, 2 and 3 [[@results.csv:2,@results.csv:3,@results.csv:4]] [[CONFIRM: C1 launch.sh passes --seed $SEED from the loop; results.csv lists the seeds]]; results are the mean over the three seeds [[@README.md:2]]. No significance test or confidence interval was computed [[GAP: Report standard deviation over seeds and a paired test or bootstrap CI for LoRA vs full fine-tuning?]].

## 4.5 Reproducibility

Code commit 4be1d0e [[@README.md:2#commit]]. Commands, run for SEED in 1 2 3 [[SRC: launch.sh:2]]:

```
torchrun --nproc_per_node 4 run_glue.py --config conf/lora.yaml --seed $SEED --output_dir out/lora_s$SEED
torchrun --nproc_per_node 4 run_glue.py --config conf/full_ft.yaml --seed $SEED --output_dir out/full_s$SEED
```

Data are public through the GLUE benchmark [[GAP: cite the GLUE/SST-2 licence and the Hugging Face dataset page]].

## 4.6 Limitations

- Model selection and reporting both use the 872-sentence validation split [[@train_lora_s1.log:3]], so the reported accuracy is optimistically biased.
- Only one model (roberta-large) [[@conf/lora.yaml:2]] and one task (SST-2) [[@run_glue.py:10]] were tested.
- Only 3 seeds per method [[@results.csv:2,@results.csv:3,@results.csv:4]]; the baseline used 10 epochs against 20 for LoRA [[@conf/full_ft.yaml:9,@conf/lora.yaml:18]], so the budgets differ.
