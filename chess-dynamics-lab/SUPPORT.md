# Support — chess-dynamics-lab

## Where to start

1. **The protocol failed?** Run `python3 dynamics.py --run Ck` for the failing check
   and read the `details` dictionary it prints — every check explains itself.
2. **First time here?** Read [INSTRUCTION.md](INSTRUCTION.md) — it covers Termux,
   Linux and macOS end to end, including the one-command GitHub publication.
3. **Want the theory?** Open `monograph/pdf/ru/main_monograph.pdf` (or the EN
   edition): chapter 2 explains the board algebra, chapter 12 explains the protocol,
   Appendix B is the reproduction guide. Each theorem has its own monograph.

## Common questions

**Q: perft(5) is slow on my phone.**
A: Use `python3 dynamics.py --run C5` (depth 4) for daily verification; `--deep`
(depth 5) is a one-time certificate, minutes on a phone, seconds on a laptop.

**Q: `gh auth login` fails in Termux.**
A: Use the token route: `export GH_TOKEN=<classic token with repo scope>` — see
INSTRUCTION.md, Part 1, Step 6, Option B.

**Q: The Rust/Go/Julia/Java backend prints FAIL.**
A: Those backends are verified in CI. Run `bash polyglot/run_all.sh` locally, copy the
`[FAIL] Cn ...` line and open an issue with your platform details.

**Q: How do I cite the program?**
A: See [CITATION.cff](CITATION.cff) and README §15.

**Q: May I reuse the theorems/model in my own project?**
A: No — the license is individual and exclusive. See [LICENSE](LICENSE).

## Contact

- Bug reports and reproduction logs: GitHub Issues of the repository.
- Licensing: only via direct contact with the copyright holder
  Isaev Iskhak Khamzatovich (see LICENSE).
- Documentation: [README.md](README.md) · [INSTRUCTION.md](INSTRUCTION.md) ·
  [CONTRIBUTING.md](CONTRIBUTING.md)
