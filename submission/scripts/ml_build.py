"""Step 2 of methods-ledger: check the agent's draft (work/draft.md) against the extracted facts and build every output.

python ml_build.py --work /app/work --out /app/output
Exit 0 = chapter built (status success; flagged items are marked inline and listed for the author), 1 = no draft text yet
(status partial), 2 = no state (run ml_extract first), 3 = internal error (an existing result.json is left untouched).
Tag slips (unknown/malformed tags, untagged or mis-tagged numbers) never block: numbers are auto-aligned to the fact ledger.

Draft tags: [[F12]] / [[F12,F30]] cite facts · [[GAP: question]] missing information · [[CONFIRM: C1 ...]] conflicting or
assumed value the author must confirm · [[CALC: 8000/10000 = 0.8 | F3,F4]] derived number · [[SRC: file:line]] material line
not in facts.md · [[PARAM_TABLE]] where the generated parameter table goes."""
import argparse
import datetime
import difflib
import hashlib
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ml_common as C  # noqa: E402

TAG_RE = re.compile(r"\[\[(.*?)\]\]", re.S)
FIDS_RE = re.compile(r"^\s*F\d+(?:\s*[,，;；\s]\s*F\d+)*\s*$")
EXEMPT_BEFORE = re.compile(r"(?i)(?:step|stage|phase|section|sec\.|§|table|tab\.|fig\.|figure|eq\.|equation|algorithm|alg\.|appendix|chapter|line|lines|see|cf\.|步骤|阶段|表|图|式|公式|算法|附录|第|章|节|行|见|参见|详见)\s*\(?$|(?-i:(?<![A-Za-z])[CGFQ])\s*$")
EXEMPT_AFTER = re.compile(r"^\s*(?:章|节|步|部分)")
CITE_RE = re.compile(r"\[\d+(?:\s*[,–\-]\s*\d+)*\]|et al\.?,?\s*\(?\d{4}[a-z]?\)?|\([A-Z][A-Za-z\-]+(?: et al\.?| and [A-Z][A-Za-z\-]+)?,?\s*\d{4}[a-z]?\)")
LIST_MARK_RE = re.compile(r"^\s*(?:[-*+]\s+)?(?:\(?\d+[.)、）]|（\d+）|\d+\.\d+(?:\.\d+)*\s|step\s*\d+\s*[:：.]?|步骤\s*\d+\s*[:：.]?|第[一二三四五六七八九十\d]+步)", re.I)
PLACEHOLDER_RE = re.compile(r"(?<![A-Za-z])(?:XX+|xx+|TBD|TODO|\?\?+|N/A|待补充|待定|若干|某某)(?![A-Za-z])|＿{2,}|_{3,}")
UNIT_CONSTANTS = {10.0 ** k for k in range(-12, 13)} | {60.0, 24.0, 3600.0, 1024.0, 86400.0, 2.0, 0.5}
LIMIT_HEAD_RE = re.compile(r"(?i)limitation|threats? to validity|caveat|scope|failure|局限|限制|不足|失效|适用范围|边界")
PARAM_HEAD_RE = re.compile(r"(?i)param|hyper|参数")
STRUCT_NAME_SKEL = re.compile(r"^(?:stage|step|phase|fold|epoch|run|seed|layer|block|top|fig|tab|eq|sec|part|group|batch|trial|iter|round|v)-?#+$|^#d$|^l#$")
PROSE_STEP_RE = re.compile(r"(?i)\b(?:first(?:ly)?|second(?:ly)?|third(?:ly)?|next|then|subsequently|finally|step\s*\d+)\b|首先|其次|随后|接着|然后|最后|第[一二三四五六七八九十\d]+步")


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------- draft parsing

def parse_draft(text):
    """Units: headings, sentences of paragraphs/list items, table rows, code blocks. Each unit keeps its line,
    section path, raw text (with tags) and tag-free text."""
    text = re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    lines = text.split("\n")
    units, section, code, code_buf, code_start = [], [], False, [], 0
    para, para_start = [], 0

    def flush_para():
        nonlocal para
        if not para:
            return
        block = " ".join(x.strip() for x in para)
        for s in split_sentences(block):
            units.append(mk_unit("sentence", s, para_start, section, list_item=bool(LIST_MARK_RE.match(para[0]))))
        para = []
    for i, line in enumerate(lines, 1):
        s = line.rstrip()
        if s.strip().startswith("```"):
            if code:
                units.append(mk_unit("code", "\n".join(code_buf), code_start, section))
                code, code_buf = False, []
            else:
                flush_para()
                code, code_start = True, i
            continue
        if code:
            code_buf.append(s)
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            flush_para()
            level = len(m.group(1))
            section = section[:level - 1] + [m.group(2).strip()]
            units.append(mk_unit("heading", m.group(2).strip(), i, section, level=level))
            continue
        if s.strip().startswith("|"):
            flush_para()
            if re.match(r"^\s*\|?\s*:?-{2,}", s):
                continue
            units.append(mk_unit("table_row", s.strip(), i, section))
            continue
        if not s.strip():
            flush_para()
            continue
        if LIST_MARK_RE.match(s) and para:
            flush_para()
        if not para:
            para_start = i
        para.append(s)
    flush_para()
    if code and code_buf:
        units.append(mk_unit("code", "\n".join(code_buf), code_start, section))
    # tags at the very start of a sentence belong to the previous sentence
    for k in range(1, len(units)):
        u = units[k]
        m = re.match(r"^\s*((?:\[\[[^\]]*\]\]\s*)+)", u["raw"])
        if m and u["type"] == "sentence" and units[k - 1]["type"] == "sentence" and units[k - 1]["line"] == u["line"]:
            units[k - 1]["raw"] += " " + m.group(1).strip()
            u["raw"] = u["raw"][m.end():]
            for uu in (units[k - 1], u):
                refresh_unit(uu)
    for n, u in enumerate(units, 1):
        u["uid"] = f"u{n}"
    return [u for u in units if u["raw"].strip()]


def split_sentences(block):
    parts, buf, i = [], "", 0
    # protect tags and decimals
    tokens = re.split(r"(\[\[.*?\]\])", block)
    out = []
    for t in tokens:
        if t.startswith("[["):
            if out:
                out[-1] += t
            else:
                out.append(t)
            continue
        pieces = re.split(r"(?<=[。！？；])|(?<=[.!?])\s+(?=[A-Z一-鿿(\[`*])|(?<=[.!?])(?=\[\[)", t)
        for j, p in enumerate(pieces):
            if p is None:
                continue
            if j == 0 and out and not re.search(r"[。！？；.!?]\s*(\[\[.*?\]\])*\s*$", out[-1]):
                out[-1] += p
            else:
                out.append(p)
    return [o.strip() for o in out if o and o.strip()]


def mk_unit(kind, raw, line, section, level=None, list_item=False):
    u = {"type": kind, "raw": raw, "line": line, "section": " > ".join(section), "section_leaf": section[-1] if section else "", "level": level,
         "list_item": list_item}
    refresh_unit(u)
    return u


def refresh_unit(u):
    u["tags"] = [t.strip() for t in TAG_RE.findall(u["raw"])]
    u["text"] = re.sub(r"\s+", " ", TAG_RE.sub(" ", u["raw"])).strip() if u["type"] != "code" else TAG_RE.sub("", u["raw"])


def parse_tags(tags):
    out = {"facts": [], "gaps": [], "confirms": [], "calcs": [], "srcs": [], "param_table": False, "bad": []}
    for t in tags:
        if FIDS_RE.match(t):
            out["facts"] += re.findall(r"F\d+", t)
            continue
        m = re.match(r"^(GAP|待确认|缺失|缺口|TODO|MISSING)\s*[:：]\s*(.*)$", t, re.S | re.I)
        if m:
            out["gaps"].append(m.group(2).strip())
            continue
        m = re.match(r"^(CONFIRM|确认|冲突|ASSUME|假设)\s*[:：]\s*(.*)$", t, re.S | re.I)
        if m:
            out["confirms"].append(m.group(2).strip())
            out["facts"] += re.findall(r"\bF\d+\b", m.group(2))
            continue
        m = re.match(r"^CALC\s*[:：]\s*(.*?)\s*=\s*([^|=]+?)\s*(?:\|\s*(.*))?$", t, re.S | re.I)
        if m:
            out["calcs"].append({"expr": m.group(1), "result": m.group(2), "facts": re.findall(r"F\d+", m.group(3) or "")})
            continue
        m = re.match(r"^SRC\s*[:：]\s*(.+?):(\d+)(?:-(\d+))?\s*$", t, re.I)
        if m:
            out["srcs"].append({"file": m.group(1).strip(), "line": int(m.group(2)), "end": int(m.group(3) or m.group(2))})
            continue
        if re.match(r"^(PARAM_TABLE|参数表)$", t.strip(), re.I):
            out["param_table"] = True
            continue
        out["bad"].append(t)
    return out



LOOSE_FIDS = r"[Ff]\s?\d+(?:\s*[,，;；、/]\s*[Ff]\s?\d+)*"


def normalize_tags(text):
    """Repair common tag slips so they count as citations: [F12] / 【F12】 / (F12) / [[f 12; F13]] / [[ GAP - x ]]."""
    n = [0]

    def fid(m):
        n[0] += 1
        return "[[" + ",".join("F" + x for x in re.findall(r"\d+", m.group(1))) + "]]"
    text = re.sub(r"(?<!\[)\[\s*(" + LOOSE_FIDS + r")\s*\](?!\]|\()", fid, text)
    text = re.sub(r"【\s*(" + LOOSE_FIDS + r")\s*】", fid, text)
    text = re.sub(r"[(（]\s*(" + LOOSE_FIDS + r")\s*[)）]", fid, text)

    def inner(m):
        b = m.group(1)
        if re.fullmatch(r"\s*" + LOOSE_FIDS + r"\s*", b) and not FIDS_RE.match(b):
            n[0] += 1
            return "[[" + ",".join("F" + x for x in re.findall(r"\d+", b)) + "]]"
        mm = re.match(r"^\s*(GAP|CONFIRM|CALC|SRC)\s*[-—–]\s*(.*)$", b, re.S | re.I)
        if mm:
            n[0] += 1
            return f"[[{mm.group(1).upper()}: {mm.group(2)}]]"
        return m.group(0)
    text = TAG_RE.sub(inner, text)
    return text, n[0]


ANCHOR_RE = re.compile(r"@([^\s\[\],;，；:]+):(\d+)(?:#([^\s\],;，；]+))?")


