# INVENTORY — Kiểm kê dữ liệu, số liệu và hình ảnh

> **Mục đích.** Đây là **nguồn sự thật duy nhất** cho mọi con số và hình ảnh xuất hiện trong luận văn.
> Mọi giá trị trong các chương phải truy vết được về một dòng trong file này.
> Ngày lập: 2026-07-26. Repo: `e:\Master\thesis-clean` (branch `main`, commit `82055f5`).
>
> **Quy ước ký hiệu nguồn:**
> - `NB0x[c##]` = notebook số `0x`, cell index `##` (theo thứ tự cell trong file `.ipynb`, tính từ 0), giá trị lấy từ **output cell đã thực thi**.
> - `NB0x[md]` = chỉ có trong **markdown narration**, KHÔNG có output cell chứng minh → mức tin cậy thấp.
> - `JSON:<path>` = đọc trực tiếp từ file kết quả đã lưu trên đĩa.
> - `RECOMPUTED` = người viết tính lại trực tiếp từ artefact trên đĩa (script kiểm chứng, xem §5).

---

## 0. Bản đồ notebook (tên file thực tế ≠ README)

README.md và `run_all_notebooks.ps1` mô tả một cách đánh số khác với tên file thực tế trên đĩa.
Bảng dưới là **tên file thực tế** — luận văn sẽ dùng cách đánh số này.

| # | File thực tế | Vai trò | Trạng thái output |
|---|---|---|---|
| 01 | `01-data-exploration.ipynb` | EDA | ✅ đầy đủ |
| 02 | `02-classification-baseline.ipynb` | EfficientNet-B0 classification | ✅ đầy đủ |
| 03 | `03-xai-gradcam-analysis.ipynb` | Grad-CAM trên 3.104 ảnh train | ✅ đầy đủ |
| 04 | `04-pseudo-labeling.ipynb` | Pseudo-label V1 | ✅ đầy đủ |
| 05 | `05-segmentation-model.ipynb` | Segmentation V1 (EfficientNet-UNet) | ✅ đầy đủ |
| 06 | `06-pseudo-labeling-v2.ipynb` | Pseudo-label V2 (GradCAM++ multi-scale) | ✅ đầy đủ |
| 07 | `07-segmentation-v2.ipynb` | Segmentation V2 (UNet++) | ✅ đầy đủ |
| 08 | `08-segmentation-v3-sam.ipynb` | SAM refinement + Segmentation V3 | ⚠️ một phần (xem G-08) |
| 09 | `09-segmentation-v4-crf.ipynb` | Pseudo-label V4.1 + Segmentation V4 | ❌ training bị ngắt (xem G-09) |
| 10 | `10-inference-single-image.ipynb` | Inference 1 ảnh | ✅ đã sửa & chạy lại 2026-07-26 (G-10) |

> `README.md` liệt kê `06-model-evaluation.ipynb` và `run_all_notebooks.ps1` gọi `06-model-evaluation-fixed.ipynb` — **cả hai file này KHÔNG tồn tại** trong repo. Xem G-01.

---

## 1. BẢNG SỐ LIỆU ĐÃ XÁC MINH

### 1.1 Dataset

| Đại lượng | Giá trị | Nguồn |
|---|---|---|
| Tổng số ảnh | 4.437 | NB01[c7], NB01[c35] |
| Số lớp | 5 | NB01[c9] |
| Algal Leaf Spot (tổng) | 733 (16,5 %) | NB01[c9], NB01[c35] |
| Allocaridara Attack (tổng) | 913 (20,6 %) | NB01[c9] |
| Healthy Leaf (tổng) | 976 (22,0 %) | NB01[c9] |
| Leaf Blight (tổng) | 937 (21,1 %) | NB01[c9] |
| Phomopsis Leaf Spot (tổng) | 878 (19,8 %) | NB01[c9] |
| Imbalance ratio (max/min) | 1,33 | NB01[c10] |
| **Split classification** | **Train 3.104 / Val 443 / Test 890** | NB01[c7], NB01[c13], NB02[c4] |
| Tỉ lệ split thực tế | 70,0 % / 10,0 % / 20,1 % | NB01[c13] |
| Train — Algal Leaf Spot | 513 ảnh | NB03[c4], NB04[c3], NB06[c3], NB09[c4] |
| Train — Allocaridara Attack | 639 ảnh | NB03[c4] |
| Train — Healthy Leaf | 683 ảnh | NB03[c4] |
| Train — Leaf Blight | 655 ảnh | NB03[c4] |
| Train — Phomopsis Leaf Spot | 614 ảnh | NB03[c4] |
| Kích thước ảnh | 224 × 224, aspect ratio = 1,0, std = 0 (toàn bộ mẫu 100 ảnh) | NB01[c25] |
| Dung lượng file trung bình | 10,9 KB (std 1,0; min 8,5; max 14,3) — mẫu 100 ảnh | NB01[c25] |
| Dung lượng file (mẫu 250 ảnh) | mean 11,36 KB; std 0,80; min 8,91; max 15,07 | NB01[c26] |
| **Split segmentation** (dùng chung V1–V4) | **2.172 train / 465 val / 467 test** (từ 3.104), seed = 42 | NB05[c4], NB07[c7], NB08[c13], NB09[c16] |

**Mean RGB per class** (mẫu 30 ảnh/lớp) — NB01[c22]:

| Lớp | R | G | B |
|---|---|---|---|
| Algal Leaf Spot | 95,8 | 125,8 | 106,6 |
| Allocaridara Attack | 94,4 | 134,5 | 98,9 |
| Healthy Leaf | 96,4 | 133,0 | 92,1 |
| Leaf Blight | 103,5 | 137,8 | 107,2 |
| Phomopsis Leaf Spot | 97,2 | 138,6 | 88,5 |

**Kiểm tra pipeline DataLoader** — NB01[c31]: batch `[32, 3, 224, 224]`, giá trị pixel sau normalize ∈ [−2,118 ; 2,640], channel means `[−0,6184 ; 0,0006 ; −0,3201]`, channel stds `[1,0298 ; 1,0201 ; 1,0387]`.

---

### 1.2 Classification — EfficientNet-B0 (NB02)

**Cấu hình đã xác minh** — NB02[c4], NB02[c6], NB02[c8]:

| Tham số | Giá trị thực tế | Nguồn |
|---|---|---|
| Backbone | EfficientNet-B0, ImageNet pretrained, fine-tune toàn bộ | NB02[c6] |
| Head | Dropout(0,2) + Linear(1280 → 5) | `utils/models.py:19` |
| Optimizer | Adam, lr = 1e-4 | NB02[c6] |
| Scheduler | ReduceLROnPlateau(mode='max', patience=2, factor=0.5) trên `val_acc` | NB02[c6] |
| Loss | CrossEntropyLoss | NB02[c6] |
| **Batch size** | **16** | NB02[c4] |
| **Max epochs** | **50** | NB02[c8] |
| **Early stopping** | **patience = 5** trên `val_acc`, kích hoạt tại **epoch 16** | NB02[c8] |
| Augmentation | flip, crop, color jitter (qua `utils/preprocessing.py`) | NB02[md c3] |

