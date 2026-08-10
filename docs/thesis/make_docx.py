#!/usr/bin/env python3
r"""
make_docx.py — dung ban .docx cua luan van tu chinh nguon LaTeX.

Y tuong: KHONG duy tri hai ban thao. Nguon duy nhat van la chapters/*.tex;
script nay chi dich sang .docx bang Pandoc, kem mot lop tien xu ly vi Pandoc
khong hieu het cac cau truc ma XeLaTeX hieu.

Cac buoc:
  1. Chep toan bo .tex sang thu muc trung gian _docx/ roi tien xu ly ban chep
     (nguon goc KHONG bi sua):
       - cot bang tu dinh nghia L{} C{} R{}  -> p{} c r   (Pandoc bo qua bang
         co cot la, khien 23/43 bang bi mat)
       - \en{} long trong \text{} trong cong thuc -> tach ra \mathit{}
         (texmath khong phan tich duoc lenh chu long trong \text)
       - \num{4437} -> 4.437 theo dung \sisetup cua preamble
       - tikzpicture -> anh PNG dung san (Pandoc bo qua TikZ)
       - chuong/muc phu luc -> danh so thu cong A, A.1, A.1.1
       - \clearpage / \tableofcontents -> moc de hau xu ly
  2. Dung reference.docx quy dinh dinh dang (Times New Roman 13pt, gian dong
     1,5; le 3,5/2/3/3 cm; chuong sang trang moi).
  3. Goi Pandoc (co --citeproc + ieee-numeric.csl thay cho biblatex).
  4. Hau xu ly document.xml: chen truong MUC LUC dung cho, ngat trang, va
     dua danh muc tham khao ve truoc phan phu luc.

Chay:  python docs/thesis/make_docx.py       (hoac .\build-docx.ps1)
"""
import os
import re
import shutil
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD = os.path.join(ROOT, '_docx')
OUT = os.path.join(ROOT, 'thesis.docx')
CSL = os.path.join(ROOT, 'ieee-numeric.csl')

# Moc van ban dat vao nguon tien xu ly, den buoc 4 se bien thanh XML thuc su.
# Chon chuoi mot tu, khong dau, de Pandoc chac chan khong cat thanh nhieu run.
MARK_TOC = 'XPANDOCTOCX'
MARK_BREAK = 'XPANDOCPAGEBREAKX'
MARK_REFS = 'XPANDOCREFSX'
REFS_TITLE = 'TÀI LIỆU THAM KHẢO'

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

notes = []


def say(msg):
    print('    ' + msg)


def step(msg):
    print('==> ' + msg)


# ===========================================================================
#  1. Tim Pandoc
# ===========================================================================
def find_pandoc():
    cand = [
        shutil.which('pandoc'),
        os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Pandoc', 'pandoc.exe'),
        r'C:\Program Files\Pandoc\pandoc.exe',
    ]
    for c in cand:
        if c and os.path.exists(c):
            return c
    sys.exit(
        'LOI: khong tim thay pandoc.\n'
        '     Tai tai https://pandoc.org/installing.html roi chay lai.'
    )


# ===========================================================================
#  2. Tien xu ly nguon LaTeX
# ===========================================================================
def match_brace(s, i):
    """Tra ve chi so NGAY SAU dau } dong cap voi dau { tai vi tri i."""
    assert s[i] == '{'
    depth = 0
    while i < len(s):
        if s[i] == '\\':
            i += 2
            continue
        if s[i] == '{':
            depth += 1
        elif s[i] == '}':
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError('dau { khong duoc dong')


def read_group(s, i):
    """Doc nhom {..} bat dau tai i; tra ve (noi_dung, chi_so_ke_tiep)."""
    end = match_brace(s, i)
    return s[i + 1:end - 1], end


COLTYPE = re.compile(r'\b([LCR])\{([^{}]*)\}')


def text_width_cm():
    r"""Do rong khung chu, doc tu \geometry trong preamble.tex."""
    p = open(os.path.join(ROOT, 'preamble.tex'), encoding='utf-8').read()
    m = re.search(r'\\geometry\{(.*?)\}', p, re.S)
    page = 21.0                                   # A4
    left = right = None
    if m:
        for key, val in re.findall(r'(\w+)\s*=\s*([\d.]+)cm', m.group(1)):
            if key == 'left':
                left = float(val)
            elif key == 'right':
                right = float(val)
    if left is None or right is None:
        return 15.5
    return page - left - right


TW = None


def to_fraction(width):
    r"""'3.6cm' -> '0.2323\textwidth'.

    Pandoc CHI ghi nhan do rong cot khi no duoc viet theo ti le cua \textwidth;
    do rong tuyet doi (cm, mm, pt) bi bo qua va moi cot bi chia deu. Bang chia
    deu lam cot hep bi ep duoi be rong mot tu, Word dut chu ra giua chung.
    """
    m = re.fullmatch(r'\s*([\d.]+)\s*(cm|mm|in|pt)\s*', width)
    if not m:
        return None
    v = float(m.group(1))
    cm = {'cm': v, 'mm': v / 10, 'in': v * 2.54, 'pt': v * 2.54 / 72.27}[m.group(2)]
    return r'%.4f\textwidth' % max(0.02, min(1.0, cm / TW))


