"""Shared helpers for methods-ledger: robust reading, number parsing and comparison, key normalisation,
rules loading. Python 3.8+, standard library only (PyMuPDF optional for PDF materials)."""
import json
import math
import os
import re
import zipfile

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES_DIR = os.path.join(SKILL_DIR, "rules")
CJK = "㐀-䶿一-鿿豈-﫿"
VERSION = "0.1.0"


def load_json(path, default=None):
    if not path or not os.path.exists(path):
        return default
    with open(path, encoding="utf-8-sig") as fh:
        return json.load(fh)


def dump_json(obj, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)


def write_text(path, text):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


_RULES = {}


def rules(name):
    if name not in _RULES:
        _RULES[name] = load_json(os.path.join(RULES_DIR, name + ".json"), {})
    return _RULES[name]


# ---------------------------------------------------------------- reading

MOJI_RUN = re.compile("[Â-ô][\u0080-¿ŒœŠšŸŽžƒˆ˜–—‘-„†-•…‰‹›€™]+")


def _mojibake_score(s):
    return len(re.findall("�|锟斤拷|ï¿½|[\x80-\x9f]", s)) + len(MOJI_RUN.findall(s))


def _repair_runs(text):
    n = [0]

    def fix(m):
        seg = m.group(0)
        for enc in ("cp1252", "latin-1"):
            try:
                out = seg.encode(enc).decode("utf-8")
                n[0] += 1
                return out
            except (UnicodeEncodeError, UnicodeDecodeError):
                continue
        return seg
    return MOJI_RUN.sub(fix, text), n[0]


def decode_bytes(raw):
    """(text, info). UTF-8, UTF-16 (BOM), GB18030; reverses UTF-8-read-as-CP1252 runs and reports every repair."""
    info = {"encoding": None, "repairs": []}
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        text, info["encoding"] = raw.decode("utf-16"), "utf-16"
    else:
        text = None
        for enc in ("utf-8-sig", "gb18030"):
            try:
                text = raw.decode(enc)
                info["encoding"] = enc
                break
            except UnicodeDecodeError:
                continue
        if text is None:
            text = raw.decode("utf-8", errors="replace")
            info["encoding"] = "utf-8 (errors replaced)"
    before = _mojibake_score(text)
    if before >= 2:
        fixed, nrun = _repair_runs(text)
        if nrun and _mojibake_score(fixed) < before:
            info["repairs"].append(f"reversed UTF-8 read as CP1252 in {nrun} places; check those words")
            text = fixed
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    info["replacement_chars"] = text.count("�")
    return text, info


def read_docx(path):
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    paras = []
    for p in re.findall(r"<w:p[ >].*?</w:p>", xml, flags=re.S):
        p = re.sub(r"<w:tab/>", "\t", p)
        p = re.sub(r"<w:br/>", "\n", p)
        if "<w:tc>" in p or "<w:tc " in p:
            pass
        t = "".join(re.findall(r"<w:t(?: [^>]*)?>(.*?)</w:t>", p, flags=re.S))
        t = t.replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"').replace("&apos;", "'").replace("&amp;", "&")
        paras.append(t)
    return "\n".join(x for x in paras if x.strip())


def read_pdf(path):
    fitz = None
    try:
        import pymupdf as fitz  # noqa
    except ImportError:
        try:
            import fitz  # noqa
        except ImportError:
            fitz = None
    if fitz is not None:
        doc = fitz.open(path)
        if doc.needs_pass:
            raise ValueError("encrypted PDF")
        pages = []
        for i, page in enumerate(doc):
            pages.append(f"[page {i + 1}]\n" + page.get_text("text"))
        return "\n".join(pages), {"pages": len(pages), "extractor": "pymupdf"}
    import subprocess
    r = subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True)
    if r.returncode != 0:
        raise ValueError("no PDF text extractor (install pymupdf or poppler-utils)")
    return r.stdout.decode("utf-8", errors="replace"), {"extractor": "pdftotext"}


