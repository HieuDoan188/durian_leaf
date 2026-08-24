"""Project configuration and a clean experiment registry.

The thesis had several historical notebook versions. In this command-line
pipeline we keep only experiments that represent distinct research questions.
Deprecated experiments remain in notebooks/models for traceability, but are not
part of the default pipeline.
"""
from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"
DATA_DIR = NOTEBOOKS_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
MODELS_DIR = NOTEBOOKS_DIR / "models"
VISUALIZATIONS_DIR = NOTEBOOKS_DIR / "visualizations"
APP_PATH = PROJECT_ROOT / "app" / "app.py"

CLASS_NAMES = [
    "ALGAL_LEAF_SPOT",
    "ALLOCARIDARA_ATTACK",
    "HEALTHY_LEAF",
    "LEAF_BLIGHT",
    "PHOMOPSIS_LEAF_SPOT",
]

CLASS_LABELS = [
    "Algal Leaf Spot",
    "Allocaridara Attack",
    "Healthy Leaf",
    "Leaf Blight",
    "Phomopsis Leaf Spot",
]

CLASSIFIER = {
    "key": "classifier",
    "label": "EfficientNet-B0 classifier",
    "architecture": "EfficientNet-B0",
    "checkpoint": MODELS_DIR / "classification" / "checkpoints" / "best_model.pth",
    "metrics_dir": MODELS_DIR / "classification" / "metrics",
}

EXPERIMENTS = {
    "gradcam_unet": {
        "version": "V1",
        "label": "GradCAM baseline",
        "role": "baseline",
        "architecture": "EfficientNet-B0 encoder + custom U-Net decoder",
        "pseudo_label": "Single-layer Grad-CAM with fixed threshold",
        "model_dir": MODELS_DIR / "segmentation",
        "checkpoint": MODELS_DIR / "segmentation" / "checkpoints" / "efficientnet_unet_best.pth",
        "pseudo_stats": DATA_DIR / "pseudo_labels_train" / "pseudo_label_stats.json",
        "include_by_default": True,
    },
    "gradcampp_unetpp": {
        "version": "V2",
        "label": "GradCAM++ pseudo-labels",
        "role": "xai_improvement",
        "architecture": "UNet++ with EfficientNet-B0 encoder",
        "pseudo_label": "Multi-scale GradCAM++ with adaptive percentile threshold",
        "model_dir": MODELS_DIR / "segmentation_v2",
        "checkpoint": MODELS_DIR / "segmentation_v2" / "checkpoints" / "unetpp_best.pth",
        "pseudo_stats": DATA_DIR / "pseudo_labels_v2_train" / "pseudo_label_stats_v2.json",
        "include_by_default": True,
    },
    "sam_guard_unetpp": {
        "version": "V3",
        "label": "SAM refinement diagnostic",
        "role": "boundary_refinement_diagnostic",
        "architecture": "UNet++ with EfficientNet-B0 encoder",
        "pseudo_label": "SAM-refined GradCAM++ masks with two-sided coverage guard",
        "model_dir": MODELS_DIR / "segmentation_v3",
        "checkpoint": MODELS_DIR / "segmentation_v3" / "checkpoints" / "unetpp_v3_best.pth",
        "pseudo_stats": DATA_DIR / "sam_refined_labels_v3_train" / "pseudo_label_stats_v3.json",
        "include_by_default": True,
    },
    "color_prior_unetpp": {
        "version": "V5",
        "label": "Disease color prior",
        "role": "current_candidate",
        "architecture": "UNet++ with EfficientNet-B0 encoder",
        "pseudo_label": "GradCAM++ intersected with class-specific disease color priors",
        "model_dir": MODELS_DIR / "segmentation_v5",
        "checkpoint": MODELS_DIR / "segmentation_v5" / "checkpoints" / "unetpp_v5_best.pth",
        "pseudo_stats": DATA_DIR / "pseudo_labels_v5_train" / "pseudo_label_stats_v5.json",
        "include_by_default": True,
    },
}

DEPRECATED_EXPERIMENTS = {
    "leaf_bilateral_unetpp": {
        "version": "V4",
        "label": "Leaf/bilateral exploratory branch",
        "role": "deprecated_exploratory",
        "reason": "Mixed leaf masking and bilateral smoothing changed too many variables; kept only for traceability.",
        "architecture": "UNet++ with EfficientNet-B0 encoder",
        "pseudo_label": "Leaf mask + bilateral-smoothed GradCAM++",
        "model_dir": MODELS_DIR / "deprecated" / "segmentation_v4",
        "checkpoint": MODELS_DIR / "deprecated" / "segmentation_v4" / "checkpoints" / "unetpp_v4_best.pth",
        "pseudo_stats": DATA_DIR / "deprecated" / "pseudo_labels_v4_train" / "pseudo_label_stats_v4.json",
        "include_by_default": False,
    },
}


def selected_experiments(include_deprecated: bool = False):
    experiments = dict(EXPERIMENTS)
    if include_deprecated:
        experiments.update(DEPRECATED_EXPERIMENTS)
    return experiments