def fix_columns(src):
    r"""Doi cot tu dinh nghia L{w}/C{w}/R{w} sang cot Pandoc hieu.

    preamble.tex dinh nghia chung bang \newcolumntype; Pandoc khong doc
    \newcolumntype nen gap cot la thi bo ca bang, chi con lai mot khoi van ban
    khong dinh dang. L giu do rong (doi sang ti le cua \textwidth); C va R chi
    can can le nen dung c / r cho Word tu tinh rong.
    """
    out, n = [], 0
    pos = 0
    for m in re.finditer(r'\\begin\{(tabular|tabularx|longtable)\}', src):
        i = m.end()
        # bo qua tuy chon [..] va, voi tabularx, doi so do rong {..}
        while i < len(src) and src[i] in ' \n\t':
            i += 1
        if i < len(src) and src[i] == '[':
            i = src.index(']', i) + 1
        if m.group(1) == 'tabularx':
            _, i = read_group(src, src.index('{', i))
        j = src.index('{', i)
        spec, end = read_group(src, j)
        if not COLTYPE.search(spec):
            continue
        def convert(c):
            if c.group(1) != 'L':
                return 'c' if c.group(1) == 'C' else 'r'
            frac = to_fraction(c.group(2))
            return 'p{%s}' % (frac if frac else c.group(2))

        new = COLTYPE.sub(convert, spec)
        out.append((j + 1, end - 1, new))
        n += 1
    for start, end, new in reversed(out):
        src = src[:start] + new + src[end:]
    return src, n


INNER_ITALIC = re.compile(r'\\(?:en|textit|emph)\{([^{}]*)\}')


def fix_math_text(src):
    r"""Tach lenh chu nghieng ra khoi \text{} trong cong thuc.

    \text{Co (\en{erosion}):} lam texmath that bai va ca khoi cong thuc bi in
    ra duoi dang ma nguon. Dang tach \text{Co (}\mathit{erosion}\text{):} cho
    ket qua giong het ma texmath phan tich duoc.
    """
    n = 0
    i = 0
    while True:
        i = src.find(r'\text{', i)
        if i < 0:
            break
        body, end = read_group(src, i + 5)
        if INNER_ITALIC.search(body):
            new_body = INNER_ITALIC.sub(lambda m: r'}\mathit{%s}\text{' % m.group(1), body)
            src = src[:i] + r'\text{' + new_body + '}' + src[end:]
            n += 1
            i += 6
        else:
            i = end
    return src, n


def fmt_num(s):
    r"""Dinh dang so theo \sisetup: dau nhom '.', dau thap phan ',', nhom tu 4 chu so."""
    s = s.strip()
    if not re.fullmatch(r'-?\d+(?:\.\d+)?', s):
        return s
    sign = '-' if s.startswith('-') else ''
    s = s.lstrip('-')
    ip, _, fp = s.partition('.')
    if len(ip) >= 4:
        ip = format(int(ip), ',').replace(',', '.')
    return sign + ip + (',' + fp if fp else '')


def fix_num(src):
    src, n = re.subn(r'\\num\{([^{}]*)\}', lambda m: fmt_num(m.group(1)), src)
    return src, n


def replace_tikz(src, png_rel):
    r"""Thay tikzpicture (ke ca khi boc trong \resizebox) bang anh da dung san."""
    n = 0
    if png_rel:
        repl = r'\includegraphics[width=\textwidth]{%s}' % png_rel
    else:
        repl = (r'\textcolor{red}{\textbf{[ CẦN BỔ SUNG: so do quy trinh — '
                r'khong dung duoc hinh TikZ, xem thong bao cua make_docx.py ]}}')

    # \resizebox{..}{..}{ ...tikz... }
    while True:
        m = re.search(r'\\resizebox\*?\s*', src)
        if not m:
            break
        i = m.end()
        try:
            _, i = read_group(src, src.index('{', i))
            _, i = read_group(src, src.index('{', i))
            body, end = read_group(src, src.index('{', i))
        except (ValueError, IndexError):
            break
        if r'\begin{tikzpicture}' not in body:
            break
        src = src[:m.start()] + repl + src[end:]
        n += 1

    # tikzpicture con lai (khong boc \resizebox)
    while r'\begin{tikzpicture}' in src:
        i = src.index(r'\begin{tikzpicture}')
        j = src.index(r'\end{tikzpicture}', i) + len(r'\end{tikzpicture}')
        if j < len(src) and src[j] == '%':
            j += 1
        src = src[:i] + repl + src[j:]
        n += 1
    return src, n


def number_appendix(src, letter):
    r"""Danh so thu cong cho phu luc: PHU LUC A. / A.1 / A.1.1.

    Pandoc khong biet \appendix. De \chapter{} thi cac phu luc bi danh tiep so
    6, 7, 8, 9 nhu chuong thuong; de \chapter*{} thi mat het so muc. Cach nay
    ghi thang so vao tieu de va tat danh so tu dong (dung dang *).
    """
    sec = [0, 0]

    def chap(m):
        return r'\chapter*{PHỤ LỤC %s. %s}' % (letter, m.group(1))

    def section(m):
        sec[0] += 1
        sec[1] = 0
        return r'\section*{%s.%d\quad %s}' % (letter, sec[0], m.group(1))

    def subsection(m):
        sec[1] += 1
        return r'\subsection*{%s.%d.%d\quad %s}' % (letter, sec[0], sec[1], m.group(1))

    src = re.sub(r'\\chapter\{([^{}]*)\}', chap, src)
    src = re.sub(r'\\section\{([^{}]*)\}', section, src)
    src = re.sub(r'\\subsection\{([^{}]*)\}', subsection, src)
    return src


def strip_comments(src):
    r"""Bo chu thich LaTeX khoi ban chep.

    Can lam TRUOC moi phep thay the khac: cac chu thich trong main.tex co nhac
    ten lenh (vi du "... roi \clearpage.") va se bi thay the nham thanh moc,
    lam vo cau truc doan. Dong chi co chu thich thi xoa han — de lai dong trong
    se cat doi mot doan van dang viet do dang.
    """
    out = []
    for line in src.split('\n'):
        code, i, n = [], 0, len(line)
        while i < n:
            if line[i] == '\\' and i + 1 < n:
                code.append(line[i:i + 2])
                i += 2
                continue
            if line[i] == '%':
                break
            code.append(line[i])
            i += 1
        code = ''.join(code)
        if i < n and not code.strip():
            continue          # dong chi chua chu thich -> bo han
        out.append(code.rstrip() if i < n else line)
    return '\n'.join(out)


