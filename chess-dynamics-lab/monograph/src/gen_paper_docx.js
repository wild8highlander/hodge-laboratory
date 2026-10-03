#!/usr/bin/env node
// gen_paper_docx.js — the research paper DOCX (RU/EN): "The Particle Limit".
// R5 cover + TOC section + body with theorem/proof/figure/table blocks.

const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun,
  Footer, PageNumber, NumberFormat, SectionType, AlignmentType, HeadingLevel,
  WidthType, BorderStyle, ShadingType, TableLayoutType, TableOfContents,
} = require("docx");
const fs = require("fs");
const path = require("path");
const L = require("./docx_lib.js");

const { OUT, META, ACCENT, INK, FONT, NB, noBorders, allNoBorders,
  texToRuns, richRuns } = L;

const MAIN = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "build", "paper_data.json"), "utf8"));
const PLOTS = path.join(__dirname, "..", "..", "reports", "plots", "complexity");
const PG = { size: { width: 11906, height: 16838 },
  margin: { top: 1440, bottom: 1440, left: 1701, right: 1417 } };

const M = {
  ru: {
    tocTitle: "Содержание",
    tocHint: "Примечание: оглавление построено на кодах полей. После редактирования документа щёлкните по оглавлению правой кнопкой мыши и выберите «Обновить поле», чтобы актуализировать номера страниц.",
    keywords: "Ключевые слова",
    label: "ИССЛЕДОВАТЕЛЬСКАЯ СТАТЬЯ · ПРОГРАММА CHESS-DYNAMICS-LAB",
    school: "CHESS-DYNAMICS-LAB",
    bib: "Библиография",
    meta: [
      { label: "Автор", value: "Исаев Исхак Хамзатович" },
      { label: "Серия", value: "Исследовательская статья" },
      { label: "Программа", value: "chess-dynamics-lab" },
      { label: "Состав", value: "7 разделов · 2 теоремы · 2 рисунка · 10 источников" },
      { label: "Лицензия", value: "Индивидуальная исключительная" },
    ],
    footer: "© 2026 chess-dynamics-lab · Индивидуальная исключительная лицензия",
  },
  en: {
    tocTitle: "Contents",
    tocHint: "Note: this Table of Contents is generated via field codes. To ensure page number accuracy after editing, please right-click the TOC and select \"Update Field.\"",
    keywords: "Keywords",
    label: "RESEARCH PAPER · CHESS-DYNAMICS-LAB PROGRAM",
    school: "CHESS-DYNAMICS-LAB",
    bib: "Bibliography",
    meta: [
      { label: "Author", value: "Isaev Iskhak Khamzatovich" },
      { label: "Series", value: "Research paper" },
      { label: "Program", value: "chess-dynamics-lab" },
      { label: "Contents", value: "7 sections · 2 theorems · 2 figures · 10 references" },
      { label: "License", value: "Individual exclusive" },
    ],
    footer: "© 2026 chess-dynamics-lab · Individual exclusive license",
  },
};

// ─── cover (R5, same rules as the theorem monographs) ───────────────────
function calcTitleLayoutMixed(title, maxWidthTw, preferredPt = 30, minPt = 22) {
  const estimate = (text, pt) => {
    let w = 0;
    for (const ch of text) {
      const code = ch.codePointAt(0);
      const isCJK = (code >= 0x4E00 && code <= 0x9FFF) || (code >= 0x3000 && code <= 0x303F);
      w += isCJK ? pt * 20 : pt * 11;
    }
    return w;
  };
  const split = (t, pt) => {
    const words = t.split(/\s+/); const lines = []; let cur = "";
    for (const wd of words) {
      const cand = cur ? cur + " " + wd : wd;
      if (estimate(cand, pt) <= maxWidthTw || !cur) cur = cand;
      else { lines.push(cur); cur = wd; }
    }
    if (cur) lines.push(cur);
    if (lines.length >= 2 && lines[lines.length - 1].length <= 3) {
      lines[lines.length - 2] += " " + lines.pop();
    }
    return lines;
  };
  let pt = preferredPt, lines;
  while (pt >= minPt) {
    lines = split(title, pt);
    if (lines.length <= 3) break;
    pt -= 2;
  }
  if (!lines || lines.length > 3) { pt = minPt; lines = split(title, pt); }
  return { titlePt: pt, titleLines: lines };
}

