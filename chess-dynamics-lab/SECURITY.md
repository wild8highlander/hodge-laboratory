# Security Policy — chess-dynamics-lab

## Scope

The laboratory is an offline computational program. It contains **no network code, no
telemetry, no dynamic execution of external input**:

- `dynamics.py`, `engine/*`, `tests/*` — pure Python standard library;
- the polyglot cores — pure local computation (C, Rust, Go, Julia, JavaScript, Java);
- `web/chess-particles/` — a static page; the only storage it touches is
  `localStorage` (the UI language);
- the monograph generators (`monograph/src/`) are build-time tools; their outputs
  (PDF/DOCX) are static documents.

## Supported versions

| Version | Supported |
|---|---|
| 1.0.x | current |

## Reporting

If you believe you found a security-relevant issue (e.g. a parser that could be
crashed by malformed FEN input, a path-traversal issue in a script, or an injection
vector in the web laboratory), please report it **privately** through the contact
channel of the copyright holder (see LICENSE) rather than opening a public issue.

Please include: the affected file/line, the exact input, the observed behaviour, and
the platform.

## Safe-use notes

- The `scripts/termux_push.sh` script sends data **only** to `github.com` using the
  credentials you provide (`gh` session or `GH_TOKEN`). Read it before running;
  never share your token.
- The laboratory never executes content from `results/*.json.gz`; those files are
  data, loaded with the standard `json`/`gzip` modules.
- FEN strings from users are parsed by `Position.set_fen`, which validates and never
  evaluates code; still, do not feed untrusted data to long-running analyses if you
  do not control the input.