def resolve_anchors(text, facts):
    """[[@file:line]] / [[@file:line#key]] (also inside a multi-tag) -> the fact ids on that line (stable across re-extraction).
    A line without a structured fact becomes [[SRC: file:line]]."""
    notes = []
    byloc = {}
    for f in facts:
        byloc.setdefault((f["file"], f["line"]), []).append(f)

    def one(m):
        file, line, key = m.group(1), int(m.group(2)), m.group(3)
        cands = byloc.get((file, line)) or next((v for (fl, ln), v in byloc.items() if ln == line and fl.endswith(file)), [])
        if key:
            sel = [f for f in cands if f["path"] == key or f["key"] == key or f["path"].endswith("." + key) or f["canon"] == key]
        else:
            sel = cands
        if not sel:
            return None
        return ",".join(f["id"] for f in sel[:6])

    def tag(m):
        body = m.group(1)
        if "@" not in body or re.match(r"^\s*(GAP|CONFIRM|CALC|SRC|待确认|确认|ASSUME)", body, re.I):
            if "@" in body and re.match(r"^\s*(CALC|CONFIRM)", body, re.I):
                return "[[" + ANCHOR_RE.sub(lambda mm: one(mm) or f"{mm.group(1)}:{mm.group(2)}", body) + "]]"
            return m.group(0)
        parts, srcs = [], []
        for mm in ANCHOR_RE.finditer(body):
            r = one(mm)
            if r:
                parts.append(r)
            else:
                srcs.append(f"[[SRC: {mm.group(1)}:{mm.group(2)}]]")
        rest = ANCHOR_RE.sub("", body).strip(" ,;")
        if rest:
            parts.append(rest)
        out = ("[[" + ",".join(parts) + "]]" if parts else "") + "".join(srcs)
        return out or m.group(0)
    new = TAG_RE.sub(tag, text)
    return new, notes


def split_spans(raw):
    """[(clause_text_without_tags, [tags that follow it])]. A tag covers the text since the previous tag group;
    text after the last tag group is returned with an empty tag list (untagged)."""
    out, pos, cur_tags, buf = [], 0, [], ""
    for m in TAG_RE.finditer(raw):
        seg = raw[pos:m.start()]
        if seg.strip() and cur_tags:
            out.append((buf, cur_tags))
            buf, cur_tags = "", []
        buf += seg
        cur_tags.append(m.group(1).strip())
        pos = m.end()
    if cur_tags:
        out.append((buf, cur_tags))
        buf = ""
    buf += raw[pos:]
    if buf.strip():
        out.append((buf, []))
    return out


def safe_eval(expr):
    expr = expr.replace("×", "*").replace("÷", "/").replace("−", "-").replace("^", "**").replace(",", "")
    expr = re.sub(r"(\d+(?:\.\d+)?)\s*%", r"(\1/100)", expr)
    if not re.match(r"^[\d\s.+\-*/()eE]+$", expr):
        return None
    try:
        return float(eval(expr, {"__builtins__": {}}, {}))  # noqa: S307 - digits and operators only
    except Exception:  # noqa
        return None


# ---------------------------------------------------------------- checks

class Report:
    def __init__(self):
        self.items = []

    def add(self, level, code, msg, uid=None, line=None, **kw):
        d = {"level": level, "code": code, "msg": msg, "unit": uid, "line": line}
        d.update(kw)
        self.items.append(d)

    def fails(self):
        return [x for x in self.items if x["level"] == "fail"]

    def warns(self):
        return [x for x in self.items if x["level"] == "warn"]


def material_corpus(state):
    texts = {}
    for fi in state["files"]:
        if fi["class"] in ("binary-skipped", "unreadable", "too-large"):
            continue
        p = os.path.join(state["input_dir"], fi["path"]) if not os.path.isabs(fi["path"]) else fi["path"]
        try:
            t = C.read_any(p)[0]
            if p.lower().endswith(".ipynb"):
                from ml_extract import notebook_text
                t = notebook_text(t)
            texts[fi["path"]] = t
        except Exception:  # noqa
            pass
    return texts


def equivalents_for(f, v, pct):
    """80% <-> 0.8 only when one side is written as a percentage (not 0.37 <-> 37 degC)."""
    eq = {v}
    if pct:
        eq.add(v / 100.0)
    elif 0 < abs(v) <= 1 and ("%" in f["value"] or re.search(r"(?i)pct|percent|百分", f["path"] + " " + f.get("context", ""))):
        eq.add(v * 100.0)
    return eq


def fact_matches_value(f, v, pct):
    eq = equivalents_for(f, v, pct)
    for x in f["nums"]:
        for e in eq:
            if C.nums_close(x, e):
                return "exact"
    for x in f["nums"]:
        for e in eq:
            if C.rounds_to(e, x):
                return "rounded"
    return None


def build_index(facts):
    idx = {}
    for f in facts:
        for x in f["nums"]:
            idx.setdefault(round(x, 9), []).append(f)
    return idx


def lookup_any(idx, facts, v, pct):
    out = []
    for e in C.num_equivalents(v, pct):
        out += [f for f in idx.get(round(e, 9), []) if fact_matches_value(f, v, pct) == "exact"]
    if not out:
        for f in facts:
            if fact_matches_value(f, v, pct) == "rounded":
                out.append(f)
                if len(out) > 5:
                    break
    seen, res = set(), []
    for f in out:
        if f["id"] not in seen:
            seen.add(f["id"])
            res.append(f)
    return res


def auto_cite(cands):
    """An auto-aligned number counts as a citation only when every candidate fact names the same parameter."""
    return bool(cands) and len({c["canon"] or c["path"] for c in cands}) == 1


def exempt_number(text, start, end, tok):
    before = text[max(0, start - 14):start]
    after = text[end:end + 4]
    if EXEMPT_BEFORE.search(before) or EXEMPT_AFTER.match(after):
        return True
    for m in CITE_RE.finditer(text):
        if m.start() <= start and end <= m.end():
            return True
    return False


def only_gap_sent(raw):
    tags = [t.strip() for t in TAG_RE.findall(raw)]
    if not tags:
        return False
    tg = parse_tags(tags)
    return bool((tg["gaps"] or tg["confirms"]) and not (tg["facts"] or tg["calcs"] or tg["srcs"]))


