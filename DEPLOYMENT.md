# Internet Deployment

This Streamlit app can be deployed with Streamlit Community Cloud, Hugging Face
Spaces, or Render.

## Required Files

- `app/app.py`
- `utils/`
- `requirements.txt`
- `packages.txt`
- `runtime.txt`
- `.streamlit/config.toml`
- Required checkpoints:
  - `notebooks/models/classification/checkpoints/best_model.pth`
  - `notebooks/models/segmentation/checkpoints/efficientnet_unet_best.pth`
  - `notebooks/models/segmentation_v2/checkpoints/unetpp_best.pth`
  - `notebooks/models/segmentation_v3/checkpoints/unetpp_v3_best.pth`
  - `notebooks/models/segmentation_v5/checkpoints/unetpp_v5_best.pth`

The SAM checkpoint is not required by the app and should stay out of deployment.

## Streamlit Community Cloud

1. Push this repository to GitHub.
2. Create a new Streamlit app.
3. Set the main file path to:

```text
app/app.py
```

4. Optional secrets:

```toml
OPENAI_API_KEY = "your_api_key"
OPENAI_MODEL = "gpt-4o-mini"
```

Without `OPENAI_API_KEY`, the app uses rule-based advisory fallback.

## Render

Use the included `Dockerfile`.

Recommended settings:

- Environment: Docker
- Port: `8501`
- Optional env vars: `OPENAI_API_KEY`, `OPENAI_MODEL`

Local Docker preview:

```powershell
docker compose up --build
```

Then open:

```text
http://localhost:8501
```

## Hugging Face Spaces

Create a Streamlit Space and upload the same required files. Set app file:

```text
app/app.py
```

Add `OPENAI_API_KEY` in Space secrets only if LLM advisory is needed.
