import React, { useMemo, useState } from 'react';
import { THEOREMS, PARTS } from '../data/theorems.js';
import Formula from './Formula.jsx';

/**
 * Theorems — the card gallery with part filters, live search, KaTeX formulas
 * and direct links to the monograph folders and the RU/EN PDFs.
 */
export default function TheoremGrid() {
  const [part, setPart] = useState(0);          // 0 = all
  const [q, setQ] = useState('');

  const cards = useMemo(() => {
    const needle = q.trim().toLowerCase();
    return THEOREMS.filter((t) => (part === 0 || t.part === part)).filter((t) =>
      !needle ||
      t.name.toLowerCase().includes(needle) ||
      t.short.toLowerCase().includes(needle) ||
      t.result.toLowerCase().includes(needle) ||
      `t${String(t.num).padStart(2, '0')}`.includes(needle));
  }, [part, q]);

  return (
    <div>
      <div className="filters">
        <input type="search" placeholder="Search: genus, Klein, SNF, t16 …"
               value={q} onChange={(e) => setQ(e.target.value)} />
        <span className={part === 0 ? 'fchip on' : 'fchip'}
              style={part === 0 ? { background: '#e2e8f0' } : {}}
              onClick={() => setPart(0)}>All 22</span>
        {PARTS.map((p) => (
          <span key={p.id} className={part === p.id ? 'fchip on' : 'fchip'}
                style={part === p.id ? { background: p.color, borderColor: p.color } : {}}
                onClick={() => setPart(p.id)}>
            {p.label} · {p.title.split('(')[0].trim()}
          </span>
        ))}
      </div>

      {cards.length === 0 && (
        <p style={{ color: 'var(--text-dim)' }}>No monograph matches “{q}”.</p>
      )}

      <div className="cards">
        {cards.map((t) => (
          <div className="glass tcard" key={t.id}>
            <div className="head">
              <img className="ticon" src={t.icon} alt={`T${String(t.num).padStart(2, '0')} icon`} />
              <div>
                <div className="num" style={{ color: t.partColor }}>
                  {t.partLabel.toUpperCase()} · T{String(t.num).padStart(2, '0')} / 22
                </div>
                <div className="name">{t.name}</div>
              </div>
            </div>
            <div className="formula"><Formula display tex={t.katex} /></div>
            <p className="result">{t.result}</p>
            <div className="links">
              <a href={t.links.folder} target="_blank" rel="noreferrer">📂 folder</a>
              <a href={t.links.pdfEn} target="_blank" rel="noreferrer">📕 EN PDF</a>
              <a href={t.links.pdfRu} target="_blank" rel="noreferrer">📗 RU PDF</a>
              <a href={t.cover} target="_blank" rel="noreferrer">🖼 cover</a>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
