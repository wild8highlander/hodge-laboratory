---
name: Reproduction report
about: Report the result of reproducing the V1–V9 protocol on your machine
title: '[REPRO] '
labels: verification
---

**Environment**

- OS / platform:
- Python version:
- mpmath version:
- CPU architecture (for the C/Fortran/Rust backends):

**Command**

```
python3 laboratory.py --run all
```

**Verdict**

- [ ] ALL PASS
- [ ] FAILURES PRESENT

**Details**

Failing check names and residuals (from the console or
`reports/hodge_report.json`). For `ALL PASS` reports, please include
the total runtime and the protocol duration printed at the end —
timing data helps the documentation.

**Backends run (optional)**

| Stack   | Verdict (exit code) |
|---------|---------------------|
| C       | 0 / 1               |
| Rust    | 0 / 1               |
| Julia   | 0 / 1               |
| Fortran | 0 / 1               |
| Lean 4  | 0 / 1               |
