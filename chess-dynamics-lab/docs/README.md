# docs/ — the GitHub Pages landing

A single static page (`index.html` + `style.css`) summarizing the program for the
front page of `https://wild8highlander.github.io/chess-dynamics-lab/`.

## What is on it

- the hero: *Chess Particle Dynamics — a certifiable laboratory*, with the verdict
  line `ALL CHECKS PASSED · C1–C9 · 10/10 polyglot`;
- the three-layer cards **K3 / TORUS / KLEIN** with the frozen formulas
  (ΣΘ(c) = Σa(π); E = [M(w)−M(b)] + μ[m(w)−m(b)], μ = 0.1; t\* = lcm(·), γ = π⁴/256);
- the table of the twelve theorem monographs T01–T12 with their key constants and
  protocol checks, plus the MAIN row;
- the reproduction block: Linux/macOS and Termux commands;
- the footer with the authorship and the individual exclusive license;
- full RU/EN interface (a language pill, `localStorage` persistence).

## Deployment

The Pages workflow (`.github/workflows/pages.yml`) assembles the site: the landing at
the root and the web laboratory under `/lab/`:

```text
https://wild8highlander.github.io/chess-dynamics-lab/           -> docs/index.html
https://wild8highlander.github.io/chess-dynamics-lab/lab/       -> web/chess-particles/index.html
```

Enable *Settings → Pages → Source: GitHub Actions* once; the workflow deploys on
every push that touches `docs/**` or `web/**`.

## Design

The page shares the visual system of `web/chess-particles` (dark navy `#0A1120`, gold
`#C9A96A`, violet, teal; Playfair Display / Inter / JetBrains Mono; aurora blobs) —
the two pages read as one product.
