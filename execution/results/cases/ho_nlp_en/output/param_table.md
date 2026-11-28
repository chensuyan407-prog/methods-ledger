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
