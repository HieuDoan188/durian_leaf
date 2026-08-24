"""Dataset manifest/statistics utilities used by the clean pipeline."""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from config import CLASS_NAMES, DATA_DIR, RAW_DATA_DIR
from io_utils import project_chdir, write_json

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp"}


def iter_images(split_dir: Path):
    for class_dir in sorted(p for p in split_dir.iterdir() if p.is_dir()):
        for path in sorted(class_dir.rglob("*")):
            if path.suffix.lower() in IMAGE_EXTS:
                yield class_dir.name, path


def build_manifest():
    project_chdir()
    manifest = []
    for split in ["train", "val", "test"]:
        split_dir = RAW_DATA_DIR / split
        if not split_dir.exists():
            continue
        for class_name, path in iter_images(split_dir):
            manifest.append({
                "split": split,
                "class_name": class_name,
                "class_index": CLASS_NAMES.index(class_name) if class_name in CLASS_NAMES else None,
                "path": str(path),
                "filename": path.name,
            })
    return manifest


def summarize_manifest(manifest):
    by_split = Counter(row["split"] for row in manifest)
    by_class = Counter(row["class_name"] for row in manifest)
    by_split_class = Counter((row["split"], row["class_name"]) for row in manifest)
    return {
        "total_images": len(manifest),
        "by_split": dict(by_split),
        "by_class": dict(by_class),
        "by_split_class": {f"{split}/{cls}": count for (split, cls), count in sorted(by_split_class.items())},
    }


def main():
    manifest = build_manifest()
    summary = summarize_manifest(manifest)
    write_json(DATA_DIR / "processed" / "dataset_manifest.json", manifest)
    write_json(DATA_DIR / "processed" / "dataset_summary_clean.json", summary)
    print(f"Images: {summary['total_images']}")
    print(summary)


if __name__ == "__main__":
    main()

