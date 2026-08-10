<#
.SYNOPSIS
    Biên dịch luận văn thành docs/thesis/thesis.pdf.

.DESCRIPTION
    Dùng Tectonic — một trình biên dịch LaTeX gọn trong đúng một tệp .exe, tự tải
    các gói cần thiết, không cần quyền quản trị và không cần cài TeX Live.
    Nếu chưa có tectonic.exe trong thư mục tools/, script sẽ tự tải về.

    Tài liệu bắt buộc dùng engine XeTeX (vì có fontspec + polyglossia cho tiếng
    Việt); Tectonic mặc định chạy XeTeX nên không cần cấu hình thêm.

.PARAMETER Clean
    Xoá toàn bộ tệp trung gian trước khi biên dịch. Dùng khi mục lục hoặc tham
    chiếu chéo bị sai lệch sau nhiều lần sửa.

.PARAMETER KeepIntermediates
    Giữ lại các tệp trung gian (.aux, .log, .bbl...) để chẩn đoán lỗi.

.EXAMPLE
    .\build.ps1
    .\build.ps1 -Clean
#>

[CmdletBinding()]
param(
    [switch]$Clean,
    [switch]$KeepIntermediates
)

$ErrorActionPreference = 'Stop'
Set-Location -Path $PSScriptRoot

$TectonicVersion = '0.17.0'
$ToolsDir  = Join-Path $PSScriptRoot 'tools'
$Tectonic  = Join-Path $ToolsDir 'tectonic.exe'
$OutputPdf = Join-Path $PSScriptRoot 'thesis.pdf'

# --- Tệp trung gian do LaTeX sinh ra -----------------------------------------
$Intermediates = @(
    'main.aux', 'main.bbl', 'main.blg', 'main.log', 'main.out',
    'main.toc', 'main.lof', 'main.lot', 'main.run.xml', 'main-blx.bib',
    'main.xdv'
)

