#!/usr/bin/env node
// gen_docx.js — 24 theorem monographs (12 x RU/EN) via docx-js.
// Architecture per document (3 sections):
//   S1 cover (R5 Clean White, margin 0, 16838 wrapper, allNoBorders)
//   S2 front matter: TOC (Roman numerals)  — TableOfContents + refresh hint
//   S3 body (Arabic, restart at 1): header block + theorem blocks
// Math: LaTeX inline $...$ -> TextRuns with Unicode + super/subscript props.
// Post-processing (done by shell afterwards):
//   add_toc_placeholders.py --auto ; footer instrText patch ; postcheck.py

const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  PageBreak, Header, Footer, PageNumber, NumberFormat, SectionType,
  AlignmentType, HeadingLevel, WidthType, BorderStyle, ShadingType,
  TableLayoutType, TableOfContents,
} = require("docx");
const fs = require("fs");
const path = require("path");

const DATA = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "build", "docx_data.json"), "utf8"));
const OUT = path.join(__dirname, "..", "docx");

// ─── shared constants ────────────────────────────────────────────────────
const ACCENT = "8B7E5A";          // gold of the program identity
const INK = "162032";             // deep navy (labels on cover)
const MUTED = "8898A8";
const TBOX_FILL = "F6F4EF";       // theorem box background
const FONT = { ascii: "Times New Roman", eastAsia: "SimSun" };

const NB = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: NB, bottom: NB, left: NB, right: NB };
const allNoBorders = { top: NB, bottom: NB, left: NB, right: NB,
  insideHorizontal: NB, insideVertical: NB };

const META = {
  ru: {
    author: "Исаев Исхак Хамзатович",
    program: "chess-dynamics-lab",
    school: "CHESS-DYNAMICS-LAB",
    tocTitle: "Содержание",
    tocHint: "Примечание: оглавление построено на кодах полей. После редактирования документа щёлкните по оглавлению правой кнопкой мыши и выберите «Обновить поле», чтобы актуализировать номера страниц.",
    keywords: "Ключевые слова",
    meta: (t) => [
      { label: "Автор", value: "Исаев Исхак Хамзатович" },
      { label: "Серия", value: "Монография " + t.id },
      { label: "Программа", value: "chess-dynamics-lab" },
      { label: "Слой", value: (t.subtitle.ru.split("—")[1] || t.subtitle.ru).trim() },
      { label: "Лицензия", value: "Индивидуальная исключительная" },
    ],
    footer: "© 2026 chess-dynamics-lab · Индивидуальная исключительная лицензия",
  },
  en: {
    author: "Isaev Iskhak Khamzatovich",
    program: "chess-dynamics-lab",
    school: "CHESS-DYNAMICS-LAB",
    tocTitle: "Contents",
    tocHint: "Note: this Table of Contents is generated via field codes. To ensure page number accuracy after editing, please right-click the TOC and select \"Update Field.\"",
    keywords: "Keywords",
    meta: (t) => [
      { label: "Author", value: "Isaev Iskhak Khamzatovich" },
      { label: "Series", value: "Theorem monograph " + t.id },
      { label: "Program", value: "chess-dynamics-lab" },
      { label: "Layer", value: (t.subtitle.en.split("—")[1] || t.subtitle.en).trim() },
      { label: "License", value: "Individual exclusive" },
    ],
    footer: "© 2026 chess-dynamics-lab · Individual exclusive license",
  },
};

// ─── LaTeX inline math -> TextRuns ───────────────────────────────────────
const SYM = {
  Delta: "Δ", Theta: "Θ", alpha: "α", beta: "β", gamma: "γ", delta: "δ",
  chi: "χ", mu: "μ", pi: "π", rho: "ρ", sigma: "σ",
  approx: "≈", cdot: "·", cdots: "⋯", circ: "∘", cong: "≅", equiv: "≡",
  ge: "≥", gg: "≫", in: "∈", infty: "∞", lceil: "⌈", ldots: "…", le: "≤",
  lfloor: "⌊", ll: "≪", mapsto: "↦", ne: "≠", oplus: "⊕", pm: "±",
  rceil: "⌉", rfloor: "⌋", times: "×", to: "→", bullet: "•", sum: "∑",
  mid: "|", bmod: " mod ",
};
const UPRIGHT = new Set(["min", "max", "gcd"]);
const BB = { Z: "ℤ", R: "ℝ", N: "ℕ", Q: "ℚ", C: "ℂ" };

function readGroup(s, i) {
  // s[i] must be "{"; returns [content, indexAfter]
  let depth = 0;
  for (let j = i; j < s.length; j++) {
    if (s[j] === "{") depth++;
    else if (s[j] === "}") {
      depth--;
      if (depth === 0) return [s.slice(i + 1, j), j + 1];
    }
  }
  return [s.slice(i + 1), s.length];
}