# Chi cac lenh chuyen co chu / kieu chu — KHONG duoc nuot cac lenh co doi so
# nhu \TODO, neu khong noi dung ben trong se bien mat.
FONT_SWITCH = re.compile(
    r'\{\s*((?:\\(?:LARGE|Large|large|normalsize|small|footnotesize|scriptsize'
    r'|tiny|huge|Huge|bfseries|itshape|slshape|scshape|normalfont|rmfamily'
    r'|sffamily|ttfamily)\s*)+)')


def fix_font_groups(src):
    r"""{\LARGE\bfseries X} -> \textbf{X};  {\large X} -> X.

    Pandoc bo qua cac lenh chuyen co chu/kieu chu dang cong tac (\bfseries), nen
    tieu de trang bia mat het phan in dam. Doi sang dang co doi so (\textbf) la
    dang Pandoc hieu.
    """
    i = 0
    while i < len(src):
        if src[i] != '{':
            i += 1
            continue
        m = FONT_SWITCH.match(src, i)
        if not m:
            i += 1
            continue
        try:
            end = match_brace(src, i)
        except ValueError:
            break
        body = src[m.end(1):end - 1]
        if r'\bfseries' in m.group(1):
            # Doi so cua \textbf khong duoc chua dong trong (ngat doan). Tieu de
            # trang bia gom nhieu dong nen phai in dam tung dong mot.
            new = '\n\n'.join(r'\textbf{%s}' % c.strip()
                              for c in re.split(r'\n\s*\n', body) if c.strip())
        else:
            new = body
        src = src[:i] + new + src[end:]
        i += 1
    return src


def fix_frontmatter(src):
    r"""Dung lai trang bia va cac trang loi noi dau.

    Trang bia LaTeX la mot khoi can giua, moi dong ngat bang \\[2,5cm]. Pandoc
    bo het cac lenh do dan (\vspace, \vfill, \\[..]) nen ca trang bi don thanh
    MOT doan chu lien nhau. Cach xu ly: bien moi dau ngat dong thanh mot doan
    rieng — buoc hau xu ly se can giua tat ca doan nam truoc chuong dau tien.
    """
    import datetime
    src = src.replace(r'\the\year', str(datetime.date.today().year))
    for cmd in (r'\vfill', r'\centering', r'\begingroup', r'\endgroup', r'\par'):
        src = src.replace(cmd, '')
    src = re.sub(r'\\vspace\*?\{[^{}]*\}', '', src)
    src = re.sub(r'\\thispagestyle\{[^{}]*\}', '', src)
    src = re.sub(r'\\begin\{(minipage|flushright)\}(\{[^{}]*\})?|\\end\{(minipage|flushright)\}',
                 '', src)
    # \\[2.5cm] va \\ -> ngat DOAN (dong trong), khong phai ngat dong.
    # Phai lam TRUOC fix_font_groups de ham do biet tieu de gom nhung dong nao.
    src = re.sub(r'\\\\\s*(\[[^\]]*\])?', '\n\n', src)
    src = fix_font_groups(src)
    return src


def fix_main(src):
    """Dat moc cho muc luc / danh muc tham khao / ngat trang trong main.tex."""
    head, sep, tail = src.partition(r'\tableofcontents')
    if sep:
        src = fix_frontmatter(head) + sep + tail
    src = src.replace(r'\tableofcontents', '\n\n%s\n\n' % MARK_TOC)
    # Pandoc khong dung duoc danh muc hinh/bang: chu thich do Pandoc sinh ra
    # khong co truong SEQ nen Word khong lap duoc danh muc. Bo hai lenh nay.
    src = src.replace(r'\listoffigures', '').replace(r'\listoftables', '')
    src = re.sub(r'\\printbibliography(\[[^\]]*\])?', '\n\n%s\n\n' % MARK_REFS, src)
    return src


# ===========================================================================
#  2b. Cross-reference & danh so (doc so that tu main.aux)
# ===========================================================================
#  Pandoc khong giai duoc \cref/\ref cua LaTeX nen no de nguyen thanh lien ket
#  hong dang [[eq:iou_guard]](#eq:iou_guard). Ta doc san so cua moi nhan tu ban
#  bien dich LaTeX (main.aux) roi thay lenh tham chieu bang chu that TRUOC khi
#  dua vao pandoc. Ten loai lay theo \crefname trong preamble.tex.
CREF_NAME = {
    'figure': 'Hình', 'table': 'Bảng', 'chapter': 'Chương',
    'section': 'Mục', 'subsection': 'Mục', 'subsubsection': 'Mục',
    'equation': 'Công thức', 'appendix': 'Phụ lục',
}


def load_refmap():
    """Doc main.aux -> {nhan: (loai, so)} tu cac muc @cref cua cleveref."""
    path = os.path.join(ROOT, 'main.aux')
    refmap = {}
    if not os.path.exists(path):
        say('CANH BAO: khong thay main.aux — khong the danh so cross-reference')
        return refmap
    text = open(path, encoding='utf-8').read()
    pat = re.compile(
        r'\\newlabel\{([^}]+)@cref\}\{\{\[([a-z]+)\]\[[^\]]*\]\[[^\]]*\]([^}\[\]]*)\}')
    for m in pat.finditer(text):
        refmap[m.group(1)] = (m.group(2), m.group(3))
    return refmap


def _join_vn(items):
    items = list(items)
    if len(items) <= 1:
        return ''.join(items)
    return ', '.join(items[:-1]) + ' và ' + items[-1]


