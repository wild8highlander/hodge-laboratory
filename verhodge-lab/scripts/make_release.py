"""Build the release ZIP of verhodge-lab (Wave 6)."""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else "verhodge-lab_v1.9.zip"


def main():
    # refresh the protocol baseline before packaging
    subprocess.run([sys.executable, "-m", "verhodge.cli"], cwd=ROOT,
                   check=True)
    excl = {"__pycache__", ".pytest_cache", ".git", "*.pyc", "build",
            "*.egg-info"}
    cmd = ["zip", "-r", OUT, ".", "-x"]
    for e in excl:
        cmd.append(e)
    subprocess.run(cmd, cwd=ROOT, check=True)
    print("release ->", os.path.join(ROOT, OUT))


if __name__ == "__main__":
    main()
