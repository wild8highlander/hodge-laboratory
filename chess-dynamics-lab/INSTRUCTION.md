# Complete guide: publishing chess-dynamics-lab to GitHub
#    Android (Termux) · Linux · macOS

**Program author:** Isaev Iskhak Khamzatovich (Исаев Исхак Хамзатович)
**Repository:** `chess-dynamics-lab` · account: `wild8highlander`
**Version:** 1.0.0 (2026)

---

## Part 0. What you are publishing

| Component | Description |
|---|---|
| `dynamics.py` | the single-file laboratory: 0x88 board, full legal move generation, the three-layer particle model (K3 / TORUS / KLEIN), retrograde KRK/KQK bases, alpha-beta search, protocol C1–C9, CLI, 600 dpi plots |
| `engine/` | the importable package: particles, mate solver, playing engine (self-play), analyzer |
| `polyglot/` | the C1–C10 battery in seven languages: Python, C, Rust, Go, Julia, JavaScript, Java |
| `tests/` | 36 pytest tests over the core, the engine and the frozen baseline |
| `results/` | the frozen certificates: KRK/KQK DTM bases, the knight tour, `baseline_c1_c9.json` |
| `reports/plots/` | five protocol plots (600 dpi) |
| `monograph/` | the main monograph + 12 theorem monographs — PDF and DOCX, Russian and English (26 files) |
| `web/chess-particles/` | the browser laboratory with the honestly computed protocol |
| `docs/` | the GitHub Pages landing |
| `scripts/termux_push.sh` | the one-command publication script |
| `.github/workflows/` | CI (protocol ×3 Python versions + 7-language polyglot + web sanity) and Pages |

Everything ships in one ZIP. The script `scripts/termux_push.sh` performs the
publication in a single run.

---

## Part 1. Android · Termux — step by step

### Step 1. Install Termux

**From F-Droid only:** `https://f-droid.org/packages/com.termux/`
(the Google Play build is outdated and broken). Open the app.

### Step 2. Update the packages

```bash
pkg update
pkg upgrade
```

### Step 3. Install the toolchain

```bash
pkg install python git gh      # gh is the GitHub CLI (optional but recommended)
# clang/make are NOT required for the laboratory itself (pure Python);
# they are needed only if you want to compile the C polyglot backend locally:
pkg install clang make
```

### Step 4. Unpack the laboratory

If you received the project as a ZIP (e.g. downloaded to `~/storage/downloads/`):

```bash
cd ~
unzip ~/storage/downloads/chess-dynamics-lab.zip -d .
cd chess-dynamics-lab
```

If it is already on GitHub, clone it:

```bash
git clone https://github.com/wild8highlander/chess-dynamics-lab.git
cd chess-dynamics-lab
```

### Step 5. Verify the protocol on the phone

```bash
python3 dynamics.py --report
```

You should see nine `[PASS]` lines and `verdict: ALL CHECKS PASSED`.
The full report takes tens of seconds on a phone (the C5 perft check dominates);
individual checks are fast:

```bash
python3 dynamics.py --run C5          # seconds
python3 dynamics.py --run C5 --deep   # perft(5) = 4865609 — about a minute
python3 dynamics.py --run C8          # retrograde bases + the tactical suite
python3 engine/game_player.py --selfplay --depth 4
```

### Step 6. Authorize on GitHub

**Option A — the gh CLI (recommended):**

```bash
gh auth login
# choose: GitHub.com → HTTPS → Login with a web browser
# open https://github.com/login/device on any device and enter the one-time code
```

**Option B — a personal access token:**

1. On any device open `https://github.com/settings/tokens` →
   *Generate new token (classic)* → scope `repo`.
2. In Termux:

```bash
export GH_TOKEN=ghp_your_token_here
```

(add the line to `~/.bashrc` to persist it; the token stays on the phone and is sent
only to github.com).

### Step 7. Publish with one command

```bash
bash scripts/termux_push.sh
```

The script: checks the environment → makes the initial commit → creates the
repository `https://github.com/wild8highlander/chess-dynamics-lab` → pushes `main`.
Custom account/name:

```bash
GH_USER=your_account GH_REPO=your_name bash scripts/termux_push.sh
```

### Step 8. Watch the CI

Open `https://github.com/wild8highlander/chess-dynamics-lab/actions` — the workflow
`ci` verifies on GitHub's servers: the protocol on Python 3.9/3.11/3.13, deep perft,
36 pytest tests, the self-play determinism, and the polyglot battery in **all seven
languages** (Rust, Go, Julia and Java are verified there — no local toolchains needed).
The workflow `pages` deploys the landing and the web laboratory to
`https://wild8highlander.github.io/chess-dynamics-lab/` (enable *Settings → Pages →
Source: GitHub Actions* if it did not start automatically).

---

## Part 2. Linux · macOS

```bash
# Debian/Ubuntu
sudo apt install python3 git curl
# macOS (Homebrew)
brew install python git gh

git clone https://github.com/wild8highlander/chess-dynamics-lab.git
cd chess-dynamics-lab
python3 dynamics.py --report
python3 -m pytest tests/ -q

# publish (same as on Termux)
gh auth login        # or export GH_TOKEN=...
bash scripts/termux_push.sh
```

---

## Part 3. Verification matrix

| Check | Command | Expected |
|---|---|---|
| protocol C1–C9 | `python3 dynamics.py --report` | ALL CHECKS PASSED |
| deep perft | `python3 dynamics.py --run C5 --deep` | perft(5) = 4865609 |
| pytest | `python3 -m pytest tests/ -q` | 36 passed |
| polyglot (available backends) | `bash polyglot/run_all.sh` | verdict: 10/10 per backend |
| web core from Node | see `ci.yml` «web» job | verdict: 10/10 |
| monographs | open `monograph/pdf/{ru,en}/` | 26 documents |

All 26 documents of `monograph/` carry frozen constants (see README §10) that must
match `results/baseline_c1_c9.json` and the live protocol output — the theory and the
executable share one source of truth.

---

## Part 4. Troubleshooting

| Symptom | Fix |
|---|---|
| `gh: command not found` | `pkg install gh`, or use `export GH_TOKEN=...` (Option B) |
| `401` from the GitHub API | the token expired or lacks the `repo` scope — regenerate |
| `422 name already exists` | normal — the script reuses the existing repository and pushes |
| `python3: command not found` (Termux) | `pkg install python` |
| matplotlib is missing | the core never requires it; only `--plots` does: `pip install matplotlib` |
| C5 is slow on a phone | normal — use `--run C5` without `--deep` for daily checks |
| CI failed in Rust/Go/Julia/Java | open the job log; the backend prints `[FAIL] Cn ...` lines locally too — rerun `bash polyglot/run_all.sh` after fixing |
| Pages did not deploy | Settings → Pages → Source: **GitHub Actions**, then re-run the `pages` workflow |

---

## Part 5. What must NOT be changed

- `LICENSE` — the individual exclusive license (all rights of Isaev Iskhak
  Khamzatovich); any redistribution requires the author's written permission;
- `results/baseline_c1_c9.json` and the DTM bases — the frozen certificates; they are
  the reference for every cross-check;
- the constants of the monographs and the README — they are pinned by the protocol;
  if a check fails, fix the implementation, never the baseline.

© 2026 Isaev Iskhak Khamzatovich. All rights reserved.
