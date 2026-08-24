# Kế hoạch cải tiến & bổ sung — Luận văn / Bài báo phân loại–phân đoạn bệnh lá sầu riêng

*Soạn ngày 20/08/2026. Dựa trên `thesispaper/main.tex` (bản Elsevier) và cấu trúc luận văn `docs/thesis`.*

---

## 0. Nhận định tổng quan (đọc trước)

Bốn hạn chế và bốn đề xuất mà người phản biện nêu **đã có sẵn trong bài báo**: mục *Limitations* (5.13) liệt kê đủ 4 điểm, và *Future work* (i)–(v) ở Conclusion trùng khớp gần như từng chữ với 4 kiến nghị (tập ground-truth 50–100 ảnh, ràng buộc coverage hai chiều, chọn checkpoint theo IoU, SAM2, phân đoạn đa lớp).

Hệ quả quan trọng: nếu chỉ *liệt kê* hạn chế và *hứa* future work, một reviewer Q2 sẽ đánh giá **đóng góp mỏng** — vì phần lớn "phát hiện" của bài là tự chỉ ra lỗi của chính phương pháp mình (IoU guard một chiều, đánh giá vòng lặp). Sự trung thực khoa học này là điểm mạnh, nhưng để đạt Q2 phải **biến hạn chế thành cải tiến đã chạy thực nghiệm** — tức tạo ra một phiên bản **V4** khắc phục các lỗi đã nêu và báo cáo số liệu, thay vì để ở dạng lời hứa.

Kế hoạch dưới đây chia 3 mức ưu tiên: **P0 = bắt buộc để qua Q2 / bảo vệ**, **P1 = nên có, tăng đáng kể sức thuyết phục**, **P2 = điểm cộng nếu còn thời gian**.

---

## PHẦN A — Nâng cấp 4 đề xuất sẵn có: từ "hứa" thành "đã làm"

### A1. [P0] Tập kiểm chứng ground-truth do chuyên gia gán nhãn
Đây là điểm chí tử của toàn bộ bài. Không có nó thì mọi con số IoU đều là "đánh giá vòng lặp".

**Cách làm cụ thể — vượt mức tối thiểu 50–100 ảnh:**
- Gán nhãn pixel **≥ 30 ảnh/lớp bệnh** (bỏ lớp Healthy), tổng ~120–150 ảnh, lấy **từ tập test** để không rò rỉ.
- **Đo độ đồng thuận giữa người gán nhãn (inter-annotator agreement):** cho 2 chuyên gia (hoặc 1 chuyên gia + bạn) gán độc lập một phần ~30 ảnh, báo cáo IoU/Dice giữa hai người. Con số này chính là **trần trên (upper bound)** của mô hình — reviewer rất thích chi tiết này vì nó định lượng "độ khó vốn có" của bài toán.
- Báo cáo **hai loại kết quả** trên tập GT: (a) IoU của V2/V3/V4 so với GT thật; (b) IoU của chính các pseudo-label V2/V3 so với GT — để chứng minh trực tiếp mức độ lệch của "nhãn giả" và biện minh cho toàn bộ lập luận comparability caveat.
- Công cụ: CVAT, Labelme, hoặc Roboflow (miễn phí, xuất mask PNG nhị phân).

**Ước lượng:** 2–4 ngày gán nhãn + 1 ngày viết. **Đây là việc phải làm đầu tiên** vì nhiều phân tích khác phụ thuộc vào nó.

### A2. [P0] Chạy thật V4: ràng buộc coverage hai chiều thay IoU guard một chiều
Bài đã *phân tích lý thuyết* rằng IoU guard chỉ chặn "drift" chứ không chặn "expansion", và đề xuất fallback khi `SAM_coverage > 2 × V2_coverage`. **Hãy chạy nó** và tạo cột V4.

