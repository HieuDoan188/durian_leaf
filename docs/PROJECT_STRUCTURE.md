# Project Structure And Experiment Rationale

This repository keeps two layers:

- `notebooks/`: research history, figures, and detailed experiment notebooks.
- `main/`: cleaned execution surface for dataset preparation, status checks,
  experiment comparison, and app launch.

## Kept Experiments

| Version | Key | Why it remains |
|---:|---|---|
| V1 | `gradcam_unet` | Baseline needed to show the original GradCAM pseudo-label approach. |
| V2 | `gradcampp_unetpp` | Clean improvement over V1: GradCAM++ and UNet++ without changing the whole pipeline. |
| V3 | `sam_guard_unetpp` | Important negative/diagnostic result: SAM can expand from lesion to whole-leaf masks, so coverage guards are scientifically necessary. |
| V5 | `color_prior_unetpp` | Current candidate: uses class-specific disease color priors to suppress green leaf/background regions and intersect with GradCAM evidence. |

## Deprecated Experiment

V4 is not part of default comparison. It combined leaf masking and bilateral
smoothing, so the branch changes too many variables at once and is difficult to
present as a clean ablation. Its notebook, masks, processed images, and model
artifacts are moved under `deprecated/` folders so they remain recoverable
without competing with the active V1/V2/V3/V5 storyline.

## Archived During Cleanup

Temporary chunks, old drafts, sample20 debug outputs, root-level visualization
duplicates, unrelated internship documents, and a V4 resume checkpoint were
moved to `_repo_cleanup_archive/2026-08-24/`. Exploratory V4 artifacts that may
still be useful for explanation were moved to `notebooks/*/deprecated/`. This
keeps the active project focused while preserving recoverability.

## Presentation Guidance

In the thesis defense, present V1, V2, V3, and V5 as the main experimental
story. Mention V4 only briefly as an exploratory branch that was rejected
because it was not a clean controlled experiment.
