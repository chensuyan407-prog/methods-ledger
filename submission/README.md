# methods-ledger 0.3.0 — Methods / Experiments section writer with source checking

Skill for 写作09｜方法与实验章节写作. It turns scattered research materials (configs, code, run logs, environment
files, data cards, notebooks, tables, lab notes, old drafts) into an editable Methods/Experiments chapter in which
**every number, version, model/GPU name and command traces to a file:line**. Conflicts between sources and missing
elements are marked for the author instead of being smoothed over.

Problem it solves: a fluent methods section written from memory or a single config file usually (a) reports the config
value instead of the value the run used, (b) silently picks one of two conflicting values, (c) leaves out seeds, split
seeds, dataset versions, baseline budgets or repetitions, (d) adds plausible defaults that appear nowhere in the
materials, and (e) ends with generic limitations. A grep for "is this number somewhere in my files" misses most of
these (see Results). methods-ledger separates the work: scripts find facts and check; the agent writes.

## Files

| path | purpose |
|---|---|
| `SKILL.md` | entry file for the agent: workflow, tag syntax, writing rules, check codes, outputs, failure handling |
| `scripts/ml_extract.py` | step 1: read materials, extract facts with provenance, detect conflicts, gaps, pipeline stages; writes `work/facts.md` |
| `scripts/ml_build.py` | step 2: check `work/draft.md` against the facts, render outputs, write `result.json` |
| `scripts/ml_common.py` | reading (UTF-8/UTF-16/GB18030, mojibake repair, DOCX, PDF), number/version parsing, key normalisation |
| `rules/keys.json` | 109 canonical parameter keys with aliases (en/zh), category, labels (en/zh) |
| `rules/checklist.json` | 22 chapter elements in 6 groups, per domain profile (ml, wetlab, simulation, stats, generic), draft patterns, author questions (en/zh), boilerplate-limitation phrases |
| `templates/` | draft skeletons (zh/en), `agent.json` template, author question checklist |
| `examples/minimal_example.md` | a complete small call with inputs, commands and illustrative output |

Requirements: Python ≥ 3.8, standard library only. Optional: PyMuPDF ≥ 1.23 (PDF materials; PDF/PNG preview of the chapter).
Install: copy this folder (e.g. to `/skills/weekly-skill`). No network access is needed.

## Interface

Input: `case.json` (any of `case_id`, `task`/`instruction`, `output_contract` as dict, list of names, list of
`{name, description}` or JSON schema) + `task.md` + any material files in the same directory tree.

```bash
python scripts/ml_extract.py --case /input/case.json --out /app/output --work /app/work [--lang zh|en] [--profile ml|wetlab|simulation|stats|generic]
# agent reads work/facts.md, writes work/draft.md (+ optional work/agent.json)
python scripts/ml_build.py --work /app/work --out /app/output     # exit 0 once draft.md has text; FLAGs are marked, not blocking
```

### What extraction recognises

| source | extracted |
|---|---|
| YAML (subset parser, line numbers), JSON, TOML, INI/cfg/.env, GROMACS mdp, VASP INCAR/KPOINTS, LAMMPS input (timestep, run, fix nvt/npt temp/press, velocity seed, pair_style) | every key path → canonical key via aliases; generic keys (`version`, `size`, `n`, `alpha`, `sample`…) only with a domain word in the path or file name |
| Python/R/shell/notebooks | argparse defaults (marked *argparse default*, dropped from conflicts when a CLI/config/log sets the key), constants, keyword arguments (`test_size`, `random_state` in split calls → *split seed*), seed calls, optimizers, schedulers, `from_pretrained`, `load_dataset` (+ config/revision), losses, metrics, statistical tests, `library(x) # version`, notebook outputs |
| logs | key=value / key: value / dict entries; values that change during a run become *series* (first/last/min/max), never conflicts; commands (also after timestamps) → pipeline stages + CLI flags; every numeric line as a citable line fact |
| requirements / conda | pinned versions (ranges reported as a reproducibility gap) |
| CSV/TSV | cells with row labels (≤ 80 rows) or column summaries |
| notes, data cards, drafts (md/txt/docx/pdf) | `key: value` lines, parameter words followed by a number (only separators between them, so "Seed HeLa cells at 5,000" is not a seed), every line with a number |
| any file | GPU/CPU models and counts, software versions, commits, dataset snapshot dates, split counts/ratios, durations with their object (`MTT 30 min`), replicate counts (`three independent experiments`, `只跑了一条`), lot/ATCC numbers, system sizes, wall time, imputation counts |

Conflict = same canonical key (+ sub-key such as the incubated object, + val/test/baseline scope) with incompatible values
in different files. Not conflicts: 1e-3 vs 0.001, `2.1.2+cu121` vs `2.1.2`, version ranges, overridden code defaults,
logged series, shell placeholders (`$SEED`), per-row table values (one seed per row), sibling config files of another run
(e.g. a baseline config whose keys differ from the run that was logged). A precedence guess (log > CLI > env > config > code
default > notes) is shown but never applied silently.