**Nâng cấp cách làm (mạnh hơn "just SAM2"):**
- Thay/kết hợp point prompt bằng **box prompt** lấy từ bounding box của mask GradCAM++ — box prompt ràng buộc SAM trong vùng, giảm mạnh hiện tượng nuốt cả lá.
- Hoặc dùng **mask prompt dày** (đưa chính mask GradCAM++ làm `mask_input` cho SAM) + điểm nền trên mô lá khoẻ.
- Khi SAM trả `multimask_output=True` (3 mask), **chọn mask theo IoU với GradCAM++**, không theo điểm IoU tự dự đoán của SAM.
- Ngưỡng hai chiều: giữ SAM nếu `0.15 ≤ IoU` **và** `SAM_cov ≤ k × V2_cov` (thử k = 1,5 / 2,0 / 2,5 trong ablation).

**Kỳ vọng báo cáo:** bảng coverage sau V4 giảm từ +70% xuống mức chấp nhận được; và IoU của V4 so với **GT thật** (mục A1) cao hơn V3 — đây mới là bằng chứng cải tiến thực, không phải "IoU cao hơn vì nhãn dễ hơn".

### A3. [P0→dễ] Chọn checkpoint theo validation IoU
Việc nhỏ, làm ngay: đổi tiêu chí early stopping / `best model` sang **val IoU** (hoặc val Dice) thay vì val loss. Bài đã ghi rõ epoch 17 (IoU 0,698) tốt hơn epoch 12 (IoU 0,648) đúng 0,050 IoU. Chạy lại, con số headline của V3/V4 tăng gần như "miễn phí". **Nửa ngày.**

### A4. [P1] SAM2 — chỉ nêu nếu chạy được
SAM2 tốt hơn về ranh giới, nhưng **chỉ đưa vào nếu thực sự chạy và so sánh** SAM ViT-B vs SAM2 trên cùng prompt. Nếu không kịp, để ở future work là chấp nhận được — đừng để nửa vời. Lưu ý VRAM 2,15 GB: SAM2 nặng, có thể phải chạy giai đoạn refine trên Colab/Kaggle (giai đoạn này offline, không ảnh hưởng train).

### A5. [P2] Phân đoạn đa lớp
Đúng hướng nhưng **tốn công nhất và rủi ro nhất** (cần pseudo-label đa lớp nhất quán). Với phạm vi một luận văn ThS, khuyến nghị **để future work**, tập trung nguồn lực vào A1–A3 + Phần B. Nếu committee ép, làm bản rút gọn: phân đoạn nhị phân + gán nhãn lớp cho mỗi vùng bằng đầu ra của classifier (multi-label ở mức vùng, rẻ hơn multi-class segmentation thật).

---

## PHẦN B — Cải tiến BỔ SUNG (ngoài 4 điểm), reviewer Q2 gần như chắc chắn sẽ hỏi

### B1. [P0] Nhiều seed + kiểm định ý nghĩa thống kê
Toàn bộ kết luận "+21,5% IoU" hiện dựa trên **một seed duy nhất (42)**. Đây là điểm yếu bị bắt lỗi nhiều nhất ở vòng phản biện.
- Chạy V2, V3, V4 với **≥ 3–5 seed**, báo cáo **trung bình ± độ lệch chuẩn**.
- Kiểm định **paired t-test hoặc Wilcoxon signed-rank** trên IoU theo từng ảnh giữa V2 và V3/V4, báo cáo p-value.
- Nếu +21,5% vẫn giữ được sau nhiều seed và p < 0,05 → kết luận vững; nếu không → phải hạ giọng khẳng định. **Bắt buộc cho Q2.**

