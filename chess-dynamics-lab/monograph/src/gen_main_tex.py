#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the main monograph PDFs (RU/EN): Template 04 cover + TOC + body.

Pipeline: content -> LaTeX (TOC first page of the body, per academic brief)
-> tectonic; Template 04 cover -> html2poster.js; pypdf merge; pdf_qa.
"""

import os
import shutil
import sys

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)
PROJECT = os.path.dirname(ROOT)
SKILL = '/home/z/my-project/skills/pdf'
PLOTS = os.path.join(PROJECT, 'reports', 'plots')

sys.path.insert(0, SRC)
from gen_tex import (tex_escape, table_latex, merge_pdf, run,  # noqa: E402
                     AUTHOR, SKILL as PDF_SKILL, BUILD)

from content_main import MAIN  # noqa: E402

OUT = os.path.join(ROOT, 'pdf')
MAIN_BUILD = os.path.join(BUILD, 'main')

LABEL = {'ru': 'ГЛАВНАЯ МОНОГРАФИЯ · ПРОГРАММА CHESS-DYNAMICS-LAB',
         'en': 'MAIN MONOGRAPH · CHESS-DYNAMICS-LAB PROGRAM'}
INSTITUTION = {
    'ru': 'Лаборатория динамики шахматных частиц · chess-dynamics-lab',
    'en': 'Chess Particle Dynamics Laboratory · chess-dynamics-lab',
}
FOOTER = {'ru': 'chess-dynamics-lab · сертифицируемая программа · 2026',
          'en': 'chess-dynamics-lab · certifiable program · 2026'}
TOC_TITLE = {'ru': 'Содержание', 'en': 'Contents'}
KW_LABEL = {'ru': 'Ключевые слова', 'en': 'Keywords'}

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
      --c-muted: #90A8C0;
    }
    html, body { margin: 0; padding: 0; width: 794px; height: 1123px; background: var(--c-bg); color: var(--c-text); font-family: 'Inter', 'Noto Sans SC', sans-serif; }
    @media screen {
      html { height: auto; display: flex; justify-content: center; min-height: 100vh; background: var(--c-bg); }
      body { transform-origin: top center; scale: min(1, calc(100vw / 794), calc(100vh / 1123)); margin: 0 auto; box-shadow: 0 0 60px rgba(0,0,0,0.3); }
    }
    .cover { width: 794px; height: 1123px; position: relative; box-sizing: border-box; }
    .rule-top, .rule-bottom { position: absolute; left: 114px; right: 114px; height: 2px; background: var(--c-accent); }
    .rule-top { top: 114px; }
    .rule-bottom { bottom: 114px; }
    .center-block { position: absolute; top: 160px; bottom: 160px; left: 114px; right: 114px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
    .label { font-size: 9pt; color: var(--c-accent); letter-spacing: 3px; text-transform: uppercase; margin-bottom: 40px; font-family: 'Inter', 'Noto Sans SC', sans-serif; }
    .title { font-size: %(tsize)s; font-weight: 700; line-height: 1.3; font-family: 'Playfair Display', 'Noto Serif SC', serif; margin-bottom: 26px; max-width: 520px; }
    .subtitle { font-size: 12.5pt; color: var(--c-muted); margin-bottom: 44px; max-width: 470px; line-height: 1.55; }
    .authors { font-size: 12pt; margin-bottom: 12px; }
    .institution { font-size: 10pt; color: var(--c-muted); line-height: 1.4; }
    .footer { position: absolute; bottom: 57px; left: 114px; right: 114px; text-align: center; font-size: 9pt; color: var(--c-muted); }
  </style>
</head>
<body>
  <div class="cover">
    <div class="rule-top"></div>
    <div class="rule-bottom"></div>
    <div class="center-block">
      <div class="label">%(label)s</div>
      <div class="title">%(title)s</div>
      <div class="subtitle">%(subtitle)s</div>
      <div class="authors">%(authors)s</div>
      <div class="institution">%(institution)s</div>
    </div>
    <div class="footer">%(footer)s</div>
  </div>
</body>
</html>
'''


def html_escape(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def build_cover_html(lang):
    title = MAIN['title'][lang]
    tsize = '30pt' if len(title) <= 50 else ('26pt' if len(title) <= 70 else '23pt')
    return COVER_TPL % {
        'langcode': lang,
        'tsize': tsize,
        'label': html_escape(LABEL[lang]),
        'title': html_escape(title),
        'subtitle': html_escape(MAIN['subtitle'][lang]),
        'authors': html_escape(AUTHOR[lang]),
        'institution': html_escape(INSTITUTION[lang]),
        'footer': html_escape(FOOTER[lang]),
    }


def blocks_to_latex(blocks, lang):
    out = []
    for b in blocks:
        kind = b[0]
        if kind == 'h1':
            out.append('\\vspace{6pt}\\section*{%s}\\addcontentsline{toc}{section}{%s}\\vspace{-4pt}'
                       % (tex_escape(b[1]), tex_escape(b[1])))
        elif kind == 'p':
            out.append('\\noindent %s\\par\\medskip' % tex_escape(b[1]))
        elif kind == 'abs':
            out.append('\\begin{quote}\\itshape %s\\end{quote}\\medskip' % tex_escape(b[1]))
        elif kind == 'fig':
            fname, caption, wpct = b[1], b[2], b[3]
            out.append('\\begin{center}\\includegraphics[width=%.2f\\linewidth]{plots/%s}'
                       '\\par\\vspace{4pt}{\\small\\color{muted} %s}\\end{center}\\medskip'
                       % (wpct / 100.0, fname, tex_escape(caption)))
        elif kind == 'bib':
            items = '\\item '.join(tex_escape(x) for x in b[1])
            out.append('\\begin{enumerate}[leftmargin=2.2em, itemsep=2pt]\n\\item %s\n\\end{enumerate}'
                       % items)
        elif kind == 'table':
            out.append(table_latex(b[1], b[2], b[3]))
        else:
            raise ValueError('unknown block: %r' % kind)
    return '\n\n'.join(out)


PREAMBLE = r'''\documentclass[11pt]{article}
\usepackage{polyglossia}
\setmainlanguage{%(mainlang)s}
\setotherlanguage{%(otherlang)s}
\usepackage{amsmath,amssymb}
\usepackage{geometry}
\usepackage{xcolor}
\usepackage{array,booktabs}
\usepackage{framed}
\usepackage{graphicx}
\usepackage{enumitem}
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
\newcommand{\hruleaccent}{\noindent{\color{accent}\rule{\linewidth}{1.2pt}}\par}
\linespread{1.08}
\setlength{\parindent}{0pt}
\setlength{\parskip}{5pt plus 1pt minus 1pt}
\emergencystretch=3em
\tolerance=2000
\hbadness=10000
\widowpenalty=10000
\clubpenalty=10000
\begin{document}
'''


def build_tex(lang):
    mainlang = 'russian' if lang == 'ru' else 'english'
    otherlang = 'english' if lang == 'ru' else 'russian'
    head = PREAMBLE % {'mainlang': mainlang, 'otherlang': otherlang}
    title = MAIN['title'][lang]
    head += ('\\hypersetup{pdftitle={%s}, pdfauthor={%s}}\n' %
             (title.replace('%', r'\%').replace('#', r'\#'), AUTHOR[lang]))
    # TOC page (first page of the body, per academic brief)
    # polyglossia renders its own localized TOC title (double-title fix)
    tocpage = '\\tableofcontents\n\\newpage\n'
    header = (
        '\\begin{center}'
        '{\\color{accent}\\sffamily\\footnotesize\\bfseries %s}\\par\\vspace{10pt}'
        '{\\Large\\bfseries %s}\\par\\vspace{8pt}'
        '{\\color{muted}\\large %s}\\par\\vspace{12pt}'
        '{\\small %s}\\par\\vspace{2pt}'
        '{\\footnotesize\\color{muted} %s}\\par\\vspace{8pt}'
        '{\\footnotesize\\color{muted} %s: %s}\\par'
        '\\end{center}'
        '\\vspace{4pt}\\hruleaccent\\vspace{14pt}'
    ) % (tex_escape(LABEL[lang]), tex_escape(title),
         tex_escape(MAIN['subtitle'][lang]), tex_escape(AUTHOR[lang]),
         tex_escape(INSTITUTION[lang]), KW_LABEL[lang],
         tex_escape(MAIN['keywords'][lang]))
    body = blocks_to_latex(MAIN['content'][lang], lang)
    copy = {
        'ru': '© 2026 Исаев Исхак Хамзатович · chess-dynamics-lab · '
              'Индивидуальная исключительная лицензия',
        'en': '© 2026 Isaev Iskhak Khamzatovich · chess-dynamics-lab · '
              'Individual exclusive license',
    }[lang]
    return (head + tocpage + header + '\n' + body + '\n\n' +
            '\\vspace{16pt}\\hruleaccent\\vspace{8pt}\n'
            '\\noindent{\\footnotesize\\color{muted} %s}\\par\n'
            '\\end{document}\n' % tex_escape(copy))


def main():
    for lang in ('ru', 'en'):
        d_tex = os.path.join(MAIN_BUILD, 'tex', lang)
        d_pdf = os.path.join(MAIN_BUILD, 'pdf', lang)
        d_cov = os.path.join(MAIN_BUILD, 'cover', lang)
        plots_dst = os.path.join(d_tex, 'plots')
        for d in (d_tex, d_pdf, d_cov, plots_dst):
            os.makedirs(d, exist_ok=True)
        for fn in os.listdir(PLOTS):
            if not os.path.isfile(os.path.join(PLOTS, fn)):
                continue          # skip subdirectories (e.g. complexity/)
            shutil.copy2(os.path.join(PLOTS, fn), os.path.join(plots_dst, fn))

        tex_path = os.path.join(d_tex, 'main_monograph.tex')
        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(build_tex(lang))
        run(['tectonic', '--outdir', d_pdf, tex_path,
             '--keep-intermediates' if False else '--keep-logs'])
        body_pdf = os.path.join(d_pdf, 'main_monograph.pdf')

        html_path = os.path.join(d_cov, 'cover_%s.html' % lang)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(build_cover_html(lang))
        cov_pdf = os.path.join(d_cov, 'cover_%s.pdf' % lang)
        run(['node', os.path.join(PDF_SKILL, 'scripts', 'html2poster.js'),
             html_path, '--output', cov_pdf, '--width', '794px'])

        out_dir = os.path.join(OUT, lang)
        os.makedirs(out_dir, exist_ok=True)
        out_pdf = os.path.join(out_dir, 'main_monograph.pdf')
        merge_pdf(cov_pdf, body_pdf, out_pdf,
                  title='%s — %s' % ('MAIN', MAIN['title'][lang]),
                  author=AUTHOR[lang])
        print('  %s -> %s' % (lang, out_pdf))


if __name__ == '__main__':
    main()
