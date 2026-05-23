# Durian Leaf Disease Classification & Segmentation

Master's thesis project. The pipeline goes: classify the disease first, use Grad-CAM to see where the model is looking, turn those attention maps into segmentation masks via pseudo-labeling, then train a proper segmentation model on top.

---

## Pipeline Overview

```
Raw Images
    │
    ▼
01 · EDA ──────────────────────── understand the dataset
    │
    ▼
02 · Classification (EfficientNet-B0) ── tell apart the 5 disease classes
    │
    ▼
03 · Grad-CAM (XAI) ────────────── visualize where the model focuses
    │
    ▼
04/07 · Pseudo-Labeling ────────── convert attention maps → segmentation masks
    │
    ▼
05/08/09 · Segmentation (EfficientNet-UNet + SAM) ── localize the lesions
    │
    ▼
06 · Evaluation ────────────────── benchmark everything end-to-end
    │
    ▼
10 · Inference ─────────────────── run on a single image
```

---

## Dataset

5 classes of durian leaf disease, 4,437 images total (224×224 RGB).

| Label | Class | Count |
|:---:|---|:---:|
| 0 | Algal Leaf Spot | 733 |
| 1 | Allocaridara Attack | 913 |
| 2 | Healthy Leaf | 976 |
| 3 | Leaf Blight | 937 |
| 4 | Phomopsis Leaf Spot | 878 |

Split: **70% train / 10% val / 20% test** — imbalance ratio 1.33, no oversampling needed.

Data lives in `notebooks/data/raw/{train,val,test}/{CLASS_NAME}/`.

---

## Notebooks

| # | Notebook | What it does |
|---|---|---|
| 01 | `01-data-exploration.ipynb` | EDA — class distribution, RGB analysis, image statistics |
| 02 | `02-classification-baseline.ipynb` | Train EfficientNet-B0 with early stopping |
| 03 | `03-xai-gradcam-analysis.ipynb` | Grad-CAM visualizations per class |
| 04 | `04-pseudo-labeling.ipynb` | Generate segmentation masks from Grad-CAM |
| 05 | `05-segmentation-model.ipynb` | Train EfficientNet-UNet v1 |
| 06 | `06-model-evaluation.ipynb` | Full evaluation — classification + segmentation |
| 07 | `07-pseudo-labeling-v2.ipynb` | Improved pseudo-label generation |
| 08 | `08-segmentation-v2.ipynb` | EfficientNet-UNet v2 |
| 09 | `09-segmentation-v3-sam.ipynb` | Segmentation refined with SAM |
| 10 | `10-inference-single-image.ipynb` | End-to-end inference on a single image |

---

## Results

**Classification (EfficientNet-B0)**
- Val Accuracy: **97.52%**
- Test Accuracy: **96.29%** · Macro F1: **96.29%**
- Hardest pair: Algal Leaf Spot ↔ Phomopsis Leaf Spot

**Segmentation (EfficientNet-UNet)**
- IoU: **0.461** · Dice: **0.565**
- Recall > Precision — tuned to minimize missed detections

---

## Project Structure

```
thesis-clean/
├── notebooks/
│   ├── 01–10 *.ipynb
│   ├── data/
│   │   └── raw/{train,val,test}/{CLASS}/
│   ├── models/
│   │   ├── classification/checkpoints/
│   │   └── segmentation*/checkpoints/
│   └── visualizations/
│       ├── eda/
│       └── classification/
└── utils/
    ├── preprocessing.py
    ├── models.py
    ├── metrics.py
    ├── gradcam.py
    └── visualization.py
```

---

## Setup

```bash
pip install torch torchvision efficientnet-pytorch \
            opencv-python pillow matplotlib seaborn \
            scikit-learn tqdm
```

Tested on Python 3.10, PyTorch 2.x, CUDA 12.4 (Quadro M1000M).

---

## Running

Run notebooks in order (01 → 10). Each notebook saves its outputs to `models/` and `visualizations/` so downstream notebooks can pick up from there without rerunning everything.

```bash
# or run all at once (PowerShell)
.\run_all_notebooks.ps1
```
