"""Minimal KiCad s-expression helpers + library symbol loader."""
import re, os, math

SYMDIR = r"C:/Program Files/KiCad/10.0/share/kicad/symbols"

_tok = re.compile(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()"]+')

def parse(text):
    stack = [[]]
    for m in _tok.finditer(text):
        t = m.group(0)
        if t == '(':
            stack.append([])
        elif t == ')':
            x = stack.pop(); stack[-1].append(x)
        else:
            stack[-1].append(t)
    return stack[0]

def dump(x, ind=0):
    if not isinstance(x, list):
        return x
    if all(not isinstance(e, list) for e in x):
        return '(' + ' '.join(x) + ')'
    s = '(' + ' '.join(e for e in x if not isinstance(e, list) and x.index(e) == 0)
    parts = []
    head = []
    for e in x:
        if isinstance(e, list):
            parts.append('\n' + '  ' * (ind + 1) + dump(e, ind + 1))
        else:
            if parts:
                parts.append(' ' + e)
            else:
                head.append(e)
    return '(' + ' '.join(head) + ''.join(parts) + ')'

def unq(s):
    return s[1:-1] if s.startswith('"') else s

def q(s):
    return '"' + str(s).replace('\\', '\\\\').replace('"', '\\"') + '"'

_cache = {}
def lib(name):
    if name not in _cache:
        p = os.path.join(SYMDIR, name + '.kicad_sym')
        _cache[name] = parse(open(p, encoding='utf-8').read())[0]
    return _cache[name]

def find(node, key):
    return [e for e in node if isinstance(e, list) and e and e[0] == key]

def get_symbol(libname, symname, libtree=None):
    """Return flattened symbol node (extends resolved), renamed lib:sym."""
    tree = libtree if libtree is not None else lib(libname)
    syms = {unq(s[1]): s for s in find(tree, 'symbol')}
    s = syms[symname]
    ext = find(s, 'extends')
    if ext:
        base = get_symbol(libname, unq(ext[0][1]), tree)
        basename = unq(base[1]).split(':', 1)[1]
        # take base, replace properties with derived ones
        new = [e for e in base if not (isinstance(e, list) and e[0] == 'property')]
        props = find(s, 'property')
        # keep base props not overridden
        names = {unq(p[1]) for p in props}
        bprops = [p for p in find(base, 'property') if unq(p[1]) not in names]
        out = ['symbol', q(f'{libname}:{symname}')]
        for e in new[2:]:
            if isinstance(e, list) and e[0] == 'symbol':
                sub = list(e)
                sub[1] = q(unq(sub[1]).replace(basename, symname, 1))
                out.append(sub)
            else:
                out.append(e)
        # insert properties after first non-symbol header entries
        idx = next(i for i, e in enumerate(out) if isinstance(e, list) and e[0] == 'symbol')
        out[idx:idx] = props + bprops
        return out
    out = list(s)
    out[1] = q(f'{libname}:{symname}')
    return out

def pins(sym):
    """List of (number, name, type, x, y, angle) in symbol coords (y up)."""
    res = []
    def walk(n):
        for e in n:
            if isinstance(e, list):
                if e[0] == 'pin':
                    at = find(e, 'at')[0]
                    nm = unq(find(e, 'name')[0][1]); nu = unq(find(e, 'number')[0][1])
                    res.append((nu, nm, e[1], float(at[1]), float(at[2]), float(at[3]) if len(at) > 3 else 0))
                else:
                    walk(e)
    walk(sym)
    return res

def prop(sym, key):
    for p in find(sym, 'property'):
        if unq(p[1]) == key:
            return unq(p[2])
    return None