### B2. [P0] So sánh với baseline/SOTA bên ngoài, không chỉ V1/V2/V3 của mình
Hiện bài **không có baseline độc lập nào**. Reviewer sẽ hỏi "vì sao cần SAM?".
- **Baseline rẻ thay SAM:** DenseCRF hoặc GrabCut để tinh chỉnh biên từ mask GradCAM++. Nếu SAM/SAM2 thắng CRF thì mới chứng minh được giá trị của foundation model; nếu không, đó cũng là phát hiện đáng giá.
- **So kiến trúc phân đoạn:** U-Net thường vs UNet++ vs DeepLabV3+ (cùng encoder EfficientNet-B0) trên cùng nhãn V3/V4.
- **So phương pháp sinh pseudo-label:** GradCAM++ percentile (của bạn) vs Otsu vs Grad-CAM ngưỡng cố định — đưa số liệu để bảo vệ lựa chọn thiết kế.

### B3. [P0] Bảng ablation cho các lựa chọn thiết kế
Phương pháp có rất nhiều "con số ma thuật" chưa được biện minh; reviewer sẽ hỏi từng cái. Làm **một bảng ablation**:
- Trọng số hợp nhất đa tỉ lệ **0,6/0,4** (thử 0,5/0,5; 0,7/0,3).
- Cặp tầng đặc trưng `features.6 (14×14)` + `features.8 (7×7)` (thử chỉ một tầng).
- Percentile theo lớp (18–22%) vs percentile toàn cục vs Otsu.
- Lọc **top-3 connected component ≥ 400 px** (thử top-1, top-5, ngưỡng px khác).
- Thiết kế prompt SAM (centroid+5 FG+3 BG, dilation 30 px) và ngưỡng guard 0,15.

Không cần ablate tất cả — chọn **3–4 yếu tố ảnh hưởng lớn nhất** (trọng số fusion, percentile vs Otsu, prompt SAM point vs box, ngưỡng guard).

### B4. [P1] Kiểm tra rò rỉ dữ liệu (data leakage) giữa các tập
Accuracy 97,52% rất cao — reviewer sẽ nghi ngờ **cùng một chiếc lá xuất hiện ở cả train và test** (ảnh chụp nhiều góc cùng lá). Cần:
- Mô tả rõ quy trình thu ảnh: mỗi lá bao nhiêu ảnh, chụp ngoài đồng hay trong phòng, thiết bị, độ phân giải, điều kiện sáng.
- Nếu có ảnh gần trùng: chia tập **theo lá/theo cây (group split)** thay vì theo ảnh, rồi báo cáo lại accuracy. Nếu accuracy tụt → phát hiện quan trọng; nếu giữ nguyên → bằng chứng mạnh chống nghi ngờ.
- Có thể dùng perceptual hash (pHash) để rà ảnh trùng lặp gần.

### B5. [P1] Ngưỡng thích ứng theo từng ảnh (giải quyết gốc rễ hạn chế #3)
Percentile cố định theo lớp không bám được mức độ nặng của từng lá. Thay vì chỉ "nêu hạn chế", đề xuất & thử một cơ chế thích ứng:
- Chạy **Otsu/Triangle trong vùng hoạt hoá cao** (sau khi đã lọc nền), thay vì trên toàn heatmap — tránh được đúng lỗi bimodal mà bài đã chỉ ra.
- Hoặc dò **điểm gãy (knee/elbow)** trên đường cong giá trị heatmap đã sắp xếp để tự chọn ngưỡng mỗi ảnh.
- Gắn coverage mục tiêu với **độ tin cậy của classifier** hoặc năng lượng của connected component → lá nặng được vùng bao lớn hơn.

### B6. [P1] Lọc/gán trọng số pseudo-label theo độ tin cậy classifier
Hiện dùng cả 3.104 mask như nhau. Ảnh classifier dự đoán tin cậy thấp → CAM kém tin → nhãn nhiễu lan sang segmentation. Đề xuất: loại hoặc giảm trọng số các ảnh có confidence < ngưỡng, báo cáo ảnh hưởng. Rẻ, thuyết phục.

