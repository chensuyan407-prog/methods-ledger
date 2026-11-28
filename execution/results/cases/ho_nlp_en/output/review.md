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