def check_units(units, facts, conflicts, gaps, state, agent, corpus, rep):
    byid = {f["id"]: f for f in facts}
    idx = build_index(facts)
    conf_of = {}
    for c in conflicts:
        for fid in c["facts"]:
            conf_of.setdefault(fid, []).append(c)
    resolved = {r.get("conflict") or r.get("id"): r for r in (agent.get("resolutions") or []) if isinstance(r, dict)}
    accept = agent.get("accept") or {}
    corpus_low = "\n".join(corpus.values()).lower()
    corpus_lines = {p: t.split("\n") for p, t in corpus.items()}
    cited, fact_map = set(), []
    lang = state["lang"]
    for u in units:
        tg = parse_tags(u["tags"])
        u["parsed"] = tg
        entry = {"unit": u["uid"], "line": u["line"], "type": u["type"], "section": u["section"], "text": u["text"][:400],
                 "facts": [], "numbers": [], "gaps": tg["gaps"], "confirms": tg["confirms"], "status": "ok"}
        for b in tg["bad"]:
            rep.add("warn", "T03", f"unknown tag [[{b[:60]}]] (use F-ids, GAP:, CONFIRM:, CALC:, SRC:, PARAM_TABLE)", u["uid"], u["line"])
        tagged = []
        for fid in tg["facts"]:
            f = byid.get(fid)
            if not f:
                rep.add("warn", "T01", f"tag cites {fid}, which does not exist in facts.json", u["uid"], u["line"])
                continue
            tagged.append(f)
            cited.add(fid)
            entry["facts"].append({"id": fid, "value": f["value"][:120], "source": f"{f['file']}:{f['line']}", "kind": f["kind"], "key": f["path"]})
        calc_vals, calc_ok, calc_results = [], True, {}
        for cc in tg["calcs"]:
            res = safe_eval(cc["expr"])
            stated = C.parse_num(cc["result"].strip().split()[0]) if C.num_tokens(cc["result"]) else None
            if stated is None and C.num_tokens(cc["result"]):
                stated = C.num_tokens(cc["result"])[0][1]
            if res is None or stated is None or not (C.nums_close(res, stated, 1e-3) or C.rounds_to(stated, res)):
                rep.add("fail", "K10", f"CALC '{cc['expr']} = {cc['result']}' does not evaluate (got {res})", u["uid"], u["line"])
                calc_ok = False
                continue
            # operands must be traceable
            for tok, v, pct, s, e in C.num_tokens(cc["expr"]):
                pool = [byid[x] for x in cc["facts"] if x in byid] + tagged
                if v in UNIT_CONSTANTS:
                    continue
                if not any(fact_matches_value(f, v, pct) for f in pool) and not lookup_any(idx, facts, v, pct):
                    rep.add("fail", "K11", f"CALC operand {tok} is not a value in the materials", u["uid"], u["line"])
                    calc_ok = False
            for x in cc["facts"]:
                if x in byid:
                    cited.add(x)
                    entry["facts"].append({"id": x, "value": byid[x]["value"][:120], "source": f"{byid[x]['file']}:{byid[x]['line']}", "kind": byid[x]["kind"], "key": byid[x]["path"], "via": "calc"})
            calc_vals.append(stated)
            calc_vals.append(res)
        src_nums = []
        for sr in tg["srcs"]:
            ls = corpus_lines.get(sr["file"]) or next((v for k, v in corpus_lines.items() if k.endswith(sr["file"])), None)
            if not ls or sr["line"] < 1 or sr["line"] > len(ls):
                rep.add("warn", "T06", f"[[SRC: {sr['file']}:{sr['line']}]] does not point to a line of a material file", u["uid"], u["line"])
                continue
            seg = "\n".join(ls[sr["line"] - 1:sr["end"]])
            src_nums += [(t[1], t[2]) for t in C.num_tokens(seg)]
            entry["facts"].append({"id": f"SRC:{sr['file']}:{sr['line']}", "value": seg.strip()[:160], "source": f"{sr['file']}:{sr['line']}", "kind": "source-line"})
        if u["type"] == "heading":
            fact_map.append(entry)
            continue
        if u["type"] == "code":
            check_code(u, facts, corpus, corpus_low, rep, entry, state=state)
            fact_map.append(entry)
            continue
        text = u["text"]
        for m in re.finditer(r"`([^`]{6,})`", text):
            if re.match(r"^\$?\s*(python3?|torchrun|accelerate|deepspeed|bash|sh|Rscript|julia|gmx|lmp|mpirun|srun|sbatch|make)\b", m.group(1)):
                check_code({"text": m.group(1), "uid": u["uid"], "line": u["line"] - 1}, facts, corpus, corpus_low, rep, entry, state=state)
        if PLACEHOLDER_RE.search(text):
            rep.add("fail", "M01", f"placeholder '{PLACEHOLDER_RE.search(text).group(0)}' in text: write [[GAP: ...]] instead", u["uid"], u["line"], token=PLACEHOLDER_RE.search(text).group(0))
        unit_vals = set()
        for f in tagged:
            unit_vals.update(round(x, 9) for x in f["nums"])
        spans = split_spans(u["raw"])
        for si, (stext, stags) in enumerate(spans):
            stg = parse_tags(stags) if stags else None
            s_tagged = [byid[x] for x in (stg["facts"] if stg else []) if x in byid]
            for cc in (stg["calcs"] if stg else []):
                s_tagged += [byid[x] for x in cc["facts"] if x in byid]
            s_calc = [cv for cc in (stg["calcs"] if stg else []) for cv in calc_results.get(id(cc), [])] if stg else []
            if stg:
                for cc in stg["calcs"]:
                    r = safe_eval(cc["expr"])
                    if r is not None:
                        s_calc.append(r)
                        st = C.num_tokens(cc["result"])
                        if st:
                            s_calc.append(st[0][1])
            s_src, s_src_ok = [], False
            for sr in (stg["srcs"] if stg else []):
                ls = corpus_lines.get(sr["file"]) or next((v for k, v in corpus_lines.items() if k.endswith(sr["file"])), None)
                if ls and 1 <= sr["line"] <= len(ls):
                    s_src_ok = True
                    s_src +=[(t[1], t[2]) for t in C.num_tokens("\n".join(ls[sr["line"] - 1:sr["end"]]))]
            lm = LIST_MARK_RE.match(stext) if si == 0 else None
            body_start = lm.end() if lm else 0
            covered = bool(stg and (stg["facts"] or stg["calcs"] or stg["srcs"]))
            only_gap = bool(stg and not covered and (stg["gaps"] or stg["confirms"]))
            for tok, v, pct, st_, en_ in C.num_tokens(stext):
                if st_ < body_start or exempt_number(stext, st_, en_, tok):
                    continue
                rec = {"token": tok, "value": v}
                hit = None
                for f in s_tagged:
                    r = fact_matches_value(f, v, pct)
                    if r:
                        hit = (f, r)
                        break
                if hit:
                    rec.update({"matched": hit[0]["id"], "how": "tag" + ("-rounded" if hit[1] == "rounded" else "")})
                    if hit[1] == "rounded":
                        rep.add("warn", "N05", f"{tok} is {hit[0]['id']}={hit[0]['value'][:30]} rounded; state the rounding or give the exact value", u["uid"], u["line"])
                    entry["numbers"].append(rec)
                    continue
                if any(C.nums_close(v, cv, 1e-3) or C.rounds_to(v, cv) or (pct and C.nums_close(v / 100, cv, 1e-3)) for cv in s_calc):
                    rec.update({"matched": "CALC", "how": "calc"})
                    entry["numbers"].append(rec)
                    continue
                if any(C.nums_close(x, e2) for x, p2 in s_src for e2 in C.num_equivalents(v, pct)):
                    rec.update({"matched": "SRC", "how": "source-line"})
                    entry["numbers"].append(rec)
                    continue
                other_tag = next((f for f in tagged if fact_matches_value(f, v, pct)), None)
                if other_tag and covered and not (v == int(v) and abs(v) <= 3 and not pct):
                    names = ", ".join(f"{f['id']}={f['value'][:25]}" for f in s_tagged)[:160]
                    rec.update({"matched": None, "candidates": [other_tag["id"]], "how": "mismatch-other-clause"})
                    rep.add("fail", "T02", f"{tok} is not the value of the fact(s) tagged on this clause ({names}); it is the value of {other_tag['id']} "
                            f"({other_tag['path']}), tagged on another clause - move the tag or correct the value", u["uid"], u["line"], token=tok)
                    entry["status"] = "mismatch"
                    entry["numbers"].append(rec)
                    continue
                if other_tag:
                    rec.update({"matched": other_tag["id"], "how": "tag-elsewhere-in-sentence"})
                    if covered:
                        rep.add("warn", "T07", f"{tok} is supported by {other_tag['id']}, which is tagged on another clause of the sentence", u["uid"], u["line"])
                    entry["numbers"].append(rec)
                    continue
                cands = lookup_any(idx, facts, v, pct)
                small = v == int(v) and abs(v) <= 3 and not pct
                if covered:
                    names = ", ".join(f"{f['id']}={f['value'][:25]}" for f in s_tagged)[:160]
                    if cands and (s_tagged or s_src_ok):
                        # a valid tag points at another value: a real mismatch, kept for review (non-blocking)
                        rec.update({"matched": None, "candidates": [c["id"] for c in cands[:6]], "how": "mismatch"})
                        rep.add("fail", "T02", f"{tok} is cited as {names}, but in the materials it is the value of "
                                f"{', '.join(c['id'] + '=' + c['path'] for c in cands[:3])} ({cands[0]['file']}:{cands[0]['line']}) - check which parameter is meant",
                                u["uid"], u["line"], token=tok, candidates=[c["id"] for c in cands[:6]])
                        entry["status"] = "mismatch"
                    elif cands:
                        rec.update({"matched": cands[0]["id"], "candidates": [c["id"] for c in cands[:6]], "how": "auto-aligned"})
                        if auto_cite(cands):
                            cited.add(cands[0]["id"])
                        rep.add("warn", "T02", f"{tok} is not the value of the tagged fact(s) ({names}); auto-aligned to "
                                f"{', '.join(c['id'] for c in cands[:3])} ({cands[0]['file']}:{cands[0]['line']})",
                                u["uid"], u["line"], token=tok, candidates=[c["id"] for c in cands[:6]])
                    elif small:
                        rec.update({"matched": None, "how": "small-integer"})
                        rep.add("info", "N06", f"small integer {tok} not traced (enumeration?)", u["uid"], u["line"])
                    else:
                        rec.update({"matched": None, "how": "none"})
                        rep.add("fail", "N01", f"number {tok} has no source in the materials (clause tagged {names}) - use the sourced value or write [[GAP: ...]]",
                                u["uid"], u["line"], token=tok)
                        entry["status"] = "unsourced"
                    entry["numbers"].append(rec)
                    continue
                if cands:
                    # Check for unit mismatch (e.g. 24 min vs 24 h) or parameter-name mismatch (e.g. learning rate vs subsample)
                    tok_pos = text.find(tok)
                    after_tok = text[tok_pos + len(tok):tok_pos + len(tok) + 16].lower() if tok_pos >= 0 else ""
                    u_tok = re.match(r"^\s*(h|hr|hrs|hour|hours|min|mins|minute|minutes|s|sec|secs|second|seconds|ms|gb|mb|kb)\b", after_tok)
                    unit_norm = {"h": "h", "hr": "h", "hrs": "h", "hour": "h", "hours": "h",
                                 "min": "min", "mins": "min", "minute": "min", "minutes": "min",
                                 "s": "s", "sec": "s", "secs": "s", "second": "s", "seconds": "s", "ms": "ms",
                                 "gb": "gb", "mb": "mb", "kb": "kb"}
                    t_unit = unit_norm.get(u_tok.group(1)) if u_tok else None
                    f0_ctx = (cands[0].get("value", "") + " " + cands[0].get("context", "")).lower()
                    f_unit_m = re.search(r"\b(h|hr|hrs|hour|hours|min|mins|minute|minutes|s|sec|secs|second|seconds|ms|gb|mb|kb)\b", f0_ctx)
                    f_unit = unit_norm.get(f_unit_m.group(1)) if f_unit_m else None
                    unit_mismatch = bool(t_unit and f_unit and t_unit != f_unit)
                    sent_low = text.lower()
                    param_mismatch = bool(
                        (re.search(r"\blearning[_ ]rate\b|\blr\b", sent_low) and cands[0].get("canon") not in (None, "lr", "learning_rate"))
                        or (re.search(r"\bbatch[_ ]size\b", sent_low) and cands[0].get("canon") not in (None, "batch_size"))
                        or (re.search(r"\bsubsample\b", sent_low) and cands[0].get("canon") not in (None, "subsample"))
                    )
                    if unit_mismatch or param_mismatch:
                        why = f"unit mismatch ({t_unit} vs {f_unit})" if unit_mismatch else f"parameter mismatch (candidate {cands[0].get('key')})"
                        rec.update({"matched": None, "candidates": [c["id"] for c in cands[:6]], "how": "mismatch-untagged"})
                        rep.add("warn", "N03", f"{tok} untagged and {why}; candidate {', '.join(c['id'] for c in cands[:4])}", u["uid"], u["line"],
                                candidates=[c["id"] for c in cands[:6]])
                    else:
                        rec.update({"matched": cands[0]["id"] if not small else None, "candidates": [c["id"] for c in cands[:6]], "how": "auto-aligned-untagged" if not small else "untagged"})
                        if not small:
                            if auto_cite(cands):
                                cited.add(cands[0]["id"])
                            rep.add("warn", "N03", f"{tok} untagged; auto-aligned to {', '.join(c['id'] for c in cands[:4])} ({cands[0]['file']}:{cands[0]['line']})", u["uid"], u["line"],
                                    candidates=[c["id"] for c in cands[:6]])
                elif re.search(r"(?<![\w.])" + re.escape(tok.replace(",", "")) + r"(?![\w]|\.\d)", corpus_low):
                    rec.update({"matched": None, "how": "literal-in-materials"})
                    rep.add("warn", "N04", f"{tok} appears in the materials but not as an extracted fact: add [[SRC: file:line]]", u["uid"], u["line"])
                elif small:
                    rec.update({"matched": None, "how": "small-integer"})
                    rep.add("info", "N06", f"small integer {tok} not traced (enumeration?)", u["uid"], u["line"])
                elif only_gap:
                    rec.update({"matched": None, "how": "inside-gap-clause"})
                    rep.add("warn", "N07", f"{tok} has no source; the clause is marked GAP/CONFIRM - keep it only if the author supplied it", u["uid"], u["line"])
                else:
                    rec.update({"matched": None, "how": "none"})
                    rep.add("fail", "N01", f"number {tok} has no source in the materials - remove it, replace it with the sourced value, or write [[GAP: ...]]",
                            u["uid"], u["line"], token=tok)
                    entry["status"] = "unsourced"
                entry["numbers"].append(rec)
        # versions and names with digits (strip section numbers like 2.1.1 / Section 3.1.2 first)
        ver_text = re.sub(r"(?i)(?:^|\b(?:section|sec\.?|chapter|ch\.?|§)\s*|第\s*)\d+(?:\.\d+)+", " ", text)
        if not only_gap_sent(u["raw"]):
            for m in C.VERSION_RE.finditer(ver_text):
                tok = m.group(0).lstrip("v")
                if any(tok in f["value"] for f in tagged):
                    entry["numbers"].append({"token": m.group(0), "matched": next(f["id"] for f in tagged if tok in f["value"]), "how": "version-tag"})
                elif tok.lower() in corpus_low:
                    cands = [f["id"] for f in facts if tok in f["value"]][:4]
                    entry["numbers"].append({"token": m.group(0), "matched": None, "candidates": cands, "how": "version-untagged"})
                    rep.add("warn", "N03", f"version {m.group(0)} is in the materials ({', '.join(cands) or 'text'}) but not tagged", u["uid"], u["line"])
                else:
                    rep.add("fail", "N01", f"version {m.group(0)} has no source in the materials", u["uid"], u["line"], token=m.group(0))
                    entry["status"] = "unsourced"
        for m in C.NAME_NUM_RE.finditer(text):
            tok = m.group(0)
            if C.VERSION_RE.fullmatch(tok) or re.match(r"^(F|C|G)\d+$", tok):
                continue
            if tok.lower() in corpus_low or tok.lower().replace("-", "") in corpus_low.replace("-", ""):
                continue
            from ml_extract import GPU_RE
            level = "fail" if GPU_RE.search(tok) else "warn"
            skel = re.sub(r"\d+", "#", tok.lower())
            near = sorted({w for w in re.findall(r"[a-z0-9][\w\-]*\d[\w\-]*(?:/\d+)?", corpus_low) if re.sub(r"\d+", "#", w) == skel})[:3]
            if near and not STRUCT_NAME_SKEL.match(skel):
                level = "fail"
            if only_gap_sent(u["raw"]) and level == "fail":
                level = "warn"
            rep.add(level, "N02", f"name '{tok}' does not occur in any material file" + (f" (materials have {', '.join(near)})" if near else ""), u["uid"], u["line"], token=tok)
        # tagged string facts should appear in the sentence
        squash = lambda x: re.sub(r"[\s_\-./]+", "", x.lower())  # noqa: E731
        tsq = squash(text)
        for f in tagged:
            if not f["nums"] and f["kind"] != "doc" and len(f["value"]) <= 40 and len(f["value"].split()) <= 3 and C.norm_str(f["value"]) not in ("true", "false", "none", "null"):
                val = re.sub(r"^(torch\.)?optim\.", "", f["value"]).lower()
                if lang == "zh" and re.fullmatch(r"[a-z][a-z ]+", val) and " " in val:
                    continue  # English phrase rendered in Chinese
                if val and squash(val) not in tsq and squash(os.path.basename(val)) not in tsq:
                    rep.add("warn", "T05", f"cited {f['id']} ({f['path']} = {f['value'][:30]}) but its value is not in the sentence", u["uid"], u["line"])
        # conflicts
        touched = set()
        for f in tagged:
            for c in conf_of.get(f["id"], []):
                touched.add(c["id"])
        for rec in entry["numbers"]:
            for fid in rec.get("candidates", []) or []:
                for c in conf_of.get(fid, []):
                    touched.add(c["id"])
        for cid in sorted(touched):
            c = next(x for x in conflicts if x["id"] == cid)
            vals = [C.norm_str(v["value"])[:40] for v in c["values"]]
            mentioned = any(cid in x or any(re.search(r"\b%s\b" % fid, x) for fid in c["facts"])
                            or sum(1 for v in vals if v and v in C.norm_str(x)) >= 2 for x in tg["confirms"])
            if not mentioned and cid not in resolved and not accept.get(cid):
                rep.add("fail", "C01", f"uses a value of conflict {cid} ({c['label']}: " + " vs ".join(v["value"][:20] for v in c["values"][:3]) +
                        f") without [[CONFIRM: {cid} ...]] or a resolution in agent.json", u["uid"], u["line"], conflict=cid,
                        values=[v["value"][:30] for v in c["values"][:3]])
        # split crossover
        splits_here = {name for name, rx in [("train", r"(?i)\btrain(?:ing)?\b|训练"), ("val", r"(?i)\bvalidation\b|\bval\b|\bdev\b|验证"), ("test", r"(?i)\btest(?:ing)?\b|测试")] if re.search(rx, text)}
        for f in tagged:
            fsplit = f["scope"].split("/")[-1] if f["scope"] else ""
            if fsplit in ("val", "test") and f["nums"] and splits_here and fsplit not in splits_here:
                rep.add("warn", "X01", f"{f['id']} comes from the {f['scope']} context ({f['file']}:{f['line']}) but the sentence talks about {'/'.join(sorted(splits_here))}", u["uid"], u["line"])
        # significance
        sig = C.rules("checklist")["significance_words"]
        if re.search(sig.get(lang, sig["en"]), text) and not any(f["canon"] in ("statistical_test", "alpha_level") for f in tagged) and not tg["gaps"] and not tg["confirms"]:
            if not any(f["canon"] == "statistical_test" for f in facts):
                rep.add("warn", "S01", "claims significance but no statistical test exists in the materials", u["uid"], u["line"])
            else:
                rep.add("warn", "S01", "claims significance without citing the statistical-test fact", u["uid"], u["line"])
        fact_map.append(entry)
    return cited, fact_map


