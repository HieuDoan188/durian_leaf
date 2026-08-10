<#
.SYNOPSIS
    Biên dịch luận văn thành docs/thesis/thesis.docx.

.DESCRIPTION
    Bản Word được sinh ra từ ĐÚNG nguồn LaTeX đang dùng cho bản PDF — không có
    bản thảo thứ hai phải đồng bộ bằng tay. Mọi sửa đổi chỉ cần thực hiện trong
    chapters/*.tex, sau đó chạy lại script này.

    Công cụ dùng đến:
      - Pandoc           bắt buộc — tải tại https://pandoc.org/installing.html
      - PyMuPDF (pip)    tuỳ chọn — chỉ cần cho sơ đồ TikZ ở Hình 3.1
      - tools/tectonic   tuỳ chọn — chỉ cần cho sơ đồ TikZ ở Hình 3.1
                         (build.ps1 tự tải về trong lần biên dịch PDF đầu tiên)

    Thiếu hai công cụ tuỳ chọn thì bản .docx vẫn dựng được, chỉ riêng sơ đồ quy
    trình bị thay bằng một ghi chú màu đỏ.

.PARAMETER KeepIntermediates
    Giữ lại thư mục trung gian _docx/ để đối chiếu khi kết quả có chỗ bất thường.
    Thư mục này chứa bản .tex đã tiền xử lý mà Pandoc thực sự đọc.

.EXAMPLE
    .\build-docx.ps1
    .\build-docx.ps1 -KeepIntermediates
#>

[CmdletBinding()]
param(
    [switch]$KeepIntermediates
)

$ErrorActionPreference = 'Stop'
Set-Location -Path $PSScriptRoot

function Write-Step($msg) { Write-Host "==> $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "    $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "    $msg" -ForegroundColor Yellow }

# --- 1. Chọn trình thông dịch Python -----------------------------------------
# Ưu tiên bản có sẵn PyMuPDF, vì chỉ bản đó dựng được sơ đồ TikZ thành ảnh.
$candidates = @(
    (Join-Path $PSScriptRoot '..\..\venv\Scripts\python.exe'),
    (Get-Command python -ErrorAction SilentlyContinue).Source,
    (Get-Command py -ErrorAction SilentlyContinue).Source
) | Where-Object { $_ -and (Test-Path $_) }

if (-not $candidates) {
    Write-Host 'LỖI: không tìm thấy Python.' -ForegroundColor Red
    exit 1
}

$python = $candidates[0]
foreach ($c in $candidates) {
    & $c -c 'import fitz' 2>$null
    if ($LASTEXITCODE -eq 0) { $python = $c; break }
}

& $python -c 'import fitz' 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Warn 'Chưa cài PyMuPDF — sơ đồ quy trình (Hình 3.1) sẽ bị thiếu.'
    Write-Warn "Khắc phục: $python -m pip install pymupdf"
}

# --- 2. Kiểm tra cấu trúc nguồn trước khi chuyển đổi --------------------------
$checker = Join-Path $PSScriptRoot 'check_tex.py'
if (Test-Path $checker) {
    Write-Step 'Kiểm tra cấu trúc nguồn LaTeX'
    & $python $checker | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host 'LỖI: phát hiện lỗi cấu trúc — chạy check_tex.py để xem chi tiết.' -ForegroundColor Red
        exit 1
    }
    Write-Ok 'OK'
}

# --- 3. Chuyển đổi ------------------------------------------------------------
# PYTHONIOENCODING: bảng điều khiển Windows mặc định dùng cp1252, không in được
# tiếng Việt có dấu trong thông báo tiến trình.
$env:PYTHONIOENCODING = 'utf-8'
& $python (Join-Path $PSScriptRoot 'make_docx.py')
$exit = $LASTEXITCODE

# --- 4. Dọn thư mục trung gian ------------------------------------------------
if (-not $KeepIntermediates -and (Test-Path '_docx')) {
    Remove-Item '_docx' -Recurse -Force
}

if ($exit -ne 0) { exit $exit }

Write-Host ''
Write-Warn 'Lần mở đầu tiên, Word sẽ hỏi "Update fields?" — chọn Yes để điền mục lục.'
