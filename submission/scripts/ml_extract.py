"""Step 1 of methods-ledger: read every material file of a case and extract source-located facts
(parameters, setup, data, controls, reproducibility items, pipeline stages), detect conflicts between sources
and gaps against the element checklist, and write the agent's working files.

python ml_extract.py --case /input/case.json --out /app/output --work /app/work [--lang zh|en] [--profile ml|wetlab|simulation|stats|generic]
Writes work/facts.json, work/facts.md (what the agent reads), work/state.json, work/draft.md (skeleton, only if absent),
and a provisional output/result.json (status partial) so a valid result exists from the first minute."""
import argparse
import ast
import csv
import io
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ml_common as C  # noqa: E402

CONFIG_EXT = {".yaml", ".yml", ".json", ".toml", ".ini", ".cfg", ".conf", ".env", ".properties", ".mdp", ".params", ".hparams"}
CODE_EXT = {".py", ".r", ".m", ".jl", ".sh", ".bash", ".zsh", ".slurm", ".sbatch", ".pbs", ".lsf", ".ipynb", ".js", ".ts", ".cpp", ".c", ".java", ".scala", ".do", ".sas"}
LOG_EXT = {".log", ".out", ".err", ".stdout", ".stderr", ".trace"}
TABLE_EXT = {".csv", ".tsv"}
DOC_EXT = {".md", ".markdown", ".txt", ".rst", ".tex", ".docx", ".pdf", ".text", ".org", ".html", ".htm"}
SKIP_EXT = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif", ".tiff", ".svg", ".pt", ".pth", ".ckpt", ".bin", ".npy", ".npz", ".pkl", ".h5", ".hdf5", ".zip", ".gz", ".tar", ".xz", ".7z", ".safetensors", ".parquet", ".arrow", ".xls", ".pptx", ".so", ".dll", ".exe"}
SPECIAL_NAMES = {"incar": "config", "kpoints": "config", "poscar": "data", "makefile": "code", "dockerfile": "code", "snakefile": "code", "procfile": "code"}
KIND_RANK = {"log": 1, "cli": 2, "env": 3, "config": 4, "code": 5, "table": 6, "doc_kv": 7, "doc": 8}
SPLIT_WORDS = [("val", r"(?i)(?<![a-z_])(?:val|valid|validation|dev)(?![a-z])|验证"), ("test", r"(?i)(?<![a-z_])(?:test|testing|eval|evaluation)(?![a-z])|测试|评测")]
BASELINE_RE = re.compile(r"(?i)baseline|tfidf|tf-idf|(?<![a-z])control|对照|基线|(?<![a-z])base_")
LOG_PREFIX_RE = re.compile(r"^\s*\[?\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(?::\d{2}(?:[.,]\d+)?)?\]?\s*(?:\[?(?:INFO|WARNING|WARN|DEBUG|ERROR|CRITICAL)\]?\s*[:\-]?\s*)?")
SNAPSHOT_RE = re.compile(r"(?i)(?:downloaded|accessed|retrieved|snapshot|dumped|下载(?:于|日期)?|获取(?:于|日期)|快照)\s*(?:on|at|date|:|：|于|\()?\s*(?:\d{4}-\d{1,2}-\d{1,2}|\d{4}/\d{1,2}/\d{1,2}|\d{4}年\d{1,2}月(?:\d{1,2}日)?)")
PATTERN_HOWS = ("pattern", "epoch-of", "version", "seed-call", "split-count", "ratio", "snapshot")
TEXT_NUM_CANONS = {"n_samples", "n_imputations", "seed", "split_seed", "n_runs", "num_gpus", "num_nodes", "k_folds", "test_size", "val_size", "train_size", "alpha_level", "num_classes", "epochs", "max_steps"}

GPU_RE = re.compile(r"(?i)\b(?:NVIDIA\s+)?(?:GeForce\s+|Tesla\s+|Quadro\s+)?(?:RTX\s*)?(A100|H100|H800|A800|H200|B200|V100|A6000|A5000|A40|A30|A10G?|L40S?|L4|T4|P100|P40|K80|RTX\s*[2-5]0[5-9]0(?:\s*Ti)?|[2-5]0[5-9]0\s*Ti|TITAN\s*(?:RTX|V|Xp?)|MI2[05]0X?|MI300X?|TPU\s*v\d\w*|Ascend\s*910\w?)(?:[-\s]*(?:SXM\d?|PCIe|NVL))?(?:[-\s]*(\d+)\s*GB)?")
CPU_RE = re.compile(r"(?i)\b(Intel\(?R?\)?\s+Xeon\(?R?\)?[\w\s\-]{0,30}?\d{4}\w?|AMD\s+EPYC\s+\d{4}\w*|Apple\s+M[1-4](?:\s+(?:Pro|Max|Ultra))?|Intel\s+Core\s+i[3579]-\d{4,5}\w*|AMD\s+Ryzen\s+\d\s+\d{4}\w*)")
GPU_COUNT_RE = re.compile(r"(?i)(\d+)\s*[x×*]\s*(?:NVIDIA\s+)?(?:RTX\s*)?(?:A100|H100|H800|A800|V100|A6000|A40|L40S?|T4|P100|RTX|GPU)|(\d+)\s+(?:NVIDIA\s+)?(?:A100|H100|V100|A6000|A40|L40S?|T4|RTX\s*\d{4})\s+GPUs?|(\d+)\s*(?:块|张|个)\s*(?:GPU|显卡)|(?:A100|H100|H800|A800|V100|A6000|A40|L40S?|T4|P100|RTX\s*\d{4})[\w\-]*\s*[x×*]\s*(\d+)\b|gres=gpu(?::\w+)?:(\d+)|nproc_per_node[= ](\d+)|CUDA_VISIBLE_DEVICES=([\d,]+)")
VER_LINE_RE = re.compile(r"(?i)\b(python|xgboost|catboost|statsmodels|torch|pytorch|torchvision|cuda|cudnn|nccl|numpy|scipy|pandas|scikit-learn|sklearn|transformers|datasets|accelerate|deepspeed|peft|tensorflow|keras|jax|lightning|timm|xgboost|lightgbm|gromacs|lammps|vasp|openmm|rdkit|matlab|R|lme4|spss|stata|graphpad prism|prism|imagej|fiji|cellpose|scanpy|seurat|vllm|gcc|openmpi|driver)\b(?:\s+version)?\s*(?:[:=]|==|\bv|\s)\s*v?(\d+(?:\.\d+){0,3}[\w.+-]*)")
STAT_RE = re.compile(r"\b(ttest_ind|ttest_rel|ttest_1samp|wilcoxon|mannwhitneyu|kruskal|f_oneway|chi2_contingency|fisher_exact|pearsonr|spearmanr|t\.test|wilcox\.test|aov|anova|TukeyHSD|lmer|glmer|glm|bootstrap|permutation_test|multipletests|bonferroni|holm|fdr_bh)\b")
METRIC_RE = re.compile(r"\b(accuracy_score|f1_score|precision_score|recall_score|roc_auc_score|average_precision_score|mean_squared_error|mean_absolute_error|r2_score|matthews_corrcoef|cohen_kappa_score|top_k_accuracy_score)\b|evaluate\.load\(\s*['\"]([\w-]+)['\"]|load_metric\(\s*['\"]([\w-]+)['\"]")
OPT_RE = re.compile(r"\b(?:torch\.)?optim\.(AdamW|Adam|SGD|RMSprop|Adagrad|Adadelta|Adamax|NAdam|RAdam|LBFGS)\b|\b(AdamW|Adafactor|Lion|LAMB)\s*\(")
SCHED_RE = re.compile(r"\blr_scheduler\.(\w+)|\b(get_(?:cosine|linear|constant|polynomial_decay)_schedule(?:_with_warmup)?)\b|\b(CosineAnnealingLR|CosineAnnealingWarmRestarts|OneCycleLR|StepLR|MultiStepLR|ExponentialLR|ReduceLROnPlateau|LinearLR)\b")
MODEL_RE = re.compile(r"from_pretrained\(\s*['\"]([^'\"]+)['\"]|\bmodels\.(resnet\d+|vit_\w+|efficientnet_\w+|densenet\d+|vgg\d+\w*|mobilenet_\w+|convnext_\w+)\b|timm\.create_model\(\s*['\"]([^'\"]+)['\"]")
DATASET_RE = re.compile(r"load_dataset\(\s*['\"]([^'\"]+)['\"](?:\s*,\s*['\"]([^'\"]+)['\"])?|datasets\.(CIFAR10|CIFAR100|MNIST|FashionMNIST|ImageNet|SVHN|STL10|CelebA|VOCDetection|CocoDetection)\b")
LOSS_RE = re.compile(r"\bnn\.(CrossEntropyLoss|BCEWithLogitsLoss|BCELoss|MSELoss|L1Loss|SmoothL1Loss|NLLLoss|KLDivLoss|HuberLoss|CTCLoss)\b")
SEED_CALL_RE = re.compile(r"\b(manual_seed|manual_seed_all|seed_everything|set_seed|random\.seed|np\.random\.seed|numpy\.random\.seed|set\.seed|tf\.random\.set_seed|default_rng|RandomState|PRNGKey|rng)\s*\(\s*(\d+)\s*\)")
COMMIT_RE = re.compile(r"(?i)\b(?:commit|git[_ ]?(?:hash|sha|rev)|revision|HEAD is now at|code version)\b\s*[:=]?\s*([0-9a-f]{7,40})\b")
CMD_RE = re.compile(r"^\s*(?:\$\s*|>\s*|srun\s+|mpirun(?:\s+-n?p?\s*\d+)?\s+|CUDA_VISIBLE_DEVICES=[\d,]+\s+)?((?:python3?|torchrun|accelerate\s+launch|deepspeed|bash|sh|Rscript|julia|matlab|gmx|lmp|lmp_\w+|mpirun|vasp_\w+|make|snakemake|nextflow)\b[^\n]*)")
EPOCH_OF_RE = re.compile(r"(?i)\bepoch\s*[:\[]?\s*(\d+)\s*/\s*(\d+)")
SPLITCOUNT_RE = re.compile(r"(?i)(\d[\d,]*)\s+(train(?:ing)?|val(?:idation)?|dev|test(?:ing)?)\s+(?:samples|examples|images|instances|sentences|records|pairs|items|documents|utterances|subjects|patients|molecules|structures)|\b(train(?:ing)?|val(?:idation)?|dev|test(?:ing)?)(?:[ _](?:set|split))?(?:[ _](?:size|samples|examples))?\s*[:=]\s*(\d[\d,]*)(?![\d.,])|(训练集|验证集|测试集)\s*[:：为有共]?\s*(\d[\d,]*)(?![\d.])")
RATIO_RE = re.compile(r"(?<![\d.])(\d{1,2}(?:\.\d+)?)\s*[:/]\s*(\d{1,2}(?:\.\d+)?)\s*[:/]\s*(\d{1,2}(?:\.\d+)?)(?![\d.])")
KV_LINE_RE = re.compile(r"(?<![\w.\-])([A-Za-z_一-鿿][\w./\-一-鿿]{0,40}?)\s*(?:[=:：]|\bis\b|\bof\b|为|设为|设置为)\s*([-+]?\d[\w.,\-+%×^]*|True|False|true|false|None|null|'[^'\n]{0,80}'|\"[^\"\n]{0,80}\"|[A-Za-z][\w.\-/]{0,60}(?:\s+\d[\d.]*(?![\w.]))?)")
DICT_KV_RE = re.compile(r"['\"]([A-Za-z_][\w.\-]{0,40})['\"]\s*:\s*([-+]?\d[\w.,\-+]*|True|False|None|'[^']{0,80}'|\"[^\"]{0,80}\")")
CLI_RE = re.compile(r"(?<!\S)--?([A-Za-z][\w.\-]*)(?:[= ](?!--?[A-Za-z])((?:\"[^\"]*\"|'[^']*'|[^\s\\]+)))?")


