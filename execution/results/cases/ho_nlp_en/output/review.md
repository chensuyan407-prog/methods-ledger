# Review — ho_nlp_sst2

status: **success** — all checks pass; 13 items await author confirmation

facts extracted 83, cited 68; conflicts 2; questions 13; preview: pymupdf story, 3 pages

## Coverage
- E_steps (steps, required): **covered** — ordered procedure (input -> operation -> output per step)
- E_dataset (data, required): **covered** — dataset name and source
- E_dataset_version (data, required): **covered** — dataset version / release / snapshot date
- E_split (data, required): **covered** — split sizes/ratios and how they were drawn
- E_preproc (data, recommended): **missing** — preprocessing / filtering
- E_model (control, recommended): **covered** — model / architecture and initialisation
- E_hparams (params, required): **covered** — optimiser, learning rate, batch size, training length
- E_hardware (setup, required): **covered** — hardware (device type and count)
- E_software (setup, required): **covered** — software and versions
- E_seed (repro, required): **covered** — random seed(s)
- E_repeats (control, required): **covered** — number of repetitions / replicates and how results are aggregated
- E_baseline (control, required): **covered** — baselines with versions and same-budget conditions
- E_metric (control, required): **covered** — evaluation metrics / measured outcomes
- E_stats (control, recommended): **marked_gap** — statistical test / uncertainty estimate
- E_code (repro, required): **covered** — code version and run commands
- E_data_access (repro, recommended): **missing** — data availability / access
- E_limits (repro, required): **covered** — limitations tied to concrete failure scenarios

## Check items
- WARN T05 l.6: cited F71 (lora.target_modules = [query, value]) but its value is not in the sentence
- WARN T05 l.7: cited F15 (config = conf/full_ft.yaml) but its value is not in the sentence
- WARN T05 l.7: cited F16 (seed = $SEED) but its value is not in the sentence
- WARN T05 l.7: cited F17 (output_dir = out/full_s$SEED) but its value is not in the sentence
- WARN T05 l.19: cited F10 (config = conf/lora.yaml) but its value is not in the sentence
- WARN T05 l.19: cited F11 (seed = $SEED) but its value is not in the sentence
- WARN T05 l.19: cited F12 (output_dir = out/lora_s$SEED) but its value is not in the sentence
- WARN T05 l.38: cited F32 (revision = bcdcba79d07bc864c1c254ccfcedcc) but its value is not in the sentence
- WARN T05 l.38: cited F33 (dataset = glue) but its value is not in the sentence
- WARN X01 l.38: F20 comes from the test context (results.csv:2) but the sentence talks about val
- WARN X01 l.38: F22 comes from the test context (results.csv:3) but the sentence talks about val
- WARN X01 l.38: F24 comes from the test context (results.csv:4) but the sentence talks about val
- WARN K02 l.None: element not covered and not marked as a gap: preprocessing / filtering -> write it with sources or add [[GAP: Describe preprocessing and filtering (what was removed and h...]]
- WARN K02 l.None: element not covered and not marked as a gap: data availability / access -> write it with sources or add [[GAP: How can readers obtain the data (URL/DOI, license, access re...]]