function texToPlain(tex) {
  // plain string form of a (nested) latex fragment
  let out = "", i = 0;
  while (i < tex.length) {
    const ch = tex[i];
    if (ch === "\\") {
      const m = /^\\([a-zA-Z]+|.)/.exec(tex.slice(i));
      const name = m ? m[1] : " ";
      i += m ? m[0].length : 1;
      if (name in SYM) { out += SYM[name]; continue; }
      if (name === "mathrm" || name === "text" || name === "rm") {
        while (tex[i] === " ") i++;
        if (tex[i] === "{") { const [g, ni] = readGroup(tex, i); out += texToPlain(g); i = ni; }
        continue;
      }
      if (name === "mathbb") {
        while (tex[i] === " ") i++;
        if (tex[i] === "{") { const [g, ni] = readGroup(tex, i); out += (BB[g.trim()] || g); i = ni; }
        continue;
      }
      if (name === "frac" || name === "binom") {
        while (tex[i] === " ") i++;
        const [g1, i1] = readGroup(tex, i);
        let g2 = "", i2 = i1;
        if (tex[i1] === "{") [g2, i2] = readGroup(tex, i1);
        out += name === "frac" ? texToPlain(g1) + "/" + texToPlain(g2)
                               : "C(" + texToPlain(g1) + ", " + texToPlain(g2) + ")";
        i = i2; continue;
      }
      if (name === "pmod") {
        while (tex[i] === " ") i++;
        if (tex[i] === "{") { const [g, ni] = readGroup(tex, i); out += " mod " + texToPlain(g); i = ni; }
        continue;
      }
      if (name === "sqrt") {
        while (tex[i] === " ") i++;
        if (tex[i] === "{") { const [g, ni] = readGroup(tex, i); out += "√(" + texToPlain(g) + ")"; i = ni; }
        continue;
      }
      if (name === "left" || name === "right") continue;
      if (name === "min" || name === "max" || name === "gcd") { out += name; continue; }
      if (",;!? ".includes(name) && name.length === 1) { out += " "; continue; }
      if ("{}".includes(name)) { out += name; continue; }
      out += name;
      continue;
    }
    if (ch === "^" || ch === "_") {
      i++;
      if (tex[i] === "{") { const [g, ni] = readGroup(tex, i); out += texToPlain(g); i = ni; }
      else { out += texToPlain(tex[i]); i++; }
      continue;
    }
    out += ch; i++;
  }
  return out;
}

function texToRuns(tex, props) {
  // props: base TextRun props (size, font...). Math words italic by default.
  const runs = [];
  let buf = "", i = 0;
  const flush = () => { if (buf) { runs.push(new TextRun(Object.assign({}, props, { text: buf }))); buf = ""; } };
  const pushScript = (content, kind) => {
    const t = texToPlain(content);
    if (t) runs.push(new TextRun(Object.assign({}, props, { text: t },
      kind === "^" ? { superScript: true } : { subScript: true })));
  };
  while (i < tex.length) {
    const ch = tex[i];
    if (ch === "\\") {
      const m = /^\\([a-zA-Z]+|.)/.exec(tex.slice(i));
      const name = m ? m[1] : " ";
      i += m ? m[0].length : 1;
      if (name === "mathrm" || name === "text" || name === "rm") {
        flush();
        while (tex[i] === " ") i++;
        if (tex[i] === "{") {
          const [g, ni] = readGroup(tex, i); i = ni;
          runs.push(new TextRun(Object.assign({}, props, { text: texToPlain(g), italics: false })));
        }
        continue;
      }
      if (name === "mathbb") {
        while (tex[i] === " ") i++;
        if (tex[i] === "{") { const [g, ni] = readGroup(tex, i); buf += (BB[g.trim()] || g); i = ni; }
        continue;
      }
      if (name === "frac" || name === "binom") {
        while (tex[i] === " ") i++;
        const [g1, i1] = readGroup(tex, i);
        let g2 = "", i2 = i1;
        if (tex[i1] === "{") [g2, i2] = readGroup(tex, i1);
        buf += name === "frac" ? texToPlain(g1) + "/" + texToPlain(g2)
                               : "C(" + texToPlain(g1) + ", " + texToPlain(g2) + ")";
        i = i2; continue;
      }
      if (name === "pmod") {
        while (tex[i] === " ") i++;
        if (tex[i] === "{") { const [g, ni] = readGroup(tex, i); buf += " mod " + texToPlain(g); i = ni; }
        continue;
      }
      if (name === "sqrt") {
        while (tex[i] === " ") i++;
        if (tex[i] === "{") { const [g, ni] = readGroup(tex, i); buf += "√(" + texToPlain(g) + ")"; i = ni; }
        continue;
      }
      if (name === "left" || name === "right") continue;
      if (name in SYM) { buf += SYM[name]; continue; }
      if (UPRIGHT.has(name)) { flush(); runs.push(new TextRun(Object.assign({}, props, { text: name, italics: false }))); continue; }
      if (name.length === 1 && ",;!".includes(name)) { buf += " "; continue; }
      if (name === "quad" || name === "qquad") { buf += "  "; continue; }
      buf += name;
      continue;
    }
    if (ch === "^" || ch === "_") {
      flush(); i++;
      if (tex[i] === "{") { const [g, ni] = readGroup(tex, i); pushScript(g, ch); i = ni; }
      else { pushScript(tex[i], ch); i++; }
      continue;
    }
    if (ch === "~") { buf += " "; i++; continue; }
    if (ch === "{" || ch === "}") { i++; continue; }   // bare groups
    if (ch === " ") { if (!buf.endsWith(" ")) buf += " "; i++; continue; }
    buf += ch; i++;
  }
  flush();
  return runs;
}

// mixed text + $math$ paragraph -> children array of TextRuns
function richRuns(text, baseProps, mathProps) {
  const children = [];
  let last = 0;
  const re = /\$([^$]+)\$/g;
  let m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) children.push(new TextRun(Object.assign({}, baseProps, { text: text.slice(last, m.index) })));
    children.push(...texToRuns(m[1], mathProps));
    last = m.index + m[0].length;
  }
  if (last < text.length) children.push(new TextRun(Object.assign({}, baseProps, { text: text.slice(last) })));
  return children;
}

module.exports = { DATA, OUT, META, ACCENT, INK, MUTED, TBOX_FILL, FONT, NB, noBorders,
  allNoBorders, texToRuns, texToPlain, richRuns };