def resolve_refs(src, refmap, stats):
    """Thay \\cref/\\Cref/\\ref/\\eqref/\\autoref bang chu that co so."""
    def repl(m):
        cmd, arg = m.group(1), m.group(2)
        labels = [x.strip() for x in arg.split(',') if x.strip()]
        infos = []
        for lab in labels:
            if lab in refmap:
                infos.append(refmap[lab])
            else:
                stats.setdefault('missing', []).append(lab)
                infos.append((None, '??'))
        nums = [n for _, n in infos]
        typ = infos[0][0]
        if cmd == 'ref':                       # so tran
            return _join_vn(nums)
        if cmd == 'eqref':                     # (so)
            return _join_vn('(%s)' % n for n in nums)
        # cref / Cref / autoref: ten loai + so
        name = CREF_NAME.get(typ, '')
        if typ == 'equation':
            body = _join_vn('(%s)' % n for n in nums)
        else:
            body = _join_vn(nums)
        return ('%s %s' % (name, body)).strip()

    src, n = re.subn(r'\\(ref|cref|Cref|autoref|eqref)\{([^}]*)\}', repl, src)
    stats['refs'] = stats.get('refs', 0) + n
    return src


def _caption_arg(body, start):
    """Tu ngay sau '\\caption', bo qua khoang trang va tham so tuy chon [..],
    tra ve chi so cua dau '{' cua tham so bat buoc (hoac -1 neu khong co)."""
    i = start
    while i < len(body) and body[i] in ' \t\n':
        i += 1
    if i < len(body) and body[i] == '[':          # bo qua [tieu de ngan]
        depth = 0
        while i < len(body):
            c = body[i]
            if c == '\\':
                i += 2
                continue
            if c == '[':
                depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    i += 1
                    break
            i += 1
        while i < len(body) and body[i] in ' \t\n':
            i += 1
    return i if i < len(body) and body[i] == '{' else -1


def number_captions(src, refmap, stats):
    """Them tien to 'Bang X.Y:' / 'Hinh X.Y:' vao \\caption cua bang/hinh.

    Ho tro ca hai dang \\caption{..} va \\caption[tieu de ngan]{..}.
    """
    def do(m):
        env, body = m.group(1), m.group(2)
        lm = re.search(r'\\label\{((?:tab|fig)[^}]*)\}', body)
        ci = body.find('\\caption')
        if not lm or ci == -1 or lm.group(1) not in refmap:
            return m.group(0)
        bstart = _caption_arg(body, ci + len('\\caption'))
        if bstart == -1:
            return m.group(0)
        typ, num = refmap[lm.group(1)]
        name = CREF_NAME.get(typ, '')
        content, nxt = read_group(body, bstart)
        newcap = '%s{%s %s: %s}' % (body[ci:bstart], name, num, content)
        stats['caps'] = stats.get('caps', 0) + 1
        return '\\begin{%s}%s%s%s\\end{%s}' % (env, body[:ci], newcap, body[nxt:], env)
    return re.sub(r'\\begin\{(figure|table|longtable)\}(.*?)\\end\{\1\}',
                  do, src, flags=re.S)


def convert_labels(src, refmap, stats):
    """Nhan cong thuc -> so '(X.Y)' dung cho; nhan khac -> bo (da bien thanh chu)."""
    def do(m):
        info = refmap.get(m.group(1))
        if info and info[0] == 'equation':
            stats['eqnums'] = stats.get('eqnums', 0) + 1
            return r'\qquad (%s)' % info[1]
        return ''
    return re.sub(r'\\label\{([^}]*)\}', do, src)


def preprocess():
    """Chep nguon sang _docx/ va tien xu ly ban chep."""
    global TW
    TW = text_width_cm()

    if os.path.isdir(BUILD):
        shutil.rmtree(BUILD)
    os.makedirs(BUILD)

    png_rel = render_tikz()
    refmap = load_refmap()

    # thu tu phu luc trong main.tex quyet dinh chu cai A, B, C, D
    main_src = open(os.path.join(ROOT, 'main.tex'), encoding='utf-8').read()
    order = re.findall(r'\\input\{appendix/([^}]+)\}', main_src)
    letters = {name: chr(ord('A') + k) for k, name in enumerate(order)}

    stats = dict(cols=0, math=0, num=0, tikz=0, files=0)
    for sub in ('', 'chapters', 'appendix'):
        srcdir = os.path.join(ROOT, sub) if sub else ROOT
        dstdir = os.path.join(BUILD, sub) if sub else BUILD
        os.makedirs(dstdir, exist_ok=True)
        for name in sorted(os.listdir(srcdir)):
            if not name.endswith('.tex'):
                continue
            text = open(os.path.join(srcdir, name), encoding='utf-8').read()
            text = strip_comments(text)

            text, n = fix_columns(text)
            stats['cols'] += n
            text, n = fix_math_text(text)
            stats['math'] += n
            text, n = fix_num(text)
            stats['num'] += n
            text, n = replace_tikz(text, png_rel)
            stats['tikz'] += n

            # Giai cross-reference, danh so caption va cong thuc tu main.aux
            text = resolve_refs(text, refmap, stats)
            text = number_captions(text, refmap, stats)
            text = convert_labels(text, refmap, stats)

            if sub == 'appendix':
                key = os.path.splitext(name)[0]
                if key in letters:
                    text = number_appendix(text, letters[key])
            if not sub and name == 'main.tex':
                text = fix_main(text)

            text = re.sub(r'\\(clearpage|newpage)\b', '\n\n%s\n\n' % MARK_BREAK, text)

            open(os.path.join(dstdir, name), 'w', encoding='utf-8').write(text)
            stats['files'] += 1

    shutil.copy(os.path.join(ROOT, 'refs.bib'), os.path.join(BUILD, 'refs.bib'))
    return stats