**Đường cong huấn luyện đầy đủ 16 epoch** — NB02[c8] (dùng để vẽ lại nếu cần):

| Epoch | train_loss | train_acc | val_loss | val_acc |
|---|---|---|---|---|
| 1 | 1,0963 | 0,5892 | 0,4712 | 0,8623 |
| 2 | 0,4369 | 0,8547 | 0,2316 | 0,9187 |
| 3 | 0,2740 | 0,9056 | 0,1820 | 0,9368 |
| 4 | 0,2293 | 0,9249 | 0,1222 | 0,9616 |
| 5 | 0,1906 | 0,9327 | 0,1175 | 0,9639 |
| 6 | 0,1602 | 0,9478 | 0,1017 | 0,9684 |
| 7 | 0,1487 | 0,9507 | 0,1356 | 0,9503 |
| 8 | 0,1220 | 0,9597 | 0,0926 | 0,9729 |
| 9 | 0,1130 | 0,9613 | 0,0887 | 0,9729 |
| 10 | 0,0989 | 0,9662 | 0,0890 | **0,9752** |
| **11** | 0,0977 | 0,9671 | 0,0811 | **0,9819 ← best** |
| 12 | 0,0820 | 0,9729 | 0,0910 | 0,9774 |
| 13 | 0,0791 | 0,9771 | 0,1023 | 0,9684 |
| 14 | 0,0747 | 0,9758 | 0,1108 | 0,9729 |
| 15 | 0,0559 | 0,9800 | 0,1050 | 0,9616 |
| 16 | 0,0476 | 0,9858 | 0,0831 | 0,9684 |

**Kết quả cuối** — NB02[c8], NB02[c14], `JSON:notebooks/models/classification/metrics/test_metrics.json`:

| Metric | Giá trị | Nguồn |
|---|---|---|
| **Best val accuracy** | **98,19 %** (epoch 11) | NB02[c8], NB02[c12], `JSON:.../training_history.json` |
| **Test accuracy** | **97,30 %** (866/890) | NB02[c14], NB02[c17] |
| Test precision (weighted) | 97,344 % | NB02[c14] |
| Test recall (weighted) | 97,303 % | NB02[c14] |
| Test macro/weighted F1 | 97,312 % | NB02[c14] |
| Số mẫu test | 890 | NB02[c14] |

**Per-class trên test set** — NB02[c14]:

| Lớp | Precision | Recall | F1 | Số mẫu (tổng hàng CM) |
|---|---|---|---|---|
| Algal Leaf Spot | 94,70 % | 97,28 % | 95,97 % | 147 |
| Allocaridara Attack | 98,90 % | 98,36 % | 98,63 % | 183 |
| Healthy Leaf | 96,95 % | 97,45 % | 97,20 % | 196 |
| Leaf Blight | 100,00 % | 96,28 % | 98,10 % | 188 |
| Phomopsis Leaf Spot | 95,53 % | 97,16 % | 96,34 % | 176 |

**Confusion matrix (test, 890 ảnh)** — NB02[c14]:

```
                   pred: ALG  ALL  HEA  BLI  PHO
true ALGAL_LEAF_SPOT     143    0    2    0    2
true ALLOCARIDARA         2  180    0    0    1
true HEALTHY_LEAF         1    0  191    0    4
true LEAF_BLIGHT          2    1    3  181    1
true PHOMOPSIS            3    1    1    0  171
```
Tổng sai: 24/890.

---

### 1.3 Grad-CAM / XAI (NB03)

| Đại lượng | Giá trị | Nguồn |
|---|---|---|
| Target layer (single-scale) | `base.features.8.0` (7 × 7) | NB03[c8], NB04[c6] |
| Số ảnh chạy Grad-CAM | 3.104 (toàn bộ train) | NB03[c4] |
| Checkpoint dùng | `best_model.pth`, val_acc = 0,9819 | NB03[c6] |

**Accuracy & confidence per class trên train set** — NB03[c17], `JSON:notebooks/visualizations/gradcam/gradcam_summary.json`:

| Lớp | n | Accuracy | conf_mean | conf_min |
|---|---|---|---|---|
| Algal Leaf Spot | 513 | 99,03 % | 0,971 | 0,165 |
| Allocaridara Attack | 639 | 99,22 % | 0,981 | 0,220 |
| Healthy Leaf | 683 | 99,56 % | 0,979 | 0,204 |
| Leaf Blight | 655 | 99,85 % | 0,988 | 0,354 |
| Phomopsis Leaf Spot | 614 | 99,84 % | 0,991 | 0,415 |

> ⚠️ File `notebooks/outputs/gradcam_summary.json` chứa một bộ số **khác** (500 ảnh, accuracy 98,8 %) — đây là tàn dư của lần chạy cũ trên subset. **Không dùng.** Xem G-04.

---

### 1.4 Pseudo-label V1 (NB04)

| Tham số | Giá trị | Nguồn |
|---|---|---|
| Phương pháp | Grad-CAM single-layer `features.8.0`, threshold cố định ≥ 0,5 | NB04[c8] |
| Post-process | MORPH_CLOSE rồi MORPH_OPEN, kernel **vuông** 5 × 5 (`np.ones`) | NB04[c8] |
| **Số mask sinh ra** | **3.104** (toàn bộ train, KHÔNG phải 500) | NB04[c8], NB04[c15] |
| Thời gian sinh nhãn | **14 phút 00 giây** (3,69 it/s, GPU) | NB04[c8] |
| Accuracy (pred == true) | 99,52 % | NB04[c15] |
| Mean confidence | 0,9822 | NB06[c17] |
| Mask coverage trung bình (toàn bộ) | 0,1660 | NB06[c17] |
| Mask < 0,05 coverage | 1 | NB04[c15] |
| Mask > 0,80 coverage | 0 | NB04[c15] |

**Coverage per class (V1)** — NB04[c15]:

| Lớp | mean | std | min | 25% | 50% | 75% | max |
|---|---|---|---|---|---|---|---|
| Algal Leaf Spot | 0,151 | 0,056 | 0,057 | 0,109 | 0,142 | 0,180 | 0,426 |
| Allocaridara Attack | 0,137 | 0,039 | 0,050 | 0,108 | 0,135 | 0,164 | 0,265 |
| Healthy Leaf | **0,264** | 0,076 | 0,111 | 0,209 | 0,252 | 0,311 | **0,591** |
| Leaf Blight | 0,123 | 0,047 | 0,055 | 0,092 | 0,108 | 0,140 | 0,436 |
| Phomopsis Leaf Spot | 0,145 | 0,048 | 0,054 | 0,109 | 0,140 | 0,173 | 0,375 |

---

### 1.5 Pseudo-label V2 (NB06)

