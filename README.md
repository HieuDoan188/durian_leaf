# Durian Leaf Disease Classification & Segmentation

Master's thesis project for durian leaf disease classification, explainability,
pseudo-mask generation, segmentation, evaluation, and a Streamlit demo app.

## Clean Pipeline

The cleaned command-line entry point is `main/`. It is intentionally not a
one-file-per-notebook dump. It keeps the thesis workflow coherent:

```text
Raw data / GT_OK
  -> dataset manifest and statistics
  -> EfficientNet-B0 classification
  -> GradCAM/GradCAM++ pseudo-label experiments
  -> UNet/UNet++ segmentation evaluation
  -> experiment comparison
  -> Streamlit prediction app
```

Run from the project root:

```powershell
.\venv\Scripts\python.exe main\pipeline.py --list
.\venv\Scripts\python.exe main\pipeline.py prepare
.\venv\Scripts\python.exe main\pipeline.py status
.\venv\Scripts\python.exe main\pipeline.py compare
.\venv\Scripts\python.exe main\pipeline.py all
.\venv\Scripts\python.exe main\app.py --port 8501
```

Optional LLM advisory in the app:

```powershell
$env:OPENAI_API_KEY="your_api_key"
$env:OPENAI_MODEL="gpt-4o-mini"
.\venv\Scripts\python.exe main\app.py --port 8501
```

If no API key is configured, the app still shows a deterministic rule-based
disease severity assessment and treatment suggestion.

Use `main\pipeline.py compare --include-deprecated` only when a historical
experiment is needed for traceability.

## Experiments Kept

| Key | Version | Purpose |
|---|---:|---|
| `gradcam_unet` | V1 | Baseline GradCAM pseudo-label segmentation |
| `gradcampp_unetpp` | V2 | Stronger GradCAM++ pseudo labels and UNet++ |
| `sam_guard_unetpp` | V3 | SAM refinement diagnostic with coverage guard |
| `color_prior_unetpp` | V5 | Current candidate using disease color priors |

V4 is deprecated because it mixed leaf masking and bilateral smoothing in one
branch, making the experiment harder to explain as a clean ablation. It is kept
only as optional historical context, not as the default result.

## Dataset

The project uses five classes and 4,437 images:

| Class | Count |
|---|---:|
| Algal Leaf Spot | 733 |
| Allocaridara Attack | 913 |
| Healthy Leaf | 976 |
| Leaf Blight | 937 |
| Phomopsis Leaf Spot | 878 |

Data lives under `notebooks/data/raw/`. The manually checked ground-truth set is
kept in `notebooks/data/raw/GT_OK.zip` when available.

## Project Structure

```text
app/                 Streamlit prediction interface
main/                Clean CLI pipeline and experiment registry
notebooks/           Research notebooks and reproducible experiment records
notebooks/data/      Raw data, processed splits, pseudo labels, GT_OK
notebooks/models/    Saved metrics and checkpoints
notebooks/*/deprecated
                     Archived exploratory V4 notebook/data/model artifacts
utils/               Shared preprocessing, model, metric, GradCAM helpers
docs/                Thesis, final report files, templates, article drafts
```

Heavy/generated files such as checkpoints, local archives, caches, and generated
images are ignored by Git.
