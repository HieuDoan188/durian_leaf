"""Launch the Streamlit demo application."""
from __future__ import annotations

import argparse
import subprocess
import sys

from config import PROJECT_ROOT
from io_utils import project_chdir


def main():
    project_chdir()
    parser = argparse.ArgumentParser(description="Run Streamlit prediction app.")
    parser.add_argument("--port", type=int, default=8501)
    args = parser.parse_args()
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(PROJECT_ROOT / "app" / "app.py"),
        "--server.port",
        str(args.port),
    ]
    print("$", " ".join(cmd))
    raise SystemExit(subprocess.call(cmd, cwd=PROJECT_ROOT))


if __name__ == "__main__":
    main()