def _cmd_matches_known(s2, known, corpus_norm, state):
    if s2 in known or s2 in corpus_norm:
        return True, None
    # python <-> python3 equivalence
    alt = re.sub(r"^python3?\b", "python" if s2.startswith("python3") else "python3", s2)
    if alt != s2 and (alt in known or alt in corpus_norm):
        return True, None
    # pip install -r <file> or conda env create -f <file> when that file exists in materials
    mat_files = {f["path"].lower() for f in state.get("files", [])}
    m_req = re.match(r"^(?:pip3?\s+install\s+-r|conda\s+env\s+create\s+-f)\s+(\S+)$", s2)
    if m_req and any(mf.endswith(m_req.group(1).lower()) for mf in mat_files):
        return True, None
    # Shell variable expansion ($SEED / ${SEED}) against a known command pattern
    for kcmd, f in known.items():
        k_alt = re.sub(r"^python3?\b", s2.split()[0] if s2.startswith(("python", "python3")) else "python", kcmd)
        if "$" in k_alt:
            parts = re.split(r"\$\{?\w+\}?", k_alt)
            pat = "^" + r"\S+".join(re.escape(p) for p in parts) + "$"
            if re.match(pat, s2):
                return True, f
    return False, None


def check_code(u, facts, corpus, corpus_low, rep, entry, state=None):
    cmds = [f for f in facts if f["canon"] == "command"]
    norm = lambda s: re.sub(r"\s+", " ", s.strip().rstrip("\\").strip())  # noqa: E731
    known = {norm(f["value"]): f for f in cmds}
    corpus_norm = re.sub(r"[ \t]+", " ", "\n".join(corpus.values()))
    for i, line in enumerate(u["text"].split("\n")):
        s = norm(line)
        if not s or s.startswith("#"):
            continue
        s2 = re.sub(r"^\$\s*", "", s)
        if s2 in known:
            f = known[s2]
            entry["facts"].append({"id": f["id"], "value": f["value"][:160], "source": f"{f['file']}:{f['line']}", "kind": f["kind"], "key": "command"})
            continue
        if s2 in corpus_norm:
            entry["facts"].append({"id": "literal", "value": s2[:160], "source": "materials (literal)", "kind": "text"})
            continue
        ok, mf = _cmd_matches_known(s2, known, corpus_norm, state or {})
        if ok:
            entry["facts"].append({"id": mf["id"] if mf else "literal", "value": s2[:160], "source": f"{mf['file']}:{mf['line']}" if mf else "materials (equiv)", "kind": "command"})
            continue
        script = re.search(r"([\w./-]+\.(?:py|sh|R|r|jl|m|yaml|yml|json))", s2)
        if re.match(r"^(cd|export|mkdir|source|conda\s+activate)\b", s2) and not script:
            continue
        if re.match(r"^(python3?|torchrun|accelerate|deepspeed|bash|sh|Rscript|julia|gmx|lmp|mpirun|srun|sbatch|make|pip|conda|git|docker|cd|export)\b", s2):
            hint = f"; script {script.group(1)} exists in the materials" if script and script.group(1).lower() in corpus_low else ""
            rep.add("fail", "P02", f"command not found in the materials: `{s2[:100]}`{hint} - copy it from a log/script or mark [[GAP: exact command]]", u["uid"], u["line"] + i + 1)


def coverage(units, facts, gaps, state, rep, cited):
    lang = state["lang"]
    from ml_extract import elements_for
    elems = elements_for(state["profile"])
    content = [u for u in units if u["type"] in ("sentence", "table_row", "code")]
    result = []
    for e in elems:
        pat = e["draft_patterns"].get(lang) or e["draft_patterns"]["en"]
        pat_en = e["draft_patterns"]["en"]
        hits = [u for u in content if re.search(pat, u["raw"]) or (lang != "en" and re.search(pat_en, u["raw"]))]
        anchored = [u for u in hits if u["parsed"]["facts"] or u["parsed"]["srcs"] or u["parsed"]["calcs"] or u["parsed"]["gaps"] or u["parsed"]["confirms"]]
        key_cited = [fid for fid in cited for f in [next((x for x in facts if x["id"] == fid), None)] if f and f["canon"] in e["keys"]]
        status = "missing"
        if e["id"] == "E_steps":
            items = [u for u in content if u["list_item"] or re.search(pat, u["raw"]) or PROSE_STEP_RE.search(u["text"])]
            has_gap = any(u["parsed"]["gaps"] for u in content if re.search(r"(?i)step|order|stage|procedure|步骤|顺序|流程", " ".join(u["parsed"]["gaps"])))
            status = "covered" if len(items) >= 2 else ("marked_gap" if has_gap else "missing")
        elif e["id"] == "E_limits":
            lim = [u for u in content if LIMIT_HEAD_RE.search(u["section"]) or re.search(pat, u["raw"])]
            status = "covered" if lim else "missing"
        elif anchored:
            status = "covered" if any(u["parsed"]["facts"] or u["parsed"]["srcs"] or u["parsed"]["calcs"] for u in anchored) else "marked_gap"
        elif any(re.search(pat, g) or re.search(pat_en, g) for u in content for g in u["parsed"]["gaps"] + u["parsed"]["confirms"]):
            status = "marked_gap"
        elif hits and any(idx_u + 1 < len(content) and content[idx_u + 1]["section"] == content[idx_u]["section"] and (content[idx_u + 1]["parsed"]["gaps"] or content[idx_u + 1]["parsed"]["confirms"])
                          for idx_u, u in enumerate(content) if u in hits):
            status = "marked_gap"
        if status == "missing":
            lvl = "fail" if e["level"] == "required" else "warn"
            rep.add(lvl, "K01" if lvl == "fail" else "K02", f"element not covered and not marked as a gap: {e['label'][lang]} -> write it with sources or add [[GAP: {e['question'][lang][:60]}...]]", element=e["id"], question=e["question"][lang])
        result.append({"element": e["id"], "category": e["category"], "label": e["label"][lang], "level": e["level"], "status": status,
                       "units": [u["uid"] for u in (hits if e["id"] not in ("E_steps", "E_limits") else [])][:10], "facts_cited": key_cited[:10]})
    # important facts never used
    used_vals = " ".join(u["text"].lower() for u in content)
    unused = {}
    for f in facts:
        if f["canon"] and f["category"] in ("params", "setup", "data", "repro", "control") and f["kind"] not in ("doc",) and not f.get("series") \
                and f["id"] not in cited and f["canon"] not in ("output_dir", "data_path", "command", "checkpoint", "preprocessing", "deterministic", "num_workers", "eval_batch_size") \
                and not f["key"].endswith(".choices"):
            if f["value"].lower()[:30] in used_vals and len(f["value"]) > 2:
                continue
            unused.setdefault(f["canon"], []).append(f["id"])
    canon_cited = {f["canon"] for f in facts if f["id"] in cited}
    miss = {k: v for k, v in unused.items() if k not in canon_cited}
    if miss:
        rep.add("warn", "K03", "facts in the materials never used in the chapter: " + "; ".join(f"{C.key_label(k)} ({', '.join(v[:3])})" for k, v in list(miss.items())[:14]),
                unused=miss)
    return result


