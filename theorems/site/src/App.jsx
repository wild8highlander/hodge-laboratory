import React from 'react';
import Hero from './components/Hero.jsx';
import Explorer from './components/Explorer.jsx';
import Dashboard from './components/Dashboard.jsx';
import TheoremGrid from './components/TheoremGrid.jsx';
import Playground from './components/Playground.jsx';
import { DATA } from './data/theorems.js';

export default function App() {
  return (
    <div className="app">
      <nav className="nav">
        <span className="brand">
          <img src="/favicon.svg" alt="Hodge diamond logo" />
          HODGE&nbsp;LAB·THEOREMS
        </span>
        <span className="links">
          <a href="#explorer">Explorer</a>
          <a href="#dashboard">Dashboard</a>
          <a href="#theorems">Monographs</a>
          <a href="#playground">Playground</a>
          <a href={DATA.meta.repo} target="_blank" rel="noreferrer">GitHub ↗</a>
        </span>
      </nav>

      <Hero />

      <section id="explorer" className="wrap">
        <div className="sec-head">
          <span className="kicker">Explorer</span>
          <h2>The dependency graph</h2>
        </div>
        <p className="sec-sub">
          All 22 monographs and 24 logical cross-references as a force-directed graph.
          Node colors mark the six parts of the collection — drag, zoom, and click any
          theorem for its formula and the direct links to the RU/EN PDF monographs.
        </p>
        <Explorer />
      </section>

      <section id="dashboard" className="wrap">
        <div className="sec-head">
          <span className="kicker">Dashboard</span>
          <h2>The numbers of the program</h2>
        </div>
        <p className="sec-sub">
          The genus ladder of the stands, the Smith normal form spectra of every rung and
          the protocol residuals against their contract thresholds — the integer spine of
          the program as three live charts.
        </p>
        <Dashboard />
      </section>

      <section id="theorems" className="wrap">
        <div className="sec-head">
          <span className="kicker">Monographs</span>
          <h2>The 22 theorem cards</h2>
        </div>
        <p className="sec-sub">
          Filter by part or search by name, invariant or number — every card carries the
          Bauhaus icon, the headline formula and the links to the complete standalone
          monograph in both languages.
        </p>
        <TheoremGrid />
      </section>

      <section id="playground" className="wrap">
        <div className="sec-head">
          <span className="kicker">Playground</span>
          <h2>Live parameters of the pipeline</h2>
        </div>
        <p className="sec-sub">
          The dynamic principle is a function of one integer triple. Move N, a and b and
          watch the genus, the spin phase δ = π/N, the braking γ = δ⁴ and the closed
          period Ω(a,b) respond — the same identities the five-language verification
          stack checks bit-for-bit.
        </p>
        <Playground />
      </section>

      <footer>
        <div className="wrap fgrid">
          <span>
            {DATA.meta.title} · {DATA.meta.tagline}
          </span>
          <span>
            © 2026 {DATA.meta.author} · individual exclusive license ·
            {' '}<a href={DATA.meta.repo} target="_blank" rel="noreferrer">hodge-laboratory</a>
          </span>
        </div>
      </footer>
    </div>
  );
}