| Tham số | Giá trị | Nguồn |
|---|---|---|
| Layer fine (14 × 14) | `base.features.6.3.block.3.0` | NB06[c6] |
| Layer coarse (7 × 7) | `base.features.8.0` | NB06[c6] |
| Fusion | H = 0,6 × H_fine + 0,4 × H_coarse | NB06[c8] |
| CAM method | GradCAM++ (xấp xỉ gradient bậc 2) | NB06[c7] |
| Threshold | percentile per-class (giữ top-K %) | NB06[c10] |
| Morphology | kernel **ellipse** 5 × 5, CLOSE → OPEN | NB06[c10] |
| CC filter | top-3 component, diện tích ≥ 400 px | NB06[c10] |
| Số mask | 3.104 | NB06[c12] |
| **Thời gian sinh nhãn** | **4 phút 08 giây** (12,51 it/s) | NB06[c12] |
| Accuracy (pred == true) | 99,52 % | NB06[c17] |
| Mean confidence | 0,9822 | NB06[c17] |
| Mean coverage (toàn bộ) | **0,1504** | NB06[c17] |
| Mask < 0,05 coverage | 683 (toàn bộ là HEALTHY_LEAF, do hard-zero) | NB06[c17] |
| Mask > 0,60 coverage | 0 | NB06[c17] |

**Coverage target vs thực tế** — NB06[c10] (target), NB06[c17] (thực tế):

| Lớp | Target | Thực tế (mean) | Std |
|---|---|---|---|
| Algal Leaf Spot | 18 % | 17,7 % | 0,008 |
| Allocaridara Attack | 20 % | 19,7 % | 0,007 |
| Healthy Leaf | 0 % (hard-zero) | 0,0 % | 0,000 |
| Leaf Blight | 22 % | 21,7 % | 0,007 |
| Phomopsis Leaf Spot | 18 % | 17,6 % | 0,009 |

---

### 1.6 SAM refinement → nhãn V3 (NB08)

| Tham số | Giá trị | Nguồn |
|---|---|---|
| Model | SAM ViT-B, checkpoint `sam_vit_b_01ec64.pth` (375 MB) | NB08[c4] |
| Prompt FG | centroid + 4 điểm random trong mask (`n_fg=5` → `min(n_fg-1, ...)` = 4 điểm + centroid) | NB08[c6] |
| Prompt BG | 3 điểm random ngoài vùng dilate 30 px | NB08[c6] |
| IoU guard | fallback về mask V2 nếu IoU(SAM, V2) < 0,15 | NB08[c6] |
| Post-process | CC filter (bỏ CC < 5 % tổng diện tích hoặc < 30 px) + MORPH_CLOSE 5 × 5 | NB08[c6] |
| Số mask refined | 3.104 | NB08[c7], NB08[c8] |

**Coverage nhãn SAM V3 — `RECOMPUTED` trực tiếp từ 3.104 file trong `notebooks/data/sam_refined_labels_v3_train/`:**

| Lớp | n | Coverage mean | Std | Coverage V2 (§1.5) | Δ tương đối |
|---|---|---|---|---|---|
| Algal Leaf Spot | 513 | **0,3463** | 0,1210 | 0,177 | +95,7 % |
| Allocaridara Attack | 639 | **0,3198** | 0,1112 | 0,197 | +62,3 % |
| Healthy Leaf | 683 | 0,0000 | 0,0000 | 0,000 | — |
| Leaf Blight | 655 | **0,3071** | 0,1176 | 0,217 | +41,5 % |
| Phomopsis Leaf Spot | 614 | **0,3356** | 0,1207 | 0,176 | +90,7 % |
| **Toàn bộ** | 3.104 | **0,2543** | 0,1708 | 0,1504 | **+69,1 %** |

| Đại lượng | Giá trị | Nguồn |
|---|---|---|
| Số mask coverage > 0,50 | **200 / 3.104 (6,4 %)** | RECOMPUTED |
| Số mask rỗng (coverage = 0) | 683 (đúng bằng số ảnh HEALTHY_LEAF) | RECOMPUTED |

> ⚠️ NB08[md] và `paper_ijai.tex` ghi **211 mask (6,8 %)**; giá trị tính lại là **200 (6,4 %)**. Luận văn dùng số RECOMPUTED. Xem G-05.

---

### 1.7 Pseudo-label V4.1 (NB09)

| Tham số | Giá trị | Nguồn |
|---|---|---|
| Pipeline | leaf mask HSV robust → bilateral filter (d=9, σ_color=38, σ_space=7) → percentile threshold **chỉ trên pixel lá** → ellipse 5×5 CLOSE/OPEN → top-3 CC ≥ 400 px → hard fallback | NB09[c8] |
| KEEP_PCT | giống V2 (18/20/0/22/18 %) | NB09[c8] |
| Dense CRF | **KHÔNG khả dụng** — `pydensecrf` không cài được, notebook chạy nhánh fallback | NB09[c2] |
| Số mask | 3.104 | NB09[c10] |
| **Thời gian sinh nhãn** | **6 phút 30 giây** (7,94 it/s) | NB09[c10] |
| Mean coverage (toàn bộ) | 0,1417 | NB09[c11] |
| Mask < 0,05 | 684 | NB09[c11] |
| Mask > 0,50 | 0 | NB09[c11] |

**Coverage per class (V4.1)** — NB09[c11]:

| Lớp | mean | std |
|---|---|---|
| Algal Leaf Spot | 0,1589 | 0,0247 |
| Allocaridara Attack | 0,1871 | 0,0200 |
| Healthy Leaf | 0,0000 | 0,0000 |
| Leaf Blight | 0,2023 | 0,0252 |
| Phomopsis Leaf Spot | 0,1732 | 0,0120 |

> Ghi chú quan trọng: std coverage của V4.1 (0,012–0,025) **cao hơn V2** (0,007–0,009) → V4.1 khôi phục được một phần biến thiên theo mức độ bệnh của từng ảnh, điều mà percentile thuần của V2 làm mất.

---

### 1.8 Segmentation — tất cả các phiên bản

#### Cấu hình

