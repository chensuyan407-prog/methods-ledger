"""Rewrite [[F12]] tags of a draft into stable [[@file:line#path]] anchors using a facts.json.
python tests/tools/anchorize.py facts.json draft.md out.md"""
import json
import re
import sys

facts = {f["id"]: f for f in json.load(open(sys.argv[1], encoding="utf-8"))["facts"]}
text = open(sys.argv[2], encoding="utf-8").read()


def anc(fid):
    f = facts[fid]
    return f"@{f['file']}:{f['line']}#{f['path']}" if f["kind"] != "doc" else f"@{f['file']}:{f['line']}#{f['key']}"


def tag(m):
    body = m.group(1)
    if re.match(r"^\s*(GAP|待确认|PARAM_TABLE)", body):
        return m.group(0)
    return "[[" + re.sub(r"\bF\d+\b", lambda mm: anc(mm.group(0)), body) + "]]"


open(sys.argv[3], "w", encoding="utf-8", newline="\n").write(re.sub(r"\[\[(.*?)\]\]", tag, text, flags=re.S))
