#!/bin/bash
for SEED in 1 2 3; do
  torchrun --nproc_per_node 4 run_glue.py --config conf/lora.yaml --seed $SEED --output_dir out/lora_s$SEED
  torchrun --nproc_per_node 4 run_glue.py --config conf/full_ft.yaml --seed $SEED --output_dir out/full_s$SEED
done