| | **V1** (NB05) | **V2** (NB07) | **V3** (NB08) | **V4** (NB09) |
|---|---|---|---|---|
| Kiến trúc | EfficientNet-UNet (custom, `utils/models.py`) | UNet++ EfficientNet-B0 (smp) | UNet++ EfficientNet-B0 | UNet++ EfficientNet-B0 |
| Số tham số | *(chưa in ra — xem G-06)* | 6.569.581 (toàn bộ trainable) | 6.569.581 | 6.569.581 |
| Nhãn huấn luyện | pseudo V1 | pseudo V2 | SAM-refined V3 | pseudo V4.1 |
| Loss | BCEWithLogits + Dice | FocalDice (α=0,25; γ=2,0) | FocalDice (α=0,25; γ=2,0) | FocalDice (α=0,25; γ=2,0) |
| Optimizer | Adam lr=1e-4 | AdamW lr=1e-4, wd=1e-4 | AdamW lr=1e-4, wd=1e-4 | AdamW lr=1e-4, wd=1e-4 |
| Scheduler | ReduceLROnPlateau(min, p=2, f=0,5) | CosineAnnealingLR T_max=50, η_min=1e-6 | như V2 | như V2 |
| **Batch size** | **8** | **4** | **8** | **4** |
| Max epochs | 30 | 50 | 50 | 50 |
| **Early-stop patience** | **7** | **5** | **10** | **10** |
| **Tiêu chí early-stop** | val_loss | val_loss | val_loss | **val_IoU** |
| Grad clipping | không | max_norm = 1,0 | max_norm = 1,0 | max_norm = 1,0 |
| Augmentation | chỉ H/V flip (torchvision) | Albumentations mạnh¹ | như V2 | như V2 nhưng Elastic p=0,2; GridDistortion p=0,15 |
| Chia split | `torch.random_split(seed=42)` | `np.random.default_rng(42).permutation` | như V2 | như V2 |
| Epoch đã chạy | 30/30 | 25/50 | 22/50 | 24/50 |
| Best checkpoint | E23 (val_loss = 0,2959) | E20 (val_loss = 0,5957) | E12 (val_loss = 0,4478) | E14 (val_IoU = 0,4066) |

¹ RandomResizedCrop(0,7–1,0), HFlip 0,5, VFlip 0,5, RandomRotate90 0,5, ShiftScaleRotate 0,5, ElasticTransform 0,3, GridDistortion 0,2, ColorJitter 0,5, GaussNoise 0,2 — NB07[c5].

**Nguồn cấu hình:** V1 → NB05[c4,c6,c10]; V2 → NB07[c7,c11,c15]; V3 → NB08[c13,c16,c19]; V4 → NB09[c16,c18,c21].

#### Kết quả test set

| Version | Test IoU | Dice | Precision | Recall | F1 | Test loss | Nguồn |
|---|---|---|---|---|---|---|---|
| **V1** | **0,7671** | 0,8623 | 0,8562 | 0,8877 | 0,8623 | 0,3065 | NB05[c13]; `JSON:notebooks/models/segmentation/metrics/test_metrics.json` |
| **V2** | **0,5135** | 0,6301 | 0,6169 | 0,7419 | 0,6301 | 0,5993 | NB07[c17]; `JSON:.../segmentation_v2/metrics/test_metrics.json` |
| **V3** | **0,6239** | 0,7053 | 0,7090 | 0,8752 | 0,7053 | 0,4704 | NB08[c21]; `JSON:.../segmentation_v3/metrics/test_metrics.json` |
| **V4** | **0,4388** | 0,4961 | 0,5956 | 0,7615 | 0,4961 | 0,7830 | `JSON:.../segmentation_v4/metrics/test_metrics.json` ⚠️ xem G-09 |

#### Best validation (max qua toàn bộ epoch)

| Version | Best val IoU | tại epoch | Min val_loss | tại epoch | Số epoch | Nguồn |
|---|---|---|---|---|---|---|
| V1 | 0,7715 | E25 | 0,2959 | E23 | 30 | NB05[c10], NB07[c19] |
| V2 | 0,5438 | E18 | 0,5957 | E20 | 25 | `JSON:.../segmentation_v2/metrics/training_history.json` |
| V3 | 0,6981 | E17 | 0,4478 | E12 | 22 | `JSON:.../segmentation_v3/metrics/training_history.json`, NB08[c21] |
| V4 | 0,4066 | E14 | 0,8065 | E9 | 24 | `JSON:.../segmentation_v4/metrics/training_history.json` |

> Lưu ý: `best val IoU` là **max qua tất cả epoch**, không phải giá trị val IoU tại epoch checkpoint được chọn. Với V1, checkpoint được chọn là E23 (val_IoU = 0,7699), không phải E25.

#### Đường cong V1 — các mốc chính (NB05[c10])

| Epoch | train_loss | val_loss | train_IoU | val_IoU | val_Dice |
|---|---|---|---|---|---|
| 1 | 1,0133 | 0,7762 | 0,4471 | 0,6279 | 0,7619 |
| 6 | 0,3346 | 0,3378 | 0,7530 | 0,7443 | 0,8467 |
| 14 | 0,2079 | 0,3014 | 0,8211 | 0,7620 | 0,8584 |
| **23** | 0,1547 | **0,2959** | 0,8615 | 0,7699 | 0,8641 |
| **25** | 0,1482 | 0,3022 | 0,8667 | **0,7715** | **0,8650** |
| 30 | 0,1399 | 0,3006 | 0,8736 | 0,7701 | 0,8640 |

#### Đường cong V2 — các mốc in ra (NB07[c15])

| Epoch | train_loss | val_loss | train_IoU | val_IoU | val_Dice | lr |
|---|---|---|---|---|---|---|
| 2 | 0,6179 | 0,6167 | 0,4032 | 0,4476 | 0,5662 | 9,96e-5 |
| 3 | 0,6089 | 0,6121 | 0,4149 | 0,4925 | 0,6098 | 9,91e-5 |
| 5 | 0,6011 | 0,6109 | 0,4259 | 0,5023 | 0,6185 | 9,76e-5 |
| 10 | 0,5869 | 0,5979 | 0,4413 | 0,4749 | 0,5927 | 9,05e-5 |
| 15 | 0,5773 | 0,5958 | 0,4594 | 0,5090 | 0,6266 | 7,96e-5 |
| **20** | 0,5697 | **0,5957** | 0,4691 | 0,4960 | 0,6144 | 6,58e-5 |
| 25 | 0,5645 | 0,6008 | 0,4777 | 0,5339 | 0,6510 | 5,05e-5 |

#### Đường cong V3 — các mốc (NB08[md c28], đối chiếu `JSON:.../segmentation_v3/metrics/training_history.json`)

| Epoch | val_loss | val_IoU | val_Dice |
|---|---|---|---|
| 9 | 0,4514 | 0,6536 | 0,7348 |
| 11 | 0,4495 | 0,6711 | 0,7518 |
| **12 (checkpoint chọn)** | **0,4478** | 0,6479 | 0,7294 |
| 16 | 0,4508 | 0,6917 | 0,7716 |
| **17 (best IoU, bị bỏ lỡ)** | 0,4537 | **0,6981** | **0,7792** |

ΔIoU giữa E17 và E12 = **0,0502**.

#### So sánh V2 → V3 (cùng kiến trúc, cùng split, chỉ khác nhãn) — NB08[c23]

| Metric | V2 | V3 | Δ tương đối |
|---|---|---|---|
| IoU | 0,5135 | 0,6239 | **+21,5 %** |
| Dice | 0,6301 | 0,7053 | +11,9 % |
| Precision | 0,6169 | 0,7090 | +14,9 % |
| Recall | 0,7419 | 0,8752 | +18,0 % |
| F1 | 0,6301 | 0,7053 | +11,9 % |

#### So sánh V1 → V2 — NB07[c19]

