#!/usr/bin/env node
// gen_docx.js — main assembly: R5 cover + TOC section + body section.

const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  PageBreak, Footer, PageNumber, NumberFormat, SectionType,
  AlignmentType, HeadingLevel, WidthType, BorderStyle, ShadingType,
  TableLayoutType, TableOfContents,
} = require("docx");
const fs = require("fs");
const path = require("path");
const L = require("./docx_lib.js");

const { DATA, OUT, META, ACCENT, INK, TBOX_FILL, FONT, NB, noBorders,
  allNoBorders, texToRuns, richRuns } = L;

const PG = { size: { width: 11906, height: 16838 }, margin: { top: 1440, bottom: 1440, left: 1701, right: 1417 } };

// ─── title layout (width-aware for Latin/Cyrillic) ───────────────────────
function estimateTextWidth(text, pt) {
  let w = 0;
  for (const ch of text) {
    const code = ch.codePointAt(0);
    const isCJK = (code >= 0x4E00 && code <= 0x9FFF) || (code >= 0x3000 && code <= 0x303F) ||
      (code >= 0xFF00 && code <= 0xFFEF);
    w += isCJK ? pt * 20 : pt * 11;
  }
  return w;
}

function splitByWords(title, maxWidthTw, pt) {
  const words = title.split(/\s+/);
  const lines = [];
  let cur = "";
  for (const wd of words) {
    const cand = cur ? cur + " " + wd : wd;
    if (estimateTextWidth(cand, pt) <= maxWidthTw || !cur) cur = cand;
    else { lines.push(cur); cur = wd; }
  }
  if (cur) lines.push(cur);
  // orphan prevention: last line with 1 short word merges back if possible
  if (lines.length >= 2 && lines[lines.length - 1].length <= 3) {
    const lastWord = lines.pop();
    lines[lines.length - 1] += " " + lastWord;
  }
  return lines;
}

function calcTitleLayoutMixed(title, maxWidthTw, preferredPt = 36, minPt = 24) {
  let pt = preferredPt, lines;
  while (pt >= minPt) {
    lines = splitByWords(title, maxWidthTw, pt);
    if (lines.length <= 3) break;
    pt -= 2;
  }
  if (!lines || lines.length > 3) { pt = minPt; lines = splitByWords(title, maxWidthTw, pt); }
  return { titlePt: pt, titleLines: lines };
}

// ─── R5 cover ────────────────────────────────────────────────────────────
function calcR5MetaLayout(metaEntries, fontPt = 12) {
  const maxLabelLen = Math.max(...metaEntries.map(e => [...e.label].length));
  const labelNeedTw = (maxLabelLen + 2) * fontPt * 11;   // latin/cyrillic width
  const valueNeedTw = 5000;
  const totalNeedTw = labelNeedTw + valueNeedTw;
  const tablePct = Math.min(75, Math.max(55, Math.ceil(totalNeedTw / 11906 * 100)));
  const rawLabelPct = Math.ceil(labelNeedTw / (tablePct / 100 * 11906) * 100);
  return { tablePct, labelPct: Math.max(25, Math.min(45, rawLabelPct)) };
}

function buildR5MetaTable(metaEntries) {
  const { tablePct, labelPct } = calcR5MetaLayout(metaEntries);
  const valuePct = 100 - labelPct;
  const bottomBorder = { style: BorderStyle.SINGLE, size: 4, color: "000000" };
  const rows = metaEntries.map(entry => new TableRow({
    cantSplit: true,
    children: [
      new TableCell({
        width: { size: labelPct, type: WidthType.PERCENTAGE },
        borders: noBorders,
        margins: { left: 0, right: 0 },
        children: [new Paragraph({
          alignment: AlignmentType.LEFT,
          spacing: { before: 60, after: 60, line: 400 },
          children: [new TextRun({ text: entry.label + ":", size: 24, font: FONT })],
        })],
      }),
      new TableCell({
        width: { size: valuePct, type: WidthType.PERCENTAGE },
        borders: { top: NB, left: NB, right: NB, bottom: bottomBorder },
        margins: { left: 80, right: 0 },
        children: [new Paragraph({
          alignment: AlignmentType.LEFT,
          spacing: { before: 60, after: 60, line: 400 },
          children: [new TextRun({ text: entry.value, size: 24, font: FONT })],
        })],
      }),
    ],
  }));
  return new Table({
    width: { size: tablePct, type: WidthType.PERCENTAGE },
    alignment: AlignmentType.CENTER,
    layout: TableLayoutType.FIXED,
    borders: allNoBorders,
    rows,
  });
}

