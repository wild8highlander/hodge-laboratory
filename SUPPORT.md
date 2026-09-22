# Support

Thank you for using **Hodge Laboratory**. Here is how to get help
quickly and effectively.

## 📚 Documentation first

| Question | Where to look |
|----------|---------------|
| What is the dynamic principle? | [`README.md`](README.md) § The program in 60 seconds |
| How do I run the protocol? | [`README.md`](README.md) § Quick start |
| What do the certificates A–H mean? | [`README.md`](README.md) § Certificates, [`theorems/`](theorems/) |
| How do I publish from Android/Termux? | [`INSTRUCTION.md`](INSTRUCTION.md) |
| Which identities are checked where? | [`verification/README.md`](verification/README.md) |
| How do I cite this work? | [`CITATION.cff`](CITATION.cff), [`README.md`](README.md) § Citation |

## 🐛 Something does not reproduce?

1. Re-run the full protocol:
   ```bash
   python3 laboratory.py --lang en --run all --no-plots
   ```
2. If the verdict is not `ALL PASS`, open a **Reproduction report**
   issue with the failing check names and `reports/hodge_report.json`.
3. A verdict other than `ALL PASS` on unmodified code is treated as
   high priority.

## ❓ Questions and discussions

* [GitHub Discussions](https://github.com/wild8highlander/hodge-laboratory/discussions) —
  general questions about the mathematics, the code, and the monograph.
* Issues with the `question` label — specific, answerable questions.

## ⏱ Response expectations

This is a solo-maintained research repository; there are no SLAs.
Typical response time is a few days. See
[`SECURITY.md`](SECURITY.md) for private security reports.

## ⚖️ Licensing note

The repository is under the individual exclusive license of
Isaev Iskhak Khamzatovich ([`LICENSE`](LICENSE)). Support covers
running, understanding, and verifying the published work; any other
use requires the author's written permission.