function Write-Step($msg) { Write-Host "==> $msg" -ForegroundColor Cyan }
function Write-Ok($msg)   { Write-Host "    $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "    $msg" -ForegroundColor Yellow }

# --- 1. Bảo đảm có Tectonic ---------------------------------------------------
if (-not (Test-Path $Tectonic)) {
    Write-Step "Chưa có Tectonic — đang tải về (khoảng 20 MB)..."
    New-Item -ItemType Directory -Force -Path $ToolsDir | Out-Null

    $url = "https://github.com/tectonic-typesetting/tectonic/releases/download/" +
           "tectonic%40$TectonicVersion/tectonic-$TectonicVersion-x86_64-pc-windows-msvc.zip"
    $zip = Join-Path $ToolsDir 'tectonic.zip'

    try {
        Invoke-WebRequest -Uri $url -OutFile $zip -TimeoutSec 300
        Expand-Archive -Path $zip -DestinationPath $ToolsDir -Force
        Remove-Item $zip -Force
        Write-Ok "Đã cài Tectonic $TectonicVersion"
    }
    catch {
        Write-Host "LỖI: không tải được Tectonic. $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Cách khác: tải thủ công từ https://github.com/tectonic-typesetting/tectonic/releases"
        Write-Host "rồi giải nén tectonic.exe vào thư mục: $ToolsDir"
        exit 1
    }
}

# --- 2. Dọn dẹp nếu được yêu cầu ----------------------------------------------
if ($Clean) {
    Write-Step 'Xoá tệp trung gian'
    $Intermediates | ForEach-Object {
        if (Test-Path $_) { Remove-Item $_ -Force }
    }
    Write-Ok 'Đã xoá'
}

# --- 3. Kiểm tra cấu trúc nguồn trước khi biên dịch ---------------------------
$checker = Join-Path $PSScriptRoot 'check_tex.py'
$venvPy  = Join-Path $PSScriptRoot '..\..\venv\Scripts\python.exe'
if ((Test-Path $checker) -and (Test-Path $venvPy)) {
    Write-Step 'Kiểm tra cấu trúc nguồn LaTeX'
    & $venvPy $checker
    if ($LASTEXITCODE -ne 0) {
        Write-Host 'LỖI: phát hiện lỗi cấu trúc — dừng lại trước khi biên dịch.' -ForegroundColor Red
        exit 1
    }
}

# --- 4. Biên dịch -------------------------------------------------------------
# Chạy HAI lượt. Lượt đầu sinh .aux/.toc/.bbl; lượt hai mới có đủ dữ liệu để
# đánh đúng số trang trong mục lục, danh mục hình và danh mục bảng. Thiếu lượt
# thứ hai, số trang trong mục lục sẽ lệch so với thực tế.
$tectonicArgs = @('-X', 'compile', 'main.tex', '--keep-logs', '--keep-intermediates')

# Lọc bỏ các dòng nhiễu không liên quan tới chất lượng bản in:
#  - đường dẫn font hệ thống (Tectonic cảnh báo về tính tái lập)
#  - lỗi fontconfig của Windows
#  - cảnh báo UTF-8 phát sinh từ chính tệp anyfontsize.sty (mã hoá Latin-1)
$noise = 'accessing absolute path|Fontconfig error|anyfontsize\.sty|Invalid UTF-8'

foreach ($pass in 1, 2) {
    $hint = if ($pass -eq 1) { ' — lần đầu có thể mất vài phút do phải tải gói LaTeX' } else { '' }
    Write-Step "Biên dịch lượt $pass/2$hint"

    $output = & $Tectonic @tectonicArgs 2>&1
    $exit = $LASTEXITCODE

    if ($pass -eq 2) {
        $output | Where-Object { $_ -notmatch $noise } | ForEach-Object { Write-Host "    $_" }
    }

    if ($exit -ne 0) {
        Write-Host 'LỖI: biên dịch thất bại. Xem chi tiết trong main.log' -ForegroundColor Red
        $output | Where-Object { $_ -match '^error|! ' } | ForEach-Object { Write-Host "    $_" -ForegroundColor Red }
        exit 1
    }
}

if (-not (Test-Path 'main.pdf')) {
    Write-Host 'LỖI: không sinh được tệp PDF. Xem chi tiết trong main.log' -ForegroundColor Red
    exit 1
}

# --- 5. Đổi tên kết quả -------------------------------------------------------
Move-Item -Path 'main.pdf' -Destination $OutputPdf -Force

# --- 6. Báo cáo ---------------------------------------------------------------
Write-Step 'Kết quả'

$pages = '?'
if (Test-Path 'main.log') {
    $m = Select-String -Path 'main.log' -Pattern 'Output written on .*\((\d+) pages'
    if ($m) { $pages = $m.Matches.Groups[1].Value }
}
$sizeMb = [math]::Round((Get-Item $OutputPdf).Length / 1MB, 2)

Write-Ok "Tệp   : $OutputPdf"
Write-Ok "Số trang: $pages"
Write-Ok "Dung lượng: $sizeMb MB"

if (Test-Path 'main.log') {
    $overfull = (Select-String -Path 'main.log' -Pattern 'Overfull \\[hv]box').Count
    if ($overfull -gt 0) { Write-Warn "Số hộp tràn lề (chỉ ảnh hưởng thẩm mỹ): $overfull" }

    $todo = 0
    Get-ChildItem -Recurse -Include '*.tex' -Path $PSScriptRoot |
        ForEach-Object { $todo += (Select-String -Path $_.FullName -Pattern '\\TODO\{').Count }
    if ($todo -gt 0) { Write-Warn "Số mục \TODO còn phải bổ sung: $todo" }
}

# --- 7. Ghi chú về tệp trung gian ---------------------------------------------
# CỐ Ý GIỮ LẠI các tệp trung gian: chúng cho phép lần biên dịch sau hội tụ ngay
# và chạy nhanh hơn nhiều. Toàn bộ đã được liệt kê trong .gitignore nên không
# lọt vào kho mã nguồn. Dùng tham số -Clean khi cần dựng lại hoàn toàn từ đầu.

Write-Host ''
Write-Host 'HOÀN TẤT' -ForegroundColor Green