function buildCoverR5(config) {
  const PAGE_H = 16838, SAFETY = 1200;
  const safeH = PAGE_H - SAFETY;
  const simMarginLR = 1701, simMarginT = 1200;
  const contentW = 11906 - simMarginLR * 2;

  const { titlePt, titleLines } = calcTitleLayoutMixed(config.title, contentW, 30, 22);
  const titleSize = titlePt * 2;

  const metaEntries = config.metaEntries || [];
  const schoolNameH = config.schoolName ? (18 * 23 + 400) : 0;
  const titleTotalH = titleLines.length * (titlePt * 23 + 200);
  const subtitleH = config.subtitle ? (13 * 23 + 600) : 0;
  const metaRowH = 520;
  const metaTableH = metaEntries.length * metaRowH;
  const footerH = config.footer ? (12 * 23 + 200) : 0;
  const spacerParas = 3 * 350;
  const fixedH = schoolNameH + titleTotalH + subtitleH + metaTableH + footerH + spacerParas;
  const remaining = Math.max(safeH - fixedH, 600);

  const topSpacing = Math.min(Math.floor(remaining * 0.28) + simMarginT, 4200);
  const midSpacing = Math.min(Math.floor((remaining - simMarginT) * 0.18), 2000);
  const bottomSpacing = Math.max(Math.min(remaining - topSpacing + simMarginT - midSpacing, 5500), 400);

  const children = [];
  children.push(new Paragraph({ spacing: { before: topSpacing } }));

  if (config.schoolName) {
    children.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 400, line: Math.ceil(18 * 23), lineRule: "atLeast" },
      children: [new TextRun({ text: config.schoolName, size: 36, characterSpacing: 60, color: INK,
        font: FONT })],
    }));
  }

  for (let i = 0; i < titleLines.length; i++) {
    children.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: i < titleLines.length - 1 ? 120 : 300, line: Math.ceil(titlePt * 23), lineRule: "atLeast" },
      children: [new TextRun({ text: titleLines[i], size: titleSize, bold: true, color: "000000",
        font: FONT })],
    }));
  }

  if (config.subtitle) {
    children.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 200, line: Math.ceil(13 * 23), lineRule: "atLeast" },
      children: [new TextRun({ text: config.subtitle, size: 26, color: "404040", font: FONT })],
    }));
  }

  children.push(new Paragraph({ spacing: { before: midSpacing } }));
  if (metaEntries.length > 0) children.push(buildR5MetaTable(metaEntries));
  children.push(new Paragraph({ spacing: { before: bottomSpacing } }));

  if (config.footer) {
    children.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({ text: config.footer, size: 20, color: "404040", font: FONT })],
    }));
  }

  return [new Table({
    width: { size: 100, type: WidthType.PERCENTAGE },
    layout: TableLayoutType.FIXED,
    borders: allNoBorders,
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

// ─── body blocks ─────────────────────────────────────────────────────────
function bodyProps() { return { size: 24, color: "000000", font: FONT }; }
function mathProps() { return { size: 24, color: "000000", font: FONT, italics: true }; }

function h1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 160, line: 312 },
    children: [new TextRun({ text, bold: true, size: 30, color: "000000", font: FONT })],
  });
}

function bodyPara(text) {
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    indent: { firstLine: 480 },
    spacing: { line: 312, after: 80 },
    children: richRuns(text, bodyProps(), mathProps()),
  });
}

function theoremPara(label, body) {
  const children = [
    ...richRuns(label, { size: 24, color: "000000", font: FONT, bold: true }, mathProps()),
    new TextRun({ text: " ", size: 24 }),
    ...richRuns(body, bodyProps(), mathProps()),
  ];
  return new Paragraph({
    alignment: AlignmentType.JUSTIFIED,
    spacing: { line: 312, before: 120, after: 120 },
    indent: { left: 240, right: 120 },
    shading: { type: ShadingType.CLEAR, fill: TBOX_FILL },
    border: { left: { style: BorderStyle.SINGLE, size: 24, color: ACCENT, space: 8 } },
    children,
  });
}

function tableBlock(caption, headers, rows) {
  const n = headers.length;
  // content-weighted column percentages
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
      alignment: AlignmentType.LEFT,
      spacing: { line: 280 },
      children: [new TextRun({ text: String(text), bold: !!isHeader, size: 21, color: "000000", font: FONT })],
    })],
  });

  const out = [];
  out.push(new Paragraph({
    keepNext: true,
    spacing: { before: 160, after: 60, line: 312 },
    children: [new TextRun({ text: caption, bold: true, size: 21, color: "000000", font: FONT })],
  }));
  out.push(new Table({
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
        children: r.map((c, i) => cell(c === "—" ? "--" : c, false, pcts[i])) })),
    ],
  }));
  out.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
  return out;
}

function blocksToChildren(blocks) {
  const out = [];
  for (const b of blocks) {
    if (b[0] === "h1") out.push(h1(b[1]));
    else if (b[0] === "p") out.push(bodyPara(b[1]));
    else if (b[0] === "f") {
      out.push(new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { line: 312, before: 80, after: 80 },
        children: texToRuns(b[1], mathProps()),
      }));
    } else if (b[0] === "thm") {
      out.push(theoremPara(b[1], b[2]));
    } else if (b[0] === "table") {
      out.push(...tableBlock(b[1], b[2], b[3]));
    }
  }
  return out;
}

