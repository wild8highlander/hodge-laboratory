# Rust kernel (polyglot layer)

<div align="center">

[⬆ VER-HODGE](../../README.md) · [⬆ polyglot/](../../README.md#layout-mirrors-hodge-laboratory)

</div>

The propagation protocol, one picture:

```mermaid
flowchart LR
    B["results/baseline_v15_v18.json<br/>frozen expected values"] --> CK["polyglot/c<br/>the C kernel — bit-identical<br/>(v1.8 cross-check)"]
    CK -.->|"next wave · v1.9 slot"| RS["polyglot/rust<br/>the Rust port of the exact-layer<br/>integer kernels"]
```

The Rust port of the exact-layer integer kernels (the poly kernels
and the SNF 2x2 repair) is the v1.9 propagation slot: the C kernel
(polyglot/c) carries the bit-identical expected values for v1.8 and
the Rust crate lands with the next wave per the propagation protocol
(docs/ROADMAP.md, §7.6).  The expected values are frozen in
results/baseline_v15_v18.json.
