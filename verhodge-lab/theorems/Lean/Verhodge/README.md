# The Lean 4 layer (WP4)

<div align="center">

[⬆ VER-HODGE](../../../README.md) · [⬆ Hodge Laboratory](../../../../README.md) · [⬆ Lean panel of hodge-laboratory](../../../../verification/README.md)

</div>

Machine-checked integer facts and the input-grammar specification.
No axioms, no Mathlib (kernel-only `decide`), matching the
hodge-laboratory discipline.

```mermaid
flowchart LR
    G["Grammar.lean<br/>HODGE-INPUT v1 as inductive types"] -->|"level3_never_certified"| C["Census.lean<br/>frozen identities<br/>genus 7/9/11/15/30"]
    C --> S["SnfSpec.lean<br/>the certificate-H tuple<br/>product identities"]
```

- `Verhodge/Grammar.lean` — the HODGE-INPUT v1 grammar as inductive
  types + the asymmetric contract (level-3 never certified).
- `Verhodge/Census.lean` — the frozen census identities
  (genus 7/9/11/15/30).
- `Verhodge/SnfSpec.lean` — the SNF spec facts (the certificate-H
  tuple, the product identities).

Check: `lake build` (pinned toolchain in `lean-toolchain`).