# ===========================================================================
#  3. Dung anh cho so do TikZ
# ===========================================================================
TIKZ_DOC = r"""\documentclass[border=4pt]{standalone}
\usepackage{fontspec}
%(fonts)s
\usepackage{polyglossia}
\setdefaultlanguage{vietnamese}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{xcolor}
\usepackage{tikz}
%(libs)s
%(colors)s
%(styles)s
\begin{document}
%(body)s
\end{document}
"""


def tikz_preamble_bits():
    """Lay dinh nghia font, thu vien, mau va tikzset tu preamble.tex."""
    p = open(os.path.join(ROOT, 'preamble.tex'), encoding='utf-8').read()
    fonts = re.findall(r'\\set(?:main|sans|mono)font\{[^{}]*\}\[[^\]]*\]', p)
    libs = re.findall(r'\\usetikzlibrary\{[^{}]*\}', p)
    colors = re.findall(r'\\definecolor\{[^{}]*\}\{[^{}]*\}\{[^{}]*\}', p)
    styles = []
    for m in re.finditer(r'\\tikzset\s*', p):
        try:
            i = p.index('{', m.end())
            styles.append(p[m.start():match_brace(p, i)])
        except ValueError:
            pass
    return dict(fonts='\n'.join(fonts), libs='\n'.join(libs),
                colors='\n'.join(colors), styles='\n'.join(styles))


def extract_tikz_body():
    for dp, _, fs in os.walk(ROOT):
        if os.path.basename(dp).startswith('_'):
            continue
        for f in sorted(fs):
            if not f.endswith('.tex'):
                continue
            s = open(os.path.join(dp, f), encoding='utf-8').read()
            i = s.find(r'\begin{tikzpicture}')
            if i >= 0:
                j = s.index(r'\end{tikzpicture}', i) + len(r'\end{tikzpicture}')
                return s[i:j]
    return None