def check_limits(units, facts, state, rep):
    lang = state["lang"]
    bp = C.rules("checklist")["boilerplate_limits"]
    pats = [re.compile(p, re.I) for p in bp.get(lang, []) + bp.get("en", [])]
    lim = [u for u in units if u["type"] in ("sentence", "table_row") and LIMIT_HEAD_RE.search(u["section"])]
    names = {f["value"].lower() for f in facts if f["canon"] in ("dataset", "model", "hardware", "baseline", "dataset_version") and 2 < len(f["value"]) < 40}
    anchored, generic = 0, 0
    for u in lim:
        t = u["text"]
        tl = t.lower()
        anchor = bool(u["parsed"]["facts"] or u["parsed"]["srcs"] or u["parsed"]["calcs"] or C.num_tokens(t) or any(n in tl for n in names)
                      or re.search(r"(?i)\bonly\b|\bsingle\b|\bnot (tested|evaluated|measured|run)\b|仅|单一|未(测试|评估|验证|覆盖)|只在|只用", t))
        boiler = any(p.search(t) for p in pats)
        if anchor:
            anchored += 1
        if boiler and not anchor:
            generic += 1
            rep.add("warn", "L01", "generic limitation without a concrete condition (data, scale, setting, failure case): " + t[:80], u["uid"], u["line"])
    if lim and anchored == 0:
        rep.add("fail", "L02", "the limitations section names no concrete untested condition or failure scenario")
    return {"sentences": len(lim), "anchored": anchored, "generic": generic}


def check_stages(units, state, rep):
    text = " ".join(u["raw"] for u in units).lower()
    out = []
    for s in state.get("stages", []):
        m = re.search(r"([\w./-]+\.(?:py|sh|R|r|jl|m))\b", s["command"])
        if not m:
            continue
        script = os.path.basename(m.group(1)).lower()
        ok = script in text or os.path.splitext(script)[0] in text
        out.append({"script": script, "source": f"{s['file']}:{s['line']}", "described": ok})
        if not ok:
            rep.add("warn", "P01", f"pipeline stage `{script}` ({s['file']}:{s['line']}) is not described in the method steps")
    return out


# ---------------------------------------------------------------- outputs

def unit_of(value, context):
    m = re.search(re.escape(str(value)) + r"\s*(%|°C|℃|K\b|ms|s\b|min|h\b|fs|ps|ns|nm|mm|mg|mL|µL|μL|mM|µM|rpm|×\s*g|bar|eV|GB|epochs?|steps?)", context or "")
    return m.group(1) if m else ""


CAT_ORDER = {"params": 0, "data": 1, "setup": 2, "control": 3, "repro": 4, "steps": 5}
STATUS_TXT = {"zh": {"cited": "正文已引用", "untagged": "正文出现（未标注）", "unused": "正文未使用", "conflict": "冲突 {c}，待作者确认", "other": "其他取值：{v}"},
              "en": {"cited": "cited in text", "untagged": "in text (untagged)", "unused": "not used in text", "conflict": "CONFLICT {c} - author to confirm", "other": "other values: {v}"}}


def param_rows(facts, conflicts, cited, lang, units):
    T = STATUS_TXT["zh" if lang == "zh" else "en"]
    conf_of = {}
    for c in conflicts:
        for fid in c["facts"]:
            conf_of.setdefault(fid, []).append(c["id"])
    rows, seen = [], {}
    pool = [f for f in facts if f["canon"] and f["category"] in ("params", "setup", "data", "repro", "control") and f["kind"] != "doc"
            and not f.get("series") and f["canon"] not in ("command", "output_dir", "data_path") and not f["key"].endswith(".choices")]
    text = " ".join(u["text"] for u in units).lower()
    rank = {"log": 1, "cli": 2, "env": 3, "config": 4, "code": 5}
    for f in sorted(pool, key=lambda f: (CAT_ORDER.get(f["category"], 9), f["canon"], 0 if f["id"] in cited else 1, rank.get(f["kind"], 6))):
        key = (f["canon"], f["scope"], f["path"].split(".")[-1] if f["canon"] in ("software", "software_stats") else "")
        if key in seen:
            r = seen[key]
            if C.norm_str(f["value"]) != C.norm_str(r["value"]) and C.norm_str(f["value"]) not in [C.norm_str(x.split("=", 1)[-1]) for x in r["other_values"]]:
                r["other_values"].append(f"{f['file']}:{f['line']}={f['value'][:30]}")
            r["all_sources"].append(f"{f['file']}:{f['line']}")
            continue
        status = T["cited"] if f["id"] in cited else (T["untagged"] if f["value"].lower() in text and len(f["value"]) > 2 else T["unused"])
        if f["id"] in conf_of:
            status = T["conflict"].format(c=",".join(conf_of[f["id"]]))
        parent = ".".join(f["path"].split(".")[:-1])
        if parent in ("version", "text") or not parent:
            parent = ""
        applies = "/".join(dict.fromkeys(x for x in f["scope"].split("/") + parent.split(".") if x)) or "-"
        r = {"name": C.key_label(f["canon"], lang) + (f" ({f['path'].split('.')[-1]})" if f["canon"] in ("software", "software_stats") else ""),
             "canonical": f["canon"], "category": f["category"], "value": f["value"], "unit": unit_of(f["value"], f["context"]), "applies_to": applies,
             "source": f"{f['file']}:{f['line']}", "fact": f["id"], "source_kind": f["kind"], "status": status, "other_values": [], "all_sources": [f"{f['file']}:{f['line']}"]}
        seen[key] = r
        rows.append(r)
    for r in rows:
        if r["other_values"] and "CONFLICT" not in r["status"] and "冲突" not in r["status"]:
            r["status"] += "; " + T["other"].format(v="; ".join(r["other_values"][:3]))
    return rows


def md_table(rows, lang):
    hdr = ["参数", "取值", "单位", "作用对象", "来源", "状态"] if lang == "zh" else ["Parameter", "Value", "Unit", "Applies to", "Source", "Status"]
    L = ["| " + " | ".join(hdr) + " |", "|" + "---|" * len(hdr)]
    for r in rows:
        L.append("| " + " | ".join(str(x).replace("|", "\\|") for x in [r["name"], r["value"], r["unit"] or "-", r["applies_to"], f"{r['source']} ({r['fact']})", r["status"]]) + " |")
    return "\n".join(L)


def render_clean(draft_text, lang, table_md, annotated, byid):
    text = re.sub(r"<!--.*?-->\n?", "", draft_text, flags=re.S)

    def rep(m):
        t = m.group(1).strip()
        tg = parse_tags([t])
        if tg["param_table"]:
            return "\n\n" + table_md + "\n\n"
        if tg["gaps"]:
            return ("【待确认：" + tg["gaps"][0] + "】") if lang == "zh" else ("[TO CONFIRM: " + tg["gaps"][0] + "]")
        if tg["confirms"]:
            return ("【待作者确认：" + tg["confirms"][0] + "】") if lang == "zh" else ("[AUTHOR TO CONFIRM: " + tg["confirms"][0] + "]")
        if annotated:
            if tg["facts"]:
                return "<sup>[" + "; ".join(f"{fid}: {byid[fid]['file']}:{byid[fid]['line']}" if fid in byid else fid for fid in tg["facts"]) + "]</sup>"
            if tg["calcs"]:
                return "<sup>[calc: " + tg["calcs"][0]["expr"] + "]</sup>"
            if tg["srcs"]:
                return "<sup>[" + tg["srcs"][0]["file"] + ":" + str(tg["srcs"][0]["line"]) + "]</sup>"
        return ""
    out = TAG_RE.sub(rep, text)
    out = re.sub(r"[ \t]+([。，；：！？.,;:])", r"\1", out)
    out = re.sub(r"[ \t]{2,}", " ", out)
    return out.strip() + "\n"


def md_to_html(md, title):
    L = [f"<!doctype html><html><head><meta charset='utf-8'><title>{html.escape(title)}</title>",
         "<style>body{font-family:'Noto Sans CJK SC','Microsoft YaHei','PingFang SC',sans-serif;max-width:900px;margin:24px auto;line-height:1.6;color:#222}"
         "table{border-collapse:collapse;font-size:12px}td,th{border:1px solid #999;padding:3px 6px;vertical-align:top}"
         "code,pre{background:#f4f4f4;font-size:12px}pre{padding:8px;white-space:pre-wrap}sup{color:#36c;font-size:10px}.gap{background:#fff3c4}</style></head><body>"]
    in_code, in_table, in_list = False, False, False
    for line in md.split("\n"):
        if line.strip().startswith("```"):
            if in_code:
                L.append("</pre>")
            else:
                L.append("<pre>")
            in_code = not in_code
            continue
        if in_code:
            L.append(html.escape(line))
            continue
        if line.strip().startswith("|"):
            if re.match(r"^\s*\|?\s*:?-{2,}", line):
                continue
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if not in_table:
                L.append("<table>")
                in_table = True
                L.append("<tr>" + "".join(f"<th>{inline(c)}</th>" for c in cells) + "</tr>")
            else:
                L.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
            continue
        if in_table:
            L.append("</table>")
            in_table = False
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            n = len(m.group(1))
            L.append(f"<h{n}>{inline(m.group(2))}</h{n}>")
            continue
        if re.match(r"^\s*(?:[-*+]|\d+[.)])\s+", line):
            L.append(f"<p style='margin:2px 0 2px 18px'>{inline(line.strip())}</p>")
            continue
        if line.strip():
            L.append(f"<p>{inline(line)}</p>")
    if in_table:
        L.append("</table>")
    L.append("</body></html>")
    return "\n".join(L)


