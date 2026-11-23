import argparse
from datasets import load_dataset
from transformers import set_seed
p = argparse.ArgumentParser()
p.add_argument("--config")
p.add_argument("--seed", type=int, default=0)
p.add_argument("--output_dir")
args = p.parse_args()
set_seed(args.seed)
raw = load_dataset("glue", "sst2", revision="bcdcba79d07bc864c1c254ccfcedcce55bcc9a8c")
# GLUE test labels are hidden: we report on the official validation split
