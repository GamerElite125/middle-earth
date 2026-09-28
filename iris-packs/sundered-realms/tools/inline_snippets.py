"""Inline the base-pack snippets this pack uses, conformed to a target Iris version.

Iris 4.0.x ships with overworld pack 4002, which does not contain the snippet library that newer
overworld packs have. This copies each snippet referenced by build_pack.py from a newer overworld
pack, inlines nested snippet references, drops fields the target engine does not know and replaces
enum values it does not support. The result is committed as snippets-inline.json so building the
pack never depends on a particular overworld version.

usage: inline_snippets.py <schema.json for the target Iris> <newer overworld pack> <out.json>
"""
import json
import os
import re
import sys

schema = json.load(open(sys.argv[1]))
source = sys.argv[2]
HERE = os.path.dirname(os.path.abspath(__file__))
ENUM_FALLBACK = {"STRATA": "IRIS_DOUBLE", "CRATER": "CELLULAR_IRIS", "POPLAR": "BIRCH"}
SNIPPET_CLASS = {v["snippet"]: k for k, v in schema.items() if v.get("snippet")}
changes = []


def fields_of(cls):
    out = {}
    while cls and cls in schema:
        for k, v in schema[cls]["fields"].items():
            out.setdefault(k, v)
        cls = schema[cls].get("extends")
    return out


def generic(t):
    m = re.match(r"(\w+)<(.*)>$", t)
    return (m.group(1), [a.strip() for a in m.group(2).split(",")]) if m else (t, [])


def conform(val, t, where):
    base, args = generic(t)
    if base in ("KList", "List", "KSet", "Set"):
        return [conform(v, args[0], f"{where}[{i}]") for i, v in enumerate(val)] if isinstance(val, list) else val
    if base not in schema:
        return val
    info = schema[base]
    if info["kind"] == "enum":
        if isinstance(val, str) and info["enum"] and val not in info["enum"]:
            new = ENUM_FALLBACK.get(val, info["enum"][0])
            changes.append(f"{where}: {val} -> {new}")
            return new
        return val
    if isinstance(val, str) and val.startswith("snippet/"):
        return conform(json.load(open(os.path.join(source, val + ".json"))), t, val)
    if not isinstance(val, dict):
        return val
    flds = fields_of(base)
    out = {}
    for k, v in val.items():
        if k not in flds:
            changes.append(f"{where}: dropped {k}")
            continue
        out[k] = conform(v, flds[k]["type"], f"{where}.{k}")
    return out


src = open(os.path.join(HERE, "build_pack.py")).read()
result = {}
for ref in sorted(set(re.findall(r'"(snippet/[^"]+)"', src))):
    folder = ref.split("/")[1]
    cls = SNIPPET_CLASS.get(folder) or {"biome-palette": "IrisBiomePaletteLayer"}.get(folder)
    if not cls:
        sys.exit(f"no class for snippet folder {folder}")
    result[ref] = conform(json.load(open(os.path.join(source, ref + ".json"))), cls, ref)
json.dump(result, open(sys.argv[3], "w"), indent=1, sort_keys=True)
print(len(result), "snippets inlined;", len(changes), "adjustments")
for c in changes:
    print("  ", c)