// ─── document assembly ───────────────────────────────────────────────────
function pageNumFooter() {
  return new Footer({ children: [new Paragraph({
    alignment: AlignmentType.CENTER,
    children: [new TextRun({ children: [PageNumber.CURRENT], size: 18, color: "606060", font: FONT })],
  })] });
}

function headerStrip(t, lang) {
  const M = META[lang];
  const children = [];
  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 240 },
    children: [new TextRun({
      text: (lang === "ru" ? "МОНОГРАФИЯ " : "THEOREM MONOGRAPH ") + t.id +
        (lang === "ru" ? " · ПРОГРАММА " : " · ") + "CHESS-DYNAMICS-LAB",
      size: 20, color: ACCENT, font: FONT, bold: true })],
  }));
  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 160, line: Math.ceil(17 * 23), lineRule: "atLeast" },
    children: [new TextRun({ text: t.title[lang], bold: true, size: 34, color: "000000", font: FONT })],
  }));
  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 120 },
    children: [new TextRun({ text: t.subtitle[lang], size: 24, color: "404040", font: FONT })],
  }));
  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 40 },
    children: [new TextRun({ text: M.author, size: 22, color: "000000", font: FONT })],
  }));
  children.push(new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 60 },
    children: [new TextRun({ text: M.keywords + ": " + t.keywords[lang], size: 18, color: "606060", font: FONT })],
  }));
  children.push(new Paragraph({
    border: { bottom: { style: BorderStyle.SINGLE, size: 8, color: ACCENT, space: 4 } },
    spacing: { after: 240 },
    children: [],
  }));
  return children;
}

function buildDoc(t, lang) {
  const M = META[lang];
  const bodyChildren = [...headerStrip(t, lang), ...blocksToChildren(t.content[lang])];
  bodyChildren.push(new Paragraph({
    border: { top: { style: BorderStyle.SINGLE, size: 6, color: "999999", space: 6 } },
    spacing: { before: 240 },
    children: [new TextRun({ text: M.footer, size: 18, color: "606060", font: FONT })],
  }));

  return new Document({
    creator: META.en.author,
    title: t.id + " — " + t.title[lang],
    description: t.subtitle[lang],
    styles: {
      default: {
        document: {
          run: { font: FONT, size: 24, color: "000000" },
          paragraph: { spacing: { line: 312 } },
        },
        heading1: {
          run: { font: FONT, size: 30, bold: true, color: "000000" },
          paragraph: { spacing: { before: 360, after: 160, line: 312 }, outlineLevel: 0 },
        },
      },
    },
    sections: [
      { // S1 cover — margin 0, no page numbers, no footer
        properties: { page: { size: PG.size, margin: { top: 0, bottom: 0, left: 0, right: 0 } } },
        children: buildCoverR5({
          schoolName: M.school,
          title: t.title[lang],
          subtitle: t.subtitle[lang],
          metaEntries: M.meta(t),
          footer: M.footer,
        }),
      },
      { // S2 front matter — TOC, Roman numerals
        properties: {
          type: SectionType.NEXT_PAGE,
          page: { size: PG.size, margin: PG.margin,
            pageNumbers: { start: 1, formatType: NumberFormat.UPPER_ROMAN } },
        },
        footers: { default: pageNumFooter() },
        children: [
          new Paragraph({
            alignment: AlignmentType.CENTER,
            spacing: { before: 480, after: 360 },
            children: [new TextRun({ text: M.tocTitle, bold: true, size: 32, font: FONT })],
          }),
          new TableOfContents("Table of Contents", { hyperlink: true, headingStyleRange: "1-3" }),
          new Paragraph({
            spacing: { before: 200 },
            children: [new TextRun({ text: M.tocHint, italics: true, size: 18, color: "888888", font: FONT })],
          }),
        ],
      },
      { // S3 body — Arabic, restart at 1
        properties: {
          type: SectionType.NEXT_PAGE,
          page: { size: PG.size, margin: PG.margin,
            pageNumbers: { start: 1, formatType: NumberFormat.DECIMAL } },
        },
        footers: { default: pageNumFooter() },
        children: bodyChildren,
      },
    ],
  });
}

async function main() {
  const only = process.argv.slice(2);
  for (const t of DATA.theorems) {
    for (const lang of ["ru", "en"]) {
      if (only.length && !only.includes(t.id) && !only.includes(t.slug)) continue;
      const dir = path.join(OUT, lang);
      fs.mkdirSync(dir, { recursive: true });
      const file = path.join(dir, t.id.toLowerCase() + "_" + t.slug + ".docx");
      const doc = buildDoc(t, lang);
      const buf = await Packer.toBuffer(doc);
      fs.writeFileSync(file, buf);
      console.log("  " + lang + "/" + t.id + " -> " + path.basename(file));
    }
  }
}

main().catch(e => { console.error(e); process.exit(1); });