| Metric | V1 | V2 | Δ tương đối |
|---|---|---|---|
| IoU | 0,7671 | 0,5135 | −33,1 % |
| Dice | 0,8623 | 0,6301 | −26,9 % |
| Precision | 0,8562 | 0,6169 | −27,9 % |
| Recall | 0,8877 | 0,7419 | −16,4 % |

---

### 1.9 Inference đơn ảnh (NB10)

| Đại lượng | Giá trị | Nguồn |
|---|---|---|
| Ảnh thử | `data/raw/train/ALGAL_LEAF_SPOT/to_label_1.jpg` | NB10[c3] |
| Predicted class | ALGAL_LEAF_SPOT | NB10[c6] |
| Confidence | 0,9929 (99,3 %) | NB10[c6] |
| Phân phối xác suất | ALG 0,9929 / ALL 0,0000 / HEA 0,0004 / BLI 0,0005 / PHO 0,0062 | NB10[c6] |
| Model phân đoạn dùng | V3, checkpoint epoch 12, val_loss = 0,4478 | NB10[c10] |
| **Mask coverage** | **48,5 %** diện tích ảnh | NB10[c11], NB10[c14] |
| Hình kết quả | `notebooks/outputs/inference/inference_to_label_1.png` | NB10[c13] |

> Coverage 48,5 % trên một ảnh Algal Leaf Spot là minh chứng định tính rõ ràng cho hiện tượng **nở mask** của nhãn SAM (§1.6): model V3 dự đoán gần nửa ảnh là vùng bệnh. Đây là hình minh hoạ tốt cho §4.5 và §4.8.

---

## 2. BẢNG HÌNH KHẢ DỤNG

**Đây là nguồn hình DUY NHẤT.** Không có hình nào khác được phép dùng.
Kích thước ghi dạng `rộng × cao (px) | dung lượng`.

### 2.1 `notebooks/visualizations/eda/` — Chương EDA

| File | Kích thước | Nội dung |
|---|---|---|
| `class_distribution.png` | 1915 × 732 \| 104 KB | Bar chart số ảnh/lớp + pie chart tỉ lệ % |
| `dataset_splits.png` | 1934 × 736 \| 70 KB | Bar chart train/val/test + grouped bar per-class theo split |
| `sample_images_per_class.png` | 2204 × 916 \| 2.511 KB | Lưới 2 × 5 ảnh mẫu của 5 lớp |
| `rgb_histogram_per_class.png` | 2688 × 598 \| 64 KB | 5 histogram kênh R/G/B chồng nhau, mỗi lớp một panel |
| `mean_rgb_per_class.png` | 1784 × 733 \| 57 KB | Grouped bar giá trị trung bình R/G/B theo lớp |
| `file_size_and_brightness.png` | 1934 × 731 \| 58 KB | Histogram dung lượng file + histogram độ sáng theo lớp |
| `brightness_kde_per_class.png` | 2988 × 580 \| 148 KB | 5 KDE plot phân phối độ sáng |

### 2.2 `notebooks/visualizations/classification/` — Chương phân loại

| File | Kích thước | Nội dung |
|---|---|---|
| `training_curves.png` | 1934 × 732 \| 93 KB | Loss/epoch + Accuracy/epoch (train vs val), 16 epoch |
| `confusion_matrix.png` | 1130 × 885 \| 65 KB | Heatmap 5 × 5 confusion matrix trên test set |
| `per_class_metrics.png` | 1784 × 733 \| 60 KB | Grouped bar Precision/Recall/F1 theo 5 lớp |

### 2.3 `notebooks/visualizations/gradcam/` — Chương XAI

| File | Kích thước | Nội dung |
|---|---|---|
| `gradcam_samples_per_class.png` | 2170 × 11268 \| 4.804 KB | 15 hàng (3 mẫu × 5 lớp) × 3 cột (Original \| Heatmap \| Overlay). ⚠️ rất dài, cần cắt/scale khi đưa vào luận văn |
| `gradcam_best_per_class.png` | 2164 × 3683 \| 5.774 KB | 5 hàng × 3 cột — ảnh confidence cao nhất mỗi lớp |

### 2.4 `notebooks/visualizations/pseudo_labeling/` — Pseudo-label V1

| File | Kích thước | Nội dung |
|---|---|---|
| `pseudo_label_per_class.png` | 2164 × 3683 \| 7.109 KB | 5 hàng × 3 cột: Original \| Grad-CAM overlay \| Pseudo mask overlay |
| `morphological_demo.png` | 2901 × 742 \| 1.126 KB | 1 × 4: Original \| Heatmap \| Mask threshold-only \| Mask sau CLOSE+OPEN |

### 2.5 `notebooks/visualizations/pseudo_labeling_v2/` — Pseudo-label V2

| File | Kích thước | Nội dung |
|---|---|---|
| `pseudo_label_v2_per_class.png` | 2164 × 3683 \| 7.430 KB | 5 hàng × 3 cột: Original \| GradCAM++ overlay \| Mask V2 |
| `v1_vs_v2_comparison.png` | 2901 × 742 \| 1.152 KB | 1 × 4: Original \| Heatmap multi-scale \| Mask V1 (đỏ) \| Mask V2 (xanh) |
| `v2_coverage_analysis.png` | 2084 × 741 \| 85 KB | Histogram coverage V1 vs V2 + bar mean coverage per class V2 |

### 2.6 `visualizations/pseudo_labeling_v4/` — Pseudo-label V4.1

| File | Kích thước | Nội dung |
|---|---|---|
| `v4_per_class.png` | 2923 × 2947 \| 6.442 KB | 5 hàng × 5 cột: Original \| Leaf mask HSV \| Heatmap \| CAM overlay \| Mask V4 |
| `v4_coverage.png` | 2084 × 742 \| 84 KB | Histogram coverage V2 vs V4 + bar mean coverage per class V4 |

### 2.7 `notebooks/visualizations/segmentation_v1/` — Segmentation V1

| File | Kích thước | Nội dung |
|---|---|---|
| `training_curves.png` | 2684 × 740 \| 102 KB | 1 × 3: Loss \| IoU \| Dice (train vs val), 30 epoch |
| `test_predictions.png` | 1741 × 2359 \| 1.821 KB | 4 hàng × 3 cột: Input \| Pseudo-label \| Prediction |

### 2.8 `visualizations/segmentation_v2/`, `_v3/`, `_v4/` — Segmentation V2/V3/V4

