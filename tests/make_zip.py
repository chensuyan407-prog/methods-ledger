"""Package the ARM bundle: python tests/make_zip.py [out.zip]"""
import hashlib
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(ROOT), "methods-ledger_arm_v0.1.0.zip")
n = 0
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for r, ds, fs in os.walk(ROOT):
        ds[:] = sorted(d for d in ds if d not in ("__pycache__", ".git"))
        for f in sorted(fs):
            p = os.path.join(r, f)
            z.write(p, os.path.relpath(p, ROOT).replace(os.sep, "/"))
            n += 1
with open(out, "rb") as fh:
    print(n, "files", round(os.path.getsize(out) / 1e6, 2), "MB", hashlib.sha256(fh.read()).hexdigest(), out)
