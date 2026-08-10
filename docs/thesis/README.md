# Luận văn thạc sĩ — mã nguồn LaTeX

Phát hiện và phân đoạn bệnh lá sầu riêng bằng học sâu kết hợp AI khả diễn giải và gán nhãn giả.

---

## Cách build

Có hai cách, cả hai đều đã được kiểm chứng và cho ra cùng một kết quả.

### Cách 1 — Build tại máy bằng `build.ps1` (khuyến nghị)

```powershell
cd docs\thesis
.\build.ps1
```

Chỉ vậy. Script tự lo mọi thứ:

1. Tải **Tectonic** (một tệp `.exe` ~20 MB, không cần quyền quản trị, không cần cài TeX Live) vào `tools/` nếu chưa có.
2. Chạy `check_tex.py` để bắt lỗi cấu trúc *trước khi* biên dịch.
3. Biên dịch **hai lượt** — bắt buộc, vì lượt đầu mới sinh `.aux`/`.toc`/`.bbl`, lượt hai mới đánh đúng số trang trong mục lục.
4. Xuất ra **`docs/thesis/thesis.pdf`**.
5. Báo lại số trang, dung lượng, số hộp tràn lề và số mục `\TODO` còn phải bổ sung.

Tham số tuỳ chọn:

| Tham số | Tác dụng |
|---|---|
| `-Clean` | Xoá sạch tệp trung gian rồi dựng lại từ đầu. Dùng khi mục lục hoặc tham chiếu chéo bị sai lệch. |
| `-KeepIntermediates` | Giữ lại `.aux`, `.bbl`… để chẩn đoán lỗi (mặc định đã giữ). |

**Lần chạy đầu tiên** mất vài phút vì Tectonic phải tải các gói LaTeX cần thiết; các lần sau chỉ khoảng 30–60 giây.

> Vì sao chọn Tectonic mà không phải MiKTeX hay TeX Live: máy này không có `winget`,
> và Tectonic chỉ là một tệp thực thi duy nhất, tự tải đúng những gói cần dùng, không
> đụng tới hệ thống. Thư mục `tools/` đã được đưa vào `.gitignore`.

### Cách 2 — Trên Overleaf

1. Nén cả thư mục `docs/thesis/` thành file `.zip`:
   ```powershell
   Compress-Archive -Path docs\thesis\* -DestinationPath thesis.zip -Force
   ```
   *(Có thể loại `check_tex.py` và `README.md` khỏi gói — chúng không ảnh hưởng đến biên dịch.)*

2. Vào Overleaf → **New Project** → **Upload Project** → chọn `thesis.zip`.

3. ⚠️ **BẮT BUỘC — bước hay bị bỏ sót nhất:** Menu (góc trên bên trái) → **Compiler** → chọn **XeLaTeX**.

   Dòng `% !TeX program = xelatex` ở đầu `main.tex` giúp Overleaf tự chọn, nhưng
   **nếu project đã được tạo trước đó với pdfLaTeX thì thiết lập cũ vẫn được giữ** —
   phải đổi thủ công.

4. Menu → **Main document** → chọn `main.tex`.

5. Nhấn **Recompile** **hai lần** để mục lục, danh mục hình/bảng và tham chiếu chéo hiện đúng.

Tài liệu dùng `backend=bibtex` cho biblatex nên chạy được cả khi không có `biber`.
Nếu muốn dùng `biber` trên Overleaf (chất lượng sắp xếp tốt hơn), đổi dòng khai báo
`biblatex` trong `preamble.tex` thành `backend=biber`.

### Nếu có sẵn TeX Live hoặc MiKTeX trên máy

```powershell
cd docs\thesis
latexmk -xelatex main.tex
```

---

## Bản Word (`.docx`)

```powershell
cd docs\thesis
.\build-docx.ps1
```

Xuất ra **`docs/thesis/thesis.docx`** (~33 MB, khoảng 124 trang).

