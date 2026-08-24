"""Small IO/runtime helpers shared by command-line entrypoints."""
from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Iterable

from config import PROJECT_ROOT


def project_chdir() -> Path:
    os.chdir(PROJECT_ROOT)
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    return PROJECT_ROOT


def read_json(path: Path, default=None):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row.keys()})
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def run_python(script: Path, extra_args: Iterable[str] = ()) -> int:
    if not script.exists():
        raise FileNotFoundError(script)
    cmd = [sys.executable, str(script), *map(str, extra_args)]
    print("$", " ".join(cmd))
    return subprocess.call(cmd, cwd=PROJECT_ROOT)


def fmt_float(value, digits=4):
    return "" if value is None else f"{float(value):.{digits}f}"


def pick(d, *keys, default=None):
    cur = d or {}
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def best(values, mode="max"):
    values = [v for v in (values or []) if isinstance(v, (int, float))]
    if not values:
        return None
    return max(values) if mode == "max" else min(values)

