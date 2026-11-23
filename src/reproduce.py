"""Reproduce every number of this bundle (about 30 s on a laptop CPU; standard library, PyMuPDF optional).

python src/reproduce.py

Runs tests/finalize.py, which reruns tests/run_eval.py (5 cases: extraction scoring, gold drafts, 100 planted defects,
baselines, 13 robustness checks) and tests/fresh_run.py (Skill copied alone to a temp folder, new case), then rewrites
execution/run.log, execution/results/*, characterization.json, arm_manifest.json and trace/trace.jsonl.
The held-out numbers at code freeze (execution/results/metrics_holdout_at_freeze.json) are kept as recorded; rerun them
with the frozen sources listed in tests/FREEZE_v0.1.0.sha256 if needed."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
r = subprocess.run([sys.executable, os.path.join(ROOT, "tests", "finalize.py")], cwd=ROOT, env=dict(os.environ, PYTHONIOENCODING="utf-8"))
sys.exit(r.returncode)
