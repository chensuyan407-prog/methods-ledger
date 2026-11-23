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

## Check items
- WARN N02 l.18: name 'IC50' does not occur in any material file
- WARN T05 l.26: cited F13 (lot = ATCC CCL-2) but its value is not in the sentence