def read_any(path):
    """(text, info). Never raises for text files; PDF/DOCX failures are raised as ValueError."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        return read_docx(path), {"encoding": "docx-xml", "repairs": ["DOCX formatting not kept; one line per paragraph"]}
    if ext == ".pdf":
        text, info = read_pdf(path)
        info["repairs"] = ["text extracted from PDF; line numbers refer to the extracted text ([page N] markers)"]
        return text, info
    with open(path, "rb") as fh:
        raw = fh.read()
    if b"\x00" in raw[:4096] and not raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        raise ValueError("binary file")
    return decode_bytes(raw)


# ---------------------------------------------------------------- numbers

SUPER = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻⁺", "0123456789-+")
NUM_RE = re.compile(
    r"(?<![\w.])(?:[-−–+]?)(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"
    r"(?:\s*(?:[eE][-+−]?\d+|[x×]\s*10\s*\^?\s*\{?[-−+]?\d+\}?|[x×]\s*10[⁻⁺]?[⁰¹²³⁴⁵⁶⁷⁸⁹]+))?"
    r"(?:[kKMB](?![A-Za-z]))?"
    r"(?:\s*%)?"
    r"|(?<![\w.])\.\d+")
VERSION_RE = re.compile(r"(?<![\w.])v?\d+\.\d+(?:\.\d+)+[\w.+-]*|(?<![\w.])v\d+(?:\.\d+)?\b")
NAME_NUM_RE = re.compile(r"(?<![\w.])[A-Za-z][A-Za-z]*[-_]?\d+[A-Za-z0-9]*(?:[-_/][A-Za-z0-9]+)*|(?<![\w.])\d+(?:Ti|TB|GB|bit|-bit|th|st|nd|rd|D)(?![A-Za-z])")
UNIT_AFTER = re.compile(r"\s*(%|°C|℃|K\b|ms\b|s\b|sec\b|min\b|h\b|hours?\b|days?\b|fs\b|ps\b|ns\b|nm\b|µm|μm|um\b|mm\b|cm\b|mg\b|g\b|kg\b|µg|μg|ng\b|mL\b|ml\b|µL|μL|uL\b|L\b|mM\b|µM|μM|nM\b|M\b|mol\b|rpm\b|×\s*g|x\s*g\b|bar\b|atm\b|Pa\b|kPa\b|MPa\b|eV\b|Ry\b|V\b|mV\b|A\b|mA\b|Hz\b|kHz\b|MHz\b|GB\b|MB\b|TB\b|epochs?\b|steps?\b|samples?\b|images?\b|tokens?\b|params?\b|小时|分钟|秒|天|轮|步|张|条|例|名|个|次|份)")


def parse_num(tok):
    """Numeric value of a matched number token (None if not numeric). '80%' -> 80.0 (percent flag in parse_num_full)."""
    v = parse_num_full(tok)
    return None if v is None else v[0]


def parse_num_full(tok):
    t = tok.strip().translate(SUPER).replace("−", "-").replace("–", "-").replace(" ", "")
    pct = t.endswith("%")
    t = t.rstrip("%")
    mult = 1.0
    if t and t[-1] in "kKMB":
        mult = {"k": 1e3, "K": 1e3, "M": 1e6, "B": 1e9}[t[-1]]
        t = t[:-1]
    m = re.match(r"^([-+]?[\d,]*\.?\d+)(?:[x×]10\^?\{?([-+]?\d+)\}?)$", t)
    try:
        if m:
            base = float(m.group(1).replace(",", ""))
            val = base * 10 ** int(m.group(2))
        else:
            val = float(t.replace(",", ""))
    except ValueError:
        return None
    return val * mult, pct


def num_tokens(text):
    """[(token, value, is_percent, start, end)] for every number; versions and name-numbers are excluded."""
    masked = list(text)
    for rx in (VERSION_RE, NAME_NUM_RE):
        for m in rx.finditer(text):
            for i in range(m.start(), m.end()):
                masked[i] = " "
    masked = "".join(masked)
    out = []
    for m in NUM_RE.finditer(masked):
        tok = m.group(0)
        v = parse_num_full(tok)
        if v is None:
            continue
        out.append((tok.strip(), v[0], v[1], m.start(), m.end()))
    return out


def num_equivalents(value, pct):
    """All values a number may legitimately be written as: 80% <-> 0.8, 1e-3 <-> 0.001."""
    vals = {value}
    if pct:
        vals.add(value / 100.0)
    else:
        if 0 < abs(value) <= 1:
            vals.add(value * 100.0)
    return vals


def nums_close(a, b, rel=1e-6):
    if a == b:
        return True
    if a == 0 or b == 0:
        return abs(a - b) < 1e-12
    return abs(a - b) <= rel * max(abs(a), abs(b))


def rounds_to(text_val, fact_val):
    """text_val is fact_val rounded to the precision written in the text (e.g. 0.912 from 0.91234)."""
    if fact_val == 0 or text_val == 0:
        return False
    s = repr(text_val)
    dec = len(s.split(".")[1]) if "." in s and "e" not in s else 0
    try:
        return round(fact_val, dec) == round(text_val, dec) and abs(fact_val - text_val) / abs(fact_val) < 0.01
    except (OverflowError, ValueError):
        return False


def value_nums(raw):
    """Numeric values contained in a raw fact value (incl. list members)."""
    if isinstance(raw, bool):
        return []
    if isinstance(raw, (int, float)):
        return [float(raw)] if not (isinstance(raw, float) and math.isnan(raw)) else []
    if isinstance(raw, (list, tuple)):
        out = []
        for x in raw:
            out.extend(value_nums(x))
        return out
    return [t[1] for t in num_tokens(str(raw))]


def unit_after(text, end):
    m = UNIT_AFTER.match(text, end)
    return m.group(1) if m else ""


# ---------------------------------------------------------------- keys

def _nk(s):
    s = str(s).strip().strip("-").strip()
    s = re.sub(r"[\s\-./]+", "_", s.lower())
    return s.strip("_")


_ALIAS = None
GENERIC_NEEDS_CONTEXT = {
    "version": ("data", "dataset", "corpus", "benchmark", "数据"),
    "release": ("data", "dataset", "corpus"),
    "size": ("data", "dataset", "corpus", "sample", "split"),
    "n": ("data", "dataset", "sample", "participants", "subjects"),
    "source": ("data", "dataset", "corpus"),
    "url": ("data", "dataset", "corpus"),
    "root": ("data", "dataset"),
    "data": (),
    "image": ("docker", "container", "singularity"),
    "time": ("incubation", "reaction", "hold", "step", "protocol", "stage"),
    "ratio": ("split", "data", "train", "val", "test"),
    "split": ("data", "dataset"),
    "c": ("svm", "logistic", "model", "clf", "classifier", "regression"),
    "lambda": ("reg", "model", "loss"),
    "net": (), "layers": ("model", "encoder", "decoder", "net"), "depth": ("model", "tree", "net"),
    "heads": ("model", "attention", "encoder"), "classes": ("data", "model", "dataset"),
    "devices": ("trainer", "hardware", "gpu"), "workers": ("data", "loader", "dataloader"),
    "control": ("group", "experiment", "design"), "opt": ("train", "optim"),
    "temp": (), "sample": ("analytic", "clean", "survey", "questionnaire", "cohort"), "alpha": ("stat", "sig", "test", "anova", "analysis", ".r", "p_"), "benchmark": ("cudnn", "torch", "backends"), "environment": ("conda", "docker", "env"),
}


def alias_map():
    global _ALIAS
    if _ALIAS is None:
        _ALIAS = {}
        for canon, spec in rules("keys")["keys"].items():
            _ALIAS[_nk(canon)] = canon
            for a in spec.get("aliases", []):
                _ALIAS.setdefault(_nk(a), canon)
    return _ALIAS


def canon_key(path, context=""):
    """Canonical key for a dotted path or raw key -> (canon or None, how). Generic leaves such as 'version' or
    'size' only map when a parent component (or the context hint, e.g. the file name) names their domain."""
    am = alias_map()
    full = _nk(path)
    parts = [x for x in re.split(r"[.:/]|__", str(path).lower()) if x.strip()]
    leaf = _nk(parts[-1]) if parts else full
    parents = " ".join(parts[:-1]) + " " + str(context).lower()
    if full != leaf and full in am:
        return am[full], "full"
    if leaf in am:
        ctx = GENERIC_NEEDS_CONTEXT.get(leaf)
        if not ctx:
            return am[leaf], "leaf"
        if any(c in parents for c in ctx):
            return am[leaf], "leaf+context"
        return None, "generic-without-context"
    return None, None


def key_category(canon):
    spec = rules("keys")["keys"].get(canon or "", {})
    return spec.get("category")


def key_label(canon, lang="en"):
    spec = rules("keys")["keys"].get(canon or "", {})
    if lang == "zh" and spec.get("label_zh"):
        return spec["label_zh"]
    return spec.get("label", canon)


def is_series_key(k):
    return _nk(k) in {_nk(x) for x in rules("keys").get("series_keys", [])}


# ---------------------------------------------------------------- language

def lang_of(text):
    cjk = len(re.findall(f"[{CJK}]", text or ""))
    lat = len(re.findall(r"[A-Za-z]", text or ""))
    return "zh" if cjk * 2 >= max(lat, 1) * 0.5 and cjk > 0 else "en"


def norm_str(v):
    return re.sub(r"\s+", " ", str(v).strip().strip("'\"`").lower())


def sha256_file(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()
