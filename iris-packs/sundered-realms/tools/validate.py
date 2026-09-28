"""Validate an Iris pack's JSON against the field schema extracted from engine sources.

usage: validate.py schema.json <merged-pack-dir> [only-files-under-subpath ...]
"""
import json, os, re, sys

schema = json.load(open(sys.argv[1]))
pack = sys.argv[2]
only = [os.path.normpath(p) for p in sys.argv[3:]]
folders = {v['folder']: k for k, v in schema.items() if v.get('folder')}
errors = []
PRIMS = {'String', 'int', 'Integer', 'double', 'Double', 'float', 'Float', 'long', 'Long', 'boolean', 'Boolean', 'short', 'byte', 'Object', 'char'}


def fields_of(cls):
    out = {}
    while cls and cls in schema:
        for k, v in schema[cls]['fields'].items():
            out.setdefault(k, v)
        cls = schema[cls].get('extends')
    return out


def exists(folder, key, ext='.json'):
    return os.path.isfile(os.path.join(pack, folder, key + ext))


def check_ref(refcls, val, where):
    if val == "":
        return
    if refcls not in schema or not schema[refcls].get('folder'):
        return
    folder = schema[refcls]['folder']
    ext = '.iob' if refcls == 'IrisObject' else '.json'
    if refcls == 'IrisLootTable' and val.startswith('minecraft:'):
        return
    if not exists(folder, val, ext):
        errors.append(f'{where}: missing {refcls} reference "{val}" ({folder}/{val}{ext})')


def generic(t):
    m = re.match(r'(\w+)<(.*)>$', t)
    if not m:
        return t, []
    args, depth, cur = [], 0, ''
    for ch in m.group(2):
        if ch == ',' and depth == 0:
            args.append(cur); cur = ''
            continue
        depth += ch == '<'; depth -= ch == '>'
        cur += ch
    args.append(cur)
    return m.group(1), args


def walk(val, t, where, ref=None):
    base, args = generic(t)
    if base in ('KList', 'List', 'ArrayList', 'KSet', 'Set'):
        if not isinstance(val, list):
            errors.append(f'{where}: expected list for {t}, got {type(val).__name__}')
            return
        for i, v in enumerate(val):
            walk(v, args[0], f'{where}[{i}]', ref)
        return
    if base in ('KMap', 'Map', 'HashMap'):
        if not isinstance(val, dict):
            errors.append(f'{where}: expected object for {t}')
        return
    if base in PRIMS:
        if base == 'String':
            if not isinstance(val, str):
                errors.append(f'{where}: expected string, got {val!r}')
            elif ref:
                check_ref(ref, val, where)
        elif base in ('boolean', 'Boolean'):
            if not isinstance(val, bool):
                errors.append(f'{where}: expected boolean, got {val!r}')
        elif base != 'Object':
            if isinstance(val, bool) or not isinstance(val, (int, float)):
                errors.append(f'{where}: expected number, got {val!r}')
            elif base in ('int', 'Integer', 'long', 'Long', 'short') and isinstance(val, float) and not val.is_integer():
                errors.append(f'{where}: expected integer, got {val!r}')
        return
    if base not in schema:
        return  # unknown / platform type: skip
    info = schema[base]
    if info['kind'] == 'enum':
        if not isinstance(val, str) or (info['enum'] and val not in info['enum']):
            errors.append(f'{where}: invalid {base} value {val!r}')
        return
    if isinstance(val, str):
        if val.startswith('snippet/'):
            p = os.path.join(pack, val + '.json')
            if not os.path.isfile(p):
                errors.append(f'{where}: missing snippet {val}')
            else:
                walk(json.load(open(p)), t, f'{val}.json')
            return
        errors.append(f'{where}: string {val!r} given for object type {base}')
        return
    if not isinstance(val, dict):
        errors.append(f'{where}: expected object {base}, got {type(val).__name__}')
        return
    flds = fields_of(base)
    for k, v in val.items():
        if k not in flds:
            errors.append(f'{where}: unknown field "{k}" for {base}')
            continue
        walk(v, flds[k]['type'], f'{where}.{k}', flds[k]['ref'])


count = 0
for folder, cls in folders.items():
    root = os.path.join(pack, folder)
    if not os.path.isdir(root) or cls == 'IrisObject':
        continue
    for dp, _, fs in os.walk(root):
        for f in fs:
            if not f.endswith('.json'):
                continue
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, pack)
            if only and not any(rel.startswith(o) for o in only):
                continue
            try:
                data = json.load(open(p))
            except Exception as e:
                errors.append(f'{rel}: JSON parse error {e}')
                continue
            count += 1
            walk(data, cls, rel)
# snippets under the selected paths
snipdir = os.path.join(pack, 'snippet')
for dp, _, fs in os.walk(snipdir):
    for f in fs:
        p = os.path.join(dp, f); rel = os.path.relpath(p, pack)
        if only and any(rel.startswith(o) for o in only):
            try:
                json.load(open(p)); count += 1
            except Exception as e:
                errors.append(f'{rel}: JSON parse error {e}')
if only:
    inherited = [e for e in errors if not any(e.startswith(o) for o in only)]
    errors = [e for e in errors if any(e.startswith(o) for o in only)]
    if inherited:
        print(f'note: {len(inherited)} issues inside referenced base-pack snippets were ignored (stale keys Iris skips)')
for e in errors:
    print('ERR', e)
print(f'checked {count} files, {len(errors)} errors')
sys.exit(1 if errors else 0)
