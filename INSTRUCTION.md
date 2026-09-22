# 📱 COMPLETE GUIDE: publishing Hodge Laboratory to GitHub
#    Android (Termux) · Linux · macOS

**Program author:** Isaev Iskhak Khamzatovich
**Repository:** `hodge-laboratory` · account: `wild8highlander`
**Version:** 1.1.1 (2026)

---

## Part 0. What you are publishing

| Component | Description |
|---|---|
| `laboratory.py` | the single-file laboratory: menu, protocol V1–V9, stands, certificates, experiment designer, reports, 600 dpi plots, RU/EN UI |
| `tests/` | the pytest suite for the laboratory core |
| `monograph/` | the unified monograph: PDF + DOCX × RU/EN + LaTeX sources |
| `theorems/` | 16 standalone theorem monographs (32 PDFs, two languages) |
| `verification/` | Lean 4, Julia, Fortran, C, Rust |
| `results/` | the frozen baseline JSON for cross-checks |
| `docs/` | GitHub Pages — the laboratory landing page |
| `.github/` | CI (protocol on three Python versions + lint + tests + C/Fortran/Rust) and Pages workflows |

Everything ships in one ZIP. The script `scripts/github_push_termux.sh`
performs the publication in a single run; `scripts/termux_setup.sh`
bootstraps the environment first.

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

(answer `Y` to the prompts).

### Step 3. Install Python and git

```bash
pkg install python git curl
```

### Step 4. Create a GitHub token

1. Open `github.com` → sign in to the **wild8highlander** account.
2. Settings → Developer settings → Personal access tokens →
   **Tokens (classic)** → Generate new token (classic).
3. Check the scopes: **repo**, **workflow**.
4. Generate and **copy the token** (it is shown once).

### Step 5. Unpack the ZIP on the phone

Download `hodge-laboratory.zip`, then in Termux:

```bash
termux-setup-storage        # grant storage access once
cd ~/storage/downloads      # or wherever the archive landed
unzip hodge-laboratory.zip -d hodge-lab
cd hodge-lab/hodge-laboratory
```

(if `unzip` is missing: `pkg install unzip`).

### Step 6. (Optional) Bootstrap the environment and test the lab on the phone

```bash
bash scripts/termux_setup.sh
```

or manually:

```bash
pip install mpmath numpy
python3 laboratory.py --run all
```

The verdict must be `ALL CHECKS PASSED`.

### Step 7. Run the publisher

```bash
bash scripts/github_push_termux.sh
```

The script:
1. checks/installs git and curl;
2. asks for the **token** (paste it from step 4);
3. verifies the account (`wild8highlander`);
4. makes the first commit;
5. creates the `hodge-laboratory` repository via the GitHub API;
6. pushes the code;
7. enables **GitHub Pages** (the `docs/` folder).

At the end you get the links:
- repository: `https://github.com/wild8highlander/hodge-laboratory`
- site: `https://wild8highlander.github.io/hodge-laboratory/`

### Step 8. Check CI

GitHub → repository → **Actions**: the workflow
`CI — Verification Suite` must turn green in 2–4 minutes (the
protocol on Python 3.10–3.12, lint, tests, baseline cross-check, and
the C/Fortran/Rust backends).

### Step 9. Check Pages

GitHub → repository → **Settings → Pages**: source = `main` + `/docs`.
A minute later open `https://wild8highlander.github.io/hodge-laboratory/`.

### Step 10. (Optional) Mint the Zenodo DOI

See the «Zenodo & DOI» section of [`README.md`](README.md): enable
the repository in your Zenodo account, publish the `v1.1.1` GitHub
release, and put the minted DOI into the README badge and
[`CITATION.cff`](CITATION.cff).

---

## Part 2. Linux / macOS — the same, shorter

```bash
sudo apt install git curl python3-pip    # or: brew install git curl
pip3 install mpmath numpy matplotlib
cd hodge-laboratory
python3 laboratory.py --run all          # check
GH_TOKEN=your_token bash scripts/github_push_termux.sh
```

---

## Part 3. Common problems

| Problem | Solution |
|---|---|
| `pkg update` errors | `termux-change-repo` → pick a mirror; retry |
| Token "invalid" | check the scopes `repo` + `workflow`; create a new classic token |
| `push failed` | the GitHub account has no write access: the token must belong to wild8highlander; check the expiry |
| Repository already exists | the script continues and pushes into the existing one |
| Pages not enabled via API | Settings → Pages → Source: Deploy from branch → `main` → `/docs` → Save |
| Actions red | open the log; most often a dependency issue — CI installs them itself; verify `laboratory.py` runs locally |
| matplotlib missing on Termux | `pkg install matplotlib` or `pip install matplotlib`; without plots: `python3 laboratory.py --run all --no-plots` |
| Julia/Fortran checks fail | make sure you run the current version — v1.1.0 fixed the sign and precision bugs of the early backends |

---

## Part 4. Updating the repository (after changes)

```bash
cd hodge-laboratory
git add -A
git commit -m "description of the changes"
git push
```

CI re-runs the whole suite; Pages updates automatically.

---

## Part 5. Repository structure (brief)

```
hodge-laboratory/
├── laboratory.py            ← the laboratory (single file)
├── tests/                   ← pytest suite
├── monograph/               ← PDF/DOCX × RU/EN + LaTeX
├── theorems/                ← 16 theorem folders × RU/EN
├── verification/            ← lean/ julia/ fortran/ c/ rust/
├── results/                 ← baseline JSON
├── reports/                 ← reference run artifacts
├── docs/                    ← the site (GitHub Pages)
├── scripts/                 ← termux_setup.sh · github_push_termux.sh
├── .github/                 ← CI + Pages + templates
├── CITATION.cff             ← citation metadata (ORCID included)
├── .zenodo.json             ← Zenodo metadata for DOI minting
├── LICENSE                  ← individual exclusive license
└── README.md                ← the main README (English)
```

---

## Part 6. License

The entire repository is protected by the **individual exclusive
license of Isaev Iskhak Khamzatovich** (`LICENSE`): any use, copying,
and extraction of the materials without the author's written
permission is prohibited. Publishing the repository on GitHub
transfers no rights.

---

© 2026 Isaev Iskhak Khamzatovich · All rights reserved
