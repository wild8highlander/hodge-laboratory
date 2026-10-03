#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the research paper PDFs (RU/EN): "The Particle Limit".

Pipeline (same as the main monograph):
  content -> LaTeX (TOC first body page) -> tectonic;
  Template 04 cover -> html2poster.js --width 794px; pypdf merge.

For the Russian edition the two experiment figures are regenerated with
Russian labels (matplotlib) into build/paper/plots_ru and copied into the
tectonic workdir under the same file names, so the block grammar stays
language-independent.

    python3 monograph/src/gen_paper_tex.py
    → monograph/pdf/{ru,en}/particle_limit.pdf
"""

import os
import shutil
import sys

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)
PROJECT = os.path.dirname(ROOT)
SKILL = '/home/z/my-project/skills/pdf'
PLOTS = os.path.join(PROJECT, 'reports', 'plots', 'complexity')

sys.path.insert(0, SRC)
from gen_tex import (tex_escape, table_latex, merge_pdf, run,  # noqa: E402
                     AUTHOR, SKILL as PDF_SKILL, BUILD)

from content_paper import PAPER  # noqa: E402

OUT = os.path.join(ROOT, 'pdf')
PAPER_BUILD = os.path.join(BUILD, 'paper')

INSTITUTION = {
    'ru': 'Лаборатория динамики шахматных частиц · chess-dynamics-lab',
    'en': 'Chess Particle Dynamics Laboratory · chess-dynamics-lab',
}
FOOTER = {'ru': 'chess-dynamics-lab · сертифицируемая программа · 2026',
          'en': 'chess-dynamics-lab · certifiable program · 2026'}
TOC_TITLE = {'ru': 'Содержание', 'en': 'Contents'}
KW_LABEL = {'ru': 'Ключевые слова', 'en': 'Keywords'}
PROOF_LABEL = {'ru': 'Доказательство.', 'en': 'Proof.'}

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
    title = PAPER[lang]['title']
    tsize = '30pt' if len(title) <= 50 else ('26pt' if len(title) <= 70
                                             else '23pt')
    return COVER_TPL % {
        'langcode': lang, 'tsize': tsize,
        'label': html_escape(PAPER[lang]['label']),
        'title': html_escape(title),
        'subtitle': html_escape(PAPER[lang]['subtitle']),
        'authors': html_escape(AUTHOR[lang]),
        'institution': html_escape(INSTITUTION[lang]),
        'footer': html_escape(FOOTER[lang]),
    }


def blocks_to_latex(blocks, lang):
    out = []
    for b in blocks:
        kind = b[0]
        if kind == 'h1':
            out.append('\\vspace{6pt}\\section*{%s}'
                       '\\addcontentsline{toc}{section}{%s}\\vspace{-4pt}'
                       % (tex_escape(b[1]), tex_escape(b[1])))
        elif kind == 'p':
            out.append('\\noindent %s\\par\\medskip' % tex_escape(b[1]))
        elif kind == 'abs':
            out.append('\\begin{quote}\\itshape %s\\end{quote}\\medskip'
                       % tex_escape(b[1]))
        elif kind == 'thm':
            out.append('\\begin{quote}\\noindent{\\bfseries %s}\\par\\smallskip'
                       '\\noindent %s\\end{quote}\\medskip'
                       % (tex_escape(b[1]), tex_escape(b[2])))
        elif kind == 'proof':
            out.append('\\begin{quote}\\noindent{\\itshape %s}~ %s\\hfill'
                       '$\\square$\\end{quote}\\medskip'
                       % (tex_escape(PROOF_LABEL[lang]), tex_escape(b[1])))
        elif kind == 'fig':
            fname, caption, wpct = b[1], b[2], b[3]
            out.append('\\begin{center}\\includegraphics[width=%.2f'
                       '\\linewidth]{plots/%s}'
                       '\\par\\vspace{4pt}{\\small\\color{muted} %s}'
                       '\\end{center}\\medskip'
                       % (wpct / 100.0, fname, tex_escape(caption)))
        elif kind == 'bib':
            items = '\\item '.join(tex_escape(x) for x in b[1])
            out.append('\\begin{enumerate}[leftmargin=2.2em, itemsep=2pt]'
                       '\n\\item %s\n\\end{enumerate}' % items)
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
    P = PAPER[lang]
    head = PREAMBLE % {'mainlang': mainlang, 'otherlang': otherlang}
    head += ('\\hypersetup{pdftitle={%s}, pdfauthor={%s}}\n' %
             (P['title'].replace('%', r'\%').replace('#', r'\#'),
              AUTHOR[lang]))
    # polyglossia renders its own localized "Содержание/Contents" heading
    # inside \tableofcontents — do NOT add a second one (double-title bug).
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
    ) % (tex_escape(P['label']), tex_escape(P['title']),
         tex_escape(P['subtitle']), tex_escape(AUTHOR[lang]),
         tex_escape(INSTITUTION[lang]), KW_LABEL[lang],
         tex_escape(P['keywords']))
    body = blocks_to_latex(P['content'], lang)
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


# ── Russian-labelled copies of the two experiment figures ────────────────

def make_ru_plots(outdir):
    import json
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.font_manager as fm
    for _f in ('/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf',
               '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
        if os.path.exists(_f):
            fm.fontManager.addfont(_f)
    import matplotlib.pyplot as plt
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Noto Sans SC']
    plt.rcParams['axes.unicode_minus'] = False

    NAVY, GOLD, TEAL, PURPLE, RED = ('#162032', '#8B7E5A', '#2E8B8B',
                                     '#6B4E9B', '#B03A3A')
    with open(os.path.join(PROJECT, 'results',
                           'complexity_particles_vs_oracle.json')) as f:
        e1 = json.load(f)
    with open(os.path.join(PROJECT, 'results',
                           'complexity_scaling.json')) as f:
        e2 = json.load(f)

    os.makedirs(outdir, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2),
                             constrained_layout=True)
    for ax, key, title in ((axes[0], 'R', 'KRK (ладья)'),
                           (axes[1], 'Q', 'KQK (ферзь)')):
        res = e1['results'][key]
        rows = res['depth_table']
        d = [r['depth_moves'] for r in rows]
        ax.plot(d, [100 * r['save_rate'] for r in rows], 'o-',
                color=NAVY, lw=2, ms=5,
                label='жадный ход сохраняет выигрыш')
        ax.plot(d, [100 * r['optimal_rate'] for r in rows], 's--',
                color=GOLD, lw=2, ms=5, label='жадный ход оптимален')
        ax.axhline(100, color=RED, lw=1, ls=':', alpha=0.7)
        ax.set_xlabel('глубина DTM выборки (ходов)')
        ax.set_ylabel('% позиций')
        ax.set_title('%s · выборка %d выигранных позиций'
                     % (title, res['evaluated']))
        ax.set_ylim(0, 105)
        ax.grid(alpha=0.25)
        ax.legend(fontsize=8, loc='lower left')
    fig.suptitle('E1 · полиномиальный частицный решатель против точного '
                 'DTM-оракула: жадный ход теряет 17,6% выигрышей KRK '
                 '(и 4,4% KQK)', fontsize=11)
    fig.savefig(os.path.join(outdir, 'error_vs_depth.png'), dpi=600)
    plt.close(fig)

    rows = e2['rows']
    ns = [r['n'] for r in rows]
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.2),
                             constrained_layout=True)
    ax = axes[0]
    ax.plot(ns, [r['states'] for r in rows], 'o-', color=NAVY, lw=2,
            label='состояния KRK (измерено)')
    ax.plot(ns, [r['states_theory_n6'] for r in rows], 's--',
            color=GOLD, lw=2, label=r'$n^2(n^2-1)(n^2-2)\sim n^6$')
    ax.set_yscale('log')
    ax.set_xlabel('размер доски n')
    ax.set_ylabel('состояния')
    ax.set_title('фиксированный k=3: рост ~ n^6 (полином)')
    ax.grid(alpha=0.25, which='both')
    ax.legend(fontsize=8)
    ax = axes[1]
    ax.plot(ns, [r['retro_seconds'] for r in rows], 'o-',
            color=PURPLE, lw=2, label='ретроград (однократно)')
    ax.plot(ns, [r['alphabeta_d6']['mean_ms'] for r in rows], 's-',
            color=RED, lw=2, label='альфа-бета, глубина 6')
    ax.plot(ns, [r['particle']['mean_ms'] for r in rows], '^-',
            color=TEAL, lw=2, label='ход частиц (жадный)')
    ax.set_yscale('log')
    ax.set_xlabel('размер доски n')
    ax.set_ylabel('время (с для ретрограда; мс для хода)')
    ax.set_title('времена: O(n^6) препроцессинг vs O(n^4) ход')
    ax.grid(alpha=0.25, which='both')
    ax.legend(fontsize=8)
    ax = axes[2]
    dtm = [r['max_dtm_moves'] for r in rows]
    ax.plot(ns, dtm, 'o-', color=NAVY, lw=2)
    for n, d in zip(ns, dtm):
        ax.annotate('%d' % d, (n, d), textcoords='offset points',
                    xytext=(4, 4), fontsize=8)
    ax.set_xlabel('размер доски n')
    ax.set_ylabel('максимальный DTM (ходов)')
    ax.set_title('горизонт DTM растёт с n\n'
                 '(KRK 8×8: 16 ходов, верифицировано)')
    ax.grid(alpha=0.25)
    fig.suptitle('E2 · масштабирование по доске: при фиксированном составе '
                 'всё полиномиально по n — экспоненциальная стена живёт в '
                 'числе фигур', fontsize=11)
    fig.savefig(os.path.join(outdir, 'scaling.png'), dpi=600)
    plt.close(fig)
    print('  RU plots written to', outdir)


def main():
    for lang in ('ru', 'en'):
        d_tex = os.path.join(PAPER_BUILD, 'tex', lang)
        d_pdf = os.path.join(PAPER_BUILD, 'pdf', lang)
        d_cov = os.path.join(PAPER_BUILD, 'cover', lang)
        plots_dst = os.path.join(d_tex, 'plots')
        for d in (d_tex, d_pdf, d_cov, plots_dst):
            os.makedirs(d, exist_ok=True)

        if lang == 'ru':
            make_ru_plots(os.path.join(PAPER_BUILD, 'plots_ru'))
            src_dir = os.path.join(PAPER_BUILD, 'plots_ru')
        else:
            src_dir = PLOTS
        for fn in ('error_vs_depth.png', 'scaling.png'):
            shutil.copy2(os.path.join(src_dir, fn),
                         os.path.join(plots_dst, fn))

        tex_path = os.path.join(d_tex, 'particle_limit.tex')
        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(build_tex(lang))
        run(['tectonic', '--outdir', d_pdf, tex_path, '--keep-logs'])
        body_pdf = os.path.join(d_pdf, 'particle_limit.pdf')

        html_path = os.path.join(d_cov, 'cover_%s.html' % lang)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(build_cover_html(lang))
        cov_pdf = os.path.join(d_cov, 'cover_%s.pdf' % lang)
        run(['node', os.path.join(PDF_SKILL, 'scripts', 'html2poster.js'),
             html_path, '--output', cov_pdf, '--width', '794px'])

        out_dir = os.path.join(OUT, lang)
        os.makedirs(out_dir, exist_ok=True)
        out_pdf = os.path.join(out_dir, 'particle_limit.pdf')
        merge_pdf(cov_pdf, body_pdf, out_pdf,
                  title='PARTICLE LIMIT — %s' % PAPER[lang]['title'],
                  author=AUTHOR[lang])
        print('  %s -> %s' % (lang, out_pdf))


if __name__ == '__main__':
    main()
