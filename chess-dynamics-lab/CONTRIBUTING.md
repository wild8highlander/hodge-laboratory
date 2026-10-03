# Contributing to chess-dynamics-lab

Thank you for your interest. This program is distributed under an
**individual exclusive license** (see [LICENSE](LICENSE)): all rights belong to
Isaev Iskhak Khamzatovich, and any use of the material — including modifications and
derivatives — requires the author's direct written permission.

That also shapes this policy:

## What contributions are possible

1. **Issue reports** — always welcome. If a protocol check fails on your machine
   (any of C1–C9, or a polyglot backend), open an issue with:
   - the platform (OS, Python version, phone model for Termux);
   - the full output of `python3 dynamics.py --report` (and `--run Ck` for the
     failing check);
   - the backend output (`bash polyglot/run_all.sh`) if the polyglot is involved.
2. **Errata and commentary on the monographs** — the documents carry frozen constants;
   a mismatch between a document, the baseline JSON and the live protocol is a bug by
   definition (whichever side is wrong). Reports of typos and translation issues are
   welcome.
3. **Reproduction notes** — logs of successful runs on unusual platforms (aarch64,
   BSD, e-readers…) are valuable and may be included in the README verification table
   with the reporter's consent.

## What is not accepted

- Pull requests with code changes: the program is maintained by the author; proposals
  should be expressed as issues describing the *problem*, not the patch.
- Any derivative implementations of the theorems, the protocol or the particle model
  (prohibited by the license).

## Development principles (for the author and for reviewers)

1. A theorem without an executable check does not count as proved.
2. A check that cannot FAIL honestly does not count as a check.
3. A fix never edits the baseline or the frozen constants; it edits the implementation.
4. Every language of the polyglot core must reproduce the reference constants
   bit-for-bit or be marked as failing.
5. Determinism: identical inputs must produce bit-identical outputs on any machine.

## Reporting bugs responsibly

See [SECURITY.md](SECURITY.md) for the security policy. For licensing questions, use
the contact channel in [LICENSE](LICENSE).
