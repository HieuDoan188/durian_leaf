"""Build comparison tables across the clean experiment registry."""
from __future__ import annotations

import argparse

from config import CLASSIFIER, MODELS_DIR, selected_experiments
from io_utils import best, fmt_float, pick, project_chdir, read_json, write_csv, write_json


def pseudo_summary(pseudo):
    if isinstance(pseudo, list):
        coverages = [
            item.get("mask_coverage")
            for item in pseudo
            if isinstance(item, dict) and isinstance(item.get("mask_coverage"), (int, float))
        ]
        return {
            "num_masks": len(pseudo),
            "mean_coverage": (sum(coverages) / len(coverages)) if coverages else None,
        }
    if isinstance(pseudo, dict):
        return {
            "num_masks": pick(pseudo, "total_masks", default=pick(pseudo, "num_masks")),
            "mean_coverage": pick(pseudo, "mean_coverage", default=pick(pseudo, "overall", "mean_coverage")),
        }
    return {"num_masks": None, "mean_coverage": None}


def classification_row():
    metrics = read_json(CLASSIFIER["metrics_dir"] / "test_metrics.json", {})
    if not metrics:
        return None
    return {
        "experiment": "classification_efficientnet_b0",
        "task": "classification",
        "test_accuracy": pick(metrics, "accuracy"),
        "test_precision": pick(metrics, "precision"),
        "test_recall": pick(metrics, "recall"),
        "test_f1": pick(metrics, "f1_score", default=pick(metrics, "f1")),
        "checkpoint": str(CLASSIFIER["checkpoint"]),
    }


def segmentation_row(version: str, cfg: dict):
    metrics_dir = cfg["model_dir"] / "metrics"
    test = read_json(metrics_dir / "test_metrics.json", {})
    final = read_json(metrics_dir / "final_segmentation_metrics.json", {})
    manual = read_json(metrics_dir / "manual_gt_metrics.json", {})
    history = read_json(metrics_dir / "training_history.json", {})
    pseudo = read_json(cfg["pseudo_stats"], {})
    pseudo_info = pseudo_summary(pseudo)
    source = test or final or {}
    return {
        "experiment": version,
        "task": "segmentation",
        "label": cfg["label"],
        "architecture": cfg["architecture"],
        "pseudo_label": cfg["pseudo_label"],
        "test_iou": pick(source, "iou", default=pick(source, "test_iou")),
        "test_dice": pick(source, "dice", default=pick(source, "test_dice")),
        "test_precision": pick(source, "precision"),
        "test_recall": pick(source, "recall"),
        "test_loss": pick(source, "loss", default=pick(source, "test_loss")),
        "manual_gt_iou": pick(manual, "overall", "iou", default=pick(manual, "iou", default=pick(manual, "mean_iou"))),
        "manual_gt_dice": pick(manual, "overall", "dice", default=pick(manual, "dice", default=pick(manual, "mean_dice"))),
        "manual_gt_precision": pick(manual, "overall", "precision", default=pick(manual, "precision")),
        "manual_gt_recall": pick(manual, "overall", "recall", default=pick(manual, "recall")),
        "best_val_iou": pick(history, "best_val_iou", default=best(history.get("val_iou"), "max")),
        "best_val_loss": pick(history, "best_val_loss", default=best(history.get("val_loss"), "min")),
        "pseudo_num_masks": pseudo_info["num_masks"],
        "pseudo_mean_coverage": pseudo_info["mean_coverage"],
        "checkpoint": str(cfg["checkpoint"]),
    }


def build_rows(include_deprecated=False):
    rows = []
    cls = classification_row()
    if cls:
        rows.append(cls)
    for key, cfg in selected_experiments(include_deprecated).items():
        rows.append(segmentation_row(key, cfg))
    return rows


def write_markdown(path, rows):
    columns = [
        "experiment", "task", "test_accuracy", "test_f1", "test_iou", "test_dice",
        "test_precision", "test_recall", "manual_gt_iou", "manual_gt_dice",
        "best_val_iou", "best_val_loss", "pseudo_mean_coverage",
    ]
    lines = [
        "# Experiment Comparison",
        "",
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for row in rows:
        values = []
        for col in columns:
            value = row.get(col)
            values.append(fmt_float(value) if isinstance(value, (int, float)) else ("" if value is None else str(value)))
        lines.append("| " + " | ".join(values) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv=None):
    project_chdir()
    parser = argparse.ArgumentParser(description="Compare thesis experiments.")
    parser.add_argument("--include-deprecated", action="store_true", help="Include exploratory/deprecated branches such as V4.")
    args = parser.parse_args(argv)

    rows = build_rows(include_deprecated=args.include_deprecated)
    out_json = MODELS_DIR / "experiment_comparison.json"
    out_csv = MODELS_DIR / "experiment_comparison.csv"
    out_md = MODELS_DIR / "experiment_comparison.md"
    write_json(out_json, rows)
    write_csv(out_csv, rows)
    write_markdown(out_md, rows)
    print(f"Wrote {out_json}")
    print(f"Wrote {out_csv}")
    print(f"Wrote {out_md}")
    print(out_md.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
