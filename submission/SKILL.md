---
name: methods-ledger
description: Writes or completes the Methods / Experiments section (方法与实验章节) of a paper, thesis or report from scattered research materials - configs (YAML/JSON/TOML/INI/mdp/INCAR/LAMMPS), code (argparse defaults, seeds, splits, optimizers), run logs, requirements/conda files, data cards, CSV tables, lab notes, old drafts (md/txt/docx/pdf). Scripts extract every parameter, setting, dataset/split, baseline and reproducibility item with file:line provenance, flag conflicting values across sources and missing elements, then check the agent's draft sentence by sentence - every number, version, model/GPU name and command must trace to a material line, cited values must match, conflicts must be marked for the author, six element groups (steps, setup, parameters, data/splits, controls/evaluation, reproducibility/limitations) must be covered or marked as gaps, and limitations must name concrete failure conditions. Outputs an editable chapter (Markdown + DOCX + PDF/PNG preview), a sourced parameter table, a fact map, an author question list and result.json. Use for 写方法章节, 实验设置, 参数表, 复现说明, methods section, experimental setup, reproducibility checklist. Do not use for literature reviews, results/discussion interpretation or language-only polishing.
---

# methods-ledger (v0.1.0)

You write the chapter; the scripts find the facts and check that the chapter says only what the materials say.
Python 3.8+ standard library (PyMuPDF optional: PDF materials and the PDF/PNG preview). `SKILL_DIR` = directory of this
file (`/skills/weekly-skill`). Paths below use the evaluator layout (`/input`, `/app/work`, `/app/output`).

## Workflow (6-12 model requests; a valid result.json exists after step 1)

1. **Extract** (seconds):
   ```bash
   python $SKILL_DIR/scripts/ml_extract.py --case /input/case.json --out /app/output --work /app/work
   ```
   Prints case_id, contract fields, target language (zh/en, from task; override `--lang`), domain profile
   (ml | wetlab | simulation | stats | generic; override `--profile`), each file's class and fact count, conflicts.
   Writes `work/facts.md` (read this), `work/facts.json`, `work/draft.md` (heading skeleton), `work/agent.json`, and a
   provisional `output/result.json` (status partial).
