"""Extract a field schema from the Iris engine Java sources."""
import os, re, json, sys

def strip_comments(s):
    s = re.sub(r'/\*.*?\*/', '', s, flags=re.S)
    def alt(m):
        names = re.findall(r'"(\w+)"', m.group(0))
        return '@SerializedAlt__' + '__'.join(names) + ' '
    s = re.sub(r'@SerializedName\([^)]*\)', alt, s)
    s = re.sub(r'"(?:\\.|[^"\\])*"', '""', s)
    s = re.sub(r"'(?:\\.|[^'\\])'", "''", s)
    s = re.sub(r'//[^\n]*', '', s)
    s = re.sub(r'@RegistryListResource\(\s*(\w+)\.class\s*\)', r'@RegistryListResource__\1', s)
    for _ in range(3):
        s = re.sub(r'@(\w+)\s*\([^()]*\)', r'@\1', s)
    return s

def parse(root):
    classes = {}
    for dp, _, fs in os.walk(root):
        for f in fs:
            if not f.endswith('.java'):
                continue
            src = open(os.path.join(dp, f), encoding='utf-8', errors='ignore').read()
            raw = src
            src = strip_comments(src)
            # blank out string literals but keep annotation args we need
            m = re.search(r'\b(public\s+)?(abstract\s+|final\s+)*(class|enum|record)\s+(\w+)([^{]*)\{', src)
            if not m:
                continue
            kind, name, head = m.group(3), m.group(4), m.group(5)
            body_start = m.end()
            ext = re.search(r'extends\s+(\w+)', head)
            snip = None
            pre = src[:m.start()]
            rm = re.search(r'\b(class|enum|record)\s+' + name + r'\b', raw)
            sm = re.search(r'@Snippet\("([^"]+)"\)', raw[:rm.start()]) if rm else None
            if sm:
                snip = sm.group(1)
            # top-level body at depth 1
            depth = 1; i = body_start; top = []
            buf = []
            while i < len(src) and depth > 0:
                c = src[i]
                if c == '{':
                    depth += 1
                    if depth == 2:
                        buf.append(';')
                elif c == '}':
                    depth -= 1
                    if depth == 1:
                        buf.append(';')
                elif depth == 1:
                    buf.append(c)
                i += 1
            body = ''.join(buf)
            info = {'kind': kind, 'extends': ext.group(1) if ext else None, 'snippet': snip,
                    'fields': {}, 'enum': [], 'file': os.path.join(dp, f)}
            if kind == 'enum':
                # enum constants: text before first ';' in the raw depth-1 stream, parens removed
                first = ''
                d = 0; j = body_start; dd = 1
                while j < len(src):
                    ch = src[j]
                    if ch in '({': d += 1
                    elif ch in ')}':
                        if d == 0: break
                        d -= 1
                    elif ch == ';' and d == 0: break
                    elif d == 0: first += ch
                    j += 1
                first = re.sub(r'@\w+', '', first)
                info['enum'] = [x.strip() for x in first.replace('{}', '').split(',') if re.fullmatch(r'\s*[A-Z][A-Z0-9_]*\s*', x)]
            # fields (statements at depth 1 ending with ';')
            for stmt in body.split(';'):
                st = stmt.strip()
                annos = re.findall(r'@(\w+)(?:\(([^)]*)\))?', st)
                code = re.sub(r'@\w+(\([^)]*\))?', '', st).strip()
                code = code.split('=')[0].strip()
                fm = re.match(r'(?:(?:private|protected|public|final|volatile)\s+)*([\w.<>, ?\[\]]+?)\s+(\w+)$', code)
                if not fm:
                    continue
                if re.search(r'\b(static|transient)\b', stmt.split('=')[0]):
                    continue
                typ, fname = fm.group(1), fm.group(2)
                if typ in ('return', 'throw', 'new', 'else', 'case'):
                    continue
                reg = None
                for a, arg in annos:
                    if a.startswith('RegistryListResource__'):
                        reg = a.split('__', 1)[1]
                for a, _ in annos:
                    if a.startswith('SerializedAlt__'):
                        for al in a.split('__')[1:]:
                            if al != fname:
                                info['fields'][al] = {'type': typ.replace(' ', ''), 'ref': None, 'annos': []}
                info['fields'][fname] = {'type': typ.replace(' ', ''), 'ref': reg,
                                         'annos': [a for a, _ in annos]}
            fm2 = re.search(r'getFolderName\(\)\s*\{\s*return\s*"([^"]+)"', raw)
            if fm2:
                info['folder'] = fm2.group(1)
            if name not in classes or len(info['fields']) > len(classes[name]['fields']):
                classes[name] = info
    return classes

if __name__ == '__main__':
    c = parse(sys.argv[1])
    json.dump(c, open(sys.argv[2], 'w'), indent=1)
    print(len(c), 'classes')
