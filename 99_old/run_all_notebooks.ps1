$ErrorActionPreference = 'Continue'
$python  = "e:\Master\thesis-clean\venv\Scripts\python.exe"
$nb_dir  = "e:\Master\thesis-clean\notebooks"
$log_dir = "e:\Master\thesis-clean\notebooks\outputs\run_logs"
New-Item -ItemType Directory -Force -Path $log_dir | Out-Null

$notebooks = @(
    "01-data-exploration.ipynb",
    "02-classification-baseline.ipynb",
    "03-xai-gradcam-analysis.ipynb",
    "04-pseudo-labeling.ipynb",
    "05-segmentation-model.ipynb",
    "07-pseudo-labeling-v2.ipynb",
    "08-segmentation-v2.ipynb",
    "09-segmentation-v3-sam.ipynb",
    "06-model-evaluation-fixed.ipynb",
    "10-inference-single-image.ipynb"
)

$total   = $notebooks.Count
$success = 0
$failed  = @()

foreach ($nb in $notebooks) {
    $nb_path  = Join-Path $nb_dir $nb
    $log_name = $nb -replace '\.ipynb$', '.log'
    $log_path = Join-Path $log_dir $log_name

    Write-Host ""
    Write-Host "[$([datetime]::Now.ToString('HH:mm:ss'))] Running: $nb" -ForegroundColor Cyan

    & $python -m jupyter nbconvert `
        --to notebook `
        --execute `
        --inplace `
        --ExecutePreprocessor.timeout=36000 `
        --ExecutePreprocessor.kernel_name=python3 `
        $nb_path 2>&1 | Tee-Object -FilePath $log_path

    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK] $nb" -ForegroundColor Green
        $success++
    } else {
        Write-Host "  [FAIL] $nb  (exit $LASTEXITCODE) — log: $log_path" -ForegroundColor Red
        $failed += $nb
    }
}

Write-Host ""
Write-Host "=" * 60
Write-Host "DONE: $success / $total notebooks succeeded"
if ($failed.Count -gt 0) {
    Write-Host "Failed:" -ForegroundColor Red
    $failed | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
}
Write-Host "Logs: $log_dir"
