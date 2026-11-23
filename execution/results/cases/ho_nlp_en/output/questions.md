# Questions for the author

- [ ] **G1** (gap, control) How many independent runs/replicates per condition, and is mean ± SD/SE or a single run reported?
- [ ] **G2** (gap, control) Which baselines (implementation + version) were compared, and were they trained/tuned under the same budget and data?
- [ ] **G3** (gap, control) Define each metric (and on which split / at which checkpoint it is computed).
- [ ] **G4** (gap, control) Which statistical test or uncertainty estimate supports comparisons (test, alpha, correction)?
- [ ] **G5** (gap, repro) How can readers obtain the data (URL/DOI, license, access restrictions)?
- [ ] **G6** (gap, repro) Which conditions were not tested (data, scale, hardware, settings) and where is the method expected to fail?
- [ ] **C1** (conflict, params) batch size differs between sources: 32 (train_lora_s1.log:5); 16 (conf/full_ft.yaml:8). Which value did the reported run use? — facts F41, F63, F77
- [ ] **C2** (conflict, params) gradient accumulation steps differs between sources: 1 (train_lora_s1.log:5); 2 (conf/lora.yaml:17). Which value did the reported run use? — facts F42, F78
- [ ] **Q-u14c** (draft_confirm) conf/lora.yaml sets per-device batch 16 with accumulation 2; the log shows 32 and 1. Both give an effective batch of 128 on 4 GPUs, but which setting was used for seeds 2 and 3?
- [ ] **Q-u15c** (draft_confirm) batch size 16 here is the baseline config value; the LoRA log shows 32, the LoRA config 16
- [ ] **Q-u21c** (draft_confirm) C1 launch.sh passes --seed $SEED from the loop; results.csv lists the seeds
- [ ] **Q-u22** (draft_gap) Report standard deviation over seeds and a paired test or bootstrap CI for LoRA vs full fine-tuning?
- [ ] **Q-u27** (draft_gap) cite the GLUE/SST-2 licence and the Hugging Face dataset page