| File | Kích thước | Nội dung |
|---|---|---|
| `segmentation_v2/training_curves_v2.png` | 2684 × 1475 \| 316 KB | Lưới 2 × 3: Loss \| IoU \| Dice \| Val P/R/F1 \| LR schedule \| Bar V1 vs V2 |
| `segmentation_v2/test_predictions_v2.png` | 2320 × 2359 \| 1.953 KB | 4 hàng × 4 cột: Input \| Pseudo V2 \| Prob map \| Prediction (kèm IoU/Dice) |
| `segmentation_v3/training_curves_v3.png` | 2684 × 1475 \| 302 KB | Như trên, bar chart 3 chiều V1/V2/V3 |
| `segmentation_v3/test_predictions_v3.png` | 2343 × 2359 \| 2.203 KB | 4 hàng × 4 cột, nhãn SAM V3 |
| `segmentation_v4/training_curves_v4.png` | 2683 × 1475 \| 258 KB | Như trên, bar chart V2/V3/V4 ⚠️ ứng với lần chạy V4.0, xem G-09 |
| `segmentation_v4/test_predictions_v4.png` | 2320 × 2359 \| 2.226 KB | 4 hàng × 4 cột, nhãn V4 ⚠️ như trên |

### 2.9 `notebooks/models/segmentation_v3/visualizations/`

| File | Kích thước | Nội dung |
|---|---|---|
| `sam_refinement_comparison.png` | 1016 × 1181 \| 588 KB | 4 hàng × 3 cột: Image \| Pseudo-label V2 \| SAM-refined V3 — **hình quan trọng nhất để minh hoạ hiện tượng SAM mở rộng mask** |

### 2.9b `notebooks/outputs/inference/` — Demo end-to-end (mới tạo 2026-07-26)

| File | Kích thước | Nội dung |
|---|---|---|
| `inference_to_label_1.png` | 7265 × 1485 \| 516 KB | 1 × 5: Input \| Bar chart 5 lớp \| Grad-CAM overlay \| Seg mask V3 \| Grad-CAM + contour. Coverage 48,5 %. ⚠️ rất rộng — cần `\includegraphics[width=\textwidth]` hoặc xoay ngang |

### 2.10 Hình có sẵn nhưng KHÔNG NÊN DÙNG

| Thư mục / file | Lý do loại |
|---|---|
| `notebooks/outputs/gradcam*`, `gradcam_samples/*` | Tàn dư lần chạy cũ trên subset 500 ảnh, số liệu mâu thuẫn §1.3 |
| `notebooks/outputs/pseudo_labels/*`, `notebooks/outputs/segmentation/*` | Cùng lý do — không tái tạo được từ notebook hiện tại |
| `notebooks/visualizations/segmentation/*` (8 file curve rời) | Không có notebook nào trong repo sinh ra chúng; không truy vết được |
| `models/classification/gradcam/*` | Thư mục `models/` ở gốc là tàn dư; notebook hiện dùng `notebooks/models/` |

### 2.11 Hình CẦN nhưng CHƯA CÓ

| Hình cần | Dùng cho | Cách tạo |
|---|---|---|
| Sơ đồ pipeline tổng thể | Chương 3 | Có sẵn dưới dạng **TikZ** trong `paper_ijai.tex:116–147` — tái sử dụng trực tiếp, không cần file ảnh |
| Bar chart so sánh V1/V2/V3/V4 độc lập | Chương 4 | Có thể vẽ bằng TikZ/pgfplots từ §1.8 (không cần chạy lại notebook) |
| Đường cong training V4.1 thật | Chương 4 | ❌ Không tồn tại — cần chạy lại NB09. Xem G-09 |

---

## 3. DANH SÁCH LỖ HỔNG (GAPS)

> Mỗi mục dưới đây là một chỗ mà `paper_content.md` / `paper_ijai.tex` / `README.md` nêu số liệu **không được notebook chứng minh**, hoặc mâu thuẫn với output thực tế.
> Trong luận văn: dùng **cột "Giá trị đúng"**; nếu không có giá trị đúng → đánh `\todo{...}`.

### G-01 · Notebook đánh giá tổng hợp không tồn tại
- **Vấn đề:** `README.md` liệt kê `06-model-evaluation.ipynb`; `run_all_notebooks.ps1:16` gọi `06-model-evaluation-fixed.ipynb`. Cả hai đều **không có** trong repo.
- **Hệ quả:** File `notebooks/models/final_evaluation_report.json` (accuracy = 1,0 trên 500 ảnh sample) **không truy vết được** về notebook nào.
- **Xử lý:** Không dùng `final_evaluation_report.json` và `final_classification_metrics.json` (accuracy 1,0 trên 50 ảnh). Sửa `run_all_notebooks.ps1` cho khớp tên file thực tế.

### G-02 · Test accuracy classification: 97,52 % là SAI
- **Nêu ở:** `paper_content.md` §3.2.3, §4.1; `paper_ijai.tex` abstract, Table `tab:classification`, §5; `README.md` "Val Accuracy 97.52%".
- **Giá trị đúng:** **Val 98,19 % (E11) · Test 97,30 %** — NB02[c8], NB02[c14].
- **Nguồn gốc lỗi:** 97,52 % là `val_acc` tại **epoch 10**, không phải best val, cũng không phải test.
- **Thêm:** `paper_ijai.tex` Table `tab:classification` ghi Accuracy = 97,52 % cùng hàng với Precision 97,34 / Recall 97,30 / F1 97,31 → **tự mâu thuẫn** (accuracy phải bằng 97,30 %).

### G-03 · Tỉ lệ chia dữ liệu classification: 70/15/15 là SAI
- **Nêu ở:** `paper_content.md` §3.1; `paper_ijai.tex` §3.1 ("665 val / 668 test"); TikZ diagram `paper_ijai.tex:118`.
- **Giá trị đúng:** **70/10/20 → 3.104 / 443 / 890** — NB01[c13], NB02[c4].
- **Xử lý:** Sửa cả bảng lẫn node TikZ khi tái sử dụng sơ đồ.

### G-04 · Pseudo-label V1 áp dụng trên 500 ảnh là SAI
- **Nêu ở:** `paper_content.md` §3.3; `paper_ijai.tex` §3.3.
- **Giá trị đúng:** V1 sinh **3.104 mask** trên toàn bộ train set — NB04[c8].
- **Nguồn gốc:** subset 500 ảnh thuộc một lần chạy cũ (`notebooks/outputs/gradcam_summary.json`, `final_evaluation_report.json`) không còn tồn tại dưới dạng notebook.

### G-05 · Số mask SAM > 50 % coverage
- **Nêu ở:** `paper_content.md` §3.5.4 và `paper_ijai.tex` §3.6.4: "211/3.104 (6,8 %)".
- **Giá trị đúng (RECOMPUTED):** **200/3.104 (6,4 %)** — §1.6.
- Các con số coverage per-class trong bảng của bài báo (35,0 / 32,0 / 30,7 / 33,6 / 25,5 %) khớp với giá trị tính lại trong sai số làm tròn (34,6 / 32,0 / 30,7 / 33,6 / 25,4 %) → **chấp nhận được**, nhưng luận văn dùng số RECOMPUTED có 4 chữ số.
- **Lưu ý:** toàn bộ bảng coverage SAM trong bài báo **chỉ xuất hiện trong markdown narration** của NB08 (`NB08[md c28]`), không có cell code nào tính. Bảng ở §1.6 là số duy nhất có bằng chứng.

