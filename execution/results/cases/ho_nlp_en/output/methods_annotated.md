# 4 Experimental Setup

## 4.1 Procedure

1. Data loading: GLUE SST-2 was loaded with `load_dataset("glue", "sst2")` at dataset revision bcdcba79d07bc864c1c254ccfcedcce55bcc9a8c <sup>[F32: run_glue.py:10; F33: run_glue.py:10; F34: run_glue.py:10]</sup>; output: 67349 training and 872 validation sentences <sup>[F37: train_lora_s1.log:3; F38: train_lora_s1.log:3; F48: train_lora_s1.log:3; F58: train_lora_s1.log:3; F59: train_lora_s1.log:3]</sup>.
2. LoRA fine-tuning: roberta-large <sup>[F66: conf/lora.yaml:2]</sup> was adapted with LoRA on the query and value projections <sup>[F71: conf/lora.yaml:8]</sup>, training 1,838,082 of 357,199,876 parameters <sup>[F39: train_lora_s1.log:4; F40: train_lora_s1.log:4; F49: train_lora_s1.log:4]</sup>.
3. Baseline: full fine-tuning of the same roberta-large model <sup>[F60: conf/full_ft.yaml:3]</sup> with its own configuration <sup>[F13: launch.sh:4; F14: launch.sh:4; F15: launch.sh:4; F16: launch.sh:4; F17: launch.sh:4]</sup>.
4. Evaluation: accuracy on the official SST-2 validation split, because GLUE test labels are hidden <sup>[run_glue.py:11]</sup>; the best epoch was selected on the same split (epoch 14 in the logged LoRA run) <sup>[F45: train_lora_s1.log:6; F51: train_lora_s1.log:6]</sup>.

## 4.2 Hyperparameters

LoRA used rank r = 8 <sup>[F68: conf/lora.yaml:5]</sup>, alpha = 16 <sup>[F69: conf/lora.yaml:6]</sup> and dropout 0.05 <sup>[F70: conf/lora.yaml:7]</sup>. Optimisation used adamw_torch <sup>[F72: conf/lora.yaml:10]</sup> with learning rate 4e-4 <sup>[F43: train_lora_s1.log:5]</sup>, weight decay 0.1 <sup>[F74: conf/lora.yaml:12]</sup>, a linear schedule with warm-up ratio 0.06 <sup>[F75: conf/lora.yaml:13; F76: conf/lora.yaml:14]</sup>, 20 epochs <sup>[F44: train_lora_s1.log:5]</sup>, maximum sequence length 128 <sup>[F80: conf/lora.yaml:19]</sup> and bf16 <sup>[F81: conf/lora.yaml:20]</sup>. The logged run used a per-device batch size of 32 without gradient accumulation <sup>[F41: train_lora_s1.log:5; F42: train_lora_s1.log:5; F43: train_lora_s1.log:5; F44: train_lora_s1.log:5; F50: train_lora_s1.log:5]</sup> [AUTHOR TO CONFIRM: conf/lora.yaml sets per-device batch 16 with accumulation 2; the log shows 32 and 1. Both give an effective batch of 128 on 4 GPUs, but which setting was used for seeds 2 and 3?].
The full fine-tuning baseline used learning rate 1.0e-5 <sup>[F61: conf/full_ft.yaml:5]</sup>, weight decay 0.1 <sup>[F62: conf/full_ft.yaml:6]</sup>, per-device batch size 16 <sup>[F63: conf/full_ft.yaml:8]</sup> [AUTHOR TO CONFIRM: batch size 16 here is the baseline config value; the LoRA log shows 32, the LoRA config 16] for 10 epochs <sup>[F64: conf/full_ft.yaml:9]</sup> at sequence length 128 <sup>[F65: conf/full_ft.yaml:10]</sup>.



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
| hardware (gpu) | NVIDIA A100-SXM4-40GB | - | - | train_lora_s1.log:2 (F57) | cited in text |
| number of GPUs / devices | 4 | - | - | train_lora_s1.log:2 (F36) | cited in text |
| numeric precision | true | - | training | conf/lora.yaml:20 (F81) | cited in text |
| Python version | 3.10.13 | - | - | train_lora_s1.log:1 (F52) | cited in text |
| software (transformers) | 4.40.0 | - | - | train_lora_s1.log:1 (F54) | cited in text |
| software (peft) | 0.10.0 | - | - | train_lora_s1.log:1 (F55) | cited in text |
| PyTorch version | 2.2.1 | - | - | train_lora_s1.log:1 (F53) | cited in text |
| model / architecture | roberta-large | - | model | conf/full_ft.yaml:3 (F60) | cited in text |
| code version / commit | bcdcba79d07bc864c1c254ccfcedcce55bcc9a8c | - | - | run_glue.py:10 (F32) | cited in text; other values: README.md:2=4be1d0e; conf/lora.yaml:3=main |
| random seed | $SEED | - | - | launch.sh:3 (F11) | cited in text; other values: run_glue.py:6=0 |
| random seed | 1 | - | val | README.md:2 (F2) | cited in text |
| random seed | 1 | - | lora | results.csv:2 (F19) | cited in text; other values: results.csv:3=2; results.csv:4=3 |
| random seed | 1 | - | full_ft | results.csv:5 (F25) | not used in text; other values: results.csv:6=2; results.csv:7=3 |



## 4.3 Compute and software

