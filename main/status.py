"""Report artifact availability for the clean thesis pipeline."""
from __future__ import annotations

from config import CLASSIFIER, DEPRECATED_EXPERIMENTS, EXPERIMENTS, RAW_DATA_DIR
from io_utils import project_chdir


def exists(path):
    return "OK" if path.exists() else "MISSING"


def main():
    project_chdir()
    print("DATA")
    for split in ["train", "val", "test"]:
        path = RAW_DATA_DIR / split
        print(f"  {split:5s} {exists(path):8s} {path}")

    print("\nCLASSIFIER")
    print(f"  checkpoint {exists(CLASSIFIER['checkpoint']):8s} {CLASSIFIER['checkpoint']}")
    metrics = CLASSIFIER["metrics_dir"] / "test_metrics.json"
    print(f"  metrics    {exists(metrics):8s} {metrics}")

    print("\nSEGMENTATION EXPERIMENTS")
    for key, cfg in EXPERIMENTS.items():
        metrics = cfg["model_dir"] / "metrics" / "test_metrics.json"
        manual = cfg["model_dir"] / "metrics" / "manual_gt_metrics.json"
        print(f"  {key}")
        print(f"    ckpt      {exists(cfg['checkpoint']):8s} {cfg['checkpoint']}")
        print(f"    metrics   {exists(metrics):8s} {metrics}")
        print(f"    manual_gt {exists(manual):8s} {manual}")
        print(f"    pseudo    {exists(cfg['pseudo_stats']):8s} {cfg['pseudo_stats']}")

    print("\nDEPRECATED")
    for key, cfg in DEPRECATED_EXPERIMENTS.items():
        print(f"  {key}: {cfg['reason']}")


if __name__ == "__main__":
    main()

