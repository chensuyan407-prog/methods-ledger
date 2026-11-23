"""Fresh-directory run: copy only submission/ into a new temp folder, run the documented workflow on a case that is
not part of the evaluation (tests/fresh_case), keep the outputs under execution/results/fresh_run."""
import os
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DST = os.path.join(ROOT, "execution", "results", "fresh_run")
tmp = tempfile.mkdtemp(prefix="ml_fresh_")
skill = os.path.join(tmp, "skill")
shutil.copytree(os.path.join(ROOT, "submission"), skill, ignore=shutil.ignore_patterns("__pycache__"))
case = os.path.join(tmp, "case_input")
shutil.copytree(os.path.join(ROOT, "tests", "fresh_case", "input"), case)
work, out = os.path.join(tmp, "work"), os.path.join(tmp, "output")
env = dict(os.environ, PYTHONIOENCODING="utf-8")
log = []
t0 = time.time()
for cmd in ([sys.executable, os.path.join(skill, "scripts", "ml_extract.py"), "--case", os.path.join(case, "case.json"), "--out", out, "--work", work],
            "COPY_DRAFT",
            [sys.executable, os.path.join(skill, "scripts", "ml_build.py"), "--work", work, "--out", out]):
    if cmd == "COPY_DRAFT":
        shutil.copy(os.path.join(ROOT, "tests", "fresh_case", "draft.md"), os.path.join(work, "draft.md"))
        log.append("$ cp tests/fresh_case/draft.md work/draft.md   (draft written by the agent after reading work/facts.md)")
        continue
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    log.append("$ " + " ".join(os.path.basename(c) if os.path.isabs(c) else c for c in cmd))
    log.append(r.stdout.decode("utf-8", errors="replace").replace(tmp, "<tmp>"))
    log.append(f"[exit {r.returncode}]")
log.append(f"total {time.time() - t0:.1f} s")
if os.path.exists(DST):
    shutil.rmtree(DST)
shutil.copytree(out, os.path.join(DST, "output"))
os.makedirs(os.path.join(DST, "work"))
for fn in ("facts.md", "draft.md"):
    shutil.copy(os.path.join(work, fn), os.path.join(DST, "work", fn))
with open(os.path.join(DST, "run.log"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(log) + "\n")
print("\n".join(log))
shutil.rmtree(tmp, ignore_errors=True)
