# Main Pipeline

`main/` is the cleaned command-line surface for the thesis project. It is not a
one-file-per-notebook export anymore.

## What Is Kept In The Main Pipeline

- `gradcam_unet`: baseline segmentation from Grad-CAM pseudo labels.
- `gradcampp_unetpp`: GradCAM++ + UNet++ improvement.
- `sam_guard_unetpp`: SAM boundary-refinement diagnostic.
- `color_prior_unetpp`: current disease-color-prior candidate.

The old V4 leaf/bilateral branch is marked deprecated because it mixed too many
variables and is not part of the default comparison.

## Files

- `config.py`: central paths, class labels, checkpoints, and experiment registry.
- `data.py`: dataset manifest and summary generation.
- `status.py`: artifact availability report.
- `compare.py`: comparison tables from saved metrics.
- `app.py`: Streamlit app launcher.
- `pipeline.py`: unified CLI.
- `run_pipeline.py`: backward-compatible alias for `pipeline.py`.
- `io_utils.py`: small shared helpers.

## Commands

```powershell
.\venv\Scripts\python.exe main\pipeline.py --list
.\venv\Scripts\python.exe main\pipeline.py prepare
.\venv\Scripts\python.exe main\pipeline.py status
.\venv\Scripts\python.exe main\pipeline.py compare
.\venv\Scripts\python.exe main\pipeline.py compare --include-deprecated
.\venv\Scripts\python.exe main\pipeline.py all
.\venv\Scripts\python.exe main\app.py --port 8501
```

Optional LLM advisory in the Streamlit app:

```powershell
$env:OPENAI_API_KEY="your_api_key"
$env:OPENAI_MODEL="gpt-4o-mini"
.\venv\Scripts\python.exe main\app.py --port 8501
```

Without `OPENAI_API_KEY`, the app falls back to a rule-based advisory that uses
predicted class, confidence, lesion coverage, and the selected segmentation
mode.

## Notes

Heavy training and pseudo-label generation are still authored in the notebooks
because they contain long exploratory cells, figures, and analysis text. The
clean `main/` layer focuses on reproducible artifact management, evaluation,
comparison, and deployment.
