"""Self-evaluation of methods-ledger on author-written cases.

python tests/run_eval.py [--cases dev|holdout|all] [--out execution/results] [--tag NAME]

1. Extraction: expected facts / conflicts / gaps per case (tests/eval/expect/<case>.json) vs ml_extract output.
2. Gold drafts (tests/eval/gold/<case>.md, written by the author with the Skill workflow) must build without FAIL.
3. Planted defects: deterministic mutations of each gold draft (wrong value, invented number, dropped CONFIRM, missing
   element, boilerplate limitations, edited command / version / model name, placeholder, wrong tag, split swap).
   Caught = an expected check code fires (fail level, and fail-or-warn level). Baselines on the same mutations:
   B1 naive grep (every number/version string of the draft must occur somewhere in the materials),
   B2 checklist only (section coverage + limitations codes, no value checks).
4. Robustness runs (missing case.json, empty dir, binary/xlsx, malformed config, huge log, no draft, bad tags,
   determinism, contract shapes, invalid agent.json, old draft in materials, PDF and DOCX materials).
Standard library only (PyMuPDF used if installed)."""
import argparse
import copy
import json
import os
import re
import shutil
import sys
import tempfile
import time
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "submission", "scripts")
sys.path.insert(0, SCRIPTS)
import ml_common as C  # noqa: E402
import ml_extract  # noqa: E402
import ml_build  # noqa: E402

CASES = os.path.join(ROOT, "tests", "cases")
GOLD = os.path.join(ROOT, "tests", "eval", "gold")
EXPECT = os.path.join(ROOT, "tests", "eval", "expect")


def quiet(fn, *a, **k):
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        return fn(*a, **k)


def run_extract(case, tmp, extra=None):
    out, work = os.path.join(tmp, "out"), os.path.join(tmp, "work")
    args = ["--case", os.path.join(CASES, case, "input", "case.json"), "--out", out, "--work", work] + (extra or [])
    quiet(ml_extract.main, args)
    return out, work