### B7. [P2] Đầu ra thực tiễn: chỉ số mức độ bệnh (severity index)
Vì coverage ≈ tỉ lệ diện tích tổn thương, có thể xuất thêm **% diện tích lá bị bệnh** làm đầu ra ứng dụng. Tăng tính thực tiễn (đúng phần "triển khai thiết bị biên" bạn quan tâm) mà gần như không tốn thêm mô hình.

### B8. [P2] Hiệu chỉnh & bảng dọn dẹp
- Trong bảng phân đoạn, cột **Dice và F1 nhị phân là **cùng một đại lượng** (0,6301 = 0,6301...) — bỏ bớt một cột hoặc chú thích rõ, kẻo reviewer bắt lỗi trùng lặp.
- Cân nhắc báo cáo **ECE (calibration)** cho classifier — nhẹ nhàng, tăng tính chỉnh chu.

---

## PHẦN C — Vấn đề định vị & trình bày (không tốn thí nghiệm)

### C1. [P0] Cân nhắc lại tạp chí đích
Bài đang để `\journal{Data and Information Management}` — tạp chí này thiên về information/data management, **không phải venue tự nhiên cho CV nông nghiệp**. Cân nhắc các Q1/Q2 hợp gu hơn, khả năng chấp nhận cao hơn: *Computers and Electronics in Agriculture* (Q1), *Plant Methods* (Q1), *Frontiers in Plant Science* (Q1), *Smart Agricultural Technology*, *Ecological Informatics*. Chọn đúng venue quan trọng ngang chất lượng bài.

### C2. [P1] Data availability
Mục hiện ghi "không công bố dữ liệu". Xu hướng Q1/Q2 ngày càng đòi dữ liệu mở. Tối thiểu nên **công bố tập GT nhỏ (A1) + mã nguồn + checkpoint** trên Zenodo/GitHub. Vừa dễ qua reviewer, vừa tăng trích dẫn.

### C3. [P1] Đồng bộ luận văn ↔ bài báo & chuẩn bị bảo vệ
- Hội đồng bảo vệ sẽ hỏi **đúng những câu reviewer hỏi**: ground-truth đâu? một seed có tin được không? vì sao dùng SAM? Chuẩn bị sẵn A1, B1, B2.
- Ràng buộc VRAM 2,15 GB đã nêu trong luận văn là điểm trung thực tốt — giữ, nhưng nói rõ giai đoạn SAM refine chạy offline nên không bị ràng buộc này (nếu bạn dùng máy khác cho A2/A4).
- Đảm bảo con số giữa `thesis` (tiếng Việt) và `thesispaper` khớp nhau sau khi chạy lại V3/V4 với checkpoint theo IoU (A3) — dễ lệch nếu chỉ sửa một bên.

---

## PHẦN D — Thứ tự thực hiện đề xuất (đường tới hạn)

1. **A3** đổi checkpoint sang val IoU (0,5 ngày) — rẻ, nâng số liệu ngay.
2. **A1** gán nhãn tập ground-truth 120–150 ảnh + inter-annotator (2–4 ngày) — mở khoá mọi đánh giá thật.
3. **A2** chạy V4 (box/mask prompt + guard hai chiều), đánh giá trên GT của A1 (2–3 ngày).
4. **B1** nhiều seed + kiểm định thống kê cho V2/V3/V4 (1–2 ngày, chủ yếu chờ train).
5. **B2 + B3** baseline CRF/GrabCut + bảng ablation (3–4 ngày).
6. **B4** kiểm tra leakage / group split (1 ngày).
7. **B5, B6** ngưỡng thích ứng + lọc theo confidence (nếu còn thời gian).
8. **C1–C3** chọn lại venue, data availability, đồng bộ hai bản, luyện bảo vệ.

**Tối thiểu để nâng lên chuẩn Q2:** A1 + A2 + A3 + B1 + B2 + B3. Đây là gói biến bài từ "phân tích trung thực về hạn chế" thành "đề xuất có kiểm chứng và cải tiến định lượng".
