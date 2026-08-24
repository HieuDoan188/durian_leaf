"""Clean command-line entrypoint for the thesis project."""
from __future__ import annotations

import argparse

from io_utils import project_chdir


TASKS = {
    "prepare": "Create dataset manifest and summary JSON files.",
    "status": "Check availability of data, checkpoints, pseudo labels, and metrics.",
    "compare": "Build experiment comparison tables.",
    "app": "Launch the Streamlit prediction app.",
}


def main():
    project_chdir()
    parser = argparse.ArgumentParser(description="Run clean thesis pipeline tasks.")
    parser.add_argument("tasks", nargs="*", help="Task names. Defaults to: status compare")
    parser.add_argument("--list", action="store_true", help="List available tasks.")
    parser.add_argument("--include-deprecated", action="store_true", help="Include deprecated experiments in compare.")
    args = parser.parse_args()

    if args.list:
        for name, desc in TASKS.items():
            print(f"{name:10s} {desc}")
        return

    selected = args.tasks or ["status", "compare"]
    if selected == ["all"]:
        selected = ["prepare", "status", "compare"]

    for task in selected:
        if task == "prepare":
            from data import main as prepare_main

            prepare_main()
        elif task == "status":
            from status import main as status_main

            status_main()
        elif task == "compare":
            from compare import main as compare_main

            compare_args = ["--include-deprecated"] if args.include_deprecated else []
            compare_main(compare_args)
        elif task == "app":
            from app import main as app_main

            app_main()
        else:
            raise SystemExit(f"Unknown task: {task}. Run: python main/pipeline.py --list")


if __name__ == "__main__":
    main()

