---
name: methods-ledger
description: Writes or completes the Methods / Experiments section (方法与实验章节) of a paper, thesis or report from scattered research materials - configs (YAML/JSON/TOML/INI/mdp/INCAR/LAMMPS), code (argparse defaults, seeds, splits, optimizers), run logs, requirements/conda files, data cards, CSV/XLSX tables, lab notes, old drafts (md/txt/docx/pdf). A script extracts every parameter, setting, dataset/split, baseline and reproducibility item with file:line provenance, flags conflicting values and missing elements, and gives the agent a required-section list and the output contract. The agent then writes the chapter in normal academic prose; a second script maps every number, version and name in it back to the materials automatically, catches unsourced numbers, values from another condition (val vs test, baseline vs proposed), invented commands and GPUs, marks conflicts and gaps for the author, and builds an editable chapter (Markdown + DOCX + PDF/PNG preview), a sourced parameter table, a fact map, an author question list and result.json. Use for 写方法章节, 实验设置, 参数表, 复现说明, methods section, experimental setup, reproducibility checklist. Do not use for literature reviews, results/discussion interpretation or language-only polishing.
---

# methods-ledger (v0.1.2)

You write the chapter as a normal academic text; the scripts find the facts and check, without any special markup, that the
chapter says only what the materials say. Python 3.8+ standard library (PyMuPDF optional: PDF input and PDF/PNG preview).
`SKILL_DIR` = directory of this file (`/skills/weekly-skill`). Use `python3` (or `python` if that is the only one).
Defaults: `/input/case.json` (else `./input/case.json`), `/app/work`, `/app/output` - the arguments below can be omitted there.

## Workflow (a provisional result.json exists after step 1)

1. **Extract** (seconds):
   ```bash
   python3 $SKILL_DIR/scripts/ml_extract.py --case /input/case.json --out /app/output --work /app/work
   ```
   Prints case_id, contract fields, language (zh/en from the task; `--lang` overrides), domain profile, each file with its
   role (primary materials declared in case.json first), class and fact count, declared-but-missing files and conflicts.
   Writes `work/facts.md` (read this), `work/facts.json`, `work/draft.md` (heading skeleton) and a provisional `result.json`.