def inline(s):
    keep = []

    def stash(m):
        keep.append(m.group(0))
        return f"\x00{len(keep) - 1}\x00"
    s = re.sub(r"</?sup>", stash, s)
    s = html.escape(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(【待[^】]*】|\[(?:TO CONFIRM|AUTHOR TO CONFIRM):[^\]]*\])", r"<span class='gap'>\1</span>", s)
    s = re.sub("\x00(\\d+)\x00", lambda m: keep[int(m.group(1))], s)
    return s


def write_docx(md, path):
    """Minimal DOCX (stdlib): headings, paragraphs, tables, code as monospace."""
    import zipfile
    esc = lambda t: html.escape(t, quote=False)  # noqa: E731

    def run(t, bold=False, mono=False):
        rpr = ""
        if bold or mono:
            rpr = "<w:rPr>" + ("<w:b/>" if bold else "") + ("<w:rFonts w:ascii='Consolas' w:hAnsi='Consolas'/>" if mono else "") + "</w:rPr>"
        return f"<w:r>{rpr}<w:t xml:space='preserve'>{esc(t)}</w:t></w:r>"

    def para(t, style=None, mono=False):
        ppr = f"<w:pPr><w:pStyle w:val='{style}'/></w:pPr>" if style else ""
        parts = re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", re.sub(r"</?sup>", "", t))
        runs = "".join(run(p[2:-2], bold=True) if p.startswith("**") else run(p[1:-1], mono=True) if p.startswith("`") else run(p, mono=mono) for p in parts if p)
        return f"<w:p>{ppr}{runs}</w:p>"
    body, table, in_code = [], [], False

    def flush_table():
        nonlocal table
        if not table:
            return
        rows = "".join("<w:tr>" + "".join(f"<w:tc><w:tcPr><w:tcW w:w='0' w:type='auto'/></w:tcPr>{para(c)}</w:tc>" for c in r) + "</w:tr>" for r in table)
        body.append("<w:tbl><w:tblPr><w:tblStyle w:val='TableGrid'/><w:tblW w:w='0' w:type='auto'/><w:tblBorders>"
                    + "".join(f"<w:{b} w:val='single' w:sz='4' w:space='0' w:color='999999'/>" for b in ("top", "left", "bottom", "right", "insideH", "insideV"))
                    + "</w:tblBorders></w:tblPr>" + rows + "</w:tbl>")
        table = []
    for line in md.split("\n"):
        if line.strip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            body.append(para(line, mono=True))
            continue
        if line.strip().startswith("|"):
            if re.match(r"^\s*\|?\s*:?-{2,}", line):
                continue
            table.append([c.strip() for c in line.strip().strip("|").split("|")])
            continue
        flush_table()
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            body.append(para(m.group(2), style=f"Heading{min(len(m.group(1)), 3)}"))
        elif line.strip():
            body.append(para(line.strip()))
    flush_table()
    doc = ("<?xml version='1.0' encoding='UTF-8' standalone='yes'?><w:document xmlns:w='http://schemas.openxmlformats.org/wordprocessingml/2006/main'><w:body>"
           + "".join(body) + "<w:sectPr><w:pgSz w:w='11906' w:h='16838'/><w:pgMar w:top='1134' w:right='1134' w:bottom='1134' w:left='1134' w:header='708' w:footer='708' w:gutter='0'/></w:sectPr></w:body></w:document>")
    styles = ("<?xml version='1.0' encoding='UTF-8' standalone='yes'?><w:styles xmlns:w='http://schemas.openxmlformats.org/wordprocessingml/2006/main'>"
              "<w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii='Times New Roman' w:hAnsi='Times New Roman' w:eastAsia='SimSun'/><w:sz w:val='21'/></w:rPr></w:rPrDefault></w:docDefaults>"
              "<w:style w:type='paragraph' w:default='1' w:styleId='Normal'><w:name w:val='Normal'/><w:pPr><w:spacing w:after='80' w:line='300' w:lineRule='auto'/></w:pPr></w:style>"
              + "".join(f"<w:style w:type='paragraph' w:styleId='Heading{i}'><w:name w:val='heading {i}'/><w:basedOn w:val='Normal'/><w:next w:val='Normal'/><w:pPr><w:keepNext/><w:spacing w:before='200' w:after='80'/><w:outlineLvl w:val='{i - 1}'/></w:pPr><w:rPr><w:b/><w:sz w:val='{32 - 4 * i}'/></w:rPr></w:style>" for i in (1, 2, 3))
              + "<w:style w:type='table' w:styleId='TableGrid'><w:name w:val='Table Grid'/></w:style></w:styles>")
    ct = ("<?xml version='1.0' encoding='UTF-8' standalone='yes'?><Types xmlns='http://schemas.openxmlformats.org/package/2006/content-types'>"
          "<Default Extension='rels' ContentType='application/vnd.openxmlformats-package.relationships+xml'/><Default Extension='xml' ContentType='application/xml'/>"
          "<Override PartName='/word/document.xml' ContentType='application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml'/>"
          "<Override PartName='/word/styles.xml' ContentType='application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml'/></Types>")
    rels = ("<?xml version='1.0' encoding='UTF-8' standalone='yes'?><Relationships xmlns='http://schemas.openxmlformats.org/package/2006/relationships'>"
            "<Relationship Id='rId1' Type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument' Target='word/document.xml'/></Relationships>")
    drels = ("<?xml version='1.0' encoding='UTF-8' standalone='yes'?><Relationships xmlns='http://schemas.openxmlformats.org/package/2006/relationships'>"
             "<Relationship Id='rId1' Type='http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles' Target='styles.xml'/></Relationships>")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/document.xml", doc)
        z.writestr("word/styles.xml", styles)
        z.writestr("word/_rels/document.xml.rels", drels)


def render_pdf(html_text, pdf_path, png_path, docx_path=None):
    """PDF + PNG preview via PyMuPDF Story; falls back to LibreOffice + pdftoppm for the DOCX. Returns a note."""
    try:
        try:
            import pymupdf as fitz  # noqa
        except ImportError:
            import fitz  # noqa
        body = re.sub(r"(?s).*?<body>|</body>.*", "", html_text)
        css = "body{font-family:sans-serif;font-size:10pt;line-height:1.45} table{border-collapse:collapse} td,th{border:1px solid #999;padding:2px 4px;font-size:8pt} pre{font-family:monospace;font-size:8pt;background:#f4f4f4} sup{font-size:6pt;color:#36c} .gap{background:#fff3c4}"
        story = fitz.Story(html=body, user_css=css)
        writer = fitz.DocumentWriter(pdf_path)
        mediabox = fitz.paper_rect("a4")
        where = mediabox + (50, 50, -50, -50)
        more = True
        n = 0
        while more and n < 60:
            dev = writer.begin_page(mediabox)
            more, _ = story.place(where)
            story.draw(dev)
            writer.end_page()
            n += 1
        writer.close()
        doc = fitz.open(pdf_path)
        doc[0].get_pixmap(dpi=100).save(png_path)
        return f"pymupdf story, {doc.page_count} pages"
    except Exception as e:  # noqa
        import shutil, subprocess
        soffice = shutil.which("soffice") or shutil.which("libreoffice")
        if soffice and docx_path and os.path.exists(docx_path):
            try:
                outdir = os.path.dirname(pdf_path)
                subprocess.run([soffice, "--headless", "--convert-to", "pdf", "--outdir", outdir, docx_path], capture_output=True, timeout=60)
                gen = os.path.join(outdir, os.path.splitext(os.path.basename(docx_path))[0] + ".pdf")
                if os.path.exists(gen) and os.path.abspath(gen) != os.path.abspath(pdf_path):
                    shutil.move(gen, pdf_path)
                if os.path.exists(pdf_path) and shutil.which("pdftoppm"):
                    stem = os.path.splitext(png_path)[0]
                    subprocess.run(["pdftoppm", "-png", "-r", "100", "-f", "1", "-l", "1", "-singlefile", pdf_path, stem], capture_output=True, timeout=60)
                if os.path.exists(pdf_path):
                    return "libreoffice + pdftoppm fallback"
            except Exception:
                pass
        return f"no PDF preview ({e})"


def map_contract(state, outputs, agent):
    fields = {}
    notes = []
    kinds = [
        ("case_id", r"^(case_?id|id)$"), ("status", r"^status$"),
        ("change_records", r"change|diff|revision|修改|版本差异|变更"),
        ("conflicts", r"conflict|冲突|不一致"),
        ("questions", r"gap|question|missing|confirm|issue|todo|pending|unresolved|query|queries|待确认|缺口|追问|human|manual|人工|问题"),
        ("uncertainty", r"uncertain|不确定|confidence|risk"),
        ("parameters", r"param|hyper|参数"),
        ("fact_map", r"source|evidence|provenance|fact|trace|citation|来源|证据|溯源|映射|mapping"),
        ("repro", r"repro|checklist|复现|环境清单"),
        ("limitations", r"limit|局限|限制|边界|boundary|scope"),
        ("datasets", r"dataset|data|split|数据|划分"),
        ("controls", r"baseline|control|对照|基线|comparison"),
        ("setup", r"setup|environment|hardware|software|环境|设置|硬件"),
        ("steps", r"step|procedure|protocol|pipeline|流程|步骤"),
        ("docx_path", r"(?:^|_)docx(?:_|$)|\bdocx\b|word"),
        ("pdf_path", r"(?:^|_)pdf(?:_|$)|\bpdf\b|preview"),
        ("files", r"artifact_?paths?|files|outputs|artifacts|paths|文件"),
        ("param_table_md", r"param_table|table|参数表"),
        ("check_report", r"check_?report|check_?result"),
        ("review_text", r"\breview\b|\breport\b|核查报告"),
        ("notes_list", r"^notes?$"),
        ("methods_text", r"method|section|chapter|draft|text|manuscript|正文|章节|草稿|content|markdown|产物|稿|deliverable|writing|写作"),
        ("summary", r"summary|摘要|概述|overview"),
    ]
    agent_fields = agent.get("fields") or {}
    for fdef in state.get("contract", []):
        name = fdef["name"]
        if name in agent_fields:
            spec = agent_fields[name]
            if isinstance(spec, dict) and "value" in spec:
                fields[name] = spec["value"]
                continue
            kind = spec.get("kind") if isinstance(spec, dict) else spec
        else:
            blob = (name + " " + (fdef.get("desc") or "")).lower()
            kind = None
            for k, rx in kinds:
                if re.search(rx, name.lower()):
                    kind = k
                    break
            if kind is None:
                for k, rx in kinds:
                    if re.search(rx, blob):
                        kind = k
                        break
        if kind is None or kind not in outputs:
            fields[name] = None
            notes.append(f"contract field '{name}' could not be mapped automatically; set it in agent.json fields")
        else:
            fields[name] = outputs[kind]
        desc = fdef.get("desc") or ""
        if '"type": "array"' in desc and not isinstance(fields[name], list):
            notes.append(f"contract field '{name}' expects array; coerced to []")
            fields[name] = []
        elif '"type": "object"' in desc and not isinstance(fields[name], dict):
            notes.append(f"contract field '{name}' expects object; coerced to {{}}")
            fields[name] = {}
        elif '"type": "string"' in desc and fields[name] is not None and not isinstance(fields[name], str):
            notes.append(f"contract field '{name}' expects string; coerced to str")
            fields[name] = str(fields[name])
    return fields, notes