### Draft tags (full table in SKILL.md)

`[[F12]]`, `[[@file:line]]`, `[[@file:line#key]]`, `[[SRC: file:line]]`, `[[CALC: expr = value | F…]]`, `[[CONFIRM: …]]`,
`[[GAP: …]]`, `[[PARAM_TABLE]]`. A tag covers the clause since the previous tag; numbers in that clause must be values of
the tagged facts (T02 otherwise), numbers in untagged text must still trace somewhere (N01 flag / N03 warn).
Since 0.3.0 tag slips never block: `[F12]`, `【F12】`, `(F12)`, `[[f12; F13]]` are normalised; unknown ids (T01), malformed
tags (T03) and untagged numbers are warnings and the number is auto-aligned to the matching fact; a valid tag that points
at a different value stays a T02 flag. Flag-level findings (N01, N02, C01, M01, P02, K01, L02, T02, K10/K11) no longer make
the run `partial` or exit 1: unsourced numbers/names get an inline 【待核实】/[UNVERIFIED] marker, unmarked conflicts a
【待作者确认】 marker, the rest an appended "open items for the author" list, and all of them go to `questions.md`.

### Outputs and result.json fields

| field / file | content |
|---|---|
| `case_id`, `status`, `status_reason` | `success` = chapter built (flags marked in the text, open author questions listed); `partial` = no draft text / provisional; `failed` = nothing readable |
| contract fields | filled by name: chapter text, parameter rows, fact map, questions, conflicts, uncertainty, change records, repro checklist, limitations, datasets, controls, setup, steps, summary, files; anything else via `agent.json` `fields` (unmapped fields are `null` and listed in `uncertainty`) |
| `sources` | every material file: class, SHA-256, bytes, number of facts, reading problems |
| `checks` | flag (`fail`)/warn counts, flag items, `flagged_in_text`, `blocking`, coverage per element (`covered` / `marked_gap` / `missing`), limitation stats, pipeline stages described |
| `needs_confirmation` | gaps (G#), conflicts (C#, with the agent's choice if any), every GAP/CONFIRM written in the draft |
| `parameters` | name (en/zh), canonical key, value, unit, applies to, source file:line, fact id, source kind, status (cited / conflict / not used; other values) |
| `change_records` | sentence diff against an old draft found among the materials; build history (fails/warns per build) |
| `repro_checklist` | code version, commands, Python/PyTorch/CUDA/other software, hardware, seeds, dataset + version, data access, container: found? values, sources, cited? |
| files | `methods.md`, `methods_annotated.md/.html`, `methods.docx`, `methods_preview.pdf/.png`, `param_table.csv/.md`, `fact_map.json`, `questions.md`, `check_report.json`, `review.md` |

## Method

1. **Extract with provenance** (deterministic, ~0.05 s per case): typed parsers per file class (above) produce facts
   `{id, file, line, kind, key, path, canonical key, category, value, numbers, scope}`.
2. **Align and compare**: canonical keys across files → conflict clusters with compatibility rules; checklist elements per
   detected domain profile → gaps with ready-made author questions in the target language.
3. **Agent writes** the chapter with clause-level tags (stable `@file:line` anchors are accepted, so a draft survives
   re-extraction).
4. **Check** (deterministic): clause-level number attribution (T02 wrong value for the cited fact, N01 no source anywhere),
   versions and digit-bearing names (a name that differs from a material name only in its digits fails), commands must exist
   in the materials (P02), arithmetic of derived numbers (CALC), conflict marking (C01), element coverage (K01/K02), unused
   material facts (K03), concrete limitations (L01/L02), placeholders (M01), val/test crossover (X01), unsupported
   significance (S01), pipeline stages described (P01).
5. **Render**: clean chapter, annotated chapter, sourced parameter table (generated from facts, so text and table cannot
   disagree), DOCX and PDF/PNG preview, question checklist, result.json.

## Results (author-written cases; no platform case and no model run is part of these numbers)

Five cases written by the author: 3 development cases (Chinese ML text classification, English wet-lab MTT assay,
Chinese LAMMPS water simulation with a GBK-encoded note) and 2 held-out cases written after the code freeze
(`tests/FREEZE_v0.1.0.sha256`): English LoRA/GLUE study with a baseline and 3 seeds, Chinese survey study in R.
Gold drafts were written by the author with the Skill workflow. Planted defects are deterministic mutations of the gold
drafts (`tests/run_eval.py`).

| measure | dev (3 cases, final code) | held-out (2) at freeze | held-out after post-freeze fixes | all 5, final |
|---|---:|---:|---:|---:|
| expected facts extracted | 73/80 | 36/47 | 44/47 | 117/127 |
| real conflicts found | 3/3 | 2/3 | 3/3 | 6/6 |
| false conflicts | 0 | 3 | 0 | 0 |
| expected gaps found | 8/8 | 4/4 | 4/4 | 12/12 |
| gold drafts without FAIL | 3/3 | 0/2 | 2/2 | 5/5 |
| planted defects caught (FAIL) | 58/60 | 39/40 | 39/40 | 97/100 |
| baseline B1: grep every number/version in the materials | 35/60 | 17/40 | 17/40 | 52/100 |
| baseline B2: checklist/coverage only | 21/60 | 14/40 | 14/40 | 35/100 |
| robustness checks | | | | 13/13 |

Planted defects by type (all 5 cases, final): wrong value 29/29 (grep 25), invented number 9/10 (grep 10),
unmarked conflict 5/5 (grep 1), missing element 30/31 (checklist-only 30), boilerplate limitations 5/5, fabricated command
2/2 (grep 1), wrong version 4/4 (grep 4), wrong name 5/5 (grep 1), placeholder 5/5 (grep 1), wrong citation 3/4 (grep 0).
The first development run (before fixing the evaluation harness and an exemption bug) caught 44/60. Testing the minimal example after the evaluation showed that a wrong value equal to a fact tagged on
another clause only warned and that a number occurring inside a longer number in the materials only warned; both now fail.

Held-out at freeze, what went wrong and was fixed afterwards (the held-out set is therefore no longer clean; both numbers
are kept): `$SEED` shell placeholder and per-seed result rows reported as seed conflicts; a baseline config
(`conf/full_ft.yaml`) reported as conflicting with the main run; survey counts (`raw responses`, `analytic sample`),
`alpha <- 0.05` in R and the imputation count `m = 20` vs `m=10` were not extracted; the checklist asked survey studies for
repetitions; "revision" was not accepted as a dataset version word. The gold drafts' remaining fails at freeze were mostly
the false conflicts plus one real error in the author's own gold (an uncited seed number), which the checker caught.

Fresh-directory run (`execution/results/fresh_run`): only `submission/` copied to a new temp folder, a new case
(XGBoost credit model: notebook, params JSON, metrics CSV) → extract 24 facts, draft, build: 0 fails, 17 author questions,
0.5 s. It exposed that notebook line numbers referred to the raw JSON; fixed (facts and checker use the same cell text).

## Limits (concrete failure cases)

- **Facts only in prose are lines, not keys**: "Incubate 24 h at 37 °C" is a citable line but 37 °C is not a separate
  temperature fact; conflicts between two prose-only values are found only for durations, replicate counts and parameter
  words followed by a number. Misses in the evaluation: incubation temperature, MTT concentration, volumes, seeding density,
  `C=1.0` in a baseline config, the cutoff inside a LAMMPS `pair_style` line, `n_runs` inferred from a 3-iteration shell loop.
- **Conflict semantics are heuristic**: a value repeated in two configs of different runs is only recognised as "another
  run" when the other config matches the logged run; with no log both configs are reported as a conflict.
- **Anchors cite the whole line**: `[[@analysis.R:5]]` also cites `m = 20` on that line and can trigger C01; use `#key`.
- **Clause attribution is positional**: a number counts as covered by the next tag after it; a value of a fact tagged on
  another clause fails (T02), except small integers ≤ 3. One of four wrong-citation mutations was not caught because the
  wrongly cited line (a `load_dataset` call) carries no number that could disagree.
- **0.37 vs 37 %**: percent equivalence is used only when one side is written as a percentage; rounding equivalence can still
  match an invented value to a nearby material value (1 invented-number mutation passed as a warning).
- **Coverage is pattern-based**: an element counts as covered when a tagged sentence matches its pattern, not when the
  sentence is complete; one "instrument removed" mutation still matched a GAP sentence mentioning the reader.
- **Not handled**: XLSX (ask for CSV), scanned PDFs (no OCR), images, LaTeX table parsing, checking that prose *describes*
  a step correctly (only that its numbers and names are sourced). Profiles: ml, wetlab, simulation, stats, generic.
- **Status semantics**: `success` means a chapter was built and every flagged item is marked in it, not that the science is
  complete or that no check fired; read `checks.fail_items` and `questions.md`.

## Self-check

`python ../tests/run_eval.py` (from the bundle) reruns extraction scoring, gold builds, 100 mutations, baselines and 13
robustness checks in ~20 s. `python scripts/ml_build.py` on the agent's draft is the per-case self-check; `review.md` lists
every finding.

Maintainer: chensuyan407 (GitHub chensuyan407-prog). Licence: MIT. Version 0.3.0 (2026-11-27; 0.1.0 frozen 2026-11-23).