2. **Read** `task.md`, `case.json` and `work/facts.md` for audience, language, numbering and requirements:
   material index, **required sections**, `output_contract`, facts by category (id, value, file:line), logged series,
   pipeline commands, **conflicts (C#)** and **gaps (G#)**. Check original records when a condition or a gap is unclear.
   For XLSX/PDF, verify comparison labels, shared controls and device roles in the actual rows or pages.
   Use the scripts as documented. Consult the review and the input evidence to resolve findings.
3. **Write `work/draft.md` promptly** in the target language, as you would write the chapter for a journal.
   Give each sample count, metric, seed and parameter its split, group or stage in the same clause.
   For an ablation, name each condition and changed setting, then say which data, metric and settings were shared.
   Cite the exact row or page for qualitative claims and shared conditions using `[[SRC: file:line]]`.
4. **Build + check**:
   ```bash
   python3 $SKILL_DIR/scripts/ml_build.py --work /app/work --out /app/output
   ```
   Inspect `result.json`, the manuscript and `review.md`. Spot-check the map for shared numbers and comparisons.
   Exit 1 requests a targeted correction. Fix the cited factual errors and restore any recorded required items (K12).
   After two fix rounds, the build records remaining failures as partial. Confirm the requested artifacts exist and stop.

## What the build checks

| In your prose | Build |
|---|---|
| number/version/name that is in the materials | mapped to the fact (file:line) in fact_map.json and the annotated chapter |
| value of a conflict (C#) | 【待作者确认】 marker inserted after the sentence, question listed |
| required element recorded in the materials but absent from the draft (K12) | restore it using the supplied source |
| required detail genuinely missing in the materials (K01) | record the question in `questions.md` and the result |
| malformed tag | ignored with a warning |
| number in no material (N01), number of another condition (X01/T02), command not in the materials (P02), GPU/model name not in the materials (N02), placeholder XX/TBD (M01) | **FAIL - fix the sentence** (use the material value or say the item is not recorded) |

Optional precision tags, only where a value occurs in several facts or must be derived: `[[F12]]` (this clause uses F12),
`[[CALC: 74000-1210-790 = 72000 | F55,F56,F57]]`, `[[SRC: notes.md:5]]`, `[[GAP: question]]`, `[[CONFIRM: C1 why]]`,
`[[PARAM_TABLE]]`. `work/agent.json` (optional): `{"resolutions": [{"conflict": "C1", "use": "F66", "reason": "..."}],
"accept": {"N02@u12": "why"}, "fields": {"<contract field>": {"kind": "methods_text"}}, "status_note": ""}`.

## Writing rules

- **Complete (写得全)**: cover all six groups - method steps; setup (hardware, software versions, precision, run time if
  logged); parameters (the table is generated; name key values in text); data (name, source, version, size, preprocessing
  with counts, split sizes/ratio, split method and seed, which subset is used for what); controls (baselines with version,
  same data/budget or not, metrics and split, checkpoint selection, repetitions, statistics); reproducibility (commit,
  exact commands, seeds, environment, data access) and limitations. State the practical consequence of a material gap
  once in the appropriate section. Put detailed author prompts in `questions.md` through `[[GAP: question]]` only when
  the task requests inline flags or a material omission needs explicit author follow-up.
- **Accurate (写得准)**: values exactly as the run used them. Precedence when sources disagree: run log > command line >
  environment file > config > code default > notes; still name the disagreement in the sentence. Never round (2e-5 is not
  1e-5), never add a plausible default (no "Adam β=(0.9,0.999)" unless a material says it), keep each value with its own
  condition (val vs test, baseline vs proposed, stage 1 vs stage 2, group A vs group B).
- **Reproducible (做得着)**: numbered steps, one operation each, input -> operation -> output / decision rule; commands copied
  verbatim from logs/scripts in a code block; training seed and data-split seed named separately.
- **Defensible (说得住)**: limitations name concrete untested conditions from the facts (single seed, one dataset version,
  truncation length, untuned baseline, one GPU type, n per group) - not "may not generalise". No significance claim
  without a test in the materials. 不要为通过检查而改写专业术语，直接说明未报告或材料缺口。
- Style: past tense; target language for prose, original spelling for identifiers, files, models and values; keep the
  author's numbering. If an old draft is among the materials, keep its correct sentences and fix wrong values (diff in
  result.json `change_records`).

## 方法与实验保真 Checklist (before the build)

- [ ] required sections use recorded values and true material gaps are documented
- [ ] no number, version, GPU, model or command that is not in facts.md / a material line
- [ ] each split's size and use and each baseline/ablation condition are tied to the correct source
- [ ] every conflict C# visible in the sentence that uses it; seeds (training, split) and repetitions named
- [ ] limitations tied to a concrete condition; open questions left for the author, not guessed

## Outputs (`/app/output`)

`result.json` (case_id and every declared field with its JSON type, plus status, status_reason, the original output_contract,
sources with SHA-256, checks, coverage, needs_confirmation, conflicts, uncertainty, change_records, parameters,
repro_checklist and output-relative artifact paths. For a closed schema, extra metadata is in `result_full.json`) ·
`methods.md` + `methods.docx` (editable) · `methods_preview.pdf|.png` (rendered preview) · `methods_annotated.md|.html`
(sources of every claim + source map) · `param_table.csv|.md` (name, value, unit, applies to, source, status) ·
`fact_map.json` · `questions.md` (author checklist) · `check_report.json` · `review.md` (review notes, every check).
Status: `success` = chapter present, no FAIL (open author questions listed, not hidden); `partial` = FAILs left or no
draft; `failed` = nothing readable. Never edit result.json by hand; rebuild instead.

## Failure handling

| Situation | Scripts | You |
|---|---|---|
| case.json missing / invalid | reported; material dir still scanned; an existing checked result.json is not overwritten | continue; say so in `status_note` |
| Declared material not found | listed in facts.md and problems | state the dependent items as not available |
| No materials | status failed/partial, gaps list everything | write only what the task states |
| XLSX | read as CSV text per sheet (cached values) | cite like any table |
| Binary / .xls / encrypted PDF | listed with the reason, skipped | ask for a text/CSV export |
| GBK / mojibake text | decoded, repairs reported | do not guess garbled values |
| Same key, different values | conflict C# with all sources | name it in the sentence; never pick silently |
| Code default overridden by CLI/config | listed as overridden, not a conflict | write the value of the run |
| Values change during a run | summarised as series | report final/selected value with its condition |
| Budget short | provisional result exists from step 1 | build what you have; the build labels it honestly |

See `README.md` for the field dictionary, method, evaluation and limits; `examples/minimal_example.md` for a worked call.
