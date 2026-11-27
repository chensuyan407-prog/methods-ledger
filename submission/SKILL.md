---
name: methods-ledger
description: Writes or completes the Methods / Experiments section (方法与实验章节) of a paper, thesis or report from scattered research materials - configs (YAML/JSON/TOML/INI/mdp/LAMMPS), code (argparse defaults, seeds, splits), run logs, requirements/conda files, data cards, CSV/.xlsx tables, lab notes, old drafts (md/txt/tex/docx/pdf). A script extracts every parameter, setting, dataset/split, baseline and reproducibility item with file:line provenance, flags conflicting values and missing elements; the agent writes the chapter; a second script aligns every number with the fact ledger, marks anything unsourced or conflicting for the author, and outputs an editable chapter (Markdown + DOCX + PDF/PNG preview), a sourced parameter table, a fact map, an author question list and result.json. Use for 写方法章节, 实验设置, 参数表, 复现说明, methods section, experimental setup, reproducibility checklist. Not for literature reviews, results/discussion or language-only polishing.
---

# methods-ledger (v0.3.0)

Scripts find the facts and check the chapter; you write the chapter. Python 3.8+ standard library (PyMuPDF optional).
Target: **3-6 model requests, one build**. A valid `result.json` exists after step 1, so a cut-off run is never empty.

```bash
SKILL_DIR=$(dirname "$(ls /skills/*/SKILL.md 2>/dev/null | head -1)"); PY=$(command -v python3 || command -v python)
```

## Workflow

1. **Extract** (seconds): `$PY "$SKILL_DIR/scripts/ml_extract.py" --case /input/case.json --out /app/output --work /app/work`
   Prints case_id, `output_contract` fields, language, profile, files, conflicts; writes `/app/work/facts.md`, a heading
   skeleton `/app/work/draft.md` and a provisional `result.json` (materials embedded in case.json are read too).
2. **Read** `/app/work/facts.md` (facts `F#` with file:line, conflicts `C#`, gaps `G#`, pipeline commands) and read full
   `/input/task.md` and `/input/case.json` constraints (audience, language, section numbering). Open a material file only if the order of stages is unclear.
3. **Write** `/app/work/draft.md` in one pass (rules below). Cite with `[[F12]]` after the clause; mark missing items with
   `[[GAP: question]]` and conflicting values with `[[CONFIRM: C1 ...]]`. Tag slips do not block anything - untagged or
   mis-tagged numbers are auto-aligned to the ledger - but each clean tag makes the source map more precise.
4. **Build**: `$PY "$SKILL_DIR/scripts/ml_build.py" --work /app/work --out /app/output`
   Exit 0 + `status: success` whenever the draft has text. `FLAG` lines are already marked in the chapter
   (【待核实】/[UNVERIFIED], 【待作者确认】) and listed in an "open items" section and `questions.md`. If you still have
   budget, fix FLAGs that are your own slips (wrong number, invented value) and rebuild once; otherwise you are done.

## Writing rules (what the graders check)

- **Complete** - one subsection each: method steps (numbered, one operation per step: input -> operation -> output);
  setup (hardware, software versions, precision, run time); parameters (key values in text, the full table is generated);
  data (name, source, version, size, preprocessing with counts, split sizes/ratio, split method and seed, use of each subset);
  controls & evaluation (baselines with version, same data/budget or not, metrics and on which split, checkpoint
  selection, repetitions, statistics); reproducibility (commit, commands, seeds, environment, data access); limitations.
  An element absent from the materials gets a `[[GAP: ...]]` sentence - never silence, never a guess.
- **Accurate** - copy values exactly as the run used them (2e-5 is not 1e-5). Do not add defaults the materials do not
  state (no "Adam β=(0.9,0.999)", no GPU model, no epoch count). Keep each value with its condition (val vs test,
  baseline vs proposed, stage 1 vs 2). Source precedence: run log > command line > env file > config > code default > notes;
  a disagreement is still a conflict: write the value you use with `[[CONFIRM: C# ...]]`.
- **Reproducible** - commands copied verbatim from logs/scripts into a code block; training seed and split seed named separately.
- **Defensible** - limitations name concrete untested conditions from the facts (single seed, one dataset version,
  truncation length, untuned baseline, one GPU type, n per group), not "may not generalise". No significance claim
  without a test in the materials.
- Style: past tense; target language for prose, original spelling for identifiers and values; keep the task's section
  numbering. An old draft among the materials: keep its correct sentences, fix wrong values (diff -> `change_records`).

## Tags (all optional; the builder repairs `[F12]`, `【F12】`, `(F12)`, `[[f12; F13]]`)

| tag | meaning |
|---|---|
| `[[F12]]`, `[[F12,F30]]`, `[[@configs/train.yaml:14]]`, `[[SRC: notes.md:5]]` | the preceding clause is supported by these facts / that material line |
| `[[CALC: 74000-1210-790 = 72000 \| F55,F56,F57]]` | derived number, operands from the materials |
| `[[CONFIRM: C1 config 3e-5, log 2e-5; text uses the logged value]]` | conflicting or assumed value for the author |
| `[[GAP: Which dataset version was used?]]` | missing information, rendered 【待确认：…】 / [TO CONFIRM: …] |
| `[[PARAM_TABLE]]` | where the parameter table goes (default: end of the parameters section) |

Optional `/app/work/agent.json`: `{"resolutions": [{"conflict": "C1", "use": "F66", "reason": ""}], "fields": {"<field>": {"kind": "methods_text"}}, "notes": []}`.
## Outputs (`/app/output`) and status

`result.json` (case_id + every `output_contract` field, status, status_reason, sources with SHA-256, checks, coverage,
needs_confirmation, conflicts, uncertainty, change_records, parameters, repro_checklist) · `methods.md` (clean, editable) ·
`methods_annotated.md|.html` (every claim with its source) · `methods.docx` + `methods_preview.pdf|.png` ·
`param_table.csv|.md` (name, value, unit, applies to, source, status) · `fact_map.json` · `questions.md` · `review.md`.
Status: `success` = chapter built (flags marked, questions listed); `partial` = no draft text yet; `failed` = nothing
readable. Never edit result.json by hand; re-running extract keeps a successful result.json.

## Failure handling

| Situation | What happens / what you do |
|---|---|
| case.json missing or invalid | scripts scan the input directory and say so; continue, note it in `notes` |
| No usable / unreadable materials (binary, encrypted PDF) | listed with the reason; write what the task states, the rest as `[[GAP: ...]]` |
| Same key, different values (per-step series such as loss/lr are not conflicts) | conflict `C#` with all sources: write one value with `[[CONFIRM: C# ...]]` |
| Build prints FLAG | already marked for the author; fix only your own slips, at most one rebuild |
| Script error (exit 2/3) | existing result.json is kept; rerun extract (exit 2) or report the error in `notes` |

See `README.md` for the method, field dictionary, evaluation and limits; `examples/minimal_example.md` for a worked call.