2. **Read** `task.md`/case requirements (audience, language, section numbering, what to include) and `work/facts.md`:
   facts by category with ids, logged series, numeric lines of notes/logs, pipeline commands, **conflicts (C#)**, **gaps (G#)**.
   Open a material file only when facts.md is not enough (e.g. to understand the order of stages).
3. **Write `work/draft.md`** in the target language (rules below). Tag right after the clause a fact supports.
4. **Build + check**:
   ```bash
   python $SKILL_DIR/scripts/ml_build.py --work /app/work --out /app/output
   ```
   Exit 1 = FAILs remain (outputs are written anyway, status partial). Every FAIL names the line, the token and the
   candidate facts.
5. **Fix every FAIL** and rebuild (idempotent). Read warnings; fix the ones that are real. Stop after 3 rounds or when
   the budget is short - the last build is always a usable, honestly labelled result.

## Tags in draft.md

| tag | meaning |
|---|---|
| `[[F12]]`, `[[F12,F30]]` | the preceding clause (text since the previous tag) is supported by these facts; every number in that clause must be a value of one of them |
| `[[@configs/train.yaml:14]]` | same, by file:line (all facts on that line; `#key` narrows); a line without a fact counts as a source line |
| `[[SRC: notes.md:5]]` / `[[SRC: run.log:10-12]]` | a material line that facts.md does not list |
| `[[CALC: 74000-1210-790 = 72000 \| F55,F56,F57]]` | derived number; the expression is evaluated, its operands must be material values |
| `[[CONFIRM: C1 config says 3e-5, log/CLI say 2e-5; text uses the logged value]]` | value from a conflict, or an assumption the author must confirm (required for every clause using a conflicting fact) |
| `[[GAP: Which dataset version was used?]]` | information that is missing; rendered as 【待确认：…】 / [TO CONFIRM: …] and listed for the author |
| `[[PARAM_TABLE]]` | where the generated parameter table goes (otherwise it is appended to the parameters section) |

`agent.json` (optional): `{"resolutions": [{"conflict": "C1", "use": "F66", "reason": "..."}], "accept": {"N03@u12": "why"},
"fields": {"<contract field>": {"kind": "methods_text"}}, "notes": [], "status_note": ""}`. A resolution still leaves the
question open for the author. `accept` silences one finding (`CODE@unit`; warnings also by `CODE`); accepted items stay listed.

## Writing rules

- **Complete (写得全)**: cover all six groups - method steps; setup (hardware, software versions, precision, run time if logged);
  parameters (table + key values in text); data (name, source, version/snapshot, size, preprocessing with counts, split sizes/
  ratio, split method and seed, which subset is used for what); controls (baselines with implementation/version, same data /
  same budget or not, metrics and on which split, checkpoint selection, repetitions, statistics); reproducibility (commit,
  exact commands, seeds, environment, data access) and limitations. Missing in the materials -> `[[GAP: ...]]`, never silence.
- **Accurate (写得准)**: copy values exactly as the run used them. Precedence when sources disagree: run log > command line >
  environment file > config > code default > notes - but a disagreement is still a conflict: write the value you use with
  `[[CONFIRM: C# ...]]`. Never "round off" (2e-5 is not 1e-5), never fill a plausible default (no "Adam β=(0.9,0.999)" unless
  a material says it), keep each value with its own condition (val vs test, baseline vs proposed model, stage 1 vs stage 2).
- **Reproducible (做得着)**: steps as a numbered list, one operation per step, each with input -> operation -> output / decision
  rule; commands copied verbatim from logs/scripts in a code block (the checker rejects commands that are not in the materials);
  name seeds for training and for data splitting separately.
- **Defensible (说得住)**: limitations name concrete untested conditions taken from the facts (single seed, one dataset version,
  truncation length, untuned baseline, one GPU type, fp16 only, n per group) - not "may not generalise". Do not claim
  significance without a test in the materials. Mark assumptions with CONFIRM.
- Style: past tense for what was done; the target language for prose, original spelling for identifiers, file names, model
  names and values; keep the author's section numbering if the task gives one. If an old draft is among the materials, keep its
  correct sentences, fix wrong values (the diff against it is recorded in result.json `change_records`).

## Check codes (ml_build.py)

Numbers: N01 number/version without any source (fail) · N02 model/GPU/dataset name with digits not in the materials (GPU: fail) ·
N03 traceable but untagged · N04 in a material line but not a fact (add SRC) · N05 rounded value · N06 small integer untraced (info) ·
N07 unsourced number inside a GAP/CONFIRM clause. Tags: T01 unknown fact id · T02 number differs from the fact tagged on its clause
(fail) · T03 malformed tag · T05 tagged text value absent · T06 SRC points nowhere · T07 value supported by a tag on another clause ·
K10/K11 CALC wrong / operand untraceable. Conflicts: C01 conflicting value used without CONFIRM or resolution (fail). Coverage:
K01 required element neither covered (with a source) nor marked GAP (fail) · K02 recommended element missing · K03 material facts never
used. Limits: L01 generic limitation sentence · L02 limitations section without any concrete condition (fail). Steps/commands:
P01 pipeline stage (script) not described · P02 command not found in the materials (fail). Other: M01 placeholder (XX, TBD, 待补充)
instead of a GAP (fail) · X01 val/test value used in a sentence about the other split · S01 significance claim without a test ·
D00 empty draft.

## Outputs (`/app/output`)

`result.json` (case_id, every contract field, status, status_reason, sources with SHA-256, checks, coverage, needs_confirmation,
conflicts, uncertainty, change_records, parameters, repro_checklist) · `methods.md` (clean, editable) · `methods_annotated.md|.html`
(every claim with its source) · `methods.docx` + `methods_preview.pdf` + `methods_preview.png` · `param_table.csv|.md`
(name, value, unit, applies to, source, status) · `fact_map.json` (per sentence: facts, numbers and how each was matched) ·
`questions.md` (gaps, conflicts, draft GAP/CONFIRM items as a checklist) · `check_report.json` · `review.md`.
Contract fields are filled by name (methods/section/text -> chapter, param -> table rows, source/evidence -> fact map,
gap/question/confirm -> questions, conflict, uncertainty, change/diff, repro, limitation, dataset, baseline/control, setup, steps);
set `fields` in agent.json for anything else. Status: `success` = draft present and no FAIL (open author questions are listed,
not hidden); `partial` = FAILs left or no draft; `failed` = nothing readable. Never edit result.json by hand.

## Failure handling

| Situation | Scripts | You |
|---|---|---|
| case.json missing / invalid | reported in problems; material dir still scanned | continue; say so in `notes` |
| No materials | status failed/partial, gaps list everything | write only what the task states, every element as GAP |
| Binary / xlsx / encrypted PDF / unreadable file | listed with the reason, skipped | ask for CSV/text export in a GAP |
| GBK / mojibake text | decoded, repairs reported | do not guess garbled values |
| Same key, different values | conflict C# with every source; precedence guess | CONFIRM in text, never pick silently |
| Code default overridden by CLI/config | dropped from the conflict, listed as overridden | write the value of the run |
| Values change during a run (loss, lr schedule) | summarised as series, not conflicts | report final/selected values with their condition |
| Number you need is derived | - | `[[CALC: ...]]` |
| A finding is wrong for your sentence | - | `accept` with a reason in agent.json |
| Budget short | provisional result exists from step 1 | build what you have; unfinished parts as GAP |

See `README.md` for the field dictionary, method, evaluation and limits; `examples/minimal_example.md` for a worked call.