def build_with(work, out, draft_text, agent=None):
    with open(os.path.join(work, "draft.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(draft_text)
    if agent is not None:
        C.dump_json(agent, os.path.join(work, "agent.json"))
    for p in ("history.json", "draft_prev.md"):
        if os.path.exists(os.path.join(work, p)):
            os.remove(os.path.join(work, p))
    status, rep, result = quiet(ml_build.build, work, out)
    return status, rep, result


# ---------------------------------------------------------------- extraction scoring

def fact_hit(facts, canon, value):
    want_nums = [t[1] for t in C.num_tokens(str(value))]
    for f in facts:
        if f["canon"] != canon:
            continue
        if want_nums and f["nums"] and all(any(C.nums_close(w, x) for x in f["nums"]) for w in want_nums):
            return f["id"]
        if str(value).lower() in f["value"].lower():
            return f["id"]
    return None


def score_extraction(case, work):
    exp = C.load_json(os.path.join(EXPECT, case + ".json"), {})
    fx = C.load_json(os.path.join(work, "facts.json"))
    st = C.load_json(os.path.join(work, "state.json"))
    facts, conflicts, gaps = fx["facts"], fx["conflicts"], fx["gaps"]
    rows = {"case": case, "facts_expected": len(exp.get("facts", [])), "facts_found": 0, "facts_missed": [],
            "conflicts_expected": exp.get("conflicts", []), "conflicts_found": [], "conflicts_unexpected": [],
            "gaps_expected": exp.get("gaps", []), "gaps_found": [], "gaps_extra": [],
            "profile_expected": exp.get("profile"), "profile": st["profile"], "lang_expected": exp.get("lang"), "lang": st["lang"]}
    for canon, value in exp.get("facts", []):
        if fact_hit(facts, canon, value):
            rows["facts_found"] += 1
        else:
            rows["facts_missed"].append(f"{canon}={value}")
    names = [c["canon"] + (":" + c["label"].split("(")[-1].rstrip(")") if "(" in c["label"] else "") for c in conflicts]
    for want in exp.get("conflicts", []):
        hit = next((n for n in names if n == want or n.split(":")[0] == want), None)
        if hit:
            rows["conflicts_found"].append(want)
    rows["conflicts_unexpected"] = [n for n in names if not any(n == w or n.split(":")[0] == w for w in exp.get("conflicts", []))]
    elems = {g["element"] for g in gaps}
    rows["gaps_found"] = [g for g in exp.get("gaps", []) if g in elems]
    rows["gaps_extra"] = sorted(elems - set(exp.get("gaps", [])))
    return rows


# ---------------------------------------------------------------- mutations

LIMIT_HEAD = re.compile(r"(?im)^(#{1,6})\s+.*(limitation|局限|限制).*$")
BOILER = {"en": ["- The method may not generalize to other domains, and future work is needed.", "- Larger datasets may further improve the results."],
          "zh": ["- 本方法的泛化能力有待进一步研究。", "- 未来工作将在更多数据上验证。"]}
INVENT = {"en": ("A label smoothing of 0.37 was applied to all runs.", "In addition, a label smoothing of 0.37 was applied to all runs [[{tag}]]."),
          "zh": ("所有实验的标签平滑系数设为 0.37。", "此外，所有实验的标签平滑系数设为 0.37 [[{tag}]]。")}


def mutations(case, gold, lang, facts, corpus_low):
    """Deterministic list of (id, type, text, expected_codes, level_hint)."""
    out = []
    units = ml_build.parse_draft(ml_build.resolve_anchors(gold, facts)[0])
    # value change on tagged numbers (every 3rd tagged number, max 6)
    cands = []
    for line in gold.split("\n"):
        pos = 0
        for m in ml_build.TAG_RE.finditer(line):
            seg = line[pos:m.start()]
            seg_start = pos
            pos = m.end()
            if not re.match(r"^\s*(F\d|@)", m.group(1)) or not seg.strip():
                continue
            lm = ml_build.LIST_MARK_RE.match(seg) if seg_start == 0 else None
            for tok, v, pct, s, e in C.num_tokens(seg):
                if (lm and s < lm.end()) or ml_build.exempt_number(seg, s, e, tok) or (v == int(v) and abs(v) <= 3):
                    continue
                cands.append((line, line, tok, v, seg_start + s, seg_start + e))
    for i, (line, sp, tok, v, ts, te) in enumerate(cands[::3][:6]):
        if v == int(v):
            new = str(int(v) * 2 if v < 1000 else int(v) + 1000)
        else:
            new = ("%g" % (v * 2))
        if tok.endswith("%"):
            new += "%"
        sp2 = sp[:ts] + new + sp[te:]
        out.append((f"value{i + 1}", "wrong_value", gold.replace(line, line.replace(sp, sp2, 1), 1), {"T02", "N01"}, f"{tok}->{new}"))
    # invented sentence, untagged and tagged with an unrelated fact
    some_fid = next((f["id"] for f in facts if f["kind"] == "config" or f["kind"] == "log"), facts[0]["id"] if facts else "F1")
    heads = [m for m in re.finditer(r"(?m)^#{1,6}\s+.*$", gold)]
    pos = heads[min(2, len(heads) - 1)].end() if heads else len(gold)
    u, t = INVENT[lang]
    out.append(("invent_untagged", "invented_number", gold[:pos] + "\n\n" + u + "\n" + gold[pos:], {"N01"}, "0.37 label smoothing"))
    out.append(("invent_tagged", "invented_number", gold[:pos] + "\n\n" + t.format(tag=some_fid) + "\n" + gold[pos:], {"N01", "T02"}, "0.37 tagged " + some_fid))
    # drop CONFIRM tags
    if "[[CONFIRM" in gold:
        out.append(("drop_confirm", "unmarked_conflict", re.sub(r"\s*\[\[CONFIRM:.*?\]\]", "", gold, flags=re.S), {"C01"}, "all CONFIRM removed"))
    # limitations removed / boilerplate
    m = LIMIT_HEAD.search(gold)
    if m:
        nxt = re.search(r"(?m)^#{1,%d}\s" % len(m.group(1)), gold[m.end():])
        end = m.end() + nxt.start() if nxt else len(gold)
        out.append(("drop_limits", "missing_element", gold[:m.start()] + gold[end:], {"K01"}, "limitations section removed"))
        out.append(("boiler_limits", "boilerplate_limits", gold[:m.end()] + "\n\n" + "\n".join(BOILER[lang]) + "\n\n" + gold[end:], {"L02"}, "generic limitations"))
    # missing elements: remove every unit matching a covered required element
    st = {"profile": PROFILE[case]}
    for eid in ("E_seed", "E_hparams", "E_split", "E_software", "E_baseline", "E_conditions", "E_repeats", "E_hardware", "E_instrument"):
        e = next((x for x in C.rules("checklist")["elements"] if x["id"] == eid), None)
        if not e or e not in ml_extract.elements_for(st["profile"]):
            continue
        pat = e["draft_patterns"].get(lang) or e["draft_patterns"]["en"]
        txt = gold
        removed = 0
        for line in gold.split("\n"):
            if line.startswith("#"):
                continue
            for sent in re.split(r"(?<=[。！？])|(?<=[.!?])\s+(?=[A-Z一-鿿(\[`*])", line):
                if sent and (re.search(pat, sent) or re.search(e["draft_patterns"]["en"], sent)):
                    txt = txt.replace(sent, "", 1)
                    removed += 1
        if removed:
            out.append((f"drop_{eid}", "missing_element", txt, {"K01"}, f"{removed} sentences on {eid} removed"))
    # command edit
    cm = re.search(r"(?m)^((?:python3?|lmp|Rscript|bash)\b[^\n`]*)$", gold) or re.search(r"`((?:python3?|lmp|Rscript|bash)\b[^`]*)`", gold)
    if cm:
        cmd = cm.group(1)
        new = re.sub(r"(\d+)(?!.*\d)", lambda mm: str(int(mm.group(1)) + 7), cmd) if re.search(r"\d", cmd) else cmd + " --fast"
        out.append(("cmd_edit", "fabricated_command", gold.replace(cmd, new, 1), {"P02"}, f"{cmd[:40]} -> {new[:40]}"))
    # version edit
    vm = C.VERSION_RE.search(re.sub(r"\[\[.*?\]\]", "", gold))
    if vm:
        v = vm.group(0)
        nv = re.sub(r"(\d+)$", lambda mm: str(int(mm.group(1)) + 3), v) if re.search(r"\d$", v) else v + ".9"
        out.append(("version_edit", "wrong_version", gold.replace(v, nv, 1), {"N01"}, f"{v}->{nv}"))
    # name with digits
    for nm in C.NAME_NUM_RE.finditer(re.sub(r"\[\[.*?\]\]", "", gold)):
        tok = nm.group(0)
        if tok.lower() in corpus_low and re.search(r"\d", tok):
            new = re.sub(r"\d", lambda mm: str((int(mm.group(0)) + 3) % 10), tok, count=1)
            if new.lower() in corpus_low:
                continue
            out.append(("name_edit", "wrong_name", gold.replace(tok, new, 1), {"N02"}, f"{tok}->{new}"))
            break
    # placeholder
    if cands:
        line, sp, tok, v, ts, te = cands[len(cands) // 2]
        out.append(("placeholder", "placeholder", gold.replace(line, line.replace(sp, sp[:ts] + "XX" + sp[te:], 1), 1), {"M01"}, f"{tok}->XX"))
    # wrong tag: move a numeric clause's tag to another line of the same file without that number
    for line in gold.split("\n"):
        mm = re.search(r"\[\[@([^\]:#,]+):(\d+)\]\]", line)
        if mm and C.num_tokens(re.sub(r"\[\[.*?\]\]", "", line)):
            file, ln = mm.group(1), int(mm.group(2))
            others = [f for f in facts if f["file"] == file and f["line"] != ln and f["kind"] != "doc"]
            if others:
                o = others[0]
                out.append(("wrong_tag", "wrong_citation", gold.replace(mm.group(0), f"[[@{o['file']}:{o['line']}]]", 1), {"T02", "N01"}, f"{mm.group(0)} -> @{o['file']}:{o['line']}"))
                break
    # split swap (val number written as test)
    sw = re.search(r"(验证集|validation set)([^。.\n]{0,40}?\d\.\d+)", gold)
    if sw:
        rep_word = "测试集" if sw.group(1) == "验证集" else "test set"
        out.append(("split_swap", "condition_crossover", gold.replace(sw.group(0), rep_word + sw.group(2), 1), {"X01"}, sw.group(1) + "->" + rep_word))
    return out


PROFILE = {}


def naive_grep_catch(draft, corpus_low):
    text = re.sub(r"\[\[.*?\]\]", " ", draft, flags=re.S)
    text = re.sub(r"(?m)^#.*$", "", text)
    norm = corpus_low.replace(",", "")
    for tok, v, pct, s, e in C.num_tokens(text):
        t = tok.replace(",", "").rstrip("%").strip()
        if t and t.lower() not in norm:
            return True
    for m in C.VERSION_RE.finditer(text):
        if m.group(0).lower().lstrip("v") not in norm:
            return True
    return False


def checklist_catch(codes):
    return bool(codes & {"K01", "L02"})


# ---------------------------------------------------------------- robustness

def robustness(tmp_root):
    res = []

    def rec(name, ok, detail):
        res.append({"check": name, "pass": bool(ok), "detail": detail})

    # R1 missing case.json: material dir only
    d = tempfile.mkdtemp(dir=tmp_root)
    shutil.copytree(os.path.join(CASES, "dev_sim", "input"), os.path.join(d, "in"))
    os.remove(os.path.join(d, "in", "case.json"))
    try:
        quiet(ml_extract.main, ["--case", os.path.join(d, "in", "case.json"), "--out", os.path.join(d, "out"), "--work", os.path.join(d, "work")])
        r = C.load_json(os.path.join(d, "out", "result.json"))
        rec("missing_case_json", r and r.get("case_id") and r.get("status") == "partial", f"case_id={r.get('case_id')} status={r.get('status')}")
    except Exception as e:  # noqa
        rec("missing_case_json", False, repr(e))
    # R2 empty dir
    d = tempfile.mkdtemp(dir=tmp_root)
    os.makedirs(os.path.join(d, "in"))
    C.dump_json({"case_id": "empty", "output_contract": ["methods_text", "status"]}, os.path.join(d, "in", "case.json"))
    try:
        quiet(ml_extract.main, ["--case", os.path.join(d, "in", "case.json"), "--out", os.path.join(d, "out"), "--work", os.path.join(d, "work")])
        st, rep, r = quiet(ml_build.build, os.path.join(d, "work"), os.path.join(d, "out"))
        rec("empty_materials", r["status"] in ("failed", "partial") and "methods_text" in r, f"status={r['status']}; reason={r['status_reason'][:80]}")
    except Exception as e:  # noqa
        rec("empty_materials", False, repr(e))
    # R3 binary + xlsx + malformed yaml/json + huge log
    d = tempfile.mkdtemp(dir=tmp_root)
    inp = os.path.join(d, "in")
    shutil.copytree(os.path.join(CASES, "dev_ml", "input"), inp)
    with open(os.path.join(inp, "weights.pt"), "wb") as fh:
        fh.write(b"\x00\x01binary" * 100)
    with zipfile.ZipFile(os.path.join(inp, "results.xlsx"), "w") as z:
        z.writestr("xl/workbook.xml", "<workbook/>")
    with open(os.path.join(inp, "configs", "broken.yaml"), "w", encoding="utf-8") as fh:
        fh.write("train:\n  lr: [0.1, \n  bad: : :\n\tmixed_tab: 3\n")
    with open(os.path.join(inp, "configs", "broken.json"), "w", encoding="utf-8") as fh:
        fh.write('{"lr": 0.5, "batch_size": ')
    with open(os.path.join(inp, "logs", "huge.log"), "w", encoding="utf-8") as fh:
        for i in range(200000):
            fh.write(f"2024-03-03 09:{i % 60:02d}:00 INFO step={i} loss={1.0 / (i + 1):.5f} lr=2e-05\n")
    t0 = time.time()
    try:
        quiet(ml_extract.main, ["--case", os.path.join(inp, "case.json"), "--out", os.path.join(d, "out"), "--work", os.path.join(d, "work")])
        dt = time.time() - t0
        stt = C.load_json(os.path.join(d, "work", "state.json"))
        cls = {f["path"]: f["class"] for f in stt["files"]}
        nf = len(C.load_json(os.path.join(d, "work", "facts.json"))["facts"])
        rec("binary_and_xlsx_skipped", cls.get("weights.pt") == "binary-skipped" and cls.get("results.xlsx") == "binary-skipped", str({k: v for k, v in cls.items() if k in ("weights.pt", "results.xlsx")}))
        rec("malformed_configs_no_crash", "configs/broken.yaml" in cls and "configs/broken.json" in cls, f"classes {cls.get('configs/broken.yaml')}/{cls.get('configs/broken.json')}")
        rec("huge_log_200k_lines", dt < 30 and nf < 3000, f"{dt:.1f} s, {nf} facts")
    except Exception as e:  # noqa
        rec("binary_and_xlsx_skipped", False, repr(e))
    # R4 no draft
    d = tempfile.mkdtemp(dir=tmp_root)
    out, work = run_extract("dev_wetlab", d)
    st, rep, r = quiet(ml_build.build, work, out)
    rec("no_draft_partial", r["status"] == "partial" and os.path.exists(os.path.join(out, "questions.md")), f"status={r['status']}")
    # R5 bad tags
    st, rep, r = build_with(work, out, "# Methods\n\n## Procedure\n\n1. Cells were seeded [[F99999]] and read at 570 nm [[FOO: bar]].\n2. Done [[@nofile.txt:3]].\n")
    codes = {x["code"] for x in rep.fails()}
    rec("bad_tags_reported", {"T01", "T03"} <= codes, f"fail codes {sorted(codes)}")
    # R6 determinism
    gold = open(os.path.join(GOLD, "dev_wetlab.md"), encoding="utf-8").read()
    build_with(work, out, gold)
    a = C.load_json(os.path.join(out, "result.json"))
    build_with(work, out, gold)
    b = C.load_json(os.path.join(out, "result.json"))
    for x in (a, b):
        x.pop("built_at", None)
        x.pop("change_records", None)
        x.pop("artifacts", None)
    rec("deterministic_rebuild", json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True), "result.json identical except timestamps/history")
    # R7 contract shapes + invalid agent.json
    d = tempfile.mkdtemp(dir=tmp_root)
    inp = os.path.join(d, "in")
    shutil.copytree(os.path.join(CASES, "dev_wetlab", "input"), inp)
    C.dump_json({"case_id": "shape", "output_contract": {"type": "object", "required": ["chapter", "param_rows", "evidence_map", "open_issues"],
                 "properties": {"chapter": {"type": "string"}, "param_rows": {"type": "array"}, "evidence_map": {"type": "array"}, "open_issues": {"type": "array"}}}},
                os.path.join(inp, "case.json"))
    quiet(ml_extract.main, ["--case", os.path.join(inp, "case.json"), "--out", os.path.join(d, "out"), "--work", os.path.join(d, "work")])
    with open(os.path.join(d, "work", "agent.json"), "w", encoding="utf-8") as fh:
        fh.write("{not json")
    with open(os.path.join(d, "work", "draft.md"), "w", encoding="utf-8") as fh:
        fh.write(gold)
    st, rep, r = quiet(ml_build.build, os.path.join(d, "work"), os.path.join(d, "out"))
    ok = isinstance(r.get("chapter"), str) and isinstance(r.get("param_rows"), list) and isinstance(r.get("evidence_map"), list) and isinstance(r.get("open_issues"), list)
    rec("json_schema_contract_mapped", ok, f"types: {[type(r.get(k)).__name__ for k in ('chapter', 'param_rows', 'evidence_map', 'open_issues')]}")
    rec("invalid_agent_json_ignored", any("agent.json invalid" in u for u in r["uncertainty"]), "noted in uncertainty")
    # R8 old draft in materials -> change records
    d = tempfile.mkdtemp(dir=tmp_root)
    inp = os.path.join(d, "in")
    shutil.copytree(os.path.join(CASES, "dev_sim", "input"), inp)
    with open(os.path.join(inp, "methods_draft_v1.md"), "w", encoding="utf-8") as fh:
        fh.write("# 2 计算方法\n\n采用 TIP4P/2005 水模型，时间步长 1 fs，模拟 1 ns。\n")
    quiet(ml_extract.main, ["--case", os.path.join(inp, "case.json"), "--out", os.path.join(d, "out"), "--work", os.path.join(d, "work")])
    st, rep, r = build_with(os.path.join(d, "work"), os.path.join(d, "out"), open(os.path.join(GOLD, "dev_sim.md"), encoding="utf-8").read())
    recs = r["change_records"]["against_input_draft"]
    rec("old_draft_diff_recorded", len(recs) > 0 and recs[0]["against"] == "methods_draft_v1.md", f"{len(recs)} change records")
    # R9 PDF + DOCX materials
    d = tempfile.mkdtemp(dir=tmp_root)
    inp = os.path.join(d, "in")
    os.makedirs(inp)
    C.dump_json({"case_id": "pdfdocx", "task": "Write the methods section in English."}, os.path.join(inp, "case.json"))
    ml_build.write_docx("# Protocol\n\nIncubate 30 min at 37 °C.\n\nRandom seed: 11\n", os.path.join(inp, "protocol.docx"))
    pdf_ok = False
    try:
        try:
            import pymupdf as fitz  # noqa
        except ImportError:
            import fitz  # noqa
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((72, 72), "Learning rate: 0.004\nBatch size: 48", fontsize=11)
        doc.save(os.path.join(inp, "notes.pdf"))
        pdf_ok = True
    except Exception:  # noqa
        pass
    quiet(ml_extract.main, ["--case", os.path.join(inp, "case.json"), "--out", os.path.join(d, "out"), "--work", os.path.join(d, "work")])
    fx = C.load_json(os.path.join(d, "work", "facts.json"))["facts"]
    got_docx = any(f["canon"] == "seed" and "11" in f["value"] for f in fx) and any(f["canon"] == "duration" for f in fx)
    got_pdf = any(f["canon"] == "learning_rate" and "0.004" in f["value"] for f in fx)
    rec("docx_material_read", got_docx, "seed 11 + incubation 30 min from DOCX")
    rec("pdf_material_read", got_pdf or not pdf_ok, "learning rate 0.004 from PDF" if pdf_ok else "PyMuPDF missing, skipped")
    # R10 v0.2: real xlsx material + multiline kwargs + section numbering 2.1.1 + python3/pip equiv + prose steps + new contract fields
    d = tempfile.mkdtemp(dir=tmp_root)
    inp = os.path.join(d, "in")
    os.makedirs(inp)
    C.dump_json({
        "case_id": "v02_features",
        "task": "Write the Methods section in English.",
        "output_contract": {"methods": "", "docx": "", "pdf": "", "param_table": "", "review": ""}
    }, os.path.join(inp, "case.json"))
    with open(os.path.join(inp, "requirements.txt"), "w", encoding="utf-8") as fh:
        fh.write("torch==2.2.1\n")
    with open(os.path.join(inp, "train.py"), "w", encoding="utf-8") as fh:
        fh.write("def run():\n    train_test_split(\n        data,\n        test_size=0.2,\n        random_state=42\n    )\n")
    with open(os.path.join(inp, "run.sh"), "w", encoding="utf-8") as fh:
        fh.write("python train.py --seed $SEED\n")
    with zipfile.ZipFile(os.path.join(inp, "metrics.xlsx"), "w") as z:
        z.writestr("xl/sharedStrings.xml", '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><si><t>metric</t></si><si><t>value</t></si><si><t>accuracy</t></si></sst>')
        z.writestr("xl/worksheets/sheet1.xml", '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="1"><c t="s"><v>0</v></c><c t="s"><v>1</v></c></row><row r="2"><c t="s"><v>2</v></c><c><v>0.915</v></c></row></sheetData></worksheet>')
    quiet(ml_extract.main, ["--case", os.path.join(inp, "case.json"), "--out", os.path.join(d, "out"), "--work", os.path.join(d, "work")])
    fx = C.load_json(os.path.join(d, "work", "facts.json"))["facts"]
    has_xlsx = any("0.915" in f["value"] for f in fx)
    has_ml_kw = any(f["canon"] == "split_seed" and "42" in f["value"] for f in fx)
    sseed = next(f["id"] for f in fx if f["canon"] == "split_seed")
    storch = next(f["id"] for f in fx if f["canon"] == "torch")
    sacc = next(f["id"] for f in fx if "0.915" in f["value"])
    draft_v02 = (
        "# 2 Methods\n\n"
        "## 2.1.1 Procedure\n\n"
        "First, data were split with seed 42 [[" + sseed + "]] (test fraction [[GAP: confirm test size 0.2]]). "
        "Next, the model was evaluated using PyTorch 2.2.1 [[" + storch + "]] reaching accuracy 0.915 [[" + sacc + "]]. "
        "Dataset details [[GAP: dataset name and version]], hardware [[GAP: GPU/CPU hardware]], "
        "hyperparameters [[GAP: optimizer, learning rate, batch size, epochs]], code version [[GAP: git commit]], and baseline [[GAP: baseline and repeats]].\n\n"
        "```bash\npip install -r requirements.txt\npython3 train.py --seed 42\n```\n\n"
        "## 2.1.2 Limitations\n\n"
        "- Only one seed 42 [[" + sseed + "]] was run; stage-2 was not tested.\n"
    )
    st, rep, r = build_with(os.path.join(d, "work"), os.path.join(d, "out"), draft_v02)
    ok_v02 = (
        has_xlsx and has_ml_kw and st == "success"
        and isinstance(r.get("methods"), str) and bool(r.get("docx")) and bool(r.get("param_table")) and bool(r.get("review"))
    )
    rec("v02_xlsx_multiline_secnum_cmds", ok_v02, f"xlsx={has_xlsx} ml_kw={has_ml_kw} status={st} fails={[x['code'] for x in rep.fails()]}")
    return res


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", default="all", choices=["dev", "holdout", "all"])
    ap.add_argument("--out", default=os.path.join(ROOT, "execution", "results"))
    ap.add_argument("--tag", default="")
    ap.add_argument("--no-robustness", action="store_true")
    a = ap.parse_args()
    names = sorted(n for n in os.listdir(CASES) if (a.cases == "all" or n.startswith("dev_" if a.cases == "dev" else "ho_")))
    tmp_root = tempfile.mkdtemp(prefix="ml_eval_")
    t0 = time.time()
    ext_rows, gold_rows, mut_rows = [], [], []
    for case in names:
        exp = C.load_json(os.path.join(EXPECT, case + ".json"), {})
        tmp = tempfile.mkdtemp(dir=tmp_root)
        out, work = run_extract(case, tmp)
        st = C.load_json(os.path.join(work, "state.json"))
        PROFILE[case] = st["profile"]
        ext_rows.append(score_extraction(case, work))
        gpath = os.path.join(GOLD, case + ".md")
        if not os.path.exists(gpath):
            continue
        gold = open(gpath, encoding="utf-8").read()
        status, rep, result = build_with(work, out, gold)
        keep = os.path.join(a.out, "cases", case)
        if os.path.exists(keep):
            shutil.rmtree(keep)
        shutil.copytree(out, os.path.join(keep, "output"))
        os.makedirs(os.path.join(keep, "work"), exist_ok=True)
        for fn in ("facts.md", "facts.json", "state.json", "draft.md", "agent.json"):
            if os.path.exists(os.path.join(work, fn)):
                shutil.copy(os.path.join(work, fn), os.path.join(keep, "work", fn))
        gold_rows.append({"case": case, "status": status, "fails": [f"{x['code']} l.{x.get('line')}: {x['msg']}" for x in rep.fails()],
                          "warns": len(rep.warns()), "warn_codes": sorted({x["code"] for x in rep.warns()}), "facts_cited": len(result["facts_cited"]),
                          "questions": len(result["needs_confirmation"]), "coverage": {c["element"]: c["status"] for c in result["checks"]["coverage"]}})
        fx = C.load_json(os.path.join(work, "facts.json"))
        corpus_low = "\n".join(ml_build.material_corpus(st).values()).lower()
        for mid, mtype, text, expected, note in mutations(case, gold, st["lang"], fx["facts"], corpus_low):
            os.environ["ML_NO_PREVIEW"] = "1"
            s2, rep2, r2 = build_with(work, os.path.join(tmp, "mut_out"), text)
            os.environ.pop("ML_NO_PREVIEW", None)
            fails = {x["code"] for x in rep2.fails()}
            allc = fails | {x["code"] for x in rep2.warns()}
            mut_rows.append({"case": case, "id": mid, "type": mtype, "note": note, "expected": sorted(expected),
                             "caught_fail": bool(fails & expected), "caught_any": bool(allc & expected),
                             "any_new_fail": bool(fails), "fail_codes": sorted(fails), "warn_codes": sorted(allc - fails),
                             "baseline_grep": naive_grep_catch(text, corpus_low), "baseline_checklist": checklist_catch(fails)})
    rob = [] if a.no_robustness else robustness(tmp_root)
    # metrics
    def rate(rows, key):
        return round(sum(1 for r in rows if r[key]) / len(rows), 4) if rows else None
    ftot = sum(r["facts_expected"] for r in ext_rows)
    ffound = sum(r["facts_found"] for r in ext_rows)
    ctot = sum(len(r["conflicts_expected"]) for r in ext_rows)
    cfound = sum(len(r["conflicts_found"]) for r in ext_rows)
    cunexp = sum(len(r["conflicts_unexpected"]) for r in ext_rows)
    gtot = sum(len(r["gaps_expected"]) for r in ext_rows)
    gfound = sum(len(r["gaps_found"]) for r in ext_rows)
    by_type = {}
    for r in mut_rows:
        b = by_type.setdefault(r["type"], {"n": 0, "caught_fail": 0, "caught_any": 0, "baseline_grep": 0, "baseline_checklist": 0})
        b["n"] += 1
        for k in ("caught_fail", "caught_any", "baseline_grep", "baseline_checklist"):
            b[k] += int(r[k])
    metrics = {
        "tag": a.tag, "cases": names, "seconds": round(time.time() - t0, 1),
        "extraction": {"fact_recall": round(ffound / ftot, 4) if ftot else None, "facts_expected": ftot, "facts_found": ffound,
                       "conflict_recall": round(cfound / ctot, 4) if ctot else None, "conflicts_expected": ctot, "conflicts_found": cfound,
                       "conflicts_unexpected": cunexp, "conflict_precision": round(cfound / (cfound + cunexp), 4) if (cfound + cunexp) else None,
                       "gap_recall": round(gfound / gtot, 4) if gtot else None, "gaps_expected": gtot, "gaps_found": gfound,
                       "profile_correct": sum(1 for r in ext_rows if r["profile_expected"] in (None, r["profile"].split("+")[0])), "language_correct": sum(1 for r in ext_rows if r["lang_expected"] in (None, r["lang"]))},
        "gold_drafts": {"n": len(gold_rows), "without_fail": sum(1 for g in gold_rows if not g["fails"])},
        "mutations": {"n": len(mut_rows), "caught_fail": rate(mut_rows, "caught_fail"), "caught_any": rate(mut_rows, "caught_any"),
                      "baseline_grep": rate(mut_rows, "baseline_grep"), "baseline_checklist": rate(mut_rows, "baseline_checklist"), "by_type": by_type},
        "robustness": {"n": len(rob), "passed": sum(1 for r in rob if r["pass"]), "failed": [r["check"] for r in rob if not r["pass"]]},
    }
    os.makedirs(a.out, exist_ok=True)
    sfx = ("_" + a.tag) if a.tag else ""
    C.dump_json(metrics, os.path.join(a.out, f"metrics{sfx}.json"))
    C.dump_json({"extraction": ext_rows, "gold": gold_rows, "mutations": mut_rows, "robustness": rob}, os.path.join(a.out, f"eval_rows{sfx}.json"))
    print(json.dumps(metrics, ensure_ascii=False, indent=1))
    shutil.rmtree(tmp_root, ignore_errors=True)


if __name__ == "__main__":
    main()
