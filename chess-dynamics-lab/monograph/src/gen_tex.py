#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate 24 theorem monograph PDFs (12 theorems x RU/EN).

Pipeline per document (academic route of the pdf skill):
  1. blocks -> LaTeX body (no title page; header info block instead)
  2. tectonic -> body.pdf
  3. cover HTML (Template 03, dark vertical anchor) -> html2poster.js -> cover.pdf
  4. pypdf merge (cover normalized to A4) -> monograph/pdf/<lang>/<id>_<slug>.pdf
"""

import os
import re
import subprocess
import sys

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)                          # monograph/
PROJECT = os.path.dirname(ROOT)                      # chess-dynamics-lab/
SKILL = '/home/z/my-project/skills/pdf'
OUT = os.path.join(ROOT, 'pdf')
BUILD = os.path.join(ROOT, 'build')

sys.path.insert(0, SRC)
from content_theorems_1 import THEOREMS_PART1        # noqa: E402
from content_theorems_2 import THEOREMS_PART2        # noqa: E402
from content_theorems_3 import THEOREMS_PART3        # noqa: E402

THEOREMS = THEOREMS_PART1 + THEOREMS_PART2 + THEOREMS_PART3

AUTHOR = {'ru': 'Исаев Исхак Хамзатович',
          'en': 'Isaev Iskhak Khamzatovich'}
LABEL = {'ru': 'МОНОГРАФИЯ %(id)s · ПРОГРАММА CHESS-DYNAMICS-LAB',
         'en': 'THEOREM MONOGRAPH %(id)s · CHESS-DYNAMICS-LAB PROGRAM'}
INSTITUTION = {
    'ru': 'Лаборатория динамики шахматных частиц · chess-dynamics-lab',
    'en': 'Chess Particle Dynamics Laboratory · chess-dynamics-lab',
}
FOOT_LEFT = {'ru': 'chess-dynamics-lab · сертифицируемая программа',
             'en': 'chess-dynamics-lab · certifiable program'}
FOOT_RIGHT = '2026'
YEAR = '2026'

# ──────────────────────────────────────────────────────────────────────────
# escaping: split into $math$ and plain segments
# ──────────────────────────────────────────────────────────────────────────

MATH_RE = re.compile(r'(\$[^$]+\$)')
POWER_RE = re.compile(r'([A-Za-z0-9\)\}])\^([A-Za-z0-9]+(?:\([A-Za-z0-9/]+\))?)')
XOR_RE = re.compile(r' \^ ')


def _fix_quotes(s):
    """Alternate straight quotes -> LaTeX `` and '' (per segment)."""
    out, opening = [], True
    for ch in s:
        if ch == '"':
            out.append('``' if opening else "''")
            opening = not opening
        else:
            out.append(ch)
    return ''.join(out)


def esc_plain(s):
    """Escape LaTeX specials in a plain (non-math) segment.

    Order matters: common operators are mathified first, the literal
    caret is replaced once, then power/XOR patterns are upgraded from
    the escaped form (so their own ^ never gets double-escaped).
    """
    s = _fix_quotes(s)
    s = s.replace('\\', r'\textbackslash{}')
    s = s.replace('%', r'\%').replace('&', r'\&').replace('#', r'\#')
    s = s.replace('_', r'\_')
    s = s.replace('~', r'\textasciitilde{}')
    s = s.replace('<<', r'\ensuremath{\ll}')
    s = s.replace('>>', r'\ensuremath{\gg}')
    s = s.replace('->', r'\ensuremath{\rightarrow}')
    s = s.replace(' * ', r' \ensuremath{\cdot} ')
    s = s.replace('^', r'\textasciicircum{}')
    # upgrade powers: x^64, sigma^-1, b^ceil(d/2), b^floor(d/2)
    s = re.sub(r'([A-Za-z0-9\)\}])\\textasciicircum\{\}((?:ceil|floor|log)\([A-Za-z0-9/]+\))',
               lambda m: r'\ensuremath{%s^{%s}}' % (m.group(1), m.group(2)), s)
    s = re.sub(r'([A-Za-z0-9\)\}])\\textasciicircum\{\}([A-Za-z0-9\-\{\}]+)',
               lambda m: r'\ensuremath{%s^{%s}}' % (m.group(1), m.group(2)), s)
    s = s.replace(r' \textasciicircum{} ', r' \ensuremath{\oplus} ')
    s = s.replace('|', r'\textbar{}')
    s = s.replace('/', r'/\allowbreak{}')   # break opportunities in paths/FENs
    s = s.replace(' — ', '~— ')          # no line-start em-dash
    s = s.replace('--', '--{}')          # keep CLI flags literal
    return s


def tex_escape(text):
    # quote pairing must be decided on the whole text, not per math segment
    text = _fix_quotes(text)
    text = text.replace(' ``', '~``')      # opening quote never starts a line
    text = text.replace(" ''", "~''")      # closing quote never starts a line
    parts = MATH_RE.split(text)
    out = []
    for p in parts:
        if p.startswith('$') and p.endswith('$') and len(p) > 2:
            out.append(p)                # math verbatim
        else:
            out.append(esc_plain(p))
    return ''.join(out)


# ──────────────────────────────────────────────────────────────────────────
# blocks -> LaTeX
# ──────────────────────────────────────────────────────────────────────────

def col_widths(headers, rows, ncol):
    """Content-weighted p-column fractions of \\linewidth."""
    weights = []
    for i in range(ncol):
        lens = [len(str(headers[i]))] + [len(str(r[i])) for r in rows]
        weights.append(max(6.0, max(lens) ** 0.85))
    total = sum(weights)
    fracs = [max(0.07, 0.94 * w / total) for w in weights]
    # renormalize after clipping
    scale = 0.94 / sum(fracs)
    return [f * scale for f in fracs]


def table_latex(caption, headers, rows):
    n = len(headers)
    ws = col_widths(headers, rows, n)
    spec = '@{}' + ''.join('>{\\raggedright\\arraybackslash}p{%.3f\\linewidth}' % w
                           for w in ws) + '@{}'
    wide = n >= 5 or sum(len(str(c)) for r in rows for c in r) > 120
    fs = '\\footnotesize' if wide else '\\small'
    hdr = ' & '.join('\\textbf{%s}' % tex_escape(h) for h in headers)
    lines = ['\\vspace{8pt}',
             '\\noindent{%s\\bfseries %s}\\par\\vspace{4pt}' % (fs, tex_escape(caption)),
             '\\noindent{%s\\setlength{\\tabcolsep}{3pt}%%' % fs,
             '\\begin{tabular}{%s}' % spec,
             '\\toprule',
             hdr + ' \\\\[2pt]',
             '\\midrule']
    for r in rows:
        cells = []
        for c in r:
            c = str(c)
            if c == '—':
                c = '--'                 # lone em-dash cell -> en-dash
            cells.append(tex_escape(c))
        lines.append(' & '.join(cells) + ' \\\\')
    lines += ['\\bottomrule', '\\end{tabular}}\\par\\vspace{10pt}']
    return '\n'.join(lines)


def blocks_to_latex(blocks):
    out = []
    for b in blocks:
        kind = b[0]
        if kind == 'h1':
            out.append('\\vspace{4pt}\\section*{%s}\\vspace{-2pt}' % tex_escape(b[1]))
        elif kind == 'p':
            out.append('\\noindent %s\\par\\medskip' % tex_escape(b[1]))
        elif kind == 'f':
            out.append('\\begin{center}\\[%s\\]\\end{center}' % b[1])
        elif kind == 'thm':
            label, latex = b[1], b[2]
            out.append('\\begin{certbar}\n\\noindent{\\bfseries %s} %s\\par\n\\end{certbar}\\medskip'
                       % (tex_escape(label), tex_escape(latex)))
        elif kind == 'table':
            out.append(table_latex(b[1], b[2], b[3]))
        else:
            raise ValueError('unknown block kind: %r' % kind)
    return '\n\n'.join(out)


PREAMBLE_RU = r'''\documentclass[11pt]{article}
\usepackage{polyglossia}
\setmainlanguage{russian}
\setotherlanguage{english}
\usepackage{amsmath,amssymb}
\usepackage{geometry}
\usepackage{xcolor}
\usepackage{array,booktabs}
\usepackage{framed}
\definecolor{accent}{HTML}{8B7E5A}
\definecolor{deep}{HTML}{162032}
\definecolor{muted}{HTML}{8898A8}
\usepackage[unicode,colorlinks=true,linkcolor=deep,urlcolor=accent]{hyperref}
\geometry{a4paper, top=2.4cm, bottom=2.4cm, left=2.4cm, right=2.4cm}
\setmainfont{DejaVu Serif}
\setsansfont{DejaVu Sans}
\setmonofont{DejaVu Sans Mono}
\newfontfamily\cyrillicfont{DejaVu Serif}[Script=Cyrillic]
\newfontfamily\cyrillicfonttt{DejaVu Sans Mono}[Script=Cyrillic]
\newenvironment{certbar}
{\def\FrameCommand{{\color{accent}\vrule width 3pt}\hspace{10pt}}%
 \MakeFramed{\advance\hsize-\width\FrameRestore}\vspace{4pt}}
{\vspace{4pt}\endMakeFramed}
\newcommand{\hruleaccent}{\noindent{\color{accent}\rule{\linewidth}{1.2pt}}\par}
\linespread{1.08}
\setlength{\parindent}{0pt}
\setlength{\parskip}{5pt plus 1pt minus 1pt}
\emergencystretch=3em
\tolerance=2000
\hbadness=10000
\widowpenalty=10000
\clubpenalty=10000
'''

PREAMBLE_EN = PREAMBLE_RU.replace(r'\setmainlanguage{russian}',
                                  r'\setmainlanguage{english}')


def header_block(t, lang):
    lines = [
        r'\begin{center}',
        '{\\color{accent}\\sffamily\\footnotesize\\bfseries %s}\\par\\vspace{10pt}'
        % tex_escape(LABEL[lang] % {'id': t['id']}),
        '{\\LARGE\\bfseries %s}\\par\\vspace{8pt}' % tex_escape(t['title'][lang]),
        '{\\color{muted}\\large %s}\\par\\vspace{14pt}' % tex_escape(t['subtitle'][lang]),
        '{\\small %s}\\par\\vspace{2pt}' % tex_escape(AUTHOR[lang]),
        '{\\footnotesize\\color{muted} %s}\\par\\vspace{10pt}' % tex_escape(INSTITUTION[lang]),
        '{\\footnotesize\\color{muted} %s: %s}\\par' % (
            'Ключевые слова' if lang == 'ru' else 'Keywords',
            tex_escape(t['keywords'][lang])),
        r'\end{center}',
        r'\vspace{4pt}\hruleaccent\vspace{14pt}',
    ]
    return '\n'.join(lines)


def build_tex(t, lang):
    pre = PREAMBLE_RU if lang == 'ru' else PREAMBLE_EN
    title = t['title'][lang]
    body = blocks_to_latex(t['content'][lang])
    copy = {
        'ru': '© 2026 Исаев Исхак Хамзатович · chess-dynamics-lab · '
              'Индивидуальная исключительная лицензия',
        'en': '© 2026 Isaev Iskhak Khamzatovich · chess-dynamics-lab · '
              'Individual exclusive license',
    }[lang]
    hypersetup = '\\hypersetup{pdftitle={%s}, pdfauthor={%s}}\n' % (
        title.replace('%', r'\%').replace('#', r'\#'), AUTHOR[lang])
    return (pre + hypersetup + r'\begin{document}' + '\n' +
            header_block(t, lang) + '\n' + body + '\n\n' +
            '\\vspace{16pt}\\hruleaccent\\vspace{8pt}\n'
            '\\noindent{\\footnotesize\\color{muted} %s}\\par\n'
            '\\end{document}\n' % tex_escape(copy))


# ──────────────────────────────────────────────────────────────────────────
# cover (Template 03: academic vertical anchor, dark bg)
# ──────────────────────────────────────────────────────────────────────────

COVER_TPL = r'''<!DOCTYPE html>
<html lang="%(langcode)s">
<head>
  <meta charset="UTF-8">
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Noto+Serif+SC:wght@400;700;900&family=Inter:wght@300;400;500&family=Noto+Sans+SC:wght@300;400;500&display=swap" rel="stylesheet">
  <style>
    @page { size: 794px 1123px; margin: 0; }
    :root {
      --c-bg: #162032;
      --c-accent: #8B7E5A;
      --c-text: #FFFFFF;
      --c-muted: #8898A8;
      --c-footer: #607080;
    }
    html, body { margin: 0; padding: 0; width: 794px; height: 1123px; background: var(--c-bg); color: var(--c-text); font-family: 'Inter', 'Noto Sans SC', sans-serif; }
    @media screen {
      html { height: auto; display: flex; justify-content: center; min-height: 100vh; background: var(--c-bg); }
      body { transform-origin: top center; scale: min(1, calc(100vw / 794), calc(100vh / 1123)); margin: 0 auto; box-shadow: 0 0 60px rgba(0,0,0,0.3); }
    }
    .cover { width: 794px; height: 1123px; position: relative; box-sizing: border-box; }
    .vline { position: absolute; left: 57px; top: 76px; bottom: 76px; width: 2.5px; background: var(--c-accent); }
    .content { position: absolute; left: 83px; right: 76px; top: 0; bottom: 0; }
    .label { position: absolute; top: 132px; font-size: 9pt; color: var(--c-accent); letter-spacing: 3px; text-transform: uppercase; font-family: 'Inter', 'Noto Sans SC', sans-serif; }
    .title { position: absolute; top: 228px; font-size: %(tsize)s; font-weight: 700; line-height: 1.3; font-family: 'Playfair Display', 'Noto Serif SC', serif; color: var(--c-text); max-width: 580px; }
    .subtitle { position: absolute; top: 530px; font-size: 12pt; line-height: 1.5; color: var(--c-muted); max-width: 500px; }
    .authors { position: absolute; top: 680px; font-size: 12pt; color: var(--c-text); }
    .institution { position: absolute; top: 740px; font-size: 10pt; color: var(--c-muted); line-height: 1.4; }
    .keywords { position: absolute; top: 800px; font-size: 8.5pt; color: var(--c-footer); max-width: 520px; line-height: 1.5; }
    .footer { position: absolute; bottom: 76px; left: 0; right: 0; display: flex; justify-content: space-between; font-size: 9pt; color: var(--c-footer); }
  </style>
</head>
<body>
  <div class="cover">
    <div class="vline"></div>
    <div class="content">
      <div class="label">%(label)s</div>
      <div class="title">%(title)s</div>
      <div class="subtitle">%(subtitle)s</div>
      <div class="authors">%(authors)s</div>
      <div class="institution">%(institution)s</div>
      <div class="keywords">%(keywords)s</div>
      <div class="footer">
        <span>%(footer_left)s</span>
        <span>%(footer_right)s</span>
      </div>
    </div>
  </div>
</body>
</html>
'''


def html_escape(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


def build_cover_html(t, lang):
    title = t['title'][lang]
    tsize = '32pt' if len(title) <= 55 else ('27pt' if len(title) <= 75 else '24pt')
    kw_label = 'Keywords: ' if lang == 'en' else 'Ключевые слова: '
    return COVER_TPL % {
        'langcode': lang,
        'tsize': tsize,
        'label': html_escape(LABEL[lang] % {'id': t['id']}),
        'title': html_escape(title),
        'subtitle': html_escape(t['subtitle'][lang]),
        'authors': html_escape(AUTHOR[lang]),
        'institution': html_escape(INSTITUTION[lang]),
        'keywords': html_escape(kw_label + t['keywords'][lang]),
        'footer_left': html_escape(FOOT_LEFT[lang] + ' · ' + t['id'] + ' · ' + YEAR),
        'footer_right': html_escape(YEAR),
    }


# ──────────────────────────────────────────────────────────────────────────
# pipeline steps
# ──────────────────────────────────────────────────────────────────────────

def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        sys.stderr.write(r.stdout[-3000:] + '\n' + r.stderr[-3000:] + '\n')
        raise RuntimeError('command failed: %s' % ' '.join(cmd))
    return r


def merge_pdf(cover_pdf, body_pdf, out_pdf, title='', author=''):
    from pypdf import PdfReader, PdfWriter
    A4_W, A4_H = 595.28, 841.89

    def norm(page):
        w, h = float(page.mediabox.width), float(page.mediabox.height)
        if abs(w - A4_W) > 0.2 or abs(h - A4_H) > 0.2:
            page.scale_to(A4_W, A4_H)
            page.mediabox.lower_left = (0, 0)
            page.mediabox.upper_right = (A4_W, A4_H)
        return page

    writer = PdfWriter()
    writer.add_page(norm(PdfReader(cover_pdf).pages[0]))
    for page in PdfReader(body_pdf).pages:
        writer.add_page(page)
    writer.add_metadata({'/Title': title, '/Author': author,
                         '/Creator': 'chess-dynamics-lab monograph pipeline',
                         '/Producer': 'tectonic + pypdf'})
    with open(out_pdf, 'wb') as f:
        writer.write(f)


def build_one(t, lang, log=print):
    tid = t['id'].lower()
    stem = '%s_%s' % (tid, t['slug'])
    d_tex = os.path.join(BUILD, 'tex', lang)
    d_pdf = os.path.join(BUILD, 'pdf', lang)
    d_cov = os.path.join(BUILD, 'cover', lang)
    for d in (d_tex, d_pdf, d_cov):
        os.makedirs(d, exist_ok=True)

    # 1. tex + tectonic
    tex_path = os.path.join(d_tex, stem + '.tex')
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(build_tex(t, lang))
    run(['tectonic', '--outdir', d_pdf, tex_path])
    body_pdf = os.path.join(d_pdf, stem + '.pdf')

    # 2. cover html -> pdf
    html_path = os.path.join(d_cov, stem + '.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(build_cover_html(t, lang))
    cov_pdf = os.path.join(d_cov, stem + '.pdf')
    run(['node', os.path.join(SKILL, 'scripts', 'html2poster.js'),
         html_path, '--output', cov_pdf, '--width', '794px'])

    # 3. merge
    out_dir = os.path.join(OUT, lang)
    os.makedirs(out_dir, exist_ok=True)
    out_pdf = os.path.join(out_dir, stem + '.pdf')
    merge_pdf(cov_pdf, body_pdf, out_pdf,
              title='%s — %s' % (t['id'], t['title'][lang]),
              author=AUTHOR[lang])
    log('  %s/%s -> %s' % (lang, t['id'], os.path.basename(out_pdf)))
    return out_pdf


def main():
    only = sys.argv[1:] or None
    for t in THEOREMS:
        for lang in ('ru', 'en'):
            if only and not (t['id'] in only or t['slug'] in only):
                continue
            build_one(t, lang)


if __name__ == '__main__':
    main()

