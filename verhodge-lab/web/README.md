# Web mirror

<div align="center">

[⬆ VER-HODGE](../README.md) · [⬆ Hodge Laboratory](../../README.md) · [🧪 Hodge Laboratory Web (live)](https://wild8highlander.github.io/hodge-laboratory-web/) · [♞ Hodge Flow Chess (live)](https://wild8highlander.github.io/hodge-flow-chess/)

</div>

The JS display mirror is the v1.9 propagation slot (the constants
are frozen in results/baseline_v15_v18.json).  v1.8 ships the C
kernel cross-check (polyglot/c) per the propagation protocol.

```mermaid
flowchart LR
    B["results/baseline_v15_v18.json<br/>the frozen constants"] --> CK["polyglot/c<br/>the C kernel cross-check<br/>(v1.8, shipped)"]
    B -.->|"v1.9 propagation slot"| WEB["web/<br/>the JS display mirror<br/>(the constants stay frozen)"]
    CK -.-> WEB
```
