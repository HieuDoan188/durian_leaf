# Notebook Layout

Top-level notebooks are the active research path. The names are intentionally
written as thesis experiments, not as raw execution history.

| Step | Notebook | Research role |
|---:|---|---|
| 01 | `01-dataset-audit-and-eda.ipynb` | Audit data quality, split, class balance, and visual assumptions |
| 02 | `02-classifier-efficientnet-b0.ipynb` | Train the classifier that produces disease predictions and XAI features |
| 03 | `03-xai-gradcam-gradcampp-analysis.ipynb` | Inspect GradCAM/GradCAM++ behavior before turning heatmaps into labels |
| 04 | `04-v1-gradcam-pseudo-labels.ipynb` | V1 baseline pseudo-label generation from GradCAM |
| 05 | `05-v1-unet-segmentation-baseline.ipynb` | V1 segmentation baseline trained from GradCAM pseudo labels |
| 06 | `06-v2-gradcampp-pseudo-labels.ipynb` | V2 pseudo-label improvement using GradCAM++ |
| 07 | `07-v2-unetpp-segmentation.ipynb` | V2 architecture experiment using UNet++ |
| 08 | `08-v3-sam-refinement-diagnostic.ipynb` | SAM refinement diagnostic and over-expansion analysis |
| 09 | `09-v5-color-prior-pseudo-labels-and-segmentation.ipynb` | Final candidate: GradCAM++ intersected with disease color priors |
| 10 | `10-inference-and-demo.ipynb` | End-to-end prediction/demo workflow |

Deprecated exploratory work is kept under `deprecated/` and is excluded from the
default `main/` comparison. V4 remains there only to explain why leaf-mask and
bilateral-smoothing experiments were not selected as the final method.

## Data Artifacts

- `data/raw/`: original train/val/test images and `GT_OK.zip` if present.
- `data/processed*`: resized images paired with pseudo masks.
- `data/pseudo_labels*`: generated binary lesion masks.
- `data/sam_refined_labels_v3_train/`: V3 SAM-refined masks.
- `data/deprecated/`: V4 artifacts kept for traceability.

## Model Artifacts

- `models/classification/`: classifier checkpoints and metrics.
- `models/segmentation*`: active segmentation checkpoints and metrics.
- `models/deprecated/`: V4 checkpoint/metrics kept out of the default story.