def diff_records(old, new):
    a = [x for x in re.split(r"(?<=[。！？.!?])\s*|\n+", old) if x.strip()]
    b = [x for x in re.split(r"(?<=[。！？.!?])\s*|\n+", new) if x.strip()]
    recs = []
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == "equal":
            continue
        recs.append({"op": op, "before": " ".join(a[i1:i2])[:600], "after": " ".join(b[j1:j2])[:600]})
    return recs


FLAG_TXT = {"zh": {"num": "【待核实：材料中未找到 {t} 的来源】", "conf": "【待作者确认：{c} 材料取值不一致（{v}）】", "ph": "【待确认：此处信息缺失】",
                    "head": "## 待作者确认事项（自动标注）", "intro": "以下条目由 ml_build.py 自动检出，未阻断成稿，请作者逐条核实：",
                    "cmd": "命令未在材料中找到：`{t}`", "elem": "缺少要素：{q}", "lim": "局限性未指向具体失效条件，请补充未测试的条件或失效场景。",
                    "calc": "推导数值无法复核：{m}"},
            "en": {"num": " [UNVERIFIED: no source for {t} in the materials]", "conf": " [AUTHOR TO CONFIRM: {c} values differ in the materials ({v})]",
                   "ph": "[TO CONFIRM: missing information]", "head": "## Open items for the author (auto-flagged)",
                   "intro": "The following items were detected by ml_build.py; they did not block the chapter and need the author's check:",
                   "cmd": "command not found in the materials: `{t}`", "elem": "missing element: {q}",
                   "lim": "the limitations name no concrete untested condition or failure scenario.", "calc": "derived value cannot be verified: {m}"}}


def mark_flags(draft_text, items, lang):
    """Quarantine flagged content instead of blocking: unsourced numbers/names and placeholders get an inline marker,
    an unmarked conflict gets an author-confirm marker, everything else goes to an appended open-items list."""
    T = FLAG_TXT[lang]
    lines = draft_text.split("\n")
    in_code, flag = [False] * len(lines), False
    for i, ln in enumerate(lines):
        if ln.strip().startswith("```"):
            flag = not flag
            in_code[i] = True
            continue
        in_code[i] = flag
    open_items, done = [], set()

    def locate(start, tok):
        i = start - 1
        while 0 <= i < len(lines) and lines[i].strip():
            body = re.sub(r"\[\[.*?\]\]", lambda m: "\0" * len(m.group(0)), lines[i])
            k = body.find(tok)
            if k >= 0 and not in_code[i]:
                return i, k
            i += 1
        return None, None
    for it in items:
        if it["level"] != "fail":
            continue
        code, tok, ln = it["code"], it.get("token"), it.get("line")
        key = (code, tok, ln, it.get("conflict"))
        if key in done:
            continue
        done.add(key)
        if code in ("N01", "N02") and tok and ln:
            i, k = locate(ln, tok)
            if i is not None:
                lines[i] = lines[i][:k + len(tok)] + T["num"].format(t=tok) + lines[i][k + len(tok):]
            else:
                open_items.append(T["num"].format(t=tok).strip())
        elif code == "M01" and tok and ln:
            i, k = locate(ln, tok)
            if i is not None:
                lines[i] = lines[i][:k] + T["ph"] + lines[i][k + len(tok):]
        elif code == "C01" and ln and 0 < ln <= len(lines) and not in_code[ln - 1]:
            i = ln - 1
            while i + 1 < len(lines) and lines[i + 1].strip() and not lines[i + 1].lstrip().startswith(("#", "|", "-", "*", "```")):
                i += 1
            lines[i] = lines[i].rstrip() + T["conf"].format(c=it.get("conflict", ""), v=" / ".join(it.get("values", [])))
        elif code == "P02":
            open_items.append(T["cmd"].format(t=re.sub(r"^command not found in the materials: `|`.*$", "", it["msg"])[:100]))
        elif code == "K01":
            open_items.append(T["elem"].format(q=it.get("question") or it["msg"]))
        elif code == "L02":
            open_items.append(T["lim"])
        elif code in ("K10", "K11"):
            open_items.append(T["calc"].format(m=it["msg"][:120]))
        else:
            open_items.append(f"{code}: {it['msg'][:160]}")
    return "\n".join(lines), list(dict.fromkeys(open_items))


def open_items_block(open_items, lang):
    T = FLAG_TXT[lang]
    return ("\n\n" + T["head"] + "\n\n" + T["intro"] + "\n\n" + "\n".join(f"- {x}" for x in open_items) + "\n") if open_items else ""


