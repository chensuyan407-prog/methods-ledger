"""Rerun the evaluation + fresh run, then write execution/run.log, trace/trace.jsonl, arm_manifest.json,
characterization.json and skills/SKILL.md from the actual outputs.  python tests/finalize.py"""
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "execution", "results")
steps, trace, log = [], [], []


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def add(d):
    d["step_order"] = len(trace) + 1
    d.setdefault("timestamp", now())
    trace.append(d)


def run(argv, cid):
    add({"step_type": "tool_call", "tool_name": "python", "tool_call_id": cid, "tool_args": {"argv": argv}})
    t0 = time.time()
    r = subprocess.run([sys.executable] + argv, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    out = r.stdout.decode("utf-8", errors="replace")
    log.append("$ python " + " ".join(argv) + "\n" + out + f"[exit {r.returncode}, {time.time() - t0:.1f} s]\n")
    add({"step_type": "tool_result", "tool_call_id": cid, "exit_code": r.returncode, "stdout_tail": out[-1500:]})
    if r.returncode:
        sys.exit(f"step failed: {argv}")
    return out


T0 = time.time()
ran_at = now()
add({"step_type": "thought", "title": "Plan", "body": "Rerun the self-evaluation of methods-ledger on all 5 author-written cases (3 dev, 2 held-out written after the code freeze): extraction vs expected facts/conflicts/gaps, gold drafts, 100 planted defects with grep and checklist baselines, 13 robustness checks; then the fresh-directory run from submission/ only; then record metrics, manifest and trace."})
run(["tests/run_eval.py", "--cases", "all", "--out", "execution/results"], "c1")
m = json.load(open(os.path.join(RES, "metrics.json"), encoding="utf-8"))
add({"step_type": "observation", "title": "Evaluation", "body": json.dumps({k: m[k] for k in ("extraction", "gold_drafts", "robustness")}, ensure_ascii=False) +
     f" mutations caught {m['mutations']['caught_fail']} (grep baseline {m['mutations']['baseline_grep']}, checklist baseline {m['mutations']['baseline_checklist']})"})
run(["tests/fresh_run.py"], "c2")
add({"step_type": "observation", "title": "Fresh run", "body": open(os.path.join(RES, "fresh_run", "run.log"), encoding="utf-8").read()[-600:]})
wall = round(time.time() - T0, 2)
os.makedirs(os.path.join(ROOT, "execution"), exist_ok=True)
with open(os.path.join(ROOT, "execution", "run.log"), "w", encoding="utf-8", newline="\n") as fh:
    fh.write(f"# methods-ledger 0.1.0 self-evaluation, started {ran_at}\n" + "\n".join(log) + f"wall {wall} s\n")
os.makedirs(os.path.join(ROOT, "skills"), exist_ok=True)
shutil.copy(os.path.join(ROOT, "submission", "SKILL.md"), os.path.join(ROOT, "skills", "SKILL.md"))


def sha(p):
    return hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest()


arts = [("metrics", "execution/results/metrics.json", "metric", "json"),
        ("metrics_holdout_at_freeze", "execution/results/metrics_holdout_at_freeze.json", "metric", "json"),
        ("metrics_dev_first_run", "execution/results/metrics_dev_v1.json", "metric", "json"),
        ("eval_rows", "execution/results/eval_rows.json", "data", "json"),
        ("eval_rows_holdout_at_freeze", "execution/results/eval_rows_holdout_at_freeze.json", "data", "json"),
        ("freeze_hashes", "tests/FREEZE_v0.1.0.sha256", "log", "text"),
        ("fresh_run_log", "execution/results/fresh_run/run.log", "log", "text"),
        ("fresh_run_result", "execution/results/fresh_run/output/result.json", "data", "json"),
        ("fresh_run_preview", "execution/results/fresh_run/output/methods_preview.png", "figure", "png")]
for case in sorted(os.listdir(os.path.join(RES, "cases"))):
    base = f"execution/results/cases/{case}/output/"
    arts += [(f"{case}_result", base + "result.json", "data", "json"), (f"{case}_methods", base + "methods.md", "data", "md"),
             (f"{case}_param_table", base + "param_table.csv", "data", "csv"), (f"{case}_questions", base + "questions.md", "data", "md"),
             (f"{case}_preview", base + "methods_preview.png", "figure", "png")]
arts = [a for a in arts if os.path.exists(os.path.join(ROOT, a[1]))]
f = json.load(open(os.path.join(RES, "metrics_holdout_at_freeze.json"), encoding="utf-8"))
ex = m["extraction"]
targets = [
    ("expected facts extracted (all 5 cases)", ex["fact_recall"], 1.0, 0.2, f"{ex['facts_found']}/{ex['facts_expected']} canonical key=value pairs listed by the author before/independently of tuning (tests/eval/expect)"),
    ("real conflicts found (all 5 cases)", ex["conflict_recall"], 1.0, 0.0, f"{ex['conflicts_found']}/{ex['conflicts_expected']}; false conflicts {ex['conflicts_unexpected']}"),
    ("conflict precision (all 5 cases)", ex["conflict_precision"], 1.0, 0.2, "share of reported conflicts that are real"),
    ("planted defects caught at fail level (all 5 cases)", m["mutations"]["caught_fail"], 1.0, 0.1, f"{m['mutations']['n']} deterministic mutations of gold drafts; baselines: grep {m['mutations']['baseline_grep']}, checklist only {m['mutations']['baseline_checklist']}"),
    ("planted defects caught at fail level (held-out, at freeze)", f["mutations"]["caught_fail"], 1.0, 0.1, f"{f['mutations']['n']} mutations; grep baseline {f['mutations']['baseline_grep']}"),
    ("expected facts extracted (held-out, at freeze)", f["extraction"]["fact_recall"], 1.0, 0.3, f"{f['extraction']['facts_found']}/{f['extraction']['facts_expected']}; conflicts {f['extraction']['conflicts_found']}/{f['extraction']['conflicts_expected']} with {f['extraction']['conflicts_unexpected']} false"),
    ("gold drafts without FAIL (held-out, at freeze)", f["gold_drafts"]["without_fail"] / f["gold_drafts"]["n"], 1.0, 0.5, "fails were false conflicts plus one real error in the author's gold"),
    ("gold drafts without FAIL (all 5, final)", m["gold_drafts"]["without_fail"] / m["gold_drafts"]["n"], 1.0, 0.0, "author-written drafts made with the Skill workflow"),
    ("robustness checks passed", m["robustness"]["passed"] / m["robustness"]["n"], 1.0, 0.0, ", ".join(r["check"] for r in json.load(open(os.path.join(RES, "eval_rows.json"), encoding="utf-8"))["robustness"])),
]
dev = []
for name, actual, ref, tol, expl in targets:
    actual = round(float(actual), 4)
    dv = abs(actual - ref)
    score = 1.0 if dv == 0 else (0.0 if tol == 0 else round(max(0.0, 1 - dv / tol), 4))
    dev.append({"target": name, "metric": "absolute_error", "actual_value": actual, "reference_value": ref, "score": score,
                "explanation": expl, "evidence_artifact": "metrics_holdout_at_freeze" if "freeze" in name else "metrics", "tolerance": tol})
json.dump({"deviations_from_paper": dev, "notes": "Self-evaluation on author-written cases with author gold drafts, expected facts and planted defects; the platform's three fixed cases and any model run (base vs Skill) are not part of it. The held-out set was changed by post-freeze fixes; both numbers are kept. Scores use max(0, 1 - deviation/tolerance) against the ideal value 1.0."},
          open(os.path.join(ROOT, "characterization.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
manifest = {
    "arm_version": "1.1",
    "paper": {"title": "写作09｜方法与实验章节写作 — methods-ledger Skill", "challenge_id": "product-arena-05-64faa4a2"},
    "entrypoint": "src/reproduce.py",
    "environment": {"dependencies": "requirements.txt", "python_version": ">=3.8", "gpu_required": False,
                    "extra_packages": ["PyMuPDF>=1.23 (optional: PDF materials, PDF/PNG preview, PDF robustness check)"]},
    "execution": {"log_path": "execution/run.log", "exit_code": 0, "ran_at": ran_at, "wall_time_s": wall, "ran_by": "agent",
                  "artifacts": [{"id": i, "path": p, "type": t, "format": fm, "checksum_sha256": sha(p)} for i, p, t, fm in arts]},
    "expected_outputs": [{"name": d["target"], "type": "metric", "produced_by": [d["evidence_artifact"]], "comparison_method": "numeric_tolerance"} for d in dev],
    "handoff": {"status": "partial",
                "next_suggestion": "Run the platform's three fixed cases with the DeepSeek harness (base vs Skill); add prose fact extraction for temperatures/concentrations/volumes, run-aware config grouping without logs, and OCR/XLSX inputs.",
                "hypothesis": "Separating fact extraction (file:line provenance, conflict and gap detection) from writing, and checking the agent's draft clause by clause against those facts, yields methods chapters whose values, versions and commands are traceable and whose gaps and conflicts are surfaced to the author, catching far more planted errors than grepping numbers or filling a checklist."},
}
json.dump(manifest, open(os.path.join(ROOT, "arm_manifest.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
add({"step_type": "thought", "title": "Record", "body": f"Wrote characterization.json ({len(dev)} targets), arm_manifest.json ({len(arts)} artifacts), execution/run.log; wall {wall} s."})
with open(os.path.join(ROOT, "trace", "trace.jsonl"), "w", encoding="utf-8", newline="\n") as fh:
    for t in trace:
        fh.write(json.dumps(t, ensure_ascii=False) + "\n")
print(json.dumps(dev, ensure_ascii=False, indent=1))
print("artifacts", len(arts), "wall", wall)