function buildR5MetaTable(metaEntries) {
  const maxLabelLen = Math.max(...metaEntries.map(e => [...e.label].length));
  const labelNeedTw = (maxLabelLen + 2) * 12 * 11;
  const tablePct = Math.min(75, Math.max(55, Math.ceil((labelNeedTw + 5000) / 11906 * 100)));
  const labelPct = Math.max(25, Math.min(45, Math.ceil(labelNeedTw / (tablePct / 100 * 11906) * 100)));
  const valuePct = 100 - labelPct;
  const bottomBorder = { style: BorderStyle.SINGLE, size: 4, color: "000000" };
  const rows = metaEntries.map(entry => new TableRow({
    cantSplit: true,
    children: [
      new TableCell({
        width: { size: labelPct, type: WidthType.PERCENTAGE },
        borders: noBorders, margins: { left: 0, right: 0 },
        children: [new Paragraph({
          alignment: AlignmentType.LEFT, spacing: { before: 60, after: 60, line: 400 },
          children: [new TextRun({ text: entry.label + ":", size: 24, font: FONT })],
        })],
      }),
      new TableCell({
        width: { size: valuePct, type: WidthType.PERCENTAGE },
        borders: { top: NB, left: NB, right: NB, bottom: bottomBorder },
        margins: { left: 80, right: 0 },
        children: [new Paragraph({
          alignment: AlignmentType.LEFT, spacing: { before: 60, after: 60, line: 400 },
          children: [new TextRun({ text: entry.value, size: 24, font: FONT })],
        })],
      }),
    ],
  }));
  return new Table({
    width: { size: tablePct, type: WidthType.PERCENTAGE },
    alignment: AlignmentType.CENTER, layout: TableLayoutType.FIXED,
    borders: allNoBorders, rows,
  });
}

function buildCoverR5(cfg) {
  const PAGE_H = 16838;
  const simMarginLR = 1701;
  const contentW = 11906 - simMarginLR * 2;
  const { titlePt, titleLines } = calcTitleLayoutMixed(cfg.title, contentW, 30, 22);
  const metaEntries = cfg.metaEntries || [];
  const fixedH = (18 * 23 + 400) + titleLines.length * (titlePt * 23 + 200) +
    (13 * 23 + 600) + metaEntries.length * 520 + (12 * 23 + 200) + 3 * 350;
  const remaining = Math.max(PAGE_H - 1200 - fixedH, 600);
  const topSpacing = Math.min(Math.floor(remaining * 0.28) + 1200, 4200);
  const midSpacing = Math.min(Math.floor((remaining - 1200) * 0.18), 2000);
  const bottomSpacing = Math.max(Math.min(remaining - topSpacing + 1200 - midSpacing, 4800), 400);

  const children = [new Paragraph({ spacing: { before: topSpacing } })];
  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 400, line: Math.ceil(18 * 23), lineRule: "atLeast" },
    children: [new TextRun({ text: cfg.school, size: 36, characterSpacing: 60, color: INK, font: FONT })],
  }));
  titleLines.forEach((line, i) => children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: i < titleLines.length - 1 ? 120 : 300,
      line: Math.ceil(titlePt * 23), lineRule: "atLeast" },
    children: [new TextRun({ text: line, size: titlePt * 2, bold: true, color: "000000", font: FONT })],
  })));
  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 200, line: Math.ceil(13 * 23), lineRule: "atLeast" },
    children: [new TextRun({ text: cfg.subtitle, size: 26, color: "404040", font: FONT })],
  }));
  children.push(new Paragraph({ spacing: { before: midSpacing } }));
  children.push(buildR5MetaTable(metaEntries));
  children.push(new Paragraph({ spacing: { before: bottomSpacing } }));
  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ text: cfg.footer, size: 20, color: "404040", font: FONT })],
  }));

  return [new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    layout: TableLayoutType.FIXED, borders: allNoBorders,
    rows: [new TableRow({
      height: { value: PAGE_H, rule: "exact" },
      children: [new TableCell({
        shading: { type: ShadingType.CLEAR, fill: "FFFFFF" },
        borders: noBorders, verticalAlign: "top",
        margins: { left: simMarginLR, right: simMarginLR },
        children,
      })],
    })],
  })];
}


const PROOF_LABEL = { ru: "Доказательство.", en: "Proof." };

function thmBlock(title, body) {
  const shaded = { type: ShadingType.CLEAR, fill: "F6F4EF" };
  const leftBorder = { left: { style: BorderStyle.SINGLE, size: 24, color: ACCENT, space: 8 } };
  return [
    new Paragraph({
      keepNext: true, shading: shaded, border: leftBorder,
      indent: { left: 360, right: 360 }, spacing: { before: 160, after: 40, line: 312 },
      children: [new TextRun({ text: title, bold: true, size: 24, color: "162032", font: FONT })],
    }),
    new Paragraph({
      shading: shaded, border: leftBorder,
      indent: { left: 360, right: 360 }, spacing: { after: 160, line: 312 },
      children: richRuns(body, bodyProps(), mathProps()),
    }),
  ];
}