def build(work, out, provisional=False):
    state = C.load_json(os.path.join(work, "state.json"))
    if not state:
        raise SystemExit("no work/state.json - run ml_extract.py first")
    fx = C.load_json(os.path.join(work, "facts.json"), {"facts": [], "conflicts": [], "gaps": []})
    facts, conflicts, gaps = fx["facts"], fx["conflicts"], fx["gaps"]
    byid = {f["id"]: f for f in facts}
    lang = state["lang"]
    agent = {}
    problems = list(state.get("problems", []))
    try:
        agent = C.load_json(os.path.join(work, "agent.json"), {}) or {}
    except ValueError as e:
        problems.append(f"agent.json invalid JSON, ignored: {e}")
    dpath = os.path.join(work, "draft.md")
    draft_text = open(dpath, encoding="utf-8-sig", errors="replace").read() if os.path.exists(dpath) else ""
    draft_text, n_norm = normalize_tags(draft_text)
    draft_text, anchor_notes = resolve_anchors(draft_text, facts)
    if n_norm:
        anchor_notes.append(f"{n_norm} tag spelling(s) normalised (e.g. [F12] -> [[F12]])")
    problems += anchor_notes
    units = parse_draft(draft_text)
    content_units = [u for u in units if u["type"] in ("sentence", "table_row", "code") and len(u["text"]) > 3]
    rep = Report()
    corpus = material_corpus(state)
    cited, fact_map = check_units(units, facts, conflicts, gaps, state, agent, corpus, rep)
    cov = coverage(units, facts, gaps, state, rep, cited) if content_units else []
    lim = check_limits(units, facts, state, rep) if content_units else {}
    stages = check_stages(units, state, rep) if content_units else []
    if not content_units:
        rep.add("fail", "D00", "draft.md has no content yet")
    # accepted warnings/fails by code+unit
    acc = agent.get("accept") or {}
    for it in rep.items:
        k1, k2 = f"{it['code']}@{it.get('unit')}", it["code"]
        if it["level"] in ("fail", "warn") and (acc.get(k1) or (it["level"] == "warn" and acc.get(k2))):
            it["accepted"] = acc.get(k1) or acc.get(k2)
            it["level"] = "accepted"
    rows = param_rows(facts, conflicts, cited, lang, units)
    table_md = md_table(rows, lang)
    has_pt = any(parse_tags(u["tags"])["param_table"] for u in units)
    flagged_items = []
    marked = draft_text
    if content_units and not provisional:
        marked, flagged_items = mark_flags(draft_text, rep.items, lang)
    draft_for_render = marked
    if not has_pt and content_units:
        cap = "\n\n**表 参数及来源**\n\n[[PARAM_TABLE]]\n" if lang == "zh" else "\n\n**Table. Parameters and their sources**\n\n[[PARAM_TABLE]]\n"
        heads = [m for m in re.finditer(r"(?m)^#{1,6}\s+(.*)$", marked)]
        pos = None
        for i, m in enumerate(heads):
            if PARAM_HEAD_RE.search(m.group(1)):
                pos = heads[i + 1].start() if i + 1 < len(heads) else len(marked)
                break
        draft_for_render = (marked[:pos] + cap + "\n" + marked[pos:]) if pos is not None else marked + cap
    draft_for_render += open_items_block(flagged_items, lang)
    clean = render_clean(draft_for_render, lang, table_md, False, byid)
    annotated = render_clean(draft_for_render, lang, table_md, True, byid)
    os.makedirs(out, exist_ok=True)
    C.write_text(os.path.join(out, "methods.md"), clean)
    C.write_text(os.path.join(out, "methods_annotated.md"), annotated)
    htm = md_to_html(annotated, f"{state['case_id']} methods (annotated)")
    C.write_text(os.path.join(out, "methods_annotated.html"), htm)
    preview_note = "skipped (provisional)"
    if not provisional and content_units and not os.environ.get("ML_NO_PREVIEW"):
        try:
            write_docx(clean, os.path.join(out, "methods.docx"))
        except Exception as e:  # noqa
            problems.append(f"DOCX not written: {e}")
        preview_note = render_pdf(md_to_html(clean, state["case_id"]), os.path.join(out, "methods_preview.pdf"), os.path.join(out, "methods_preview.png"), docx_path=os.path.join(out, "methods.docx"))
    # parameter table files
    import csv
    with open(os.path.join(out, "param_table.csv"), "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["name", "canonical", "category", "value", "unit", "applies_to", "source", "fact", "source_kind", "status"])
        for r in rows:
            w.writerow([r[k] for k in ["name", "canonical", "category", "value", "unit", "applies_to", "source", "fact", "source_kind", "status"]])
    C.write_text(os.path.join(out, "param_table.md"), table_md + "\n")
    # questions for the author
    qs = []
    for g in gaps:
        qs.append({"id": g["id"], "type": "gap", "category": g["category"], "level": g["level"], "question": g["question"], "status": g["status"], "facts": g.get("facts", [])})
    for c in conflicts:
        res = next((r for r in agent.get("resolutions") or [] if isinstance(r, dict) and (r.get("conflict") == c["id"] or r.get("id") == c["id"])), None)
        q = (f"{c['label']} 在材料中取值不一致：" if lang == "zh" else f"{c['label']} differs between sources: ") + "; ".join(f"{v['value'][:40]} ({v['source']})" for v in c["values"])
        q += ("。正文采用哪一个？" if lang == "zh" else ". Which value did the reported run use?")
        qs.append({"id": c["id"], "type": "conflict", "category": C.key_category(c["canon"]), "question": q, "facts": c["facts"],
                   "draft_choice": res, "status": "resolved_by_agent_pending_author" if res else "open"})
    for u in units:
        for g in u.get("parsed", {}).get("gaps", []):
            qs.append({"id": f"Q-{u['uid']}", "type": "draft_gap", "section": u["section"], "line": u["line"], "question": g, "status": "open"})
        for g in u.get("parsed", {}).get("confirms", []):
            qs.append({"id": f"Q-{u['uid']}c", "type": "draft_confirm", "section": u["section"], "line": u["line"], "question": g, "status": "open"})
    for x in rep.fails():
        qs.append({"id": f"A-{x['code']}-{x.get('unit') or x.get('element') or ''}", "type": "auto_flag", "code": x["code"], "line": x.get("line"),
                   "question": x["msg"], "status": "open"})
    QL = ["# 待作者确认清单" if lang == "zh" else "# Questions for the author", ""]
    for q in qs:
        QL.append(f"- [ ] **{q['id']}** ({q['type']}{', ' + q['category'] if q.get('category') else ''}) {q['question']}" + (f" — facts {', '.join(q['facts'][:5])}" if q.get("facts") else "") +
                  (f" — draft uses {q['draft_choice'].get('use')} ({q['draft_choice'].get('reason', '')})" if q.get("draft_choice") else ""))
    C.write_text(os.path.join(out, "questions.md"), "\n".join(QL) + "\n")
    # repro checklist
    rc = []
    for canon, label in [("code_version", "code version"), ("command", "commands"), ("python", "Python"), ("torch", "PyTorch"), ("cuda", "CUDA"), ("software", "other software"),
                         ("hardware", "hardware"), ("seed", "seeds"), ("dataset", "dataset"), ("dataset_version", "dataset version"), ("source_url", "data access"), ("container", "container/env")]:
        fs = [f for f in facts if f["canon"] == canon and f["kind"] != "doc"]
        rc.append({"item": label, "canonical": canon, "found": bool(fs), "values": list(dict.fromkeys(f["value"][:80] for f in fs))[:6],
                   "sources": [f"{f['file']}:{f['line']}" for f in fs][:6], "cited_in_text": any(f["id"] in cited for f in fs)})
    # change records: vs input draft (if any), vs previous build
    changes = []
    for fi in state["files"]:
        if fi["class"] == "draft":
            try:
                old = C.read_any(os.path.join(state["input_dir"], fi["path"]))[0]
                for r in diff_records(old, clean):
                    r["against"] = fi["path"]
                    changes.append(r)
            except Exception as e:  # noqa
                problems.append(f"diff against {fi['path']} failed: {e}")
    hist_p = os.path.join(work, "history.json")
    hist = C.load_json(hist_p, []) or []
    dsha = hashlib.sha256(draft_text.encode("utf-8")).hexdigest()
    fails, warns = rep.fails(), rep.warns()
    if not provisional and (not hist or hist[-1]["draft_sha256"] != dsha):
        prev_p = os.path.join(work, "draft_prev.md")
        build_changes = diff_records(open(prev_p, encoding="utf-8").read(), clean) if os.path.exists(prev_p) else []
        hist.append({"at": now(), "draft_sha256": dsha, "fails": len(fails), "warns": len(warns), "changed_sentences": len(build_changes),
                     "fail_codes": sorted({x["code"] for x in fails})})
        C.write_text(prev_p, clean)
        C.dump_json(hist, hist_p)
    # status
    contract_outputs = {}
    fm_out = [e for e in fact_map if e["type"] != "heading"]
    limits_list = [u["text"] for u in units if u["type"] in ("sentence", "table_row") and LIMIT_HEAD_RE.search(u["section"])]
    sec = lambda rx: [u["text"] for u in units if u["type"] in ("sentence", "table_row", "code") and re.search(rx, u["section"], re.I)]  # noqa: E731
    open_q = [q for q in qs if q["status"] != "resolved"]
    usable = bool(content_units)
    if provisional:
        status, reason = "partial", "provisional result written by ml_extract before the draft was checked"
    elif not usable and not facts:
        status, reason = "failed", "no readable materials and no draft"
    elif not usable:
        status, reason = "partial", "draft not written; facts, conflicts and questions are available"
    elif fails:
        status, reason = "success", (f"chapter built; {len(fails)} items auto-flagged and marked in the text for the author ("
                                     + ", ".join(sorted({x['code'] for x in fails})) + f"); {len(open_q)} items await author confirmation")
    else:
        status, reason = "success", f"all checks pass; {len(open_q)} items await author confirmation"
    if agent.get("status_note"):
        reason += "; " + str(agent["status_note"])
    uncertainty = []
    for g in gaps:
        if g["level"] == "required" and g["status"] in ("missing", "ambiguous", "only_mentioned_in_text"):
            uncertainty.append(f"{g['id']}: {g['label']} - {g['status']}")
    for c in conflicts:
        uncertainty.append(f"{c['id']}: {c['label']} has {len(c['values'])} different values in the materials")
    for fi in state["files"]:
        for p in fi.get("problems", []):
            uncertainty.append(f"{fi['path']}: {p}")
    uncertainty += [f"FLAG {x['code']} l.{x.get('line')}: {x['msg']}" for x in fails[:30]]
    uncertainty += [f"{x['code']} {x['msg']}" for x in warns[:30]]
    uncertainty += problems
    files_out = sorted(os.listdir(out)) if os.path.isdir(out) else []
    contract_outputs = {
        "case_id": state["case_id"], "status": status, "methods_text": clean, "parameters": rows, "fact_map": fm_out,
        "questions": qs, "conflicts": conflicts, "uncertainty": uncertainty, "change_records": {"against_input_draft": changes, "build_history": hist},
        "repro": rc, "limitations": limits_list, "datasets": [r for r in rows if r["category"] == "data"],
        "controls": [r for r in rows if r["category"] == "control"], "setup": [r for r in rows if r["category"] == "setup"],
        "steps": sec(r"step|procedure|pipeline|流程|步骤|方法") or [u["text"] for u in units if u.get("list_item")],
        "summary": f"{len(content_units)} text units, {len(cited)} facts cited, {len(rows)} parameters, {len(open_q)} questions, status {status}",
        "docx_path": os.path.join(out, "methods.docx") if os.path.exists(os.path.join(out, "methods.docx")) else None,
        "pdf_path": os.path.join(out, "methods_preview.pdf") if os.path.exists(os.path.join(out, "methods_preview.pdf")) else None,
        "param_table_md": table_md,
        "review_text": "\n".join([f"# Review — {state['case_id']}", f"status: {status} — {reason}", f"facts cited: {len(cited)}, questions: {len(qs)}"]),
        "notes_list": agent.get("notes") or [],
        "files": ["methods.md", "methods_annotated.md", "methods_annotated.html", "methods.docx", "methods_preview.pdf", "methods_preview.png", "param_table.csv", "param_table.md",
                  "fact_map.json", "questions.md", "check_report.json", "review.md", "result.json"],
    }
    mapped, map_notes = map_contract(state, contract_outputs, agent)
    uncertainty += map_notes
    result = {"case_id": state["case_id"]}
    result.update(mapped)
    result.update({
        "status": status, "status_reason": reason,
        "skill": {"name": "methods-ledger", "version": C.VERSION},
        "language": lang, "profile": state["profile"],
        "artifacts": {k: os.path.join(out, k) for k in contract_outputs["files"] if os.path.exists(os.path.join(out, k)) or k == "result.json"},
        "preview": preview_note,
        "sources": [{"path": f["path"], "class": f["class"], "sha256": f["sha256"], "bytes": f["bytes"], "facts": f.get("n_facts", 0), "problems": f.get("problems", [])} for f in state["files"]],
        "checks": {"fail": len(fails), "flagged_in_text": flagged_items, "blocking": 0 if usable else 1, "warn": len(warns), "accepted": len([x for x in rep.items if x["level"] == "accepted"]),
                   "fail_items": [f"{x['code']} l.{x.get('line')}: {x['msg']}" for x in fails][:40], "coverage": cov, "limitations": lim, "stages": stages},
        "needs_confirmation": qs, "conflicts": conflicts, "uncertainty": uncertainty,
        "change_records": contract_outputs["change_records"], "parameters": rows, "repro_checklist": rc,
        "facts_cited": sorted(cited, key=lambda x: int(x[1:])), "n_facts_extracted": len(facts),
        "built_at": now(),
    })
    for fdef in state.get("contract", []):
        result[fdef["name"]] = mapped.get(fdef["name"])
    if "status" in [f["name"] for f in state.get("contract", [])]:
        result["status"] = status
    C.dump_json(fm_out, os.path.join(out, "fact_map.json"))
    C.dump_json({"status": status, "reason": reason, "items": rep.items, "coverage": cov, "limitations": lim, "stages": stages}, os.path.join(out, "check_report.json"))
    R = [f"# Review — {state['case_id']}", "", f"status: **{status}** — {reason}", "",
         f"facts extracted {len(facts)}, cited {len(cited)}; conflicts {len(conflicts)}; questions {len(qs)}; preview: {preview_note}", "", "## Coverage"]
    for c in cov:
        R.append(f"- {c['element']} ({c['category']}, {c['level']}): **{c['status']}** — {c['label']}")
    R += ["", "## Check items"]
    for x in rep.items:
        if x["level"] != "info":
            R.append(f"- {'FLAG' if x['level'] == 'fail' else x['level'].upper()} {x['code']} l.{x.get('line')}: {x['msg']}" + (f" (accepted: {x['accepted']})" if x.get("accepted") else ""))
    review_md = "\n".join(R) + "\n"
    C.write_text(os.path.join(out, "review.md"), review_md)
    C.dump_json(result, os.path.join(out, "result.json"))
    return status, rep, result


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work", default="/app/work")
    ap.add_argument("--out", default="/app/output")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)
    if not os.path.exists(os.path.join(a.work, "state.json")):
        alt = next((d for d in ("/app/work", os.path.join(os.getcwd(), "work"), os.getcwd()) if os.path.exists(os.path.join(d, "state.json"))), None)
        if not alt:
            print("no state.json in work dir - run ml_extract.py first")
            return 2
        print(f"work dir {a.work} has no state.json; using {alt}")
        a.work = alt
    try:
        status, rep, result = build(a.work, a.out)
    except Exception as e:  # noqa
        import traceback
        traceback.print_exc()
        print(f"internal error: {e!r}; existing {os.path.join(a.out, 'result.json')} left untouched")
        return 3
    fails, warns = rep.fails(), rep.warns()
    print(f"status: {status} - {result['status_reason']}")
    print(f"flags {len(fails)} (auto-marked in methods.md, non-blocking)  warns {len(warns)}  facts cited {len(result['facts_cited'])}  "
          f"questions {len(result['needs_confirmation'])}  preview: {result['preview']}")
    for x in fails:
        print(f"FLAG {x['code']} l.{x.get('line')}: {x['msg']}")
    if not a.quiet:
        for x in warns[:40]:
            print(f"warn {x['code']} l.{x.get('line')}: {x['msg']}")
        if len(warns) > 40:
            print(f"... {len(warns) - 40} more warnings in check_report.json")
    print(f"outputs in {a.out}")
    return 0 if result["checks"]["blocking"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
