#!/usr/bin/env python3
r"""
Kiem tra cau truc nguon LaTeX truoc khi bien dich tren Overleaf.

Bat cac loi pho bien ma khong can TeX engine:
  1. Lech dau ngoac nhon {}
  2. Lech \begin{...} / \end{...}
  3. \input / \addbibresource tro toi file khong ton tai
  4. \includegraphics tro toi hinh khong ton tai trong figures/
  5. \cite / \parencite ... dung khoa khong co trong refs.bib
  6. \ref / \cref / \Cref tro toi nhan khong duoc dinh nghia
  7. Ky tu dac biet chua escape trong van ban thuong (& _ #)

Chay:  python docs/thesis/check_tex.py
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(ROOT, 'figures')
BIB = os.path.join(ROOT, 'refs.bib')

errors, warnings = [], []


def tex_files():
    out = []
    for dp, _, fs in os.walk(ROOT):
        # _docx/ chua ban .tex da tien xu ly cho make_docx.py, khong phai nguon
        if os.path.basename(dp) in {'figures', '_build', '_docx'} or '_docx' in dp.split(os.sep):
            continue
        for f in sorted(fs):
            if f.endswith('.tex'):
                out.append(os.path.join(dp, f))
    return out


def strip_comments(text):
    """Bo comment (% khong duoc escape) nhung giu nguyen so dong."""
    out = []
    for line in text.split('\n'):
        res, i, n = [], 0, len(line)
        while i < n:
            if line[i] == '\\' and i + 1 < n:
                res.append(line[i:i + 2])
                i += 2
                continue
            if line[i] == '%':
                break
            res.append(line[i])
            i += 1
        out.append(''.join(res))
    return '\n'.join(out)


def rel(p):
    return os.path.relpath(p, ROOT).replace(os.sep, '/')


# ---------------------------------------------------------------------------
files = tex_files()
if not files:
    print('Khong tim thay file .tex nao.')
    sys.exit(1)

all_labels, all_refs, all_cites = set(), [], []
verb_re = re.compile(r'\\(?:verb|texttt|url|href)\b')

for path in files:
    raw = open(path, encoding='utf-8').read()
    src = strip_comments(raw)

    # --- 1. dau ngoac nhon ---
    depth = 0
    for lineno, line in enumerate(src.split('\n'), 1):
        i, n = 0, len(line)
        while i < n:
            if line[i] == '\\' and i + 1 < n:
                i += 2
                continue
            if line[i] == '{':
                depth += 1
            elif line[i] == '}':
                depth -= 1
                if depth < 0:
                    errors.append(f'{rel(path)}:{lineno}  thua dau }}')
                    depth = 0
            i += 1
    if depth != 0:
        errors.append(f'{rel(path)}  lech dau ngoac nhon: thieu {depth} dau }}')

    # --- 2. begin/end ---
    stack = []
    for m in re.finditer(r'\\(begin|end)\{([^}]+)\}', src):
        lineno = src[:m.start()].count('\n') + 1
        kind, env = m.group(1), m.group(2)
        if kind == 'begin':
            stack.append((env, lineno))
        else:
            if not stack:
                errors.append(f'{rel(path)}:{lineno}  \\end{{{env}}} khong co \\begin')
            else:
                open_env, open_line = stack.pop()
                if open_env != env:
                    errors.append(
                        f'{rel(path)}:{lineno}  \\end{{{env}}} khong khop '
                        f'\\begin{{{open_env}}} (dong {open_line})')
    for env, lineno in stack:
        errors.append(f'{rel(path)}:{lineno}  \\begin{{{env}}} chua duoc dong')

    # --- 3. \input ---
    for m in re.finditer(r'\\input\{([^}]+)\}', src):
        target = m.group(1)
        cand = os.path.join(ROOT, target if target.endswith('.tex') else target + '.tex')
        if not os.path.exists(cand):
            errors.append(f'{rel(path)}  \\input{{{target}}} -> khong tim thay file')

    # --- 4. \includegraphics ---
    for m in re.finditer(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', src):
        fig = m.group(1)
        lineno = src[:m.start()].count('\n') + 1
        # Chap nhan ca "figures/ten.png" (tuong doi voi main.tex) lan "ten.png"
        # (dua vao \graphicspath). Kiem tra ca hai cach phan giai.
        found = any(os.path.exists(os.path.join(base, fig + ext))
                    for base in (ROOT, FIGDIR)
                    for ext in ('', '.png', '.jpg', '.jpeg', '.pdf'))
        if not found:
            errors.append(f'{rel(path)}:{lineno}  hinh khong ton tai: {fig}')

    # --- 5,6. cite / label / ref ---
    for m in re.finditer(r'\\(?:cite|parencite|textcite|autocite)\{([^}]+)\}', src):
        lineno = src[:m.start()].count('\n') + 1
        for key in m.group(1).split(','):
            all_cites.append((rel(path), lineno, key.strip()))
    for m in re.finditer(r'\\label\{([^}]+)\}', src):
        all_labels.add(m.group(1))
    for m in re.finditer(r'\\(?:ref|cref|Cref|autoref|nameref)\{([^}]+)\}', src):
        lineno = src[:m.start()].count('\n') + 1
        for key in m.group(1).split(','):
            all_refs.append((rel(path), lineno, key.strip()))

    # --- 7. ky tu dac biet chua escape ---
    # Bo qua ben trong moi truong dang bang (& la dau phan cot hop le)
    # va cac dong dinh nghia macro (# la tham so hop le).
    # Moi truong dang bang: & la dau phan cot hop le.
    # Moi truong toan hoc: _ ^ & deu hop le.
    SKIP_ENVS = {
        # bang
        'tabular', 'tabular*', 'tabularx', 'longtable', 'tabu', 'array',
        # toan hoc
        'equation', 'equation*', 'align', 'align*', 'alignat', 'alignat*',
        'gather', 'gather*', 'multline', 'multline*', 'displaymath',
        'eqnarray', 'eqnarray*', 'aligned', 'gathered', 'split', 'cases',
        'matrix', 'pmatrix', 'bmatrix', 'vmatrix', 'Bmatrix', 'smallmatrix',
    }
    DEF_CMDS = re.compile(r'\\(?:new|renew|provide)(?:command|environment|colinlist)?'
                          r'|\\newcolumntype|\\def\b|\\DeclareRobustCommand')

    in_skip = 0
    for lineno, line in enumerate(src.split('\n'), 1):
        opened_here = False
        for m in re.finditer(r'\\(begin|end)\{([^}]+)\}', line):
            if m.group(2) in SKIP_ENVS:
                if m.group(1) == 'begin':
                    in_skip += 1
                    opened_here = True
                else:
                    in_skip -= 1
        if (in_skip > 0 or opened_here or verb_re.search(line)
                or '$' in line or r'\[' in line or r'\]' in line
                or DEF_CMDS.search(line)):
            continue
        # Bo lenh LaTeX truoc, roi bo cac ky tu dac biet DA duoc escape (\_ \& \# ...)
        stripped = re.sub(r'\\[a-zA-Z]+\*?(\[[^\]]*\])?(\{[^{}]*\})*', '', line)
        stripped = re.sub(r'\\[&_#%$}{~^\\]', '', stripped)
        for ch in ('&', '_', '#'):
            if ch in stripped:
                warnings.append(
                    f'{rel(path)}:{lineno}  co the thieu escape "\\{ch}"  -> {line.strip()[:70]}')
                break

# --- kiem tra khoa bibliography ---
bib_keys = set()
if os.path.exists(BIB):
    bib_keys = set(re.findall(r'@\w+\{\s*([^,\s]+)\s*,', open(BIB, encoding='utf-8').read()))
else:
    errors.append('Khong tim thay refs.bib')

for path, lineno, key in all_cites:
    if key and key not in bib_keys:
        errors.append(f'{path}:{lineno}  \\cite{{{key}}} khong co trong refs.bib')

for path, lineno, key in all_refs:
    if key and key not in all_labels:
        errors.append(f'{path}:{lineno}  \\ref/\\cref{{{key}}} khong co \\label tuong ung')

# ---------------------------------------------------------------------------
print(f'Da kiem tra {len(files)} file .tex')
print(f'  nhan (label)      : {len(all_labels)}')
print(f'  tham chieu (ref)  : {len(all_refs)}')
print(f'  trich dan (cite)  : {len(all_cites)}  | khoa trong refs.bib: {len(bib_keys)}')
print(f'  hinh trong figures/: {len([f for f in os.listdir(FIGDIR) if f.endswith(".png")]) if os.path.isdir(FIGDIR) else 0}')
print()

if warnings:
    print(f'--- CANH BAO ({len(warnings)}) ---')
    for w in warnings[:40]:
        print('  ' + w)
    if len(warnings) > 40:
        print(f'  ... va {len(warnings) - 40} canh bao khac')
    print()

if errors:
    print(f'--- LOI ({len(errors)}) ---')
    for e in errors:
        print('  ' + e)
    sys.exit(1)

print('OK - khong phat hien loi cau truc.')

# --- bao cao hinh chua dung ---
if os.path.isdir(FIGDIR):
    used = set()
    for path in files:
        src = strip_comments(open(path, encoding='utf-8').read())
        for m in re.finditer(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', src):
            used.add(os.path.splitext(os.path.basename(m.group(1)))[0])
    unused = sorted(os.path.splitext(f)[0] for f in os.listdir(FIGDIR)
                    if f.endswith('.png') and os.path.splitext(f)[0] not in used)
    if unused:
        print(f'\nHinh da copy nhung chua dung ({len(unused)}):')
        for u in unused:
            print('  figures/' + u + '.png')