def render_tikz():
    """Dung so do TikZ thanh PNG. Tra ve duong dan tuong doi, hoac None."""
    body = extract_tikz_body()
    if body is None:
        return None

    step('Dung so do TikZ thanh anh')
    tectonic = os.path.join(ROOT, 'tools', 'tectonic.exe')
    if not os.path.exists(tectonic) or (tectonic.endswith('.exe') and os.name != 'nt'):
        tectonic = shutil.which('tectonic')
    xelatex = None if tectonic else (shutil.which('xelatex') or shutil.which('lualatex'))
    if not tectonic and not xelatex:
        notes.append('Khong co tectonic.exe/xelatex -> so do quy trinh (Hinh 3.1) bi thieu. '
                     'Chay .\\build.ps1 mot lan de tai tectonic roi dung lai.')
        say('BO QUA: khong tim thay tectonic/xelatex')
        return None
    try:
        import fitz  # PyMuPDF
    except ImportError:
        notes.append('Thieu goi PyMuPDF -> so do quy trinh (Hinh 3.1) bi thieu. '
                     'Cai bang: pip install pymupdf')
        say('BO QUA: khong co PyMuPDF')
        return None

    gen = os.path.join(BUILD, 'gen')
    os.makedirs(gen, exist_ok=True)
    bits = tikz_preamble_bits()
    bits['body'] = body
    tex = os.path.join(gen, 'tikz.tex')
    open(tex, 'w', encoding='utf-8').write(TIKZ_DOC % bits)

    if tectonic:
        cmd = [tectonic, '-X', 'compile', tex, '--outdir', gen]
    else:                                   # fallback: xelatex/lualatex
        cmd = [xelatex, '-interaction=nonstopmode', '-halt-on-error',
               '-output-directory', gen, tex]
    r = subprocess.run(cmd, capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    pdf = os.path.join(gen, 'tikz.pdf')
    if r.returncode != 0 or not os.path.exists(pdf):
        notes.append('Bien dich so do TikZ that bai -> Hinh 3.1 bi thieu.')
        say('BO QUA: tectonic bao loi')
        for line in (r.stderr or '').splitlines():
            if line.strip().startswith('error'):
                say('  ' + line.strip())
        return None

    png = os.path.join(gen, 'pipeline.png')
    doc = fitz.open(pdf)
    doc[0].get_pixmap(dpi=300).save(png)
    doc.close()
    say('gen/pipeline.png (%.0f KB)' % (os.path.getsize(png) / 1024))
    return 'gen/pipeline.png'


# ===========================================================================
#  4. reference.docx — quy dinh dinh dang cua ban Word
# ===========================================================================
CM = 567          # twip trong mot xang-ti-met
PT = 20           # twip trong mot diem in (dung cho w:spacing)


def el(tag, **attrs):
    a = ' '.join('w:%s="%s"' % (k.replace('_', ':'), v) for k, v in attrs.items())
    return '<w:%s%s/>' % (tag, ' ' + a if a else '')


def rpr(size=None, bold=False, italic=False, font='Times New Roman', color=None):
    x = ['<w:rPr>', el('rFonts', ascii=font, hAnsi=font, cs=font)]
    if bold:
        x.append('<w:b/>')
    if italic:
        x.append('<w:i/>')
    if color:
        x.append(el('color', val=color))
    if size:
        x.append(el('sz', val=str(size * 2)))
        x.append(el('szCs', val=str(size * 2)))
    x.append('</w:rPr>')
    return ''.join(x)


def ppr(align=None, before=0, after=0, line=None, indent=0,
        keep_next=False, page_break=False):
    # Thu tu phan tu con trong <w:pPr> phai dung theo luoc do OOXML
    # (keepNext -> pageBreakBefore -> spacing -> ind -> jc). Sai thu tu thi Word
    # bao tep hong va doi sua chua.
    x = ['<w:pPr>']
    if keep_next:
        x.append('<w:keepNext/>')
    if page_break:
        x.append('<w:pageBreakBefore/>')
    sp = {'before': str(int(before * PT)), 'after': str(int(after * PT))}
    if line:
        sp['line'] = str(int(line * 240))
        sp['lineRule'] = 'auto'
    x.append(el('spacing', **sp))
    # indent=0 phai ghi ro <w:ind firstLine="0">: cac style nay ke thua BodyText
    # nen khong ghi de thi thut dau dong 1 cm cua than bai lot ca vao o bang,
    # chu thich hinh va danh muc tham khao.
    if indent is not None:
        x.append(el('ind', firstLine=str(indent)))
    if align:
        x.append(el('jc', val=align))
    x.append('</w:pPr>')
    return ''.join(x)


# Moi muc: styleId -> (pPr, rPr). None = giu nguyen phan do.
STYLES = {
    'Normal': (ppr(align='both', after=0.35 * 13, line=1.5), rpr(13)),
    'BodyText': (ppr(align='both', after=0.35 * 13, line=1.5, indent=CM), rpr(13)),
    'FirstParagraph': (ppr(align='both', after=0.35 * 13, line=1.5, indent=CM), rpr(13)),
    'Compact': (ppr(align='both', after=2, line=1.5), rpr(13)),
    # Chuong: sang trang moi, can giua, chu hoa lon
    'Heading1': (ppr(align='center', before=0, after=20, line=1.5,
                     keep_next=True, page_break=True), rpr(16, bold=True)),
    'Heading2': (ppr(before=14, after=6, line=1.5, keep_next=True), rpr(14, bold=True)),
    'Heading3': (ppr(before=10, after=4, line=1.5, keep_next=True), rpr(13, bold=True)),
    'Heading4': (ppr(before=8, after=4, line=1.5, keep_next=True),
                 rpr(13, bold=True, italic=True)),
    'Heading5': (ppr(before=6, after=4, line=1.5, keep_next=True), rpr(13, italic=True)),
    'TOCHeading': (ppr(align='center', before=0, after=16, line=1.5), rpr(16, bold=True)),
    'Caption': (ppr(align='center', before=4, after=10, line=1.0), rpr(12)),
    'ImageCaption': (ppr(align='center', before=4, after=10, line=1.0), rpr(12)),
    'TableCaption': (ppr(align='center', before=8, after=4, line=1.0), rpr(12)),
    'Figure': (ppr(align='center', before=8, after=2, line=1.0), None),
    'CaptionedFigure': (ppr(align='center', before=8, after=2, line=1.0), None),
    'BlockText': (ppr(align='both', before=4, after=4, line=1.5), rpr(12, italic=True)),
    'FootnoteText': (ppr(align='both', after=0, line=1.0), rpr(10)),
    'Bibliography': (ppr(align='both', after=3, line=1.15), rpr(12)),
    'Author': (ppr(align='center', after=6, line=1.5), rpr(13)),
    'Date': (ppr(align='center', after=6, line=1.5), rpr(13)),
    'Title': (ppr(align='center', before=0, after=20, line=1.5), rpr(18, bold=True)),
    'VerbatimChar': (None, rpr(11, font='Consolas')),
}


def build_reference_docx(pandoc, path):
    """Sinh reference.docx tu ban mac dinh cua Pandoc roi ap dinh dang luan van."""
    base = os.path.join(BUILD, 'reference-default.docx')
    with open(base, 'wb') as f:
        f.write(subprocess.run([pandoc, '--print-default-data-file', 'reference.docx'],
                               capture_output=True, check=True).stdout)

    zin = zipfile.ZipFile(base)
    parts = {n: zin.read(n) for n in zin.namelist()}
    zin.close()

    styles = parts['word/styles.xml'].decode('utf-8')

    # --- mac dinh toan tai lieu: Times New Roman 13pt, ngon ngu tieng Viet ---
    styles = re.sub(
        r'<w:rPrDefault>.*?</w:rPrDefault>',
        '<w:rPrDefault><w:rPr>'
        + el('rFonts', ascii='Times New Roman', eastAsia='Times New Roman',
             hAnsi='Times New Roman', cs='Times New Roman')
        + el('sz', val='26') + el('szCs', val='26')
        + el('lang', val='vi-VN', eastAsia='vi-VN', bidi='ar-SA')
        + '</w:rPr></w:rPrDefault>',
        styles, flags=re.S)
    styles = re.sub(
        r'<w:pPrDefault>.*?</w:pPrDefault>',
        '<w:pPrDefault><w:pPr>'
        + el('spacing', after='91', line='360', lineRule='auto')
        + el('jc', val='both') + '</w:pPr></w:pPrDefault>',
        styles, flags=re.S)

    # --- tung style cu the ---
    applied = 0
    for style_id, (new_ppr, new_rpr) in STYLES.items():
        m = re.search(r'<w:style [^>]*w:styleId="%s"\s*>.*?</w:style>' % style_id,
                      styles, re.S)
        if not m:
            continue
        block = m.group(0)
        if new_ppr is not None:
            block = re.sub(r'<w:pPr>.*?</w:pPr>', lambda _: new_ppr, block, count=1, flags=re.S) \
                if '<w:pPr>' in block else block.replace('</w:style>', new_ppr + '</w:style>')
        if new_rpr is not None:
            block = re.sub(r'<w:rPr>.*?</w:rPr>', lambda _: new_rpr, block, count=1, flags=re.S) \
                if '<w:rPr>' in block else block.replace('</w:style>', new_rpr + '</w:style>')
        styles = styles[:m.start()] + block + styles[m.end():]
        applied += 1
    parts['word/styles.xml'] = styles.encode('utf-8')

    # --- kho giay A4 va le theo quy dinh dong quyen ---
    doc = parts['word/document.xml'].decode('utf-8')
    # footnotePr phai dung TRUOC pgSz/pgMar theo luoc do CT_SectPr.
    sect = ('<w:sectPr>'
            + '<w:footnotePr><w:numRestart w:val="eachSect"/></w:footnotePr>'
            + el('pgSz', w='11906', h='16838')
            + el('pgMar', top=str(3 * CM), right=str(2 * CM), bottom=str(3 * CM),
                 left=str(int(3.5 * CM)), header='709', footer=str(int(1.2 * CM)),
                 gutter='0')
            + '</w:sectPr>')
    doc = re.sub(r'<w:sectPr>.*?</w:sectPr>', lambda _: sect, doc, flags=re.S)
    parts['word/document.xml'] = doc.encode('utf-8')

    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in parts.items():
            z.writestr(name, data)
    say('reference.docx: da dat %d style' % applied)


# ===========================================================================
#  5. Hau xu ly ban .docx
# ===========================================================================
PBREAK = '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'

TOC_XML = (
    # outlineLvl=9 ("body text") giu cho dong "MỤC LỤC" khong tu liet ke chinh no
    # trong muc luc — style TOCHeading ke thua Heading1 nen mac dinh bi truong TOC
    # nhat vao.
    '<w:p><w:pPr><w:pStyle w:val="TOCHeading"/><w:outlineLvl w:val="9"/></w:pPr>'
    '<w:r><w:t>MỤC LỤC</w:t></w:r></w:p>'
    '<w:p>'
    '<w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r>'
    '<w:r><w:instrText xml:space="preserve"> TOC \\o "1-3" \\h \\z \\u </w:instrText></w:r>'
    '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
    '<w:r><w:t xml:space="preserve">Mở tệp trong Word rồi bấm Ctrl+A, F9 '
    'để điền mục lục.</w:t></w:r>'
    '<w:r><w:fldChar w:fldCharType="end"/></w:r>'
    '</w:p>' + PBREAK
)

PARA = re.compile(r'<w:p\b[^>]*>.*?</w:p>|<w:p\b[^>]*/>', re.S)


def para_text(p):
    return ''.join(re.findall(r'<w:t[^>]*>(.*?)</w:t>', p, re.S))


def fit_tables(doc):
    """Cho bang trai het khung chu va giu dung ti le cot.

    Mac dinh Pandoc de tblW='auto': Word tu co gian theo noi dung, cot nao chu
    dai thi lan sang cot ben canh cho toi khi cot hep hep hon mot tu va chu bi
    dut giua chung. Dat tblW=100% kem tblLayout=fixed buoc Word dung dung ti le
    cot lay tu p{..\\textwidth} cua ban LaTeX.
    """
    n = [0]

    def fix(m):
        pr = m.group(0)
        pr = re.sub(r'<w:tblW [^/]*/>', el('tblW', type='pct', w='5000'), pr, count=1)
        if '<w:tblLayout' not in pr:
            # tblLayout dung ngay truoc tblLook theo luoc do CT_TblPrBase
            layout = el('tblLayout', type='fixed')
            pr = (pr.replace('<w:tblLook', layout + '<w:tblLook', 1)
                  if '<w:tblLook' in pr else pr.replace('</w:tblPr>', layout + '</w:tblPr>', 1))
        n[0] += 1
        return pr

    doc = re.sub(r'<w:tblPr>.*?</w:tblPr>', fix, doc, flags=re.S)
    return doc, n[0]


def color_todo(doc):
    r"""To do cac muc \TODO.

    Trong ban PDF, \TODO in do dam de khong bo sot khi ra soat. Pandoc giu duoc
    phan in dam nhung bo mau (mau chu dang span khong duoc trinh ghi .docx ho tro),
    nen phai dat lai o day.
    """
    n = [0]

    def fix(m):
        run = m.group(0)
        if 'CẦN BỔ SUNG' not in run:
            return run
        n[0] += 1
        color = el('color', val='C00000')
        if '<w:rPr>' not in run:
            return run.replace('<w:r>', '<w:r><w:rPr>' + color + '</w:rPr>', 1)
        # <w:color> dung sau b/i nhung truoc spacing/sz trong <w:rPr>
        for anchor in ('<w:spacing ', '<w:sz ', '</w:rPr>'):
            if anchor in run:
                return run.replace(anchor, color + anchor, 1)
        return run

    doc = re.sub(r'<w:r>(?:(?!</w:r>).)*</w:r>', fix, doc, flags=re.S)
    return doc, n[0]


def center_cover(doc):
    """Can giua moi doan nam truoc chuong dau tien (hai trang bia).

    Khong the lam viec nay o buoc tien xu ly: \\centering cua LaTeX la lenh
    cong tac, Pandoc khong chuyen thanh thuoc tinh can le nao ca.
    """
    body = re.search(r'<w:body>(.*)</w:body>', doc, re.S)
    if not body:
        return doc, 0
    first_heading = None
    for m in PARA.finditer(doc, body.start(1), body.end(1)):
        if 'w:val="Heading1"' in m.group(0):
            first_heading = m.start()
            break
    if first_heading is None:
        return doc, 0

    n = 0
    last = body.start(1)
    out = [doc[:last]]                 # giu nguyen phan dau tep XML
    for m in PARA.finditer(doc, last, first_heading):
        p = m.group(0)
        if not para_text(p).strip():
            continue
        # <w:jc> phai dung SAU <w:pStyle> trong <w:pPr>, neu khong Word bao hong tep.
        if '<w:jc ' in p:
            new = re.sub(r'<w:jc w:val="[^"]*"\s*/>', el('jc', val='center'), p, count=1)
        elif '<w:pStyle ' in p:
            new = re.sub(r'(<w:pStyle w:val="[^"]*"\s*/>)', r'\1' + el('jc', val='center'),
                         p, count=1)
        elif '<w:pPr>' in p:
            new = p.replace('<w:pPr>', '<w:pPr>' + el('jc', val='center'), 1)
        else:
            new = re.sub(r'(<w:p\b[^>]*>)', r'\1<w:pPr>' + el('jc', val='center') + '</w:pPr>',
                         p, count=1)
        out.append(doc[last:m.start()])
        out.append(new)
        last = m.end()
        n += 1
    out.append(doc[last:])
    return ''.join(out), n


def postprocess(path):
    """Chen muc luc, ngat trang, va dua danh muc tham khao ve dung vi tri."""
    zin = zipfile.ZipFile(path)
    parts = {n: zin.read(n) for n in zin.namelist()}
    zin.close()

    doc = parts['word/document.xml'].decode('utf-8')
    paras = [(m.start(), m.end(), m.group(0)) for m in PARA.finditer(doc)]

    # --- cat khoi danh muc tham khao (citeproc luon dat o cuoi tai lieu) ---
    refs_xml = ''
    start_i = None
    for k, (s, e, p) in enumerate(paras):
        if para_text(p).strip() == REFS_TITLE and 'Heading1' in p:
            start_i = k
            break
    if start_i is not None:
        s = paras[start_i][0]
        e = paras[-1][1]
        refs_xml = doc[s:e] + PBREAK
        doc = doc[:s] + doc[e:]
    else:
        notes.append('Khong tim thay danh muc tham khao trong ban .docx.')

    # --- thay cac moc ---
    def replace_marker(text, mark, xml):
        for m in PARA.finditer(text):
            if para_text(m.group(0)).strip() == mark:
                return text[:m.start()] + xml + text[m.end():], True
        return text, False

    doc, ok = replace_marker(doc, MARK_TOC, TOC_XML)
    if not ok:
        notes.append('Khong chen duoc truong muc luc.')
    doc, ok = replace_marker(doc, MARK_REFS, refs_xml)
    if not ok and refs_xml:
        notes.append('Khong dat duoc danh muc tham khao truoc phan phu luc.')

    nbreak = 0
    while True:
        doc, ok = replace_marker(doc, MARK_BREAK, PBREAK)
        if not ok:
            break
        nbreak += 1

    doc, ncenter = center_cover(doc)
    doc, ntable = fit_tables(doc)
    doc, ntodo = color_todo(doc)
    parts['word/document.xml'] = doc.encode('utf-8')

    # --- bao Word tu cap nhat truong khi mo tep (de muc luc tu dien) ---
    st = parts['word/settings.xml'].decode('utf-8')
    if 'updateFields' not in st:
        # Vi tri hop le duy nhat: ngay truoc footnotePr / rsids / mathPr.
        anchor = next((a for a in ('<w:footnotePr>', '<w:rsids>', '<m:mathPr>',
                                   '</w:settings>') if a in st), None)
        if anchor:
            st = st.replace(anchor, '<w:updateFields w:val="true"/>' + anchor, 1)
            parts['word/settings.xml'] = st.encode('utf-8')
        else:
            notes.append('Khong dat duoc updateFields: phai tu bam Ctrl+A, F9 trong Word.')

    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, data in parts.items():
            z.writestr(name, data)
    say('muc luc + danh muc tham khao; %d ngat trang; %d doan bia can giua; '
        '%d bang tu dan cot; %d muc \\TODO to do'
        % (nbreak, ncenter, ntable, ntodo))


# ===========================================================================
#  6. Chay
# ===========================================================================
def main():
    pandoc = find_pandoc()
    ver = subprocess.run([pandoc, '--version'], capture_output=True, text=True)
    step('Pandoc: ' + ver.stdout.splitlines()[0])

    step('Tien xu ly nguon LaTeX')
    stats = preprocess()
    say('khung chu %.1f cm; %d tep .tex; %d bang doi cot; %d cong thuc; %d so; '
        '%d so do TikZ'
        % (TW, stats['files'], stats['cols'], stats['math'], stats['num'], stats['tikz']))
    say('cross-reference: %d tham chieu; %d caption danh so; %d cong thuc danh so'
        % (stats.get('refs', 0), stats.get('caps', 0), stats.get('eqnums', 0)))
    missing = stats.get('missing', [])
    if missing:
        say('CANH BAO: %d nhan khong tim thay trong main.aux: %s'
            % (len(missing), ', '.join(sorted(set(missing)))))

    step('Dung reference.docx')
    ref = os.path.join(BUILD, 'reference.docx')
    build_reference_docx(pandoc, ref)

    step('Chuyen doi bang Pandoc')
    cmd = [
        pandoc, 'main.tex',
        '--from', 'latex',
        '--to', 'docx',
        '--reference-doc', ref,
        '--citeproc',
        '--bibliography', 'refs.bib',
        '--csl', CSL,
        '--number-sections',
        '--resource-path', os.pathsep.join([BUILD, ROOT]),
        '--metadata', 'lang=vi-VN',
        '--metadata', 'reference-section-title=' + REFS_TITLE,
        '--output', OUT,
    ]
    r = subprocess.run(cmd, cwd=BUILD, capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    for line in (r.stderr or '').splitlines():
        say(line)
    if r.returncode != 0:
        sys.exit('LOI: pandoc that bai.')

    step('Hau xu ly')
    postprocess(OUT)

    step('Ket qua')
    say('Tep   : ' + OUT)
    say('Dung luong: %.2f MB' % (os.path.getsize(OUT) / 1024 / 1024))

    todo = 0
    for dp, _, fs in os.walk(ROOT):
        if os.path.basename(dp).startswith('_'):
            continue
        for f in fs:
            if f.endswith('.tex'):
                todo += open(os.path.join(dp, f), encoding='utf-8').read().count(r'\TODO{')
    if todo:
        say('So muc \\TODO con phai bo sung: %d' % todo)

    if notes:
        print()
        print('--- LUU Y ---')
        for n in notes:
            print('  ' + n)
    print()
    print('HOAN TAT')


if __name__ == '__main__':
    main()
