import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { THEOREMS, EDGES, PARTS } from '../data/theorems.js';
import Formula from './Formula.jsx';

/**
 * Explorer — D3 force-directed dependency graph of the 22 theorems.
 * Colors = the six parts of the collection; click a node for the detail panel.
 */
export default function Explorer() {
  const svgRef = useRef(null);
  const [sel, setSel] = useState(THEOREMS[0]);

  useEffect(() => {
    const svg = d3.select(svgRef.current);
    const box = svgRef.current.parentElement.getBoundingClientRect();
    const W = Math.max(box.width, 320), H = 560;

    svg.attr('viewBox', `0 0 ${W} ${H}`);
    svg.selectAll('*').remove();

    const nodes = THEOREMS.map((t) => ({
      ...t, id: t.id,
      x: W / 2 + (Math.random() - 0.5) * 220,
      y: H / 2 + (Math.random() - 0.5) * 180,
    }));
    const links = EDGES.map((e) => ({ ...e }));

    const sim = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id((d) => d.id).distance(88).strength(0.32))
      .force('charge', d3.forceManyBody().strength(-320))
      .force('center', d3.forceCenter(W / 2, H / 2))
      .force('collide', d3.forceCollide(34));

    const g = svg.append('g');

    const link = g.append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('class', 'link');

    const node = g.append('g')
      .selectAll('g')
      .data(nodes)
      .join('g')
      .attr('class', 'node')
      .style('cursor', 'pointer')
      .on('click', (event, d) => { setSel(d); event.stopPropagation(); })
      .call(d3.drag()
        .on('start', (event, d) => { if (!event.active) sim.alphaTarget(0.25).restart(); d.fx = d.x; d.fy = d.y; })
        .on('drag', (event, d) => { d.fx = event.x; d.fy = event.y; })
        .on('end', (event, d) => { if (!event.active) sim.alphaTarget(0); d.fx = null; d.fy = null; }));

    node.append('circle')
      .attr('r', (d) => (d.num <= 6 ? 17 : 14))
      .attr('fill', (d) => d.partColor)
      .attr('stroke', 'rgba(15,23,42,0.9)')
      .attr('stroke-width', 2.5);

    node.append('text')
      .text((d) => `T${String(d.num).padStart(2, '0')}`)
      .attr('text-anchor', 'middle')
      .attr('dy', 3.5)
      .attr('font-size', 9.5)
      .attr('font-weight', 700)
      .attr('fill', '#0b1120')
      .attr('pointer-events', 'none')
      .style('user-select', 'none');

    node.append('text')
      .text((d) => d.short)
      .attr('text-anchor', 'middle')
      .attr('dy', 31)
      .attr('font-size', 10.5)
      .attr('fill', '#94a3b8')
      .attr('pointer-events', 'none')
      .style('user-select', 'none');

    svg.on('click', () => setSel(null));

    // zoom
    svg.call(d3.zoom().scaleExtent([0.4, 2.6])
      .on('zoom', (event) => g.attr('transform', event.transform)));

    sim.on('tick', () => {
      link
        .attr('x1', (d) => d.source.x).attr('y1', (d) => d.source.y)
        .attr('x2', (d) => d.target.x).attr('y2', (d) => d.target.y);
      node.attr('transform', (d) => `translate(${d.x},${d.y})`);
    });

    return () => { sim.stop(); };
  }, []);

  return (
    <div className="explorer">
      <div className="glass graph-box">
        <svg ref={svgRef} role="img" aria-label="Dependency graph of the 22 theorem monographs" />
        <div className="glass legend">
          {PARTS.map((p) => (
            <span className="chip" key={p.id}>
              <span className="dot" style={{ background: p.color }} />
              {p.label} · {p.title.length > 34 ? p.title.slice(0, 32) + '…' : p.title}
            </span>
          ))}
        </div>
      </div>
      <div className="glass detail">
        {sel ? (
          <div>
            <div className="tag" style={{ color: sel.partColor }}>{sel.partLabel} · {sel.partTitle}</div>
            <h3>T{String(sel.num).padStart(2, '0')} — {sel.name}</h3>
            <div className="formula" style={{ padding: '12px 14px', borderRadius: 12, background: 'rgba(2,6,23,0.55)', border: '1px solid var(--border)', margin: '10px 0' }}>
              <Formula display tex={sel.katex} />
            </div>
            <p className="result">{sel.result}</p>
            <div style={{ color: 'var(--text-faint)', fontSize: 12.5, marginTop: 12 }}>
              Laboratory: <b style={{ color: 'var(--text-dim)' }}>{sel.lab}</b><br />
              Lean block: <code style={{ color: 'var(--violet)' }}>{sel.lean}</code>
            </div>
            <div className="row">
              <a className="btn" href={sel.links.folder} target="_blank" rel="noreferrer">📂 Monograph folder</a>
              <a className="btn violet" href={sel.links.pdfEn} target="_blank" rel="noreferrer">📕 EN PDF</a>
              <a className="btn violet" href={sel.links.pdfRu} target="_blank" rel="noreferrer">📗 RU PDF</a>
            </div>
          </div>
        ) : (
          <div style={{ color: 'var(--text-dim)' }}>
            <h3 style={{ marginTop: 0 }}>Click a node</h3>
            <p className="result">
              The graph mirrors the logical reading path of the collection: the foundation chain
              T01→T02→T03→T04, the calibration stands, the certificate arch B–H, the cubic rungs
              N=7/9, the exact layer, the quintic rung and the SNF engine that closes the system.
              Every monograph remains self-sufficient — the edges are navigation, not dependency.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
