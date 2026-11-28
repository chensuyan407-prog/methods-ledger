# Review — dev_wetlab_mtt

status: **success** — all checks pass; 11 items await author confirmation

facts extracted 65, cited 41; conflicts 2; questions 11; preview: pymupdf story, 2 pages

## Coverage
- E_steps (steps, required): **covered** — ordered procedure (input -> operation -> output per step)
- E_materials (data, required): **covered** — materials/samples with source and lot
- E_conditions (params, required): **covered** — operating conditions with units
- E_instrument (setup, required): **covered** — instruments (manufacturer, model)
- E_software (setup, required): **covered** — software and versions
- E_repeats (control, required): **covered** — number of repetitions / replicates and how results are aggregated
- E_controls (control, required): **covered** — control groups (positive/negative/vehicle)
- E_metric (control, required): **covered** — evaluation metrics / measured outcomes
- E_stats (control, recommended): **covered** — statistical test / uncertainty estimate
- E_data_access (repro, recommended): **marked_gap** — data availability / access
- E_limits (repro, required): **covered** — limitations tied to concrete failure scenarios

## Review notes (automatic source mapping)

- numbers/versions in the text: 41; matched by tag 34, auto-mapped 0, CALC/SRC 6, unsourced 0
- **N02 names not in the materials** (1):
  - l.18: name 'IC50' does not occur in any material file

| line | token | fact | source | how |
|---|---|---|---|---|
| 5 | `12` | F8 |  | tag |
| 5 | `5,000` | F17 |  | tag |
| 5 | `96` | F17 |  | tag |
| 5 | `100` | F17 |  | tag |
| 5 | `10%` | F17 |  | tag |
| 6 | `24` | F18 |  | tag |
| 6 | `37` | F18 |  | tag |
| 6 | `5%` | F18 |  | tag |
| 7 | `0` | F19 |  | tag |
| 7 | `1` | F19 |  | tag |
| 7 | `5` | F19 |  | tag |
| 7 | `10` | F19 |  | tag |
| 7 | `50` | F19 |  | tag |
| 7 | `100` | F19 |  | tag |
| 7 | `0.1%` | F19 |  | tag |
| 7 | `48` | F20 |  | tag |
| 8 | `10` | SRC |  | source-line |
| 8 | `5` | SRC |  | source-line |
| 8 | `37` | SRC |  | source-line |
| 8 | `45` | F10 |  | tag |
| 9 | `100` | F22 |  | tag |
| 9 | `10` | F22 |  | tag |
| 10 | `570` | F23 |  | tag |
| 10 | `630` | F23 |  | tag |
| 14 | `3.11` | F31 |  | tag |
| 14 | `570` | F33 |  | tag |
| 14 | `630` | F36 |  | tag |
| 14 | `8.5` | SRC |  | source-line |
| 14 | `25` | F41 |  | tag |
| 18 | `0.1%` | SRC |  | source-line |
| 18 | `1` | SRC |  | source-line |
| 18 | `3` | F50 |  | tag |
| 18 | `0.05` | F2 |  | tag |
| 18 | `3.0` | F4 |  | tag |
| 18 | `1` | F4 |  | tag |
| 18 | `7` | F5 |  | tag |
| 18 | `4.3.1` | F3 |  | version-tag |
| 26 | `12` | F8 |  | tag |
| 26 | `45` | F10 |  | tag |
| 26 | `30` | F21 |  | tag |
| 26 | `3` | F50 |  | tag |

## Check items
- WARN N02 l.18: name 'IC50' does not occur in any material file
- WARN T05 l.26: cited F13 (lot = ATCC CCL-2) but its value is not in the sentence