function proofBlock(body, lang) {
  const props = { size: 24, color: "303030", font: FONT };
  return [new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    indent: { left: 360, right: 360 }, spacing: { after: 160, line: 312 },
    children: [
      new TextRun({ text: PROOF_LABEL[lang] + " ", italics: true, size: 24, color: "303030", font: FONT }),
      ...richRuns(body, props, mathProps()),
      new TextRun({ text: "  \u25A1", size: 24, color: "303030", font: FONT }),
    ],
  })];
}

// ─── body blocks ─────────────────────────────────────────────────────────
function pngSize(file) {
  const buf = fs.readFileSync(file);
  return { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) };
}

function bodyProps() { return { size: 24, color: "000000", font: FONT }; }
function mathProps() { return { size: 24, color: "000000", font: FONT, italics: true }; }

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 160, line: 312 },
    children: [new TextRun({ text, bold: true, size: 30, color: "000000", font: FONT })],
  });
}

function figBlock(fname, caption) {
  const file = path.join(PLOTS, fname);
  const { w, h } = pngSize(file);
  const displayW = 560;
  const displayH = Math.round(displayW * h / w);
  return [
    new Paragraph({
      alignment: AlignmentType.CENTER, keepNext: true,
      spacing: { before: 160, after: 60 },
      children: [new ImageRun({ data: fs.readFileSync(file),
        transformation: { width: displayW, height: displayH }, type: "png" })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 160, line: 280 },
      children: [new TextRun({ text: caption, size: 21, color: "606060", font: FONT })],
    }),
  ];
}

function bibBlock(entries, bibTitle) {
  const out = [h1(bibTitle)];
  entries.forEach((e, idx) => out.push(new Paragraph({
    alignment: AlignmentType.LEFT,
    indent: { left: 480, hanging: 480 },
    spacing: { line: 312, after: 60 },
    children: [new TextRun({ text: "[" + (idx + 1) + "]  " + e, size: 22, color: "000000", font: FONT })],
  })));
  return out;
}

function tableBlock(caption, headers, rows) {
  const n = headers.length;
  const weights = headers.map((h, i) => {
    let mx = String(h).length;
    for (const r of rows) mx = Math.max(mx, String(r[i]).length);
    return Math.max(6, Math.pow(mx, 0.85));
  });
  const total = weights.reduce((a, b) => a + b, 0);
  let pcts = weights.map(w => Math.max(7, w / total * 94));
  const scale = 94 / pcts.reduce((a, b) => a + b, 0);
  pcts = pcts.map(p => p * scale);
  const cell = (text, isHeader, pct) => new TableCell({
    width: { size: pct, type: WidthType.PERCENTAGE },
    shading: isHeader ? { type: ShadingType.CLEAR, fill: "F1F5F9" } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [new Paragraph({
      alignment: AlignmentType.LEFT, spacing: { line: 280 },
      children: [new TextRun({ text: String(text), bold: !!isHeader, size: 21, color: "000000", font: FONT })],
    })],
  });
  return [
    new Paragraph({
      keepNext: true, spacing: { before: 160, after: 60, line: 312 },
      children: [new TextRun({ text: caption, bold: true, size: 21, color: "000000", font: FONT })],
    }),
    new Table({
      width: { size: 100, type: WidthType.PERCENTAGE },
      layout: TableLayoutType.FIXED,
      borders: {
        top: { style: BorderStyle.SINGLE, size: 6, color: "555555" },
        bottom: { style: BorderStyle.SINGLE, size: 6, color: "555555" },
        left: NB, right: NB,
        insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: "CCCCCC" },
        insideVertical: NB,
      },
      rows: [
        new TableRow({ tableHeader: true, cantSplit: true,
          children: headers.map((h, i) => cell(h, true, pcts[i])) }),
        ...rows.map(r => new TableRow({ cantSplit: true,
          children: r.map((c, i) => cell(c, false, pcts[i])) })),
      ],
    }),
    new Paragraph({ spacing: { after: 120 }, children: [] }),
  ];
}