### G-06 · Số tham số của EfficientNet-UNet V1
- **Thiếu:** NB05 không in ra tổng số tham số của model V1 (chỉ V2/V3/V4 in 6.569.581).
- **Xử lý:** `\todo{đếm tham số EfficientNetUNet}` — hoặc tính bằng 1 dòng script (không cần train lại). Kiến trúc có sẵn tại `utils/models.py:81–111`.

### G-07 · Siêu tham số segmentation trong bài báo không khớp notebook

| Mục | Bài báo nêu | Giá trị đúng | Nguồn |
|---|---|---|---|
| Classification batch size | 32 | **16** | NB02[c4] |
| Classification max epochs | 30 | **50** (dừng ở E16) | NB02[c8] |
| Classification early stopping | "qua ReduceLROnPlateau patience=2" | early stopping **riêng**, patience = 5 trên val_acc; ReduceLROnPlateau chỉ điều chỉnh lr | NB02[c8] |
| V2 early-stop patience | 10 | **5** | NB07[c15] |
| V3 batch size (`paper_ijai.tex`) | 4 | **8** | NB08[c13] |
| V1 max epochs / patience | 30 (đúng) / không nêu | 30 / **7** | NB05[c10] |
| V1 batch size | không nêu | **8** | NB05[c4] |

### G-08 · SAM refinement: không có log thời gian & thống kê trong lần chạy hiện tại
- NB08[c4] và [c8] cho thấy toàn bộ 3.104 mask **đã tồn tại từ trước**, nên nhánh chạy SAM bị bỏ qua (`SAM not loaded`).
- **Hệ quả:** thời gian refinement (~40 phút, nêu trong `paper_ijai.tex` §4.7) **không có bằng chứng**; số lần IoU guard kích hoạt cũng không được ghi nhận.
- **Xử lý:** `\todo{đo lại thời gian SAM refinement}` hoặc bỏ mục "Computational Efficiency" khỏi luận văn. Coverage thì đã cứu được bằng RECOMPUTED (§1.6).

### G-09 · Segmentation V4: notebook và file kết quả KHÔNG khớp nhau — nghiêm trọng
- **Trạng thái notebook:** NB09[c21] bị **`KeyboardInterrupt` tại epoch 1** (`val_iou = 0,3599`). Notebook hiện tại thực thi pipeline **V4.1 (bilateral filter)**.
- **Trạng thái file trên đĩa:** `notebooks/models/segmentation_v4/metrics/test_metrics.json` chứa IoU = 0,4388 và `training_history.json` có **24 epoch** — đây là kết quả của lần chạy **V4.0 (GrabCut)** trước đó (markdown NB09[c0] tự xác nhận: *"V4.0 (GrabCut) → IoU 0.44"*).
- **Cùng vấn đề:** hai hình `visualizations/segmentation_v4/*.png` cũng thuộc lần chạy V4.0.
- **Nhãn V4.1 thì hợp lệ** — `pseudo_labels_v4_train/` (3.104 file) và §1.7 đến từ lần chạy V4.1 hoàn tất.
- **QUYẾT ĐỊNH (2026-07-26):** **Bỏ hẳn V4 khỏi luận văn.** Luận văn chỉ trình bày V1 / V2 / V3.
  - §1.7 và §2.6 được giữ trong INVENTORY để lưu vết, nhưng **không đưa vào chương nào**.
  - Hai hình `visualizations/segmentation_v4/*` và `test_metrics.json` của V4 **không được dùng**.
  - Trong mọi trường hợp **không được** gán IoU 0,4388 cho V4.1.

### G-10 · NB10 có cell lỗi — ✅ ĐÃ KHẮC PHỤC (2026-07-26)
- **Lỗi cũ:** NB10[c8] báo `cv::ColorMap only supports CV_8UC1 or CV_8UC3`; các cell sau không có output.
- **Nguyên nhân:** `GradCAMGenerator.generate()` (nhánh torchcam) trả về heatmap ở độ phân giải feature-map (7 × 7) dạng `(1, H, W)`; NB03/NB04 có `np.squeeze` + `cv2.resize` còn NB10 thì thiếu.
- **Đã sửa:** thêm 4 dòng squeeze/resize/clip vào NB10[c8], chạy lại toàn bộ notebook. Kết quả nay có đầy đủ (§1.9) và hình `inference_to_label_1.png` (§2.9b).
- Bản sao notebook trước khi sửa được giữ tại scratchpad của phiên làm việc.

### G-11 · Thời gian huấn luyện & thời gian inference chưa có bằng chứng
- `paper_ijai.tex` §4.7 nêu: classification ~2 h; segmentation V2 ~3 h; V3 ~2,5 h; inference 15 ms + 45 ms = 60 ms (16 FPS).
- **Không notebook nào đo các giá trị này.** Chỉ có 3 mốc thời gian có thật (§1.4, §1.5, §1.7): pseudo-label V1 = 14:00, V2 = 4:08, V4 = 6:30.
- **Xử lý:** bỏ mục hiệu năng tính toán, hoặc `\todo{benchmark}` + đo lại (script benchmark inference rất nhanh, ~2 phút).

### G-12 · Nguồn gốc dataset — MỘT PHẦN đã truy được (rà soát 2026-07-26)

**Đã tìm thấy** (nguồn: `paper_ijai.tex`, đã rà toàn bộ repo bằng từ khoá `collected / plantation / Kaggle / Mendeley / roboflow / thu thập / bản quyền / license`):

| Thông tin | Nội dung | Nguồn |
|---|---|---|
| Địa bàn thu thập | "collected from plantations in Southeast Asia" (vườn trồng ở Đông Nam Á) | `paper_ijai.tex:155` |
| Người gán nhãn | Chuyên gia nông nghiệp cung cấp kiến thức chuyên môn và **thẩm định nhãn phân loại bệnh** | `paper_ijai.tex:616` (Acknowledgments) |
| Điều kiện chia sẻ | "available upon reasonable request from the corresponding author" | `paper_ijai.tex:628` |
| Bối cảnh đơn vị | ĐH Quy Nhơn (Gia Lai) · FPT Software Quy Nhon AI (Gia Lai) · ĐH Đà Lạt (Lâm Đồng) | `paper_ijai.tex:48–51` |

**Bằng chứng bổ sung — `RECOMPUTED` từ chính tệp ảnh:**

| Quan sát | Chi tiết |
|---|---|
| EXIF | **Bị xoá hoàn toàn** — `Image.getexif()` trả về rỗng trên mọi ảnh kiểm tra. Không còn ngày chụp / thiết bị / GPS |
| Kích thước | Toàn bộ đã là 224 × 224 JPEG, aspect ratio 1,0, std = 0 → đã tiền xử lý trước khi vào repo |
| Quy ước tên tệp | `to_label_N.jpg`, chỉ số N đánh **liên tục xuyên lớp** (`to_label_1` ∈ ALGAL, `to_label_2686` ∈ LEAF_BLIGHT) → ban đầu là một kho ảnh chung, sau đó mới phân vào thư mục lớp qua một đợt gán nhãn |
| Metadata thu thập | Không có tệp `.md/.txt/.json` nào trong `notebooks/data/raw/` mô tả nguồn gốc |

