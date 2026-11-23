# 4 Experimental Setup

## 4.1 Procedure

1. Data loading: GLUE SST-2 was loaded with `load_dataset("glue", "sst2")` at dataset revision bcdcba79d07bc864c1c254ccfcedcce55bcc9a8c; output: 67349 training and 872 validation sentences.
2. LoRA fine-tuning: roberta-large was adapted with LoRA on the query and value projections, training 1,838,082 of 357,199,876 parameters.
3. Baseline: full fine-tuning of the same roberta-large model with its own configuration.
4. Evaluation: accuracy on the official SST-2 validation split, because GLUE test labels are hidden; the best epoch was selected on the same split (epoch 14 in the logged LoRA run).

## 4.2 Hyperparameters

LoRA used rank r = 8, alpha = 16 and dropout 0.05. Optimisation used adamw_torch with learning rate 4e-4, weight decay 0.1, a linear schedule with warm-up ratio 0.06, 20 epochs, maximum sequence length 128 and bf16. The logged run used a per-device batch size of 32 without gradient accumulation [AUTHOR TO CONFIRM: conf/lora.yaml sets per-device batch 16 with accumulation 2; the log shows 32 and 1. Both give an effective batch of 128 on 4 GPUs, but which setting was used for seeds 2 and 3?].
The full fine-tuning baseline used learning rate 1.0e-5, weight decay 0.1, per-device batch size 16 [AUTHOR TO CONFIRM: batch size 16 here is the baseline config value; the LoRA log shows 32, the LoRA config 16] for 10 epochs at sequence length 128.



| Parameter | Value | Unit | Applies to | Source | Status |
|---|---|---|---|---|---|
| batch size | 32 | - | - | train_lora_s1.log:5 (F41) | CONFLICT C1 - author to confirm |
| dropout | 0.05 | - | lora | conf/lora.yaml:7 (F70) | cited in text |
| epochs | 20 | - | - | train_lora_s1.log:5 (F44) | cited in text; other values: conf/full_ft.yaml:9=10 |
| gradient accumulation steps | 1 | - | - | train_lora_s1.log:5 (F42) | CONFLICT C2 - author to confirm |
| learning rate | 4e-4 | - | - | train_lora_s1.log:5 (F43) | cited in text; other values: conf/full_ft.yaml:5=1.0e-5; conf/lora.yaml:11=4.0e-4 |
| LoRA alpha | 16 | - | lora | conf/lora.yaml:6 (F69) | cited in text |
| LoRA rank | 8 | - | lora | conf/lora.yaml:5 (F68) | cited in text |
| maximum sequence length | 128 | - | training | conf/full_ft.yaml:10 (F65) | cited in text |
| optimizer | adamw_torch | - | optim | conf/lora.yaml:10 (F72) | cited in text |
| learning-rate schedule | linear | - | optim | conf/lora.yaml:13 (F75) | cited in text |
| warm-up | 0.06 | - | optim | conf/lora.yaml:14 (F76) | cited in text |
| weight decay | 0.1 | - | optim | conf/full_ft.yaml:6 (F62) | cited in text |
| dataset | glue | - | - | run_glue.py:10 (F33) | cited in text |
| dataset version | sst2 | - | - | run_glue.py:10 (F34) | cited in text |
| training samples | 67349, | - | - | train_lora_s1.log:3 (F58) | cited in text |
| validation samples | 872 | - | - | train_lora_s1.log:3 (F59) | cited in text |
| CUDA version | 12.1 | - | - | train_lora_s1.log:1 (F56) | in text (untagged) |
| hardware | NVIDIA A100-SXM4-40GB | - | - | train_lora_s1.log:2 (F57) | cited in text |
| number of GPUs / devices | 4 | - | - | train_lora_s1.log:2 (F36) | cited in text |
| numeric precision | true | - | training | conf/lora.yaml:20 (F81) | cited in text |
| Python version | 3.10.13 | - | - | train_lora_s1.log:1 (F52) | cited in text |
| software (transformers) | 4.40.0 | - | - | train_lora_s1.log:1 (F54) | cited in text |
| software (peft) | 0.10.0 | - | - | train_lora_s1.log:1 (F55) | cited in text |
| PyTorch version | 2.2.1 | - | - | train_lora_s1.log:1 (F53) | cited in text |
| model / architecture | roberta-large | - | model | conf/full_ft.yaml:3 (F60) | cited in text |
| code version / commit | bcdcba79d07bc864c1c254ccfcedcce55bcc9a8c | - | - | run_glue.py:10 (F32) | cited in text; other values: README.md:2=4be1d0e; conf/lora.yaml:3=main |
| random seed | $SEED | - | - | launch.sh:3 (F11) | cited in text; other values: results.csv:2=1; results.csv:3=2; results.csv:4=3 |
| random seed | 1 | - | val | README.md:2 (F2) | cited in text |



## 4.3 Compute and software

Each run used 4 GPUs (torchrun, 4 processes per node) of type NVIDIA A100-SXM4-40GB, with Python 3.10.13, PyTorch 2.2.1, transformers 4.40.0, peft 0.10.0 and CUDA 12.1. Total compute was about 40 GPU-hours.

## 4.4 Seeds, repetitions and statistics

Every method was run with seeds 1, 2 and 3 [AUTHOR TO CONFIRM: C1 launch.sh passes --seed $SEED from the loop; results.csv lists the seeds]; results are the mean over the three seeds. No significance test or confidence interval was computed [TO CONFIRM: Report standard deviation over seeds and a paired test or bootstrap CI for LoRA vs full fine-tuning?].

## 4.5 Reproducibility

Code commit 4be1d0e. Commands, run for SEED in 1 2 3:

```
torchrun --nproc_per_node 4 run_glue.py --config conf/lora.yaml --seed $SEED --output_dir out/lora_s$SEED
torchrun --nproc_per_node 4 run_glue.py --config conf/full_ft.yaml --seed $SEED --output_dir out/full_s$SEED
```

Data are public through the GLUE benchmark [TO CONFIRM: cite the GLUE/SST-2 licence and the Hugging Face dataset page].

## 4.6 Limitations

- Model selection and reporting both use the 872-sentence validation split, so the reported accuracy is optimistically biased.
- Only one model (roberta-large) and one task (SST-2) were tested.
- Only 3 seeds per method; the baseline used 10 epochs against 20 for LoRA, so the budgets differ.
