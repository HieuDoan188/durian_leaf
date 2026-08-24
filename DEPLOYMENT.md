# Streamlit Deployment

Use Streamlit Community Cloud with:

```text
Main file path: app/app.py
Python: 3.11
```

Required files:

- `requirements.txt`
- `packages.txt`
- `runtime.txt`
- `.streamlit/config.toml`
- `app/app.py`
- `utils/`
- model checkpoints under `notebooks/models/.../checkpoints/`
- model metric JSON files under `notebooks/models/.../metrics/`

Optional secrets for LLM advisory:

```toml
OPENAI_API_KEY = "your_api_key"
OPENAI_MODEL = "gpt-4o-mini"
```

If `OPENAI_API_KEY` is missing, the app falls back to rule-based advisory.

The SAM checkpoint is not required by the deployed app.