class Facts:
    def __init__(self):
        self.items = []
        self._seen = {}

    def add(self, file, line, kind, key, value, context="", path=None, canon=None, how=None, ctx_hint="", extra=None):
        if value is None:
            return None
        sval = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False) if isinstance(value, (list, dict)) else str(value)
        sval = sval.strip()
        if sval == "" or len(sval) > 400:
            return None
        path = path or key
        if canon is None and how is None:
            canon, how = C.canon_key(path, ctx_hint)
        sig = (file, line, path, sval)
        if sig in self._seen:
            return self._seen[sig]
        vsig = (file, canon, sval) if how in PATTERN_HOWS and canon else None
        if vsig and vsig in self._seen:
            return self._seen[vsig]
        nums = C.value_nums(value) if not isinstance(value, str) else [t[1] for t in C.num_tokens(sval)]
        scope = ""
        low = (str(path) + " " + (context if kind in ("log", "doc", "doc_kv", "table") and how not in PATTERN_HOWS else "")).lower()
        hits = [name for name, rx in SPLIT_WORDS if re.search(rx, low)]
        if len(hits) == 1:
            scope = hits[0]
        if BASELINE_RE.search(str(file) + " " + str(path)):
            scope = ("baseline/" + scope) if scope else "baseline"
        if vsig:
            self._seen[vsig] = None
        f = {"id": None, "file": file, "line": line, "kind": kind, "key": str(key), "path": str(path), "canon": canon,
             "category": C.key_category(canon) if canon else None, "value": sval, "nums": nums,
             "scope": scope, "context": (context or "").strip()[:220]}
        if extra:
            f.update(extra)
        self.items.append(f)
        self._seen[sig] = f
        if vsig:
            self._seen[vsig] = f
        return f


# ---------------------------------------------------------------- classification

def classify(rel, text, task_text):
    name = os.path.basename(rel).lower()
    ext = os.path.splitext(name)[1]
    if name in ("case.json",):
        return "case"
    if name.startswith("task") and ext in (".md", ".txt"):
        return "task"
    if name in SPECIAL_NAMES:
        return SPECIAL_NAMES[name]
    if re.match(r"requirements.*\.txt$|.*\.lock$|pip[-_]?freeze.*|environment\.ya?ml$|conda.*\.ya?ml$|pyproject\.toml$|setup\.cfg$|env.*\.txt$", name):
        return "env"
    if name.startswith("in.") or name.endswith((".in", ".lmp")):
        return "config"
    if ext in LOG_EXT or re.search(r"(^|[_.\-])(log|stdout|stderr|output|nohup)([_.\-]|$)", name):
        return "log"
    if ext in CONFIG_EXT:
        if ext == ".json" and re.search(r"(?i)result|metric|score|eval", name):
            return "results"
        return "config"
    if ext in CODE_EXT:
        return "code"
    if ext in TABLE_EXT or ext in (".xlsx", ".xlsm"):
        return "table"
    if ext in DOC_EXT or ext == "":
        if text and re.search(r"(?im)^\s*\[?\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}", text) and len(re.findall(r"(?m)^\s*\[?\d{4}-\d{2}-\d{2}", text)) > 5:
            return "log"
        if text and len(re.findall(r"(?im)^\s*(epoch|step|iter)\b", text)) > 5:
            return "log"
        low = name + " " + (text[:3000].lower() if text else "")
        if re.search(r"(?i)draft|草稿|初稿|methods?[_ -]?section|方法章节|旧稿", name):
            return "draft"
        if re.search(r"(?i)data[_ -]?card|dataset|datasheet|数据说明|数据集说明|readme_data", low[:400]) or re.search(r"(?i)\bdata\b|数据", name):
            return "datacard"
        return "doc"
    return "other"


# ---------------------------------------------------------------- parsers