function blocksToChildren(blocks, lang) {
  const ML = M[lang];
  const out = [];
  for (const b of blocks) {
    if (b[0] === "h1") out.push(h1(b[1]));
    else if (b[0] === "p") out.push(new Paragraph({
      alignment: AlignmentType.JUSTIFIED, indent: { firstLine: 480 },
      spacing: { line: 312, after: 80 },
      children: richRuns(b[1], bodyProps(), mathProps()),
    }));
    else if (b[0] === "abs") out.push(new Paragraph({
      alignment: AlignmentType.JUSTIFIED,
      indent: { left: 360, right: 360 },
      spacing: { line: 312, before: 120, after: 160 },
      shading: { type: ShadingType.CLEAR, fill: "F6F4EF" },
      border: { left: { style: BorderStyle.SINGLE, size: 24, color: ACCENT, space: 8 } },
      children: [new TextRun({ text: b[1], italics: true, size: 24, color: "000000", font: FONT })],
    }));
    else if (b[0] === "fig") out.push(...figBlock(b[1], b[2]));
    else if (b[0] === "bib") out.push(...bibBlock(b[1], ML.bib));
    else if (b[0] === "table") out.push(...tableBlock(b[1], b[2], b[3]));
    else if (b[0] === "thm") out.push(...thmBlock(b[1], b[2]));
    else if (b[0] === "proof") out.push(...proofBlock(b[1], lang));
  }
  return out;
}

function pageNumFooter() {
  return new Footer({ children: [new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, color: "606060", font: FONT })],
  })] });
}

function headerStrip(lang) {
  const ML = M[lang];
  return [
    new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { after: 240 },
      children: [new TextRun({ text: ML.label, size: 20, color: ACCENT, font: FONT, bold: true })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 160, line: Math.ceil(17 * 23), lineRule: "atLeast" },
      children: [new TextRun({ text: MAIN.title[lang], bold: true, size: 34, color: "000000", font: FONT })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { after: 120 },
      children: [new TextRun({ text: MAIN.subtitle[lang], size: 24, color: "404040", font: FONT })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { after: 40 },
      children: [new TextRun({ text: META[lang].author, size: 22, color: "000000", font: FONT })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { after: 60 },
      children: [new TextRun({ text: ML.keywords + ": " + MAIN.keywords[lang], size: 18, color: "606060", font: FONT })],
    }),
    new Paragraph({
      border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: ACCENT, space: 4 } },
      spacing: { after: 240 }, children: [],
    }),
  ];
}

async function main() {
  for (const lang of ["ru", "en"]) {
    const ML = M[lang];
    const bodyChildren = [...headerStrip(lang), ...blocksToChildren(MAIN.content[lang], lang)];
    bodyChildren.push(new Paragraph({
      border: { top: { style: BorderStyle.SINGLE, size: 6, color: "999999", space: 6 } },
      spacing: { before: 240 },
      children: [new TextRun({ text: ML.footer, size: 18, color: "606060", font: FONT })],
    }));

    const doc = new Document({
      creator: META.en.author,
      title: "PARTICLE LIMIT — " + MAIN.title[lang],
      description: MAIN.subtitle[lang],
      styles: {
        default: {
          document: { run: { font: FONT, size: 24, color: "000000" },
            paragraph: { spacing: { line: 312 } } },
          heading1: { run: { font: FONT, size: 30, bold: true, color: "000000" },
            paragraph: { spacing: { before: 360, after: 160, line: 312 }, outlineLevel: 0 } },
        },
      },
      sections: [
        { properties: { page: { size: PG.size, margin: { top: 0, bottom: 0, left: 0, right: 0 } } },
          children: buildCoverR5({
            school: ML.school, title: MAIN.title[lang],
            subtitle: MAIN.subtitle[lang], metaEntries: ML.meta, footer: ML.footer,
          }) },
        { properties: {
            type: SectionType.NEXT_PAGE,
            page: { size: PG.size, margin: PG.margin,
              pageNumbers: { start: 1, formatType: NumberFormat.UPPER_ROMAN } } },
          footers: { default: pageNumFooter() },
          children: [
            new Paragraph({
              alignment: AlignmentType.CENTER, spacing: { before: 480, after: 360 },
              children: [new TextRun({ text: ML.tocTitle, bold: true, size: 32, font: FONT })],
            }),
            new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-3" }),
            new Paragraph({
              spacing: { before: 200 },
              children: [new TextRun({ text: ML.tocHint, italics: true, size: 18, color: "888888", font: FONT })],
            }),
          ] },
        { properties: {
            type: SectionType.NEXT_PAGE,
            page: { size: PG.size, margin: PG.margin,
              pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL } } },
          footers: { default: pageNumFooter() },
          children: bodyChildren },
      ],
    });

    const dir = path.join(OUT, lang);
    fs.mkdirSync(dir, { recursive: true });
    const file = path.join(dir, "particle_limit.docx");
    const buf = await Packer.toBuffer(doc);
    fs.writeFileSync(file, buf);
    console.log("  " + lang + " -> particle_limit.docx");
  }
}

main().catch(e => { console.error(e); process.exit(1); });