**Không có bản thảo thứ hai.** Bản Word được sinh từ đúng `chapters/*.tex` đang
dùng cho bản PDF; sửa nội dung ở đâu thì cả hai bản đều đổi theo. Đừng sửa trực
tiếp vào `thesis.docx` — lần build sau sẽ ghi đè.

Công cụ cần có:

| Công cụ | Bắt buộc? | Dùng để làm gì |
|---|---|---|
| [Pandoc](https://pandoc.org/installing.html) | ✅ bắt buộc | chuyển LaTeX → docx |
| `tools/tectonic.exe` | tuỳ chọn | dựng sơ đồ TikZ ở Hình 3.1 (`build.ps1` tự tải) |
| PyMuPDF (`pip install pymupdf`) | tuỳ chọn | chuyển sơ đồ đó thành ảnh |

Thiếu hai công cụ tuỳ chọn thì bản `.docx` vẫn dựng được, riêng sơ đồ quy trình
bị thay bằng một ghi chú màu đỏ.

### Mở lần đầu

Word sẽ hỏi **"Update fields?"** — chọn **Yes** để mục lục điền số trang. Nếu lỡ
chọn No: bấm `Ctrl+A` rồi `F9`.

### Pandoc không hiểu được gì, và đã xử lý ra sao

`make_docx.py` chép nguồn sang `_docx/` rồi tiền xử lý bản chép — **nguồn gốc
không bị sửa**. Các điểm phải bù:

| Cấu trúc LaTeX | Pandoc làm gì | Cách xử lý |
|---|---|---|
| Cột bảng `L{} C{} R{}` (`\newcolumntype`) | bỏ luôn cả bảng — mất 23/45 bảng | đổi thành `p{..\textwidth}` / `c` / `r` |
| Độ rộng cột tuyệt đối (`3,6cm`) | bỏ qua, chia đều mọi cột | quy sang tỉ lệ của `\textwidth` |
| `\en{}` lồng trong `\text{}` của công thức | in ra cả khối công thức dưới dạng mã nguồn | tách thành `\mathit{}` |
| `\num{4437}` | ra `4437` | tự định dạng theo `\sisetup` → `4.437` |
| `tikzpicture` | bỏ, chỉ còn chú thích hình | dựng sẵn thành PNG bằng Tectonic |
| `\appendix` | đánh số tiếp 6, 7, 8, 9 | ghi thẳng "PHỤ LỤC A", "A.1" vào tiêu đề |
| `\tableofcontents` | chỉ đặt được ở đầu tệp | chèn trường TOC của Word đúng vị trí |
| `\printbibliography` | đẩy tham khảo xuống sau phụ lục | chuyển khối tham khảo về trước phụ lục |
| `biblatex` style IEEE | không dùng được | `--citeproc` với `ieee-numeric.csl` kèm theo |
| `\clearpage`, `\\[2.5cm]` ở trang bìa | bỏ hết, dồn bìa thành một đoạn | tách dòng, căn giữa, chèn ngắt trang |

### Khác biệt còn lại so với bản PDF

| Điểm | Ghi chú |
|---|---|
| **Không có Danh mục hình vẽ / bảng biểu** | Chú thích do Pandoc sinh ra không có trường `SEQ` nên Word không lập được hai danh mục này. Muốn có: trong Word chọn References → Insert Caption cho từng hình, rồi Insert Table of Figures. |
| **Trang bìa canh chưa khớp** | Các khoảng trống dọc (`\vspace{2,5cm}`) không chuyển sang được. Phần này toàn `\TODO` nên sẽ phải chỉnh theo template của trường. |
| **Số trang lệch** | 124 trang so với bản PDF — do Word ngắt trang khác. |

### Xử lý sự cố

| Thông báo lỗi | Nguyên nhân | Cách khắc phục |
|---|---|---|
| `fontspec requires either XeTeX or LuaTeX` | Đang dùng pdfLaTeX | Overleaf: Menu → Compiler → **XeLaTeX** |
| `The font "TeX Gyre Termes" cannot be found` | Trình biên dịch không dùng fontconfig | Đã xử lý sẵn: font được nạp theo **tên tệp** `.otf` chứ không theo tên hệ thống |
| `Undefined control sequence \renewcaptionname` | `polyglossia` bản cũ | Đã xử lý sẵn: dùng `\AtBeginDocument` thay cho `\renewcaptionname` |
| `Command \crefpairconjunction undefined` | `cleveref` không nhận ngôn ngữ `vietnamese` | Đã xử lý sẵn: nạp `cleveref` với tuỳ chọn `english` rồi Việt hoá liên từ trong `\AtBeginDocument` |
| `program not found` khi chạy biber | Máy không có `biber` | Đã xử lý sẵn: dùng `backend=bibtex` |
| `Bibliography string 'and' untranslated` | Không có `vietnamese.lbx` | Đã xử lý sẵn: `\DeclareLanguageMapping{vietnamese}{english}` |
| Chữ nhỏ bất thường dù khai báo 13pt | `extsizes` không hỗ trợ đúng 13pt | Đã xử lý sẵn: cỡ chữ đặt qua gói `fontsize`, không qua tuỳ chọn `\documentclass` |
| Mục lục trống hoặc trích dẫn hiện `[?]` | Mới biên dịch một lượt | Chạy lượt thứ hai (`build.ps1` đã tự làm) |

---

## Kiểm tra trước khi build

Vì không biên dịch được tại chỗ, dùng bộ kiểm tra cấu trúc kèm theo:

```powershell
.\venv\Scripts\python.exe docs\thesis\check_tex.py
```

Nó bắt các lỗi sau mà không cần TeX engine:

| # | Kiểm tra |
|---|---|
| 1 | Lệch dấu ngoặc nhọn `{}` |
| 2 | Lệch `\begin{...}` / `\end{...}` |
| 3 | `\input` trỏ tới file không tồn tại |
| 4 | `\includegraphics` trỏ tới hình không có trong `figures/` |
| 5 | `\cite` dùng khoá không có trong `refs.bib` |
| 6 | `\ref` / `\cref` trỏ tới nhãn chưa được định nghĩa |
| 7 | Ký tự `&`, `_`, `#` có thể chưa escape |

Nó cũng liệt kê những hình đã copy vào `figures/` nhưng chưa được dùng ở chương nào.

Quy trình khuyến nghị: **chạy `check_tex.py` trước, sạch lỗi rồi mới upload Overleaf.**

---

## Cấu trúc thư mục

```
docs/thesis/
├── main.tex                    # file chính — bìa, mục lục, gọi các chương
├── preamble.tex                # TOÀN BỘ định dạng: font, lề, màu, macro, TikZ
├── refs.bib                    # thư mục tham khảo (biblatex, style IEEE)
├── check_tex.py                # bộ kiểm tra cấu trúc
├── build.ps1                   # dựng thesis.pdf  (Tectonic)
├── build-docx.ps1              # dựng thesis.docx (Pandoc)
├── make_docx.py                # tiền xử lý + hậu xử lý cho bản Word
├── ieee-numeric.csl            # kiểu trích dẫn IEEE cho bản Word
├── INVENTORY.md                # ★ kiểm kê số liệu — nguồn sự thật duy nhất
├── chapters/
│   ├── 00-abbreviations.tex    # danh mục từ viết tắt
│   ├── 01-mo-dau.tex           # Chương 1 — Mở đầu
│   ├── 02-co-so-ly-thuyet.tex  # Chương 2 — Cơ sở lý thuyết
│   ├── 03-phuong-phap.tex      # Chương 3 — Phương pháp đề xuất
│   ├── 04-thuc-nghiem.tex      # Chương 4 — Thực nghiệm và kết quả
│   └── 05-ket-luan.tex         # Chương 5 — Kết luận
├── appendix/
│   ├── A-hyperparameters.tex   # bảng siêu tham số đầy đủ
│   ├── B-training-logs.tex     # nhật ký huấn luyện
│   ├── C-demo-app.tex          # ứng dụng minh hoạ (app.py)
│   └── D-reproduce.tex         # hướng dẫn tái tạo kết quả
└── figures/                    # 24 hình, ~33 MB — bản COPY, không link ra ngoài
```

### Nguyên tắc tổ chức

- **Nội dung tách khỏi định dạng.** Các file trong `chapters/` không chứa lệnh
  định dạng riêng. Nếu trường yêu cầu template khác, chỉ cần thay `preamble.tex`.
- **Hình được COPY vào `figures/`**, không trỏ ra ngoài kho mã nguồn. Nhờ đó thư
  mục `docs/thesis/` là một gói độc lập, upload lên Overleaf là chạy được.
- **Mọi con số phải truy vết được về `INVENTORY.md`.** Không có ngoại lệ.

---

## Về `INVENTORY.md`

Đây là tài liệu quan trọng nhất trong thư mục này. Nó ghi lại:

- **Bảng số liệu đã xác minh** — mỗi giá trị kèm notebook và ô lệnh đã sinh ra nó.
- **Bảng hình khả dụng** — kích thước, nội dung, và danh sách hình **không được dùng** kèm lý do.
- **Danh sách lỗ hổng (GAPS)** — 15 điểm mà bài báo `paper_ijai.tex` / `paper_content.md`
  nêu số liệu không khớp với output thực tế của notebook, kèm giá trị đúng.

Ba sai lệch lớn nhất so với bài báo đã công bố:

| | Bài báo nêu | Giá trị đúng |
|---|---|---|
| Test accuracy phân loại | 97,52 % | **97,30 %** (val tốt nhất là 98,19 %) |
| Chia tập dữ liệu | 70/15/15 (3.104/665/668) | **70/10/20 (3.104/443/890)** |
| Pseudo-label V1 | 500 ảnh | **3.104 ảnh** |

Khi viết thêm bất kỳ nội dung nào, **tra `INVENTORY.md` trước**. Nếu số cần dùng
không có trong đó thì đánh dấu `\TODO{...}` chứ không tự điền.

---

## Quy ước soạn thảo

- **Ngôn ngữ:** tiếng Việt học thuật, ngôi trung tính (không dùng "tôi/chúng tôi"
  trong phần trình bày kỹ thuật; riêng Lời cam đoan dùng ngôi thứ nhất theo thông lệ).
- **Thuật ngữ tiếng Anh** giữ nguyên, bọc trong `\en{...}` ở lần xuất hiện đầu
  (in nghiêng) kèm giải thích tiếng Việt trong ngoặc.
- **Số thập phân** dùng dấu phẩy: `0,6239`. Số lớn dùng `\num{4437}` → `4.437`.
- **Tham chiếu chéo** dùng `\cref{}` / `\Cref{}` chứ không viết tay "Hình 3.1".
- **Việc còn thiếu** đánh dấu bằng `\TODO{mô tả cụ thể cần bổ sung gì}` — macro
  này in một khối vàng nổi bật, không thể bỏ sót khi rà soát lần cuối.

### Macro có sẵn

| Macro | Kết quả |
|---|---|
| `\EffNet` | EfficientNet-B0 |
| `\GradCAM` / `\GradCAMpp` | Grad-CAM / Grad-CAM++ |
| `\UNetpp` | UNet++ |
| `\SAM` | SAM |
| `\en{...}` | in nghiêng thuật ngữ tiếng Anh |
| `\TODO{...}` | khối ghi chú việc còn thiếu |

---

## Tiến độ

| Phần | Trạng thái |
|---|---|
| Khung LaTeX, preamble, refs.bib, figures/ | ✅ xong |
| Danh mục từ viết tắt | ✅ xong |
| Chương 1 — Mở đầu | ✅ xong |
| Chương 2 — Cơ sở lý thuyết | ✅ xong |
| Chương 3 — Phương pháp | ✅ xong |
| Chương 4 — Thực nghiệm | ✅ xong |
| Chương 5 — Kết luận | ✅ xong |
| Phụ lục A–D | ✅ xong |
| Trang bìa (tên trường, học viên, người hướng dẫn) | ⬜ chờ thông tin |
| Nguồn gốc bộ dữ liệu | ⬜ chờ thông tin (xem GAP G-12) |