**Đã đưa vào luận văn:** §1.1.1 "Nguồn gốc bộ dữ liệu" ([chapters/01-mo-dau.tex](chapters/01-mo-dau.tex)) — trình bày phần truy được, kèm ba đặc điểm pháp y ở trên và hệ quả của chúng lên phạm vi kết luận.

**Còn thiếu (giữ `\TODO` thu hẹp):** (1) địa phương cụ thể + thời gian thu thập; (2) thiết bị chụp và độ phân giải gốc trước khi co ảnh; (3) số lượng chuyên gia gán nhãn và mức đồng thuận; (4) giấy phép sử dụng. Bốn mục này **không tồn tại ở bất kỳ đâu trong repo hoặc công bố** — bắt buộc phải hỏi nhóm thu thập dữ liệu gốc.

> `intern_projects.md` đã được rà soát và **không liên quan** (tài liệu dự án thực tập về LLM, không nhắc tới sầu riêng).

### G-13 · Không có ground-truth pixel-level → không có số tuyệt đối
- Toàn bộ IoU/Dice ở §1.8 đo model so với **pseudo-label của chính phiên bản đó**, không phải so với annotation thật.
- Đây **không phải lỗi** mà là hạn chế bản chất, nhưng phải nêu rõ và nhất quán trong luận văn:
  - So sánh **hợp lệ**: V2 ↔ V3 (cùng kiến trúc, cùng split seed = 42, cùng loại nhãn được tạo từ cùng pipeline gốc).
  - So sánh **không hợp lệ**: V1 ↔ V2/V3 (khác kiến trúc, khác phân phối nhãn, khác cách chia split — `torch.random_split` vs `np.random.default_rng` → **tập test khác nhau**).
  - V4 ↔ V2/V3: cùng kiến trúc và cùng seed nhưng nhãn khác phân phối → so sánh **có điều kiện**.

### G-14 · Lỗi kỹ thuật đã biết trong NB05 (cần nêu ở phần Hạn chế)
- `train_seg.dataset.augment = True` (NB05[c4]) thao tác trên **dataset gốc dùng chung**, nên val/test cũng bị augment (chỉ H/V flip). Tự notebook đã thừa nhận (NB05[md c18]).
- **Ảnh hưởng:** metric V1 (IoU 0,7671) có nhiễu nhỏ. Phải ghi rõ trong luận văn.

### G-15 · Thiếu tài liệu tham khảo cho các kỹ thuật thực sự được dùng
- `refs.bib` sẽ dựng từ 15 mục trong `paper_content.md` §REFERENCES + `paper_ijai.tex` bibliography (14 mục). Các mục này **là tài liệu có thật**, được giữ nguyên.
- **Còn thiếu** (kỹ thuật có dùng nhưng chưa có trích dẫn): bilateral filter (Tomasi & Manduchi 1998), Dense CRF (Krähenbühl & Koltun 2011 — chỉ nêu vì đã thử và thất bại), GrabCut (Rother et al. 2004), segmentation-models-pytorch (Iakubovskii 2019), PyTorch (Paszke et al. 2019).
- **Xử lý:** chỉ bổ sung những tài liệu **tôi xác minh được là có thật** trước khi ghi vào `refs.bib`. Không tự bịa.

---

## 4. TÓM TẮT SỐ LIỆU TRỤ CỘT CỦA LUẬN VĂN

Đây là bộ số cuối cùng, đã kiểm chứng, sẽ dùng xuyên suốt:

| # | Phát biểu | Số | Nguồn |
|---|---|---|---|
| 1 | Dataset | 4.437 ảnh, 5 lớp, 224 × 224, imbalance 1,33 | §1.1 |
| 2 | Split classification | 3.104 / 443 / 890 (70/10/20) | §1.1 |
| 3 | Classification best val | **98,19 %** (E11) | §1.2 |
| 4 | Classification test | **97,30 %** acc, **97,31 %** F1 | §1.2 |
| 5 | Cặp nhầm lẫn chính | Algal ↔ Phomopsis (3 + 2 ảnh) | §1.2 |
| 6 | Grad-CAM trên train | 3.104 ảnh, acc 99,03–99,85 %, conf_mean 0,971–0,991 | §1.3 |
| 7 | Pseudo-label: cả 4 phiên bản | 3.104 mask mỗi phiên bản | §1.4–1.7 |
| 8 | V2 đạt coverage target | lệch < 0,4 % mỗi lớp | §1.5 |
| 9 | Hard-zero Healthy Leaf | loại 683 mask giả (V1 có coverage 26,4 %) | §1.4, §1.5 |
| 10 | SAM mở rộng mask | 15,04 % → **25,43 %** (+69,1 %); 200 mask > 50 % | §1.6 |
| 11 | Segmentation V1/V2/V3/V4 test IoU | 0,7671 / 0,5135 / 0,6239 / *(0,4388 = V4.0)* | §1.8 |
| 12 | Cải thiện V2 → V3 | IoU **+21,5 %**, Dice +11,9 % | §1.8 |
| 13 | Early-stop bỏ lỡ best IoU (V3) | E12 (0,6479) được chọn thay E17 (0,6981), ΔIoU = 0,050 | §1.8 |
| 14 | Recall > Precision ở mọi phiên bản | V1 0,888/0,856 · V2 0,742/0,617 · V3 0,875/0,709 | §1.8 |
| 15 | Thời gian sinh pseudo-label | V1 14:00 · V2 4:08 · V4 6:30 | §1.4–1.7 |

---

## 5. TÁI TẠO CÁC GIÁ TRỊ `RECOMPUTED`

Bảng coverage SAM ở §1.6 được tính bằng script sau (chạy từ gốc repo với `venv`):

```python
import os, numpy as np
from PIL import Image
from collections import defaultdict

D = 'notebooks/data/sam_refined_labels_v3_train'
CLASSES = ['ALGAL_LEAF_SPOT','ALLOCARIDARA_ATTACK','HEALTHY_LEAF',
           'LEAF_BLIGHT','PHOMOPSIS_LEAF_SPOT']
cov, over50 = defaultdict(list), 0
for f in [f for f in os.listdir(D) if f.endswith('_sam.png')]:
    cls = next((c for c in CLASSES if f.startswith(c)), 'UNKNOWN')
    c = float((np.array(Image.open(os.path.join(D, f)).convert('L')) > 127).mean())
    cov[cls].append(c)
    over50 += (c > 0.5)
for c in CLASSES:
    v = np.array(cov[c]); print(f'{c:<24}{len(v):>6}{v.mean():>10.4f}{v.std():>10.4f}')
allc = np.concatenate([np.array(cov[c]) for c in CLASSES])
print('OVERALL', len(allc), allc.mean(), allc.std(), '| >0.5:', over50)
```

Kết quả tái tạo được ghi nguyên văn ở §1.6.
