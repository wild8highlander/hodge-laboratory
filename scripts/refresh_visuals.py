#!/usr/bin/env python3
"""refresh_visuals.py — keep the README visual layer honest.

Three jobs, all deterministic and dependency-free:

1. VALIDATE every committed SVG asset (XML well-formedness + size sanity).
2. VALIDATE every relative image/asset link used by the README files.
3. REGENERATE docs/assets/genus.png from the frozen baseline JSON
   (results/baseline_v1_v9.json) so the genus ladder figure can never
   drift from the certified numbers. Matplotlib is optional: when it is
   unavailable the script degrades to validation-only (exit 0) and the
   workflow commits nothing.

Run manually or from .github/workflows/refresh-visuals.yml.

© 2026 Isaev Iskhak Khamzatovich. Part of the hodge-laboratory program.
"""

from __future__ import annotations

import json
import re
import sys
import xml.dom.minidom
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

SVG_DIRS = [
    REPO_ROOT / "docs" / "assets" / "svg",
    REPO_ROOT / "chess-dynamics-lab" / "docs" / "assets" / "svg",
    REPO_ROOT / "verhodge-lab" / "figures" / "svg",
]

README_FILES = sorted(REPO_ROOT.rglob("README.md"))

GENUS_PNG = REPO_ROOT / "docs" / "assets" / "genus.png"
BASELINE = REPO_ROOT / "results" / "baseline_v1_v9.json"

IMG_RE = re.compile(r'(?:src|href)="([^"#]+?)"')


def validate_svgs() -> list[str]:
    errors: list[str] = []
    for folder in SVG_DIRS:
        if not folder.is_dir():
            continue
        for svg in sorted(folder.glob("*.svg")):
            try:
                xml.dom.minidom.parse(str(svg))
            except Exception as exc:  # noqa: BLE001
                errors.append(f"SVG parse failure: {svg.relative_to(REPO_ROOT)}: {exc}")
                continue
            size = svg.stat().st_size
            if size > 300_000:
                errors.append(
                    f"SVG too large ({size} bytes): {svg.relative_to(REPO_ROOT)}"
                )
    return errors


def validate_readme_links() -> list[str]:
    errors: list[str] = []
    for readme in README_FILES:
        if ".git" in readme.parts:
            continue
        text = readme.read_text(encoding="utf-8", errors="replace")
        for target in IMG_RE.findall(text):
            if target.startswith(("http://", "https://", "data:", "mailto:", "#")):
                continue
            path = target.split("?")[0]
            if path.endswith((".png", ".svg", ".jpg", ".jpeg", ".gif", ".pdf")):
                resolved = (readme.parent / path).resolve()
                if not resolved.exists():
                    errors.append(
                        f"broken image link in {readme.relative_to(REPO_ROOT)}: {target}"
                    )
    return errors


def regenerate_genus_png() -> bool:
    """Redraw docs/assets/genus.png from the frozen baseline. True if written."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.font_manager as fm
        import matplotlib.pyplot as plt
    except ImportError:
        print("refresh_visuals: matplotlib not available — skipping genus.png")
        return False

    for candidate in (
        "/usr/share/fonts/truetype/chinese/NotoSansSC-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if Path(candidate).exists():
            fm.fontManager.addfont(candidate)
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Noto Sans SC"]
    plt.rcParams["axes.unicode_minus"] = False

    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    v1 = baseline["V1_census"]
    levels = [int(k) for k in v1.keys()]
    genera = {N: (N - 1) * (N - 2) // 2 for N in levels}

    xs = sorted(genera)
    ys = [genera[x] for x in xs]

    fig, ax = plt.subplots(figsize=(7.2, 4.4), dpi=300, constrained_layout=True)
    fig.patch.set_facecolor("#0B1026")
    ax.set_facecolor("#0B1026")
    ax.plot(xs, ys, "-o", color="#22D3EE", linewidth=2.2, markersize=6)
    for x, y in zip(xs, ys):
        ax.annotate(str(y), (x, y), textcoords="offset points", xytext=(0, 9),
                    ha="center", fontsize=9, color="#E5ECFF")
    ax.set_xlabel("Fermat level N", color="#9AB0D8")
    ax.set_ylabel("genus g(N)", color="#9AB0D8")
    ax.set_title("Fermat curve genus g(N) = (N−1)(N−2)/2 — rungs " +
                 ", ".join(str(x) for x in xs), color="#E5ECFF", fontsize=11)
    ax.tick_params(colors="#9AB0D8")
    for spine in ax.spines.values():
        spine.set_color("#3A4666")
    ax.grid(True, color="#3A4666", alpha=0.25)
    fig.savefig(GENUS_PNG, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"refresh_visuals: regenerated {GENUS_PNG.relative_to(REPO_ROOT)}")
    return True


def main() -> int:
    errors = validate_svgs() + validate_readme_links()
    for err in errors:
        print(f"refresh_visuals: ERROR {err}", file=sys.stderr)
    if errors:
        return 1
    print(f"refresh_visuals: all SVG assets valid; "
          f"{len(README_FILES)} README link sets checked — OK")
    regenerate_genus_png()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