def _scalar(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "'\"":
        return v[1:-1]
    return v


def _strip_comment(line):
    out, q = [], None
    for i, ch in enumerate(line):
        if q:
            if ch == q:
                q = None
        elif ch in "'\"":
            q = ch
        elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
            break
        out.append(ch)
    return "".join(out).rstrip()


def parse_yaml_lines(text):
    """Minimal YAML (mappings, '- ' lists, flow scalars). Yields (line_no, dotted_path, value_str)."""
    stack = []  # (indent, key)
    list_idx = {}
    for ln, raw in enumerate(text.split("\n"), 1):
        if raw.strip() in ("---", "...") or not raw.strip() or raw.lstrip().startswith("#"):
            continue
        line = _strip_comment(raw)
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        body = line.strip()
        is_item = body.startswith("- ") or body == "-"
        if is_item:
            while stack and stack[-1][0] >= indent and not (stack[-1][0] == indent and stack[-1][1].startswith("#list")):
                if stack[-1][0] < indent:
                    break
                stack.pop()
            parent = ".".join(k for _, k in stack if not k.startswith("#list"))
            idx = list_idx.get((parent, indent), 0)
            list_idx[(parent, indent)] = idx + 1
            body = body[1:].strip()
            m = re.match(r"^([^:{}\[\]'\"]+?):\s*(.*)$", body)
            if m:
                yield ln, (parent + "." if parent else "") + f"{idx}.{m.group(1).strip()}", _scalar(m.group(2)) if m.group(2) else None
                stack.append((indent + 1, f"{idx}"))
            elif body:
                yield ln, parent or "item", _scalar(body)
            continue
        m = re.match(r"^([^:#{}\[\]]+?|\"[^\"]+\"|'[^']+'):(?:\s+(.*))?$", body)
        if not m:
            continue
        key = _scalar(m.group(1).strip())
        val = m.group(2)
        while stack and stack[-1][0] >= indent:
            stack.pop()
        path = ".".join([k for _, k in stack] + [key])
        if val is None or val.strip() in ("", "|", ">", "|-", ">-"):
            stack.append((indent, key))
            continue
        val = val.strip()
        if val.startswith("&") or val.startswith("*"):
            val = val.split(" ", 1)[1] if " " in val else val
        yield ln, path, _scalar(val)


def _flatten(obj, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _flatten(v, f"{prefix}.{k}" if prefix else str(k))
    elif isinstance(obj, list) and obj and all(isinstance(x, (dict, list)) for x in obj):
        for i, v in enumerate(obj):
            yield from _flatten(v, f"{prefix}.{i}")
    else:
        yield prefix, obj


def _line_finder(text):
    lines = text.split("\n")
    used = {}

    def find(leaf, value):
        pat = re.compile(r"[\"']?" + re.escape(str(leaf)) + r"[\"']?\s*[:=]")
        start = used.get(leaf, 0)
        for i in range(start, len(lines)):
            if pat.search(lines[i]):
                used[leaf] = i + 1
                return i + 1
        for i, l in enumerate(lines):
            if pat.search(l):
                return i + 1
        return 1
    return find, lines


def extract_config(rel, text, F, kind="config"):
    ext = os.path.splitext(rel)[1].lower()
    name = os.path.basename(rel).lower()
    hint = rel.lower()
    done = False
    if ext == ".json":
        try:
            obj = json.loads(text)
            find, lines = _line_finder(text)
            for path, v in _flatten(obj):
                if path == "":
                    continue
                leaf = path.split(".")[-1]
                ln = find(leaf, v)
                F.add(rel, ln, kind, leaf, v, context=lines[ln - 1] if ln - 1 < len(lines) else "", path=path, ctx_hint=hint)
            done = True
        except ValueError:
            pass
    if not done and ext == ".toml":
        try:
            import tomllib  # noqa
            obj = tomllib.loads(text)
            find, lines = _line_finder(text)
            for path, v in _flatten(obj):
                leaf = path.split(".")[-1]
                ln = find(leaf, v)
                F.add(rel, ln, kind, leaf, v, context=lines[ln - 1], path=path, ctx_hint=hint)
            done = True
        except Exception:  # noqa
            pass
    lines = text.split("\n")
    if not done and ext in (".yaml", ".yml"):
        for ln, path, v in parse_yaml_lines(text):
            if v is None:
                continue
            F.add(rel, ln, kind, path.split(".")[-1], v, context=lines[ln - 1], path=path, ctx_hint=hint)
        done = True
    if done:
        return
    # INI / mdp / INCAR / env / LAMMPS / generic key = value
    section = ""
    lammps = name.startswith("in.") or ext in (".in", ".lmp")
    for ln, raw in enumerate(lines, 1):
        line = re.split(r"\s[#;!]|^[#;!]", raw, 1)[0].strip() if not lammps else raw.split("#", 1)[0].strip()
        if not line:
            continue
        m = re.match(r"^\[([^\]]+)\]$", line)
        if m:
            section = m.group(1).strip()
            continue
        if name == "kpoints" and re.match(r"^\d+\s+\d+\s+\d+(\s|$)", line):
            F.add(rel, ln, kind, "kpoints", " ".join(line.split()[:3]), context=raw, canon="kpoints", how="file")
            continue
        m = re.match(r"^(?:export\s+)?([A-Za-z_][\w.\-]*)\s*[=:]\s*(.+)$", line)
        if m:
            key, val = m.group(1), _scalar(m.group(2))
            F.add(rel, ln, kind, key, val, context=raw, path=(section + "." + key) if section else key, ctx_hint=hint)
            continue
        if lammps:
            toks = line.split()
            head = toks[0].lower()
            rest = " ".join(toks[1:])
            if head == "velocity" and len(toks) > 4 and toks[2].lower() == "create":
                F.add(rel, ln, kind, "velocity.temp", toks[3], context=raw, canon="temperature", how="lammps", path="velocity.initial_temperature")
                F.add(rel, ln, kind, "velocity.seed", toks[4], context=raw, canon="seed", how="lammps")
            elif head == "timestep":
                F.add(rel, ln, kind, "timestep", rest, context=raw, canon="timestep", how="lammps")
            elif head == "run":
                F.add(rel, ln, kind, "run", toks[1] if len(toks) > 1 else rest, context=raw, canon="nsteps", how="lammps")
            elif head == "fix" and len(toks) > 3 and toks[3].lower() in ("nvt", "npt", "nve", "langevin", "nph", "temp/berendsen", "temp/rescale"):
                F.add(rel, ln, kind, "fix", toks[3], context=raw, canon="ensemble", how="lammps")
                lt = [t.lower() for t in toks]
                if "temp" in lt:
                    i = lt.index("temp")
                    F.add(rel, ln, kind, "temp", " ".join(toks[i + 1:i + 4]), context=raw, canon="temperature", how="lammps")
                if "iso" in lt or "aniso" in lt:
                    i = lt.index("iso") if "iso" in lt else lt.index("aniso")
                    F.add(rel, ln, kind, "press", " ".join(toks[i + 1:i + 4]), context=raw, canon="pressure", how="lammps")
            elif head in ("pair_style", "pair_coeff", "units", "atom_style", "kspace_style", "velocity", "minimize", "thermo", "dump", "read_data", "lattice", "region", "create_atoms", "neighbor"):
                F.add(rel, ln, kind, head, rest, context=raw, canon={"pair_style": "force_field", "pair_coeff": "force_field"}.get(head), how="lammps")
            continue
        m = re.match(r"^([A-Za-z_][\w.\-]*)\s+(\S.*)$", line)
        if m and ext in (".cfg", ".conf", ".params", ".hparams", ""):
            F.add(rel, ln, kind, m.group(1), _scalar(m.group(2)), context=raw, ctx_hint=hint)


def extract_cli(rel, ln, cmd, F, raw_line):
    for m in CLI_RE.finditer(cmd):
        key, val = m.group(1), m.group(2)
        if val is None:
            val = "true"
        val = _scalar(val)
        F.add(rel, ln, "cli", key, val, context=raw_line, path=key)
    for m in re.finditer(r"(?<![\w-])([A-Za-z_][\w.]*)=([^\s]+)", cmd):  # hydra style key=value overrides
        if m.group(0).startswith("--"):
            continue
        F.add(rel, ln, "cli", m.group(1), _scalar(m.group(2)), context=raw_line, path=m.group(1))


def extract_common_patterns(rel, text, F, kind):
    """Hardware, versions, seeds, commits, commands, split counts, epoch totals - any file type."""
    stages = []
    lines = text.split("\n")
    for ln, line in enumerate(lines, 1):
        if len(line) > 2000:
            line = line[:2000]
        for m in GPU_RE.finditer(line):
            F.add(rel, ln, kind, "gpu", m.group(0).strip(), context=line, canon="hardware", how="pattern")
        for m in CPU_RE.finditer(line):
            F.add(rel, ln, kind, "cpu", m.group(0).strip(), context=line, canon="hardware", how="pattern")
        for m in GPU_COUNT_RE.finditer(line):
            n = next((g for g in m.groups() if g), None)
            if n is not None:
                val = str(len(n.split(","))) if "," in n or m.group(0).startswith("CUDA_VISIBLE") else n
                F.add(rel, ln, kind, "num_gpus", val, context=line, canon="num_gpus", how="pattern")
        for m in VER_LINE_RE.finditer(line):
            name = m.group(1).lower()
            if kind in ("code",) and not re.search(r"(?i)version|==|requires", line):
                continue
            if name == "r" and not re.search(r"R version|R\s*[=:]", line):
                continue
            canon = {"pytorch": "torch", "torch": "torch", "python": "python", "cuda": "cuda", "cudnn": "cudnn"}.get(name, "software_stats" if name in ("r", "spss", "stata", "graphpad prism", "prism", "lme4") else "software")
            F.add(rel, ln, kind, name, m.group(2), context=line, canon=canon, how="version", path=f"version.{name}")
        for m in SEED_CALL_RE.finditer(line):
            F.add(rel, ln, kind, m.group(1), m.group(2), context=line, canon="seed", how="seed-call")
        for m in COMMIT_RE.finditer(line):
            F.add(rel, ln, kind, "commit", m.group(1), context=line, canon="code_version", how="pattern")
        for m in SNAPSHOT_RE.finditer(line):
            F.add(rel, ln, kind, "snapshot", m.group(0).strip(), context=line, canon="dataset_version", how="snapshot")
        for m in DURATION_RE.finditer(line):
            obj = re.findall(r"\b([A-Z][A-Z0-9][A-Z0-9\-]{0,10})\b", line)
            obj = [o for o in obj if o not in ("SOP", "CO2", "DMSO", "PBS", "RT", "NVT", "NPT") and not re.fullmatch(r"P\d+", o)]
            sub = (obj[0] if obj else re.sub(r"(?i)(ion|ing|ed|e|s)$", "", m.group(1).lower())[:8])
            F.add(rel, ln, kind, f"duration.{sub}", f"{m.group(2)} {m.group(3)}", context=line, canon="duration", how="pattern",
                  path=f"text.duration.{sub}", extra={"subkey": sub})
        for m in REPEAT_RE.finditer(line):
            n = next(g for g in m.groups() if g and not re.match(r"(?i)^(experiments|replicates|repeats|runs|repetitions|trials|seeds)$", g))
            F.add(rel, ln, kind, "n_runs", WORDNUM.get(n.lower(), n), context=line, canon="n_runs", how="pattern")
        if re.search(r"(?i)imput|mice|插补", line):
            for m in re.finditer(r"(?<![\w])m\s*[=＝]\s*(\d+)", line):
                F.add(rel, ln, kind, "m", m.group(1), context=line, canon="n_imputations", how="pattern")
        for m in STATWORD_RE.finditer(line):
            F.add(rel, ln, kind, "statistical_test", (m.group(1) or m.group(2)).strip(), context=line, canon="statistical_test", how="pattern")
        for m in LOT_RE.finditer(line):
            v = next(g for g in m.groups() if g)
            F.add(rel, ln, kind, "lot", v, context=line, canon="lot" if not v.upper().startswith("ATCC") else "reagent", how="pattern")
        for m in SIMSOFT_RE.finditer(line):
            F.add(rel, ln, kind, m.group(1).lower(), m.group(2).strip(), context=line, canon="software", how="version", path=f"version.{m.group(1).lower()}")
        for m in MODULE_RE.finditer(line):
            F.add(rel, ln, kind, m.group(1).lower(), m.group(2), context=line, canon="software", how="version", path=f"version.{m.group(1).lower()}")
        for m in SIZE_RE.finditer(line):
            sub = re.sub(r"^个", "", m.group(2).lower())
            F.add(rel, ln, kind, f"system_size.{sub}", f"{m.group(1)} {m.group(2)}", context=line, canon="system_size", how="pattern",
                  path=f"text.system_size.{sub}", extra={"subkey": sub})
        for m in WALL_RE.finditer(line):
            F.add(rel, ln, kind, "wall_time", (m.group(1) or m.group(2)).strip(), context=line, canon="wall_time", how="pattern")
        if kind == "code":
            for m in re.finditer(r"library\((\w+)\)\s*#\s*(?:\1\s*)?v?(\d+\.\d+(?:[.\-]\d+)*)", line):
                F.add(rel, ln, kind, m.group(1), m.group(2), context=line, canon="software_stats", how="version", path=f"version.{m.group(1).lower()}")
        m = CMD_RE.match(LOG_PREFIX_RE.sub("", line, 1) if kind == "log" else line)
        if m and kind in ("log", "code", "doc", "datacard", "draft", "env") and not line.lstrip().startswith(("#!", "#SBATCH")):
            cmd = m.group(1).strip()
            if len(cmd) > 6 and not re.match(r"^(bash|sh)\s*$", cmd):
                F.add(rel, ln, "cli" if kind != "doc" else "doc", "command", cmd, context=line, canon="command", how="command")
                stages.append({"file": rel, "line": ln, "command": cmd})
                extract_cli(rel, ln, cmd, F, line)
        if line.lstrip().startswith("#SBATCH") or line.lstrip().startswith("#PBS"):
            extract_cli(rel, ln, line.split(None, 1)[1] if " " in line.strip() else "", F, line)
        for m in EPOCH_OF_RE.finditer(line):
            F.add(rel, ln, kind, "epoch_total", m.group(2), context=line, canon="epochs", how="epoch-of")
        for m in SPLITCOUNT_RE.finditer(line):
            g = m.groups()
            if g[0]:
                n, sp = g[0], g[1]
            elif g[2]:
                sp, n = g[2], g[3]
            else:
                sp, n = g[4], g[5]
            spn = "n_train" if re.match(r"(?i)train|训练", sp) else "n_test" if re.match(r"(?i)test|测试", sp) else "n_val"
            F.add(rel, ln, kind, spn, n, context=line, canon=spn, how="split-count")
        if re.search(r"(?i)split|ratio|划分|比例|train\s*/\s*val|训练.{0,6}验证", line):
            for m in RATIO_RE.finditer(line):
                a = [float(x) for x in m.groups()]
                if abs(sum(a) - 10) < 1e-6 or abs(sum(a) - 100) < 1e-6 or abs(sum(a) - 1) < 1e-6:
                    F.add(rel, ln, kind, "split_ratio", m.group(0), context=line, canon="split_ratio", how="ratio")
    return stages


def extract_log(rel, text, F):
    lines = text.split("\n")
    per_key = {}
    line_facts, seen_bodies = [], set()
    for ln, line in enumerate(lines, 1):
        if len(line) > 2000:
            line = line[:2000]
        body = LOG_PREFIX_RE.sub("", line, 1).strip()
        for rx in (DICT_KV_RE, KV_LINE_RE):
            for m in rx.finditer(body):
                k, v = m.group(1), _scalar(m.group(2).rstrip(",;)"))
                if re.match(r"^\d", k) or len(k) < 2 or k.lower() in ("http", "https", "info", "warning", "error", "debug", "time", "date"):
                    continue
                canon, how = C.canon_key(k, rel)
                if canon is None and not re.search(r"\d", v):
                    continue
                if canon == "hardware" and (GPU_RE.search(line) or CPU_RE.search(line)):
                    continue
                per_key.setdefault(k, []).append((ln, v, line))
        if C.num_tokens(body) and len(line_facts) < 400 and body not in seen_bodies and not CMD_RE.match(body):
            seen_bodies.add(body)
            line_facts.append((ln, body, line))
    series = {}
    for k, occ in per_key.items():
        distinct = list(dict.fromkeys(v for _, v, _ in occ))
        if C.is_series_key(k) or len(distinct) > 3:
            vals = [C.parse_num(v) for _, v, _ in occ]
            vals = [x for x in vals if x is not None]
            series[k] = {"count": len(occ), "first": occ[0][1], "first_line": occ[0][0], "last": occ[-1][1], "last_line": occ[-1][0],
                         "min": min(vals) if vals else None, "max": max(vals) if vals else None}
            F.add(rel, occ[0][0], "log", k, occ[0][1], context=occ[0][2], extra={"series": "first"})
            F.add(rel, occ[-1][0], "log", k, occ[-1][1], context=occ[-1][2], extra={"series": "last"})
            continue
        seen = set()
        for ln, v, line in occ:
            if v in seen:
                continue
            seen.add(v)
            canon, how = C.canon_key(k, rel)
            F.add(rel, ln, "log", k, v, context=line, canon=canon, how=how or "log-kv")
    for ln, body, line in line_facts:
        F.add(rel, ln, "doc", "log_line", body[:380], context=line, canon=None, how="log-line", extra={"doc_class": "log"})
    return series


def notebook_text(text):
    """Cell sources and text outputs of a .ipynb as plain text; fact line numbers of notebooks refer to this text."""
    try:
        nb = json.loads(text)
    except ValueError:
        return text
    parts = []
    for i, cell in enumerate(nb.get("cells", [])):
        src = cell.get("source", [])
        parts.append(f"# [cell {i + 1} {cell.get('cell_type')}]\n" + ("".join(src) if isinstance(src, list) else str(src)).rstrip("\n"))
        for o in cell.get("outputs", []):
            t = o.get("text", []) or o.get("data", {}).get("text/plain", [])
            t = "".join(t) if isinstance(t, list) else str(t)
            if t.strip():
                parts.append(f"# [cell {i + 1} output]\n" + t.rstrip("\n"))
    return "\n".join(parts)


def extract_code(rel, text, F):
    ext = os.path.splitext(rel)[1].lower()
    if ext == ".ipynb":
        text = notebook_text(text)
        out_lines = False
        for ln, line in enumerate(text.split("\n"), 1):
            if line.startswith("# [cell "):
                out_lines = line.endswith("output]")
                continue
            if out_lines and line.strip():
                if C.num_tokens(line) or C.VERSION_RE.search(line):
                    F.add(rel, ln, "doc", "output_line", line.strip()[:380], context=line, canon=None, how="nb-output", extra={"doc_class": "notebook output"})
                for m in VER_LINE_RE.finditer(line):
                    F.add(rel, ln, "log", m.group(1).lower(), m.group(2), context=line, canon="software", how="version", path=f"version.{m.group(1).lower()}")
    lines = text.split("\n")
    offs = [0]
    for l in lines:
        offs.append(offs[-1] + len(l) + 1)

    def ln_of(pos):
        lo, hi = 0, len(offs) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if offs[mid] <= pos:
                lo = mid
            else:
                hi = mid - 1
        return lo + 1
    for m in re.finditer(r"add_argument\(\s*['\"](--?[\w\-]+)['\"](?:\s*,\s*['\"]--?[\w\-]+['\"])*(.*?)\)\s*(?:\n|$)", text, flags=re.S):
        key = m.group(1).lstrip("-")
        body = m.group(2)
        d = re.search(r"default\s*=\s*([^,\n)]+(?:\([^)]*\))?)", body)
        ln = ln_of(m.start())
        if d:
            F.add(rel, ln, "code", key, _scalar(d.group(1).strip()), context=lines[ln - 1], extra={"code_role": "argparse default"})
        if re.search(r"action\s*=\s*['\"]store_true", body) and not d:
            F.add(rel, ln, "code", key, "False (store_true flag)", context=lines[ln - 1], extra={"code_role": "argparse flag"})
        ch = re.search(r"choices\s*=\s*(\[[^\]]*\])", body)
        if ch:
            F.add(rel, ln, "code", key + ".choices", ch.group(1), context=lines[ln - 1], path=key + ".choices", canon=None, how="choices")
    for ln, line in enumerate(lines, 1):
        s = line.strip()
        if s.startswith(("#", "//")) and not s.startswith("#SBATCH"):
            continue
        m = re.match(r"^([A-Z][A-Z0-9_]{1,40})\s*(?::\s*\w+\s*)?=\s*([-+]?[\d.][\w.eE+\-]*|True|False|'[^']*'|\"[^\"]*\"|\[[^\]]*\])\s*(?:#.*)?$", s)
        if m:
            F.add(rel, ln, "code", m.group(1), _scalar(m.group(2)), context=line, extra={"code_role": "constant"})
            continue
        m = re.match(r"^([a-z_][\w.]*)\s*(?:<-|=)\s*([-+]?\d[\w.eE+\-]*|'[^']*'|\"[^\"]*\")\s*(?:#.*)?$", s)
        if m:
            canon, how = C.canon_key(m.group(1), rel)
            if canon:
                F.add(rel, ln, "code", m.group(1), _scalar(m.group(2)), context=line, canon=canon, how=how, extra={"code_role": "assignment"})
        for m in re.finditer(r"[(,]\s*([a-z_]\w*)\s*=\s*([-+]?\d[\w.eE+\-]*|True|False|'[^']*'|\"[^\"]*\"|[a-z_]\w*)(?=\s*[,)])", line):
            k, v = m.group(1), _scalar(m.group(2))
            canon, how = C.canon_key(k, rel)
            if canon == "seed" and re.search(r"(?i)split|fold|shuffle|sample\(", line):
                canon, how = "split_seed", "split-call"
            if canon and (re.match(r"^[-+]?\d|True|False|['\"]", m.group(2)) or k in ("stratify", "shuffle")):
                F.add(rel, ln, "code", k, v, context=line, canon=canon, how=how, extra={"code_role": "keyword argument"})
        for m in OPT_RE.finditer(line):
            F.add(rel, ln, "code", "optimizer", m.group(1) or m.group(2), context=line, canon="optimizer", how="pattern")
        for m in SCHED_RE.finditer(line):
            F.add(rel, ln, "code", "scheduler", next(g for g in m.groups() if g), context=line, canon="scheduler", how="pattern")
        for m in MODEL_RE.finditer(line):
            v = next(g for g in m.groups() if g)
            if not re.match(r"^(args|cfg|config)\b", v):
                F.add(rel, ln, "code", "model", v, context=line, canon="model", how="pattern")
        for m in DATASET_RE.finditer(line):
            F.add(rel, ln, "code", "dataset", m.group(1) or m.group(3), context=line, canon="dataset", how="pattern")
            if m.group(2):
                F.add(rel, ln, "code", "dataset_config", m.group(2), context=line, canon="dataset_version", how="load_dataset config")
        for m in LOSS_RE.finditer(line):
            F.add(rel, ln, "code", "loss", m.group(1), context=line, canon="loss", how="pattern")
        for m in STAT_RE.finditer(line):
            F.add(rel, ln, "code", "statistical_test", m.group(1), context=line, canon="statistical_test", how="pattern")
        for m in METRIC_RE.finditer(line):
            F.add(rel, ln, "code", "metric", next(g for g in m.groups() if g), context=line, canon="metric", how="pattern")
    return text


def extract_env(rel, text, F):
    for ln, line in enumerate(text.split("\n"), 1):
        s = line.strip().lstrip("-").strip()
        m = re.match(r"^([A-Za-z0-9_.\-\[\]]+)\s*(==|=|>=|~=|<=|@)\s*([\w.+\-]+)", s)
        if not m or s.startswith("#"):
            continue
        pkg = re.sub(r"\[.*\]", "", m.group(1)).lower()
        ver = m.group(3)
        op = m.group(2)
        canon = {"torch": "torch", "pytorch": "torch", "python": "python", "cudatoolkit": "cuda", "pytorch-cuda": "cuda", "cuda": "cuda", "cudnn": "cudnn"}.get(pkg, "software")
        F.add(rel, ln, "env", pkg, ver if op in ("==", "=") else op + ver, context=line, canon=canon, how="requirement", path=f"version.{pkg}",
              extra={"pinned": op in ("==", "=")})


def extract_sheets(rel, text, F):
    """xlsx text from C.read_xlsx: one '## sheet <name>' block per sheet; line numbers stay those of the text."""
    lines = text.split("\n")
    starts = [i for i, ln in enumerate(lines) if ln.startswith("## sheet ")] or [-1]
    info = {"sheets": []}
    for k, st in enumerate(starts):
        end = starts[k + 1] if k + 1 < len(starts) else len(lines)
        block = "\n".join(lines[st + 1:end])
        sub = extract_table(rel, block, F, offset=st + 1, sheet=lines[st][9:].strip() if st >= 0 else "")
        info["sheets"].append({"sheet": lines[st][9:].strip() if st >= 0 else "", **sub})
    return info


def extract_table(rel, text, F, offset=0, sheet=""):
    delim = "\t" if rel.lower().endswith(".tsv") or text.count("\t") > text.count(",") else ","
    rows = list(csv.reader(io.StringIO(text), delimiter=delim))
    rows = [r for r in rows if any(c.strip() for c in r)]
    if not rows:
        return {"rows": 0}
    header = [h.strip() for h in rows[0]]
    body = rows[1:]
    info = {"rows": len(body), "columns": header}
    F.add(rel, 1 + offset, "table", (sheet + ".") * bool(sheet) + "n_rows", str(len(body)), context="header: " + ", ".join(header)[:200], canon=None, how="table-size")
    if len(body) <= 80:
        for i, r in enumerate(body, 2):
            label = r[0].strip() if r else ""
            for j, cell in enumerate(r):
                cell = cell.strip()
                if j >= len(header) or not cell:
                    continue
                canon, how = C.canon_key(header[j], rel)
                if j == 0 and not canon:
                    continue
                F.add(rel, i + offset, "table", header[j], cell, context=f"{label} | {header[j]} = {cell}", path=f"{label}.{header[j]}" if label else header[j],
                      canon=canon, how=how or "table-cell", extra={"row_label": label, "sheet": sheet})
    else:
        for j, h in enumerate(header):
            canon, how = C.canon_key(h, rel)
            if canon:
                vals = list(dict.fromkeys(r[j].strip() for r in body if j < len(r)))
                if len(vals) <= 5:
                    for v in vals:
                        F.add(rel, 2 + offset, "table", h, v, context=f"column {h}", canon=canon, how="table-column")
    return info


ALIAS_TEXT_RE = None


def _alias_text_re():
    global ALIAS_TEXT_RE
    if ALIAS_TEXT_RE is None:
        words = set()
        for canon, spec in C.rules("keys")["keys"].items():
            for a in spec.get("aliases", []) + [spec.get("label", "")]:
                a = a.strip()
                if len(a) >= 4 or re.search(f"[{C.CJK}]", a) and len(a) >= 2:
                    words.add(re.escape(a).replace("_", "[ _-]").replace("\\ ", "[ _-]"))
        alt = "|".join(sorted(words, key=len, reverse=True))
        ALIAS_TEXT_RE = re.compile(r"(?i)(?<![A-Za-z])(" + alt + r")(?![A-Za-z])([^.;。；\n]{0,25}?)(?<![\w.])([-+]?\d[\d,.]*(?:\s*(?:[eE][-+]?\d+|[x×]\s*10\^?[-−]?\d+))?\s*%?)")
    return ALIAS_TEXT_RE


def between_ok(b):
    """Text between a parameter word and its number may only be separators/stopwords (not 'Seed HeLa cells at 5,000')."""
    if len(re.findall(f"[{C.CJK}]", b)) > 6:
        return False
    rest = re.sub(f"[{C.CJK}]", "", b)
    rest = re.sub(r"(?i)\b(of|is|was|were|set|to|at|for|all|runs?|approximately|about|initial|final|used|a|an|the)\b", "", rest)
    return not re.search(r"[A-Za-z]", rest)
DURATION_RE = re.compile(r"(?i)(incubat\w*|reaction|react\w*|centrifug\w*|shak\w*|stir\w*|anneal\w*|sonicat\w*|equilibrat\w*|hold\w*|treat\w*|孵育|反应|离心|振荡|搅拌|退火|超声|平衡|处理)[^.;。；\n]{0,30}?(?<![\w.])(\d+(?:\.\d+)?)\s*(min|minutes?|h|hrs?|hours?|s|sec|seconds?|days?|d|ps|ns|fs|分钟|小时|秒|天)(?![A-Za-z])")
REPEAT_RE = re.compile(r"(?i)\b(\d+|two|three|four|five|six|seven|eight|nine|ten)\s+(?:independent\s+|biological\s+|technical\s+)?(experiments|replicates|repeats|runs|repetitions|trials|seeds)\b|\bin\s+(duplicate|triplicate|quadruplicate)\b|(?:重复|独立)\s*(\d+)\s*次|(\d+)\s*次(?:独立|重复)|(\d+)\s*个?(?:平行|复孔|生物学重复)|(?:只|仅)(?:跑|运行|做)了?\s*(一|1)\s*(?:条|次|个)")
WORDNUM = {"one": "1", "two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
           "duplicate": "2", "triplicate": "3", "quadruplicate": "4", "一": "1"}
STATWORD_RE = re.compile(r"(?i)\b(dunnett'?s?|tukey'?s?(?: hsd)?|bonferroni|holm|sidak|welch'?s? t-test|student'?s? t-test|paired t-test|t-test|mann[- ]whitney|wilcoxon|kruskal[- ]wallis|one-way anova|two-way anova|anova|chi-square|fisher'?s exact|bootstrap|permutation test|mixed[- ]effects? model|linear mixed model)\b|(t\s*检验|方差分析|卡方检验|秩和检验|多重比较)")
LOT_RE = re.compile(r"(?i)\b(?:lot|batch no\.?|lot no\.?|cat(?:alog(?:ue)?)?\.?\s*(?:no\.?|#))\s*[:#]?\s*([A-Z0-9][A-Z0-9\-]{2,})\b|\b(ATCC\s+[A-Z]{2,4}-\d+)|批号\s*[:：]?\s*([A-Za-z0-9\-]+)")
SIMSOFT_RE = re.compile(r"(?i)\b(LAMMPS|GROMACS|VASP|Gaussian|ORCA|CP2K|Quantum ESPRESSO|NAMD|AMBER|OpenMM|CHARMM|Materials Studio)\b\s*\(?\s*(?:version\s*|v)?(\d{1,2}\s+[A-Z][a-z]{2}\s+\d{4}(?:\s*-\s*Update\s*\d+)?|\d+(?:\.\d+)+[\w.\-]*|\d{4}(?:\.\d+)*)")
MODULE_RE = re.compile(r"(?i)\bmodule\s+load\s+([\w\-]+)/([\w.\-]+)")
SIZE_RE = re.compile(r"(?i)(?<![\w.])(\d[\d,]*)\s+(atoms|molecules|residues|particles|ions|个?原子|个?分子)")
WALL_RE = re.compile(r"(?i)(?:total\s+)?wall(?:[- ]clock)?\s*time\s*[:=]?\s*([\d:.]+\s*(?:s|h|min)?)|(?:运行|计算)耗时\s*[:：]?\s*([\d:.]+\s*(?:s|h|min|小时|分钟)?)")


def extract_doc(rel, text, F, kind):
    lines = text.split("\n")
    rx = _alias_text_re()
    for ln, line in enumerate(lines, 1):
        s = line.strip()
        if not s:
            continue
        m = re.match(r"^\s*(?:[-*+]\s+|\|\s*)?\**([^:：|*]{1,40}?)\**\s*[:：|]\s*(.+?)\s*\|?$", s)
        if m and not re.match(r"^(https?|ftp)$", m.group(1).strip(), re.I):
            key, val = m.group(1).strip(), m.group(2).strip()
            canon, how = C.canon_key(key, rel)
            if canon or re.search(r"\d", val):
                F.add(rel, ln, "doc_kv", key, val, context=s, canon=canon, how=how)
        for m in rx.finditer(s):
            label, between, num = m.group(1), m.group(2), m.group(3).strip().rstrip(".,")
            if not between_ok(between):
                continue
            canon, how = C.canon_key(label.replace(" ", "_"), rel)
            if canon is None:
                for c, spec in C.rules("keys")["keys"].items():
                    if spec.get("label", "").lower() == label.lower():
                        canon, how = c, "label"
                        break
            if re.match(r"\s*[:/]\s*\d", s[m.end():m.end() + 4]):
                continue
            if canon and (C.key_category(canon) == "params" or canon in TEXT_NUM_CANONS):
                F.add(rel, ln, "doc_kv", label, num, context=s, path=f"text.{label}", canon=canon, how="text-mention")
        if C.num_tokens(s) or re.search(r"(?i)\bv?\d+\.\d+", s) or (
            rel.lower().endswith(".pdf") and re.search(r"(?i)\b(?:fp16|bf16|mixed precision|gpu|cpu)\b|混合精度", s)
        ):
            F.add(rel, ln, "doc", "sentence", s[:380], context=s, canon=None, how="sentence", extra={"doc_class": kind})


# ---------------------------------------------------------------- analysis

def number_facts(facts):
    for i, f in enumerate(facts, 1):
        f["id"] = f"F{i}"


VERSIONED = ("software", "torch", "python", "cuda", "cudnn", "software_stats")
MULTI_VALUED = ("hardware", "metric", "model", "baseline", "statistical_test", "preprocessing", "reagent", "instrument", "loss",
                "dataset", "sample_source", "inclusion", "force_field", "license", "source_url", "lot", "dataset_version")


def norm_value_key(f):
    if f["canon"] in VERSIONED:
        v = C.norm_str(f["value"]).lstrip("v=")
        return ("v", re.split(r"[+\s]", v)[0])
    if f["nums"]:
        return ("n",) + tuple(sorted(round(x, 9) for x in f["nums"]))
    v = C.norm_str(f["value"])
    v = re.sub(r"^(torch\.)?optim\.", "", v)
    return ("s", v)


def compatible(k1, k2):
    if k1 == k2:
        return True
    if k1[0] == "v" and k2[0] == "v":
        a, b = k1[1], k2[1]
        return a.startswith(b) or b.startswith(a)
    if k1[0] == "n" and k2[0] == "n":
        s1, s2 = set(k1[1:]), set(k2[1:])
        return s1 <= s2 or s2 <= s1
    if k1[0] == "s" and k2[0] == "s":
        return k1[1] in k2[1] or k2[1] in k1[1]
    if {k1[0], k2[0]} == {"s", "n"}:
        s = k1 if k1[0] == "s" else k2
        n = k2 if s is k1 else k1
        return s[1] in ("true", "false") and all(x in (0.0, 1.0) for x in n[1:]) and ((s[1] == "true") == (1.0 in n[1:]))
    return False


def find_conflicts(facts, lang="en"):
    """Same canonical key + scope, incompatible values, from different files (or duplicated inside one config).
    Code defaults are dropped when a command line, config or log sets the same key (they were overridden)."""
    groups = {}
    for f in facts:
        if not f["canon"] or f["kind"] == "doc" or f.get("series") or f["category"] is None:
            continue
        if f["canon"] in ("command", "output_dir", "data_path", "checkpoint", "val_file", "test_file", "code_version") or f["key"].endswith(".choices"):
            continue
        if f["canon"] in MULTI_VALUED:
            continue
        if re.search(r"\$\{?\w+|%\(?\w*\)?[sd]|\{\w*\}", str(f["value"])):
            continue  # shell/template placeholder ($SEED), not a value
        if f["canon"] in VERSIONED:
            if str(f["value"]).startswith((">", "~", "<", "^")):
                continue
            key = (f["canon"], f["path"].split(".")[-1].lower() if f["canon"] in ("software", "software_stats") else "", f["scope"])
        else:
            sub = f.get("subkey", "") or (C._nk(f["key"]) if f["canon"] in ("n_samples", "system_size", "duration") else "")
            key = (f["canon"], sub, f["scope"])
        groups.setdefault(key, []).append(f)
    conflicts = []
    for (canon, sub, scope), fs in groups.items():
        tab = [f for f in fs if f["kind"] == "table"]
        if len({norm_value_key(f) for f in tab}) > 1:
            fs = [f for f in fs if f["kind"] != "table"]  # one value per table row (e.g. per-seed results), not a conflict
        overridden = []
        if any(f["kind"] in ("cli", "config", "log") for f in fs):
            overridden = [f for f in fs if f["kind"] == "code" and f.get("code_role") == "argparse default"]
            fs = [f for f in fs if f not in overridden]
        clusters = []
        for f in fs:
            k = norm_value_key(f)
            for c in clusters:
                if compatible(c["key"], k):
                    c["facts"].append(f)
                    break
            else:
                clusters.append({"key": k, "facts": [f]})
        run_cfg = {f["file"] for c in clusters if any(x["kind"] in ("log", "cli") for x in c["facts"]) for f in c["facts"] if f["kind"] == "config"}
        if run_cfg:
            alt = [c for c in clusters if all(x["kind"] == "config" and x["file"] not in run_cfg for x in c["facts"])]
            clusters = [c for c in clusters if c not in alt]  # sibling config of another run (e.g. a baseline), not a conflict
            fs = [f for c in clusters for f in c["facts"]]
        if len(clusters) < 2:
            continue
        files = {f["file"] for f in fs}
        if len(files) < 2 and not all(f["kind"] == "config" for f in fs):
            continue
        ordered = sorted(fs, key=lambda f: (KIND_RANK.get(f["kind"], 9), f["file"], f["line"]))
        values = []
        for c in clusters:
            cf = sorted(c["facts"], key=lambda f: (KIND_RANK.get(f["kind"], 9), f["file"], f["line"]))
            values.append({"value": cf[0]["value"], "fact": cf[0]["id"], "facts": [f["id"] for f in cf],
                           "source": f"{cf[0]['file']}:{cf[0]['line']}", "sources": [f"{f['file']}:{f['line']}" for f in cf][:8],
                           "kind": cf[0]["kind"], "kinds": sorted({f["kind"] for f in cf})})
        values.sort(key=lambda v: min(KIND_RANK.get(k, 9) for k in v["kinds"]))
        conflicts.append({"id": None, "canon": canon, "label": C.key_label(canon, lang) + (f" ({sub})" if sub else ""), "scope": scope,
                          "values": values, "facts": [f["id"] for f in ordered], "n_files": len(files),
                          "precedence_guess": values[0]["fact"],
                          "overridden_code_defaults": [f"{f['id']}={f['value']} ({f['file']}:{f['line']})" for f in overridden],
                          "note": "precedence run log > command line > environment > config > code default > notes is a guess, not a resolution - ask the author"})
    for i, c in enumerate(conflicts, 1):
        c["id"] = f"C{i}"
    return conflicts


def detect_profile(texts, task_text):
    prof = C.rules("checklist")["profiles"]
    joined = (task_text + "\n" + "\n".join(texts))[:400000]
    scores = {}
    for name, spec in prof.items():
        if spec.get("markers"):
            scores[name] = len(re.findall(spec["markers"], joined))
    best = max(scores.items(), key=lambda kv: kv[1]) if scores else ("generic", 0)
    ordered = sorted(scores.items(), key=lambda kv: -kv[1])
    if best[1] < 3:
        return "generic", scores
    second = [k for k, v in ordered[1:] if v >= max(5, best[1] * 0.6)]
    return best[0] + ("+" + "+".join(second) if second else ""), scores


def elements_for(profile):
    profs = set(profile.split("+"))
    out = []
    for e in C.rules("checklist")["elements"]:
        if "all" in e["profiles"] or profs & set(e["profiles"]):
            out.append(e)
    return out


def find_gaps(facts, profile, lang, stages, all_text):
    gaps = []
    canon_present = {}
    for f in facts:
        if f["canon"]:
            canon_present.setdefault(f["canon"], []).append(f["id"])
    for e in elements_for(profile):
        have = []
        for k in e["keys"]:
            have += canon_present.get(k, [])
        if e["id"] in ("E_baseline", "E_controls"):
            have += [f["id"] for f in facts if f["scope"].startswith("baseline")][:8]
        if e["id"] == "E_steps":
            if stages:
                continue
        if e["id"] == "E_limits":
            gaps.append({"id": None, "element": e["id"], "category": e["category"], "level": e["level"], "label": e["label"][lang],
                         "status": "author_input", "question": e["question"][lang],
                         "why": "limitations must name concrete untested conditions; materials rarely state them - derive candidates from the facts (single seed, one dataset version, one hardware type) and ask the author"})
            continue
        if e["id"] == "E_software" and have and not any(k in canon_present for k in ("torch", "python", "cuda", "software_stats")) and "ml" in profile:
            gaps.append({"id": None, "element": e["id"], "category": e["category"], "level": "recommended", "label": e["label"][lang], "status": "partial",
                         "question": e["question"][lang], "facts": have[:8], "why": "framework/Python/CUDA versions not found"})
            continue
        if not have:
            dp = e.get("draft_patterns", {}).get(lang) or e.get("draft_patterns", {}).get("en")
            mat = bool(dp and re.search(dp, all_text)) if e["id"] not in ("E_seed", "E_dataset_version", "E_repeats") else False
            gaps.append({"id": None, "element": e["id"], "category": e["category"], "level": e["level"], "label": e["label"][lang],
                         "status": "only_mentioned_in_text" if mat else "missing", "question": e["question"][lang],
                         "why": "no structured fact found" + ("; the topic appears in some material text - read the doc sentences" if mat else " in any material")})
    # specific checks
    seeds = [f for f in facts if f["canon"] == "seed"]
    runs = [f for f in facts if f["canon"] == "n_runs"]
    if seeds and not runs and len({norm_value_key(f) for f in seeds}) == 1:
        gaps.append({"id": None, "element": "E_repeats", "category": "control", "level": "required", "label": "single seed only?" if lang == "en" else "是否仅单个种子？",
                     "status": "ambiguous", "question": ("Only one seed value appears in the materials: were results from a single run? If several runs, list their seeds."
                                                        if lang == "en" else "材料中只出现一个随机种子取值：报告结果是否来自单次运行？若有多次运行，请列出各次种子。"),
                     "facts": [f["id"] for f in seeds][:5], "why": "one seed, no repetition count"})
    vers = [f for f in facts if f["canon"] in ("software", "torch", "python", "cuda") and f["kind"] == "env" and not f.get("pinned", True)]
    if vers:
        gaps.append({"id": None, "element": "E_software", "category": "setup", "level": "recommended", "label": "unpinned versions" if lang == "en" else "未锁定的版本",
                     "status": "ambiguous", "question": ("Some requirements are ranges (>=, ~=): give the exact installed versions (pip freeze) of the reported run."
                                                        if lang == "en" else "部分依赖只写了版本范围（>=、~=）：请给出报告运行时实际安装的精确版本（pip freeze）。"),
                     "facts": [f["id"] for f in vers][:8], "why": "version range is not reproducible"})
    for i, g in enumerate(gaps, 1):
        g["id"] = f"G{i}"
    return gaps


# ---------------------------------------------------------------- case / task

def load_case(case_path):
    info = {"case_path": case_path, "problems": []}
    case = {}
    if case_path and os.path.exists(case_path):
        try:
            case = C.load_json(case_path, {}) or {}
        except ValueError as e:
            info["problems"].append(f"case.json is not valid JSON: {e}")
            with open(case_path, "rb") as fh:
                raw = fh.read().decode("utf-8", errors="replace")
            m = re.search(r'"case_id"\s*:\s*"([^"]+)"', raw)
            case = {"case_id": m.group(1)} if m else {}
    else:
        info["problems"].append("case.json not found")
    return case, info


def _schema_type(v):
    if isinstance(v, dict):
        t = v.get("type")
        if isinstance(t, list):
            t = next((x for x in t if x != "null"), None)
        return t if isinstance(t, str) else None
    return None


def contract_fields(case):
    """Top-level fields of the output contract; JSON Schema (properties/required/type) is honoured."""
    oc = case.get("output_contract") or case.get("outputs") or case.get("output_fields") or case.get("expected_output") or {}
    fields = []
    if isinstance(oc, dict):
        if "fields" in oc and isinstance(oc["fields"], (list, dict)):
            return contract_fields({"output_contract": oc["fields"]})
        if isinstance(oc.get("properties"), dict):
            req = oc.get("required") if isinstance(oc.get("required"), list) else []
            names = list(oc["properties"]) + [r for r in req if isinstance(r, str) and r not in oc["properties"]]
            for k in names:
                spec = oc["properties"].get(k, {})
                desc = spec.get("description") if isinstance(spec, dict) and isinstance(spec.get("description"), str) else json.dumps(spec, ensure_ascii=False)
                fields.append({"name": k, "desc": desc[:300], "type": _schema_type(spec), "required": k in req})
            return fields
        if isinstance(oc.get("required"), list) and set(oc) <= {"required", "type", "$schema", "title", "description", "additionalProperties"}:
            return [{"name": k, "desc": "", "type": None, "required": True} for k in oc["required"] if isinstance(k, str)]
        for k, v in oc.items():
            if k in ("$schema", "title", "type", "additionalProperties") and not isinstance(v, dict):
                continue
            fields.append({"name": k, "desc": v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)[:300], "type": _schema_type(v)})
    elif isinstance(oc, list):
        for x in oc:
            if isinstance(x, str):
                fields.append({"name": x, "desc": ""})
            elif isinstance(x, dict):
                n = x.get("name") or x.get("field") or x.get("key")
                if n:
                    fields.append({"name": n, "desc": x.get("description") or x.get("desc") or json.dumps(x, ensure_ascii=False)[:300], "type": _schema_type(x)})
    elif isinstance(oc, str):
        for n in re.findall(r"[A-Za-z_][\w]*", oc):
            fields.append({"name": n, "desc": ""})
    return fields


def contract_closed(case):
    oc = case.get("output_contract") if isinstance(case, dict) else None
    return bool(isinstance(oc, dict) and oc.get("additionalProperties") is False)


PATH_KEYS = ("path", "file", "filename", "file_path", "uri", "src", "location", "name")
ROLE_KEYS = ("role", "type", "kind", "purpose", "category", "usage", "description", "label")
PRIMARY_RE = re.compile(r"(?i)primary|main|principal|core|source[_ ]?of[_ ]?truth|主材料|主要|核心|事实底稿|底稿")


def declared_materials(case):
    """[(path, role)] declared anywhere in case.json; role 'primary' when the entry or its parent key says so."""
    out = []

    def walk(o, parent=""):
        if isinstance(o, dict):
            p = next((o[k] for k in PATH_KEYS if isinstance(o.get(k), str) and re.search(r"[./\\]", o[k])), None)
            if p:
                role_txt = " ".join(str(o.get(k, "")) for k in ROLE_KEYS) + " " + parent
                if PRIMARY_RE.search(role_txt) or o.get("primary") is True or o.get("is_primary") is True:
                    role = "primary"
                else:
                    role = str(o.get("role") or o.get("type") or "")[:40] or "declared"
                out.append((p, role))
            for k, v in o.items():
                if k != "output_contract":
                    walk(v, k)
        elif isinstance(o, list):
            for v in o:
                walk(v, parent)
        elif isinstance(o, str) and parent and len(o) < 300 and re.search(r"\.\w{1,6}$", o) and not re.search(r"\s", o):
            out.append((o, "primary" if PRIMARY_RE.search(parent) else "declared"))
    walk(case)
    return out


def resolve_declared(p, in_dir, paths):
    cands = [p] if os.path.isabs(p) else []
    cands += [os.path.join(in_dir, p), os.path.join("/input", p), os.path.join(os.path.dirname(in_dir), p)]
    for c in cands:
        if os.path.isfile(c):
            return os.path.abspath(c)
    base = os.path.basename(p.replace("\\", "/"))
    hit = [x for x in paths if os.path.basename(x) == base]
    return os.path.abspath(hit[0]) if len(hit) == 1 else None


def default_case():
    for c in ("/input/case.json", os.path.join(os.getcwd(), "input", "case.json"), "/app/input/case.json", os.path.join(os.getcwd(), "case.json")):
        if os.path.isfile(c):
            return c
    return "/input/case.json"


def target_language(task_text, case, override):
    if override:
        return override
    blob = json.dumps(case, ensure_ascii=False) + "\n" + task_text
    if re.search(r"(?i)(in|into|用)\s*English|英文(撰写|写作|写|输出|稿)|language\s*[:=]\s*['\"]?en", blob):
        return "en"
    if re.search(r"(?i)(in|into)\s*Chinese|中文(撰写|写作|写|输出|稿)|language\s*[:=]\s*['\"]?zh|用中文", blob):
        return "zh"
    return C.lang_of(task_text or json.dumps(case, ensure_ascii=False))


# ---------------------------------------------------------------- output

def render_facts_md(state, facts, conflicts, gaps, stages, series, lang):
    L = []
    L.append(f"# Facts for case `{state['case_id']}` (methods-ledger {C.VERSION})")
    L.append(f"profile: **{state['profile']}** · target language: **{lang}** · {len(facts)} facts from {len(state['files'])} files · "
             f"{len(conflicts)} conflicts · {len(gaps)} gaps/questions")
    L.append("Write the chapter in normal academic prose, copying values exactly as listed. ml_build.py maps every number, version and name "
             "to these facts automatically; tags such as `[[F12]]` are optional and only help where a value occurs in several facts.")
    L.append("")
    L.append("## Material index (primary materials first)")
    for fi in sorted(state["files"], key=lambda x: (x.get("role") != "primary", x["path"])):
        L.append(f"- `{fi['path']}` — {fi.get('role') or 'material'}, {fi['class']}, {fi.get('lines', '?')} lines, {fi.get('n_facts', 0)} facts" + (f" — {'; '.join(fi['problems'])}" if fi.get("problems") else ""))
    for m in state.get("declared_missing", []):
        L.append(f"- `{m}` — declared in case.json but NOT FOUND (write the dependent items as GAP)")
    L.append("")
    L.append("## Required sections (each must be written with material values, or marked GAP)")
    for e in elements_for(state["profile"]):
        L.append(f"- [{e['level']}] {e['label'][lang]} ({e['category']})")
    if state.get("contract"):
        L.append("")
        L.append("## output_contract (ml_build.py writes these fields at the top level of result.json)")
        for f in state["contract"]:
            L.append(f"- `{f['name']}`" + (f" ({f['type']})" if f.get("type") else "") + (f": {f['desc'][:120]}" if f.get("desc") else ""))
    if state.get("task_excerpt"):
        L.append("")
        L.append("## Task (excerpt)")
        L.append(state["task_excerpt"])
    cats = C.rules("checklist")["categories"]
    struct = [f for f in facts if f["kind"] != "doc" and (f["canon"] or f["kind"] in ("config", "cli", "env", "table"))]
    conflict_of = {}
    for c in conflicts:
        for fid in c["facts"]:
            conflict_of.setdefault(fid, []).append(c["id"])
    shown = set()
    for cat in ["steps", "setup", "params", "data", "control", "repro"]:
        rows = [f for f in struct if f["category"] == cat]
        if not rows:
            continue
        L.append("")
        L.append(f"## {cats[cat]['en']} / {cats[cat]['zh']}")
        L.append("| id | key (canonical) | value | source | kind | flags |")
        L.append("|---|---|---|---|---|---|")
        for f in sorted(rows, key=lambda f: (f["canon"] or "", KIND_RANK.get(f["kind"], 9)))[:120]:
            flags = []
            if f["id"] in conflict_of:
                flags.append("CONFLICT " + ",".join(conflict_of[f["id"]]))
            if f.get("series"):
                flags.append("series " + f["series"])
            if f["scope"]:
                flags.append("scope " + f["scope"])
            if f.get("code_role"):
                flags.append(f["code_role"])
            L.append(f"| {f['id']} | {f['path']} ({f['canon']}) | `{f['value'][:80]}` | {f['file']}:{f['line']} | {f['kind']} | {'; '.join(flags)} |")
            shown.add(f["id"])
    other = [f for f in struct if f["id"] not in shown]
    if other:
        L.append("")
        L.append("## Other structured values (not mapped to a known key)")
        L.append("| id | key | value | source | kind |")
        L.append("|---|---|---|---|---|")
        for f in other[:150]:
            L.append(f"| {f['id']} | {f['path']} | `{f['value'][:80]}` | {f['file']}:{f['line']} | {f['kind']} |")
        if len(other) > 150:
            L.append(f"... {len(other) - 150} more in facts.json")
    if series:
        L.append("")
        L.append("## Logged series (values that change during a run; not conflicts)")
        for (file, k), s in list(series.items())[:40]:
            L.append(f"- `{file}` {k}: {s['count']} values, first {s['first']} (l.{s['first_line']}), last {s['last']} (l.{s['last_line']}), range {s['min']}–{s['max']}")
    docs = [f for f in facts if f["kind"] == "doc"]
    if docs:
        L.append("")
        L.append("## Evidence lines in notes / data cards / PDFs / drafts")
        for f in docs[:200]:
            L.append(f"- {f['id']} `{f['file']}:{f['line']}` {f['value'][:200]}")
        if len(docs) > 200:
            L.append(f"... {len(docs) - 200} more in facts.json")
    if stages:
        L.append("")
        L.append("## Pipeline stages / commands found (method steps should cover each)")
        for s in stages[:40]:
            L.append(f"- `{s['file']}:{s['line']}` `{s['command'][:160]}`")
    L.append("")
    L.append("## Conflicts (must be marked [[CONFIRM: ...]] or resolved in agent.json)")
    if not conflicts:
        L.append("none found")
    for c in conflicts:
        L.append(f"- **{c['id']}** {c['label']}{' [' + c['scope'] + ']' if c['scope'] else ''}: " + "; ".join(f"`{v['value'][:40]}` ({', '.join(v['facts'][:4])}; {', '.join(v['sources'][:3])}; {'/'.join(v['kinds'])})" for v in c["values"]) +
                 f" — precedence guess {c['precedence_guess']}")
    L.append("")
    L.append("## Gaps / author questions (write [[GAP: ...]] in the draft where the information belongs)")
    if not gaps:
        L.append("none")
    for g in gaps:
        L.append(f"- **{g['id']}** [{g['category']}, {g['level']}, {g['status']}] {g['label']}: {g['question']}")
    return "\n".join(L) + "\n"


SKELETON = {
    "zh": """<!-- methods-ledger draft. Cite facts as [[F12]]; mark missing items [[GAP: 问题]]; conflicting values [[CONFIRM: C1 ...]];
derived numbers [[CALC: 8000/10000 = 0.8 | F3,F4]]; a material line not in facts [[SRC: file:line]]. Delete this comment if you like. -->
# 方法与实验

## 方法步骤

## 实验设置

## 数据集与划分

## 参数设置

## 对照实验与评价

## 可复现性

## 限制条件
""",
    "en": """<!-- methods-ledger draft. Cite facts as [[F12]]; mark missing items [[GAP: question]]; conflicting values [[CONFIRM: C1 ...]];
derived numbers [[CALC: 8000/10000 = 0.8 | F3,F4]]; a material line not in facts [[SRC: file:line]]. Delete this comment if you like. -->
# Methods and Experiments

## Method steps

## Experimental setup

## Datasets and splits

## Parameters

## Baselines, controls and evaluation

## Reproducibility

## Limitations
"""}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--case", default=None, help="default: /input/case.json, ./input/case.json or /app/input/case.json")
    ap.add_argument("--input-dir", default=None, help="material directory (default: directory of case.json)")
    ap.add_argument("--out", default=None, help="default: /app/output (./output outside the evaluator)")
    ap.add_argument("--work", default=None, help="default: /app/work (./work outside the evaluator)")
    ap.add_argument("--lang", choices=["zh", "en"], default=None)
    ap.add_argument("--profile", default=None)
    ap.add_argument("--max-file-mb", type=float, default=20.0)
    a = ap.parse_args(argv)
    t0 = time.time()
    a.case = a.case or default_case()
    app = os.path.isdir("/app")
    a.out = a.out or ("/app/output" if app else os.path.join(os.getcwd(), "output"))
    a.work = a.work or ("/app/work" if app else os.path.join(os.getcwd(), "work"))
    case, cinfo = load_case(a.case)
    in_dir = a.input_dir or (os.path.dirname(os.path.abspath(a.case)) if a.case else ".")
    case_id = str(case.get("case_id") or case.get("id") or os.path.basename(os.path.normpath(in_dir)) or "case")
    files, problems = [], list(cinfo["problems"])
    task_text = ""
    for cand in ("task.md", "TASK.md", "task.txt"):
        for d in (in_dir, os.path.dirname(in_dir)):
            p = os.path.join(d, cand)
            if os.path.exists(p) and not task_text:
                task_text = C.read_any(p)[0]
    for k in ("task", "instruction", "instructions", "prompt", "description", "requirements", "constraints", "audience", "style"):
        v = case.get(k)
        if isinstance(v, str):
            task_text += "\n" + v
        elif isinstance(v, (list, dict)):
            task_text += "\n" + json.dumps(v, ensure_ascii=False)
    paths = []
    for r, ds, fs in os.walk(in_dir):
        ds[:] = sorted(d for d in ds if not d.startswith(".") and d not in ("__pycache__", "node_modules"))
        for fn in sorted(fs):
            paths.append(os.path.join(r, fn))
    # files declared in case.json (with roles), also outside in_dir
    roles, declared_missing = {}, []
    for p, role in declared_materials(case if isinstance(case, dict) else {}):
        rp = resolve_declared(p, in_dir, paths)
        if not rp:
            if not re.match(r"^(https?:|/app/output|/app/work)", p) and "output" not in role.lower() and p not in declared_missing:
                declared_missing.append(p)
            continue
        if rp not in {os.path.abspath(x) for x in paths}:
            paths.append(rp)
        if roles.get(rp) != "primary":
            roles[rp] = role
    for p in declared_missing:
        problems.append(f"material declared in case.json not found: {p}")
    F = Facts()
    stages, series, texts = [], {}, []
    state_files = []
    lang = None
    for p in paths:
        rel = os.path.relpath(p, in_dir).replace(os.sep, "/") if os.path.abspath(p).startswith(os.path.abspath(in_dir)) else p
        ext = os.path.splitext(p)[1].lower()
        fi = {"path": rel, "bytes": os.path.getsize(p), "sha256": C.sha256_file(p), "problems": [], "role": roles.get(os.path.abspath(p))}
        if ext in SKIP_EXT:
            fi["class"] = "binary-skipped"
            fi["problems"].append("binary/unsupported format, not read" + (" (export spreadsheets to CSV)" if ext in (".xlsx", ".xls") else ""))
            state_files.append(fi)
            continue
        if fi["bytes"] > a.max_file_mb * 1e6:
            fi["class"] = "too-large"
            fi["problems"].append(f"larger than {a.max_file_mb} MB, not read")
            state_files.append(fi)
            continue
        try:
            text, rinfo = C.read_any(p)
        except Exception as e:  # noqa
            fi["class"] = "unreadable"
            fi["problems"].append(f"could not read: {e}")
            state_files.append(fi)
            continue
        if rinfo.get("repairs"):
            fi["problems"] += rinfo["repairs"]
        if rinfo.get("replacement_chars"):
            fi["problems"].append(f"{rinfo['replacement_chars']} unreadable characters (U+FFFD)")
        cls = classify(rel, text, task_text)
        fi["class"] = cls
        fi["lines"] = text.count("\n") + 1
        n0 = len(F.items)
        if cls in ("case", "task"):
            state_files.append(fi)
            continue
        texts.append(text)
        if cls == "config":
            extract_config(rel, text, F)
        elif cls == "results":
            extract_config(rel, text, F, kind="table")
        elif cls == "env":
            if rel.lower().endswith((".yml", ".yaml")):
                for ln, line in enumerate(text.split("\n"), 1):
                    m = re.match(r"^\s*-\s*([A-Za-z0-9_.\-]+)\s*=+\s*([\w.+\-]+)", line)
                    if m:
                        pkg = m.group(1).lower()
                        canon = {"python": "python", "pytorch": "torch", "torch": "torch", "cudatoolkit": "cuda", "pytorch-cuda": "cuda", "cudnn": "cudnn"}.get(pkg, "software")
                        F.add(rel, ln, "env", pkg, m.group(2), context=line, canon=canon, how="conda", path=f"version.{pkg}", extra={"pinned": True})
            else:
                extract_env(rel, text, F)
        elif cls == "log":
            s = extract_log(rel, text, F)
            for k, v in s.items():
                series[(rel, k)] = v
        elif cls == "code":
            text = extract_code(rel, text, F) or text
        elif cls == "table":
            fi["table"] = extract_sheets(rel, text, F) if ext in (".xlsx", ".xlsm") else extract_table(rel, text, F)
        elif cls in ("doc", "datacard", "draft", "data", "other"):
            extract_doc(rel, text, F, cls)
        stages += extract_common_patterns(rel, text, F, {"doc": "doc_kv", "datacard": "doc_kv", "draft": "doc_kv", "other": "doc_kv"}.get(cls, cls if cls in ("log", "code", "config", "env", "table") else "doc_kv"))
        fi["n_facts"] = len(F.items) - n0
        state_files.append(fi)
    facts = F.items
    number_facts(facts)
    lang = target_language(task_text, case, a.lang)
    profile, pscores = (a.profile, {}) if a.profile else detect_profile(texts, task_text)
    conflicts = find_conflicts(facts, lang)
    # dedupe stages by command text
    seen, st2 = set(), []
    for s in stages:
        key = re.sub(r"\s+", " ", s["command"])
        if key not in seen:
            seen.add(key)
            st2.append(s)
    stages = st2
    gaps = find_gaps(facts, profile, lang, stages, "\n".join(texts))
    if not [f for f in state_files if f["class"] not in ("case", "task", "binary-skipped", "unreadable", "too-large")]:
        problems.append("no readable material files besides case/task")
    contract = contract_fields(case)
    state = {"tool": "methods-ledger", "version": C.VERSION, "case_id": case_id, "case_path": os.path.abspath(a.case) if a.case else None,
             "input_dir": os.path.abspath(in_dir), "out": os.path.abspath(a.out), "work": os.path.abspath(a.work), "lang": lang,
             "profile": profile, "profile_scores": pscores, "contract": contract, "files": state_files, "problems": problems,
             "task_excerpt": task_text.strip()[:1500], "stages": stages, "series": [{"file": k[0], "key": k[1], **v} for k, v in series.items()],
             "declared_missing": declared_missing, "contract_closed": contract_closed(case),
             "output_contract": case.get("output_contract", {}) if isinstance(case, dict) else {},
             "extract_seconds": round(time.time() - t0, 2), "case_keys": sorted(case.keys()) if isinstance(case, dict) else []}
    os.makedirs(a.work, exist_ok=True)
    C.dump_json({"facts": facts, "conflicts": conflicts, "gaps": gaps}, os.path.join(a.work, "facts.json"))
    C.dump_json(state, os.path.join(a.work, "state.json"))
    C.write_text(os.path.join(a.work, "facts.md"), render_facts_md(state, facts, conflicts, gaps, stages, series, lang))
    draft = os.path.join(a.work, "draft.md")
    if not os.path.exists(draft):
        C.write_text(draft, SKELETON[lang])
    agentp = os.path.join(a.work, "agent.json")
    if not os.path.exists(agentp):
        C.dump_json({"resolutions": [], "accept": {}, "fields": {}, "notes": [], "status_note": ""}, agentp)
    # provisional result so that a valid file exists even if the run is cut off; a checked result is never
    # replaced by a provisional one from a run whose case.json could not be read
    import ml_build  # noqa
    rp = os.path.join(a.out, "result.json")
    prev = (C.load_json(rp, {}) or {}) if os.path.exists(rp) else {}
    if cinfo["problems"] and isinstance(prev, dict) and prev.get("status") and "provisional" not in str(prev.get("status_reason", "")):
        print("NOTE: case.json could not be read; existing result.json kept")
    else:
        try:
            ml_build.build(a.work, a.out, provisional=True)
        except Exception as e:  # noqa
            fallback = {f["name"]: None for f in contract}
            fallback.update({"case_id": case_id, "status": "partial",
                             "status_reason": f"provisional result; build failed: {e}",
                             "output_contract": state["output_contract"]})
            if state["contract_closed"]:
                C.dump_json(fallback, os.path.join(a.out, "result_full.json"))
                fallback = {"case_id": case_id, **{f["name"]: fallback[f["name"]] for f in contract}}
            C.dump_json(fallback, rp)
    print(f"case_id: {case_id}")
    print(f"language: {lang}   profile: {profile}   files: {len(state_files)}   facts: {len(facts)}   conflicts: {len(conflicts)}   gaps: {len(gaps)}   ({state['extract_seconds']} s)")
    print("contract fields: " + (", ".join(f["name"] for f in contract) or "(none found in case.json)"))
    for fi in state_files:
        print(f"  {fi['class']:<14} {fi['path']}  facts={fi.get('n_facts', 0)}" + (f"  !! {'; '.join(fi['problems'])}" if fi["problems"] else ""))
    for p in problems:
        print("PROBLEM:", p)
    for c in conflicts:
        print(f"CONFLICT {c['id']} {c['label']}: " + " | ".join(f"{v['value'][:30]} ({v['source']})" for v in c["values"]))
    print(f"next: read {os.path.join(a.work, 'facts.md')}, write {draft}")


if __name__ == "__main__":
    main()