Each run used 4 GPUs (torchrun, 4 processes per node) <sup>[F7: launch.sh:3; F8: launch.sh:3; F9: launch.sh:3; F10: launch.sh:3; F11: launch.sh:3; F12: launch.sh:3]</sup> of type NVIDIA A100-SXM4-40GB <sup>[F36: train_lora_s1.log:2; F47: train_lora_s1.log:2; F57: train_lora_s1.log:2]</sup>, with Python 3.10.13, PyTorch 2.2.1, transformers 4.40.0, peft 0.10.0 and CUDA 12.1 <sup>[F35: train_lora_s1.log:1; F46: train_lora_s1.log:1; F52: train_lora_s1.log:1; F53: train_lora_s1.log:1; F54: train_lora_s1.log:1; F55: train_lora_s1.log:1]</sup>. Total compute was about 40 GPU-hours <sup>[F4: README.md:3; F5: README.md:3]</sup>.

## 4.4 Seeds, repetitions and statistics

Every method was run with seeds 1, 2 and 3 <sup>[F19: results.csv:2; F20: results.csv:2; F21: results.csv:3; F22: results.csv:3; F23: results.csv:4; F24: results.csv:4]</sup> [AUTHOR TO CONFIRM: C1 launch.sh passes --seed $SEED from the loop; results.csv lists the seeds]; results are the mean over the three seeds <sup>[F1: README.md:2; F2: README.md:2; F3: README.md:2; F6: README.md:2]</sup>. No significance test or confidence interval was computed [TO CONFIRM: Report standard deviation over seeds and a paired test or bootstrap CI for LoRA vs full fine-tuning?].

## 4.5 Reproducibility

Code commit 4be1d0e <sup>[F6: README.md:2]</sup>. Commands, run for SEED in 1 2 3 <sup>[launch.sh:2]</sup>:

```
torchrun --nproc_per_node 4 run_glue.py --config conf/lora.yaml --seed $SEED --output_dir out/lora_s$SEED
torchrun --nproc_per_node 4 run_glue.py --config conf/full_ft.yaml --seed $SEED --output_dir out/full_s$SEED
```

Data are public through the GLUE benchmark [TO CONFIRM: cite the GLUE/SST-2 licence and the Hugging Face dataset page].

## 4.6 Limitations

- Model selection and reporting both use the 872-sentence validation split <sup>[F37: train_lora_s1.log:3; F38: train_lora_s1.log:3; F48: train_lora_s1.log:3; F58: train_lora_s1.log:3; F59: train_lora_s1.log:3]</sup>, so the reported accuracy is optimistically biased.
- Only one model (roberta-large) <sup>[F66: conf/lora.yaml:2]</sup> and one task (SST-2) <sup>[F32: run_glue.py:10; F33: run_glue.py:10; F34: run_glue.py:10]</sup> were tested.
- Only 3 seeds per method <sup>[F19: results.csv:2; F20: results.csv:2; F21: results.csv:3; F22: results.csv:3; F23: results.csv:4; F24: results.csv:4]</sup>; the baseline used 10 epochs against 20 for LoRA <sup>[F64: conf/full_ft.yaml:9; F79: conf/lora.yaml:18]</sup>, so the budgets differ.

## Review notes (automatic source mapping)

- numbers/versions in the text: 38; matched by tag 31, auto-mapped 0, CALC/SRC 3, unsourced 0
- **X01 condition crossover (val/test/stage)** (3):
  - l.38: F20 comes from the test context (results.csv:2) but the sentence talks about val
  - l.38: F22 comes from the test context (results.csv:3) but the sentence talks about val
  - l.38: F24 comes from the test context (results.csv:4) but the sentence talks about val

| line | token | fact | source | how |
|---|---|---|---|---|
| 5 | `67349` | F37 |  | tag |
| 5 | `872` | F38 |  | tag |
| 6 | `1,838,082` | F39 |  | tag |
| 6 | `357,199,876` | F40 |  | tag |
| 8 | `14` | F51 |  | tag |
| 12 | `8` | F68 |  | tag |
| 12 | `16` | F69 |  | tag |
| 12 | `0.05` | F70 |  | tag |
| 12 | `4e-4` | F43 |  | tag |
| 12 | `0.1` | F74 |  | tag |
| 12 | `0.06` | F76 |  | tag |
| 12 | `20` | F44 |  | tag |
| 12 | `128` | F80 |  | tag |
| 12 | `32` | F41 |  | tag |
| 12 | `1.0e-5` | F61 |  | tag |
| 12 | `0.1` | F62 |  | tag |
| 12 | `16` | F63 |  | tag |
| 12 | `10` | F64 |  | tag |
| 12 | `128` | F65 |  | tag |
| 19 | `4` | F7 |  | tag |
| 19 | `4` | F7 |  | tag |
| 19 | `12.1` | F46 |  | tag |
| 19 | `3.10.13` | F35 |  | version-tag |
| 19 | `2.2.1` | F46 |  | version-tag |
| 19 | `4.40.0` | F46 |  | version-tag |
| 19 | `0.10.0` | F46 |  | version-tag |
| 19 | `40` | F4 |  | tag |
| 23 | `1` | F19 |  | tag |
| 23 | `2` | F21 |  | tag |
| 23 | `3` | F23 |  | tag |
| 27 | `4` | F6 |  | tag |
| 27 | `1` | SRC |  | source-line |
| 27 | `2` | SRC |  | source-line |
| 27 | `3` | SRC |  | source-line |
| 38 | `872` | F38 |  | tag |
| 38 | `3` | F23 |  | tag |
| 38 | `10` | F64 |  | tag |
| 38 | `20` | F79 |  | tag |
