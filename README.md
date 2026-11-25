# methods-ledger 0.2.0 — submission bundle for 写作09｜方法与实验章节写作

Agent Skill that writes or completes the **Methods / Experiments section** (方法与实验章节) from scattered materials —
configs, code, run logs, environment files, data cards, notebooks, CSV tables, lab notes, old drafts — so that every number,
version, model/GPU name and command in the chapter traces to a `file:line`. Scripts extract facts with provenance, report
conflicting values across sources and missing elements (steps, setup, parameters, data/splits, controls/evaluation,
reproducibility/limitations), and check the agent's draft clause by clause. Outputs: editable chapter (Markdown, DOCX,
PDF/PNG preview), sourced parameter table, fact map, author question list, `result.json`.

| path | content |
|---|---|
| `submission/` | **the Skill** (`SKILL.md`, `scripts/`, `rules/`, `templates/`, `examples/`, `README.md` = interface, method, results, limits) |
| `skills/SKILL.md` | copy of the Skill entry file |
| `src/reproduce.py` | reruns the whole self-evaluation and the fresh-directory run (~30 s, CPU, standard library) |
| `tests/` | 5 author-written cases (`cases/*/input`), expected facts (`eval/expect`), gold drafts (`eval/gold`), `run_eval.py` (mutations, baselines, robustness), `fresh_run.py` + `fresh_case/`, `FREEZE_v0.1.0.sha256`, `finalize.py`, `make_zip.py` |
| `execution/` | `run.log`, `results/metrics*.json`, `results/eval_rows*.json`, per-case outputs (`results/cases/*/output`: chapter, annotated chapter, DOCX, PDF/PNG preview, parameter table, fact map, questions, check report, result.json), `results/fresh_run/` |
| `arm_manifest.json`, `characterization.json`, `trace/trace.jsonl` | ARM bundle metadata |

## Reproduce

```bash
python src/reproduce.py        # optional: pip install pymupdf (PDF materials and previews)
```

## Results (author-written cases; not the platform's fixed cases; no model was run)

| measure | dev (3) | held-out (2) at code freeze | all 5, final |
|---|---:|---:|---:|
| expected facts extracted | 73/80 | 36/47 | 117/127 |
| real conflicts found / false conflicts | 3/3 / 0 | 2/3 / 3 | 6/6 / 0 |
| planted defects caught (FAIL) | 58/60 | 39/40 | 97/100 |
| baseline: grep numbers/versions in the materials | 35/60 | 17/40 | 52/100 |
| baseline: checklist coverage only | 21/60 | 14/40 | 35/100 |
| gold drafts without FAIL | 3/3 | 0/2 | 5/5 |
| robustness checks | | | 13/13 |

The held-out set was changed by post-freeze fixes (placeholder/per-row seeds and baseline configs no longer reported as
conflicts; survey counts, R `alpha`, imputation counts extracted); both numbers are kept. Details and concrete limits:
`submission/README.md`.
