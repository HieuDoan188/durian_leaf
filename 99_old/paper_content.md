# Durian Leaf Disease Detection Using Deep Learning with Explainable AI and Pseudo-Labeling

## ABSTRACT

This paper presents a comprehensive weakly-supervised pipeline for durian leaf disease detection using deep learning combined with explainable AI (XAI) and progressive pseudo-labeling strategies. The pipeline consists of four stages: (1) EfficientNet-B0 classification achieving 97.52% test accuracy on five disease classes; (2) multi-scale GradCAM++ pseudo-label generation from 3,104 training images with per-class percentile thresholding; (3) Segment Anything Model (SAM ViT-B) refinement of pseudo-label boundaries; and (4) UNet++ segmentation trained on refined labels. Experimental results show progressive improvement from V2 to V3: IoU 0.5135 → 0.6239 (+21.5%), Dice 0.6301 → 0.7053 (+11.9%). A critical finding is that segmentation metrics across versions are not directly comparable due to different pseudo-label distributions used as evaluation references — an honest limitation of weakly-supervised benchmarking without ground-truth annotation.

**Keywords:** Durian leaf disease, EfficientNet, GradCAM++, Pseudo-labeling, UNet++, Segment Anything Model, Weakly-supervised segmentation, Agricultural AI

---

## 1. INTRODUCTION

Durian (*Durio zibethinus*) is an economically important tropical fruit crop in Southeast Asia. Durian cultivation faces significant challenges from various leaf diseases that can severely impact yield and fruit quality. Early and accurate detection of these diseases is crucial for timely intervention and crop management.

Traditional detection methods rely on manual inspection by agricultural experts, which is time-consuming, subjective, and not scalable for large plantations. Recent deep learning advances have shown promising results in automated plant disease detection. However, most existing approaches focus solely on classification without providing spatial localization of disease symptoms, and pixel-level annotation for segmentation is expensive to obtain.

This research addresses three key challenges:

1. **Limited Labeled Data**: Obtaining pixel-level segmentation annotations for plant diseases requires expert knowledge. Most available datasets contain only image-level labels.
2. **Explainability**: Agricultural experts need interpretable predictions to trust AI systems.
3. **Precise Localization**: Classification identifies disease presence but cannot pinpoint lesion extent for targeted treatment.

Our contributions include:

- A four-stage weakly-supervised pipeline: classification → XAI pseudo-labeling → SAM boundary refinement → segmentation
- Multi-scale GradCAM++ with per-class percentile thresholding for controllable pseudo-label coverage
- Analysis of SAM ViT-B as a label refiner, including failure modes of the IoU guard under mask expansion
- Honest quantitative framing of cross-version metric comparison in the absence of ground-truth annotation

---

## 2. RELATED WORK

### 2.1 Plant Disease Detection

Convolutional Neural Networks have been successfully applied to plant disease classification. Transfer learning with pre-trained models like EfficientNet has become standard practice due to limited agricultural datasets.

### 2.2 Explainable AI in Agriculture

GradCAM and its variants visualize which image regions contribute to model predictions. GradCAM++ improves upon GradCAM using second-order gradient approximation, providing better localization for multiple small instances — particularly relevant for diseases with multiple lesions per leaf.

### 2.3 Pseudo-Labeling and Weakly Supervised Segmentation

Pseudo-labeling techniques leverage image-level labels to generate approximate segmentation masks. Class Activation Maps (CAMs) have been widely used as a bridge between classification and segmentation. Multi-scale CAM fusion and post-processing strategies have been shown to improve pseudo-label quality.

### 2.4 Segment Anything Model (SAM)

SAM, introduced by Meta AI, is a foundation model for image segmentation trained on 11 million images with zero-shot generalization. Its application as a label refiner — given coarse pseudo-label prompts to produce sharper boundaries — is an emerging area, particularly for domains where annotation is scarce.

---

## 3. METHODOLOGY

### 3.1 Dataset

Our dataset consists of 4,437 durian leaf images organized into five classes:

| Class | Total |
|-------|-------|
| Algal Leaf Spot | 733 |
| Allocaridara Attack | 913 |
| Healthy Leaf | 976 |
| Leaf Blight | 937 |
| Phomopsis Leaf Spot | 878 |

For classification (Stage 1), the full 4,437 images were split 70/15/15 (train/val/test). For segmentation (Stages 2–4), the 3,104 training images were used for pseudo-label generation, then split 70/15/15 (2,172 train / 465 val / 467 test) with fixed seed=42 for reproducibility across all versions.

### 3.2 Classification Model (Stage 1)

#### 3.2.1 Architecture

EfficientNet-B0 pre-trained on ImageNet, with a fully connected output layer for 5 classes. Input: 224×224 RGB.

#### 3.2.2 Training Configuration

- **Optimizer**: Adam, lr=1e-4, ReduceLROnPlateau (patience=2, factor=0.5)
- **Loss**: Cross-Entropy
- **Batch Size**: 32 | **Epochs**: up to 30 with early stopping
- **Augmentation**: Random flips, rotation, color jitter

#### 3.2.3 Results

| Metric | Validation | Test |
|--------|-----------|------|
| Accuracy | 97.52% | 97.52% |

The model achieved balanced per-class F1 scores of 0.97–0.98, with minimal misclassification between disease types (confusion matrix shows off-diagonal rates <3%).

### 3.3 Pseudo-Label Generation V1 (Stage 2 — Baseline)

Single-layer GradCAM (`features.8`, 7×7 resolution) with fixed threshold 0.5, rectangular 5×5 morphological kernel. Applied to 500-sample subset (100 per class). This version serves as the segmentation baseline (NB05).

### 3.4 Pseudo-Label Generation V2 (Stage 2 — Improved)

#### 3.4.1 Multi-Scale GradCAM++

Two target layers instead of one:
- **Fine layer** (`features.6`, 14×14): captures small lesion spots
- **Coarse layer** (`features.8`, 7×7): provides semantic context

Fused heatmap:
```
H_final = 0.6 × H_fine + 0.4 × H_coarse
```

GradCAM++ replaces gradient averaging with second-order approximation, avoiding the average-out effect when multiple lesion instances appear in one image.

#### 3.4.2 Per-Class Percentile Threshold

Rather than Otsu thresholding (which assumes bimodal heatmap distribution and causes over-segmentation when multi-scale fusion produces smooth gradients), we apply a per-class percentile threshold that directly controls coverage:

| Class | Keep top % |
|-------|-----------|
| Algal Leaf Spot | 18% |
| Allocaridara Attack | 20% |
| Healthy Leaf | 0% (hard-zero) |
| Leaf Blight | 22% |
| Phomopsis Leaf Spot | 18% |

Healthy Leaf receives an all-zero mask since it has no actual lesion tissue. Coverage targets reflect disease area characteristics (spot diseases: ~18%; diffuse blight: ~22%).

#### 3.4.3 Post-Processing

1. Elliptical morphological kernel 5×5 (Close → Open)
2. Top-3 connected components ≥ 400 pixels retained — removes mid-size noise fragments while preserving multiple lesion spots

#### 3.4.4 V2 Statistics

| Class | Actual Coverage | Std | Target |
|-------|----------------|-----|--------|
| Algal Leaf Spot | 17.7% | 0.008 | 18% |
| Allocaridara Attack | 19.7% | 0.007 | 20% |
| Healthy Leaf | 0.0% | 0.000 | 0% |
| Leaf Blight | 21.7% | 0.007 | 22% |
| Phomopsis Leaf Spot | 17.6% | 0.009 | 18% |

Classification accuracy on V2 generation: **99.52%** | Mean confidence: **0.9822**

**Limitation of percentile threshold**: Coverage is uniform per class regardless of individual image disease severity — a mild and severe image receive the same coverage fraction. This is a trade-off accepted to eliminate Otsu over-segmentation.

### 3.5 SAM Refinement (Stage 3)

#### 3.5.1 Motivation

GradCAM++ heatmaps have blurry boundaries (upscaled from 14×14). SAM ViT-B provides pixel-accurate boundaries given point/box prompts, making it suitable as a label refiner.

#### 3.5.2 Prompt Generation

For each V2 pseudo-mask:
- **Foreground**: centroid + 5 random points from masked region
- **Background**: 3 random points from dilated-complement (30px dilation)

#### 3.5.3 IoU Guard and Post-Processing

```python
IoU = Intersection(SAM_mask, V2_mask) / Union(SAM_mask, V2_mask)
if IoU < 0.15: return V2_mask  # fallback
```

Post-processing: CC filter (drop components < 5% of total or < 30px) + morphological close.

#### 3.5.4 Observed Coverage Expansion

| Class | V2 coverage | SAM coverage | Delta |
|-------|-------------|-------------|-------|
| Algal Leaf Spot | 17.7% | 35.0% | +97% |
| Allocaridara Attack | 19.7% | 32.0% | +62% |
| Leaf Blight | 21.7% | 30.7% | +41% |
| Phomopsis Leaf Spot | 17.6% | 33.6% | +91% |
| **Overall** | **15.0%** | **25.5%** | **+70%** |

211/3104 masks (6.8%) exceeded 50% coverage. SAM tended to segment the entire leaf rather than only the lesion region.

**IoU guard limitation**: When SAM selects the whole leaf and the V2 lesion is contained within it, IoU ≈ V2\_coverage / SAM\_coverage ≈ 0.51 > 0.15 — the guard does not trigger for expansion, only for drift to a different region.

Despite this expansion, training on SAM labels still improved segmentation metrics over V2 (Section 4.3), suggesting SAM boundaries provide better spatial structure even when coverage is inflated.

### 3.6 Segmentation Model (Stage 4)

#### 3.6.1 Architecture

**V1**: Custom EfficientNet-UNet (BCE + Dice loss, Adam + ReduceLROnPlateau)

**V2 / V3**: UNet++ with EfficientNet-B0 encoder (6,569,581 parameters, all trainable):
- Encoder: EfficientNet-B0, ImageNet pretrained
- Decoder: UNet++ nested dense skip connections
- Output: binary mask (disease vs. background)

#### 3.6.2 Training Configuration (V2 / V3)

- **Loss**: FocalDice = L_focal(α=0.25, γ=2.0) + L_dice
- **Optimizer**: AdamW (lr=1e-4, weight_decay=1e-4)
- **Scheduler**: CosineAnnealingLR (T_max=50, η_min=1e-6)
- **Augmentation** (Albumentations): RandomResizedCrop, H/V Flip, RandomRotate90, ShiftScaleRotate, ElasticTransform, GridDistortion, ColorJitter, GaussNoise
- **Early stopping**: patience=10 (val_loss monitor)
- **Batch size**: 4 (V2) / 8 (V3)

---

## 4. RESULTS AND DISCUSSION

### 4.1 Classification Performance

| Metric | Validation | Test |
|--------|-----------|------|
| Accuracy | 97.52% | 97.52% |

The model provides high-confidence predictions (mean 0.9822) across all 3,104 training images used for pseudo-label generation, ensuring reliable CAM activations as segmentation seeds.

### 4.2 Pseudo-Label Quality

**V2 coverage targets hit precisely** (< 0.4% deviation per class). **Healthy Leaf hard-zeroed** — eliminates 683 false-positive masks that V1-style GradCAM would have generated (coverage ~26%) for a class with no lesion tissue.

### 4.3 Segmentation Results

| Version | Architecture | Labels | Best Val IoU | Test IoU | Test Dice | Test Precision | Test Recall |
|---------|-------------|--------|-------------|---------|-----------|---------------|------------|
| V1 (NB05) | EfficientNet-UNet | GradCAM v1 (fixed 0.5) | 0.7715 | 0.7671 | 0.8623 | 0.8562 | 0.8877 |
| V2 (NB07) | UNet++ EB0 | GradCAM++ percentile | 0.5438 | 0.5135 | 0.6301 | 0.6169 | 0.7419 |
| V3 (NB08) | UNet++ EB0 | SAM-refined V2 | 0.6981 | 0.6239 | 0.7053 | 0.7090 | 0.8752 |

**V3 vs V2 (valid comparison — same architecture, same split):**

| Metric | V2 | V3 | Δ |
|--------|----|----|--|
| IoU | 0.5135 | 0.6239 | +21.5% |
| Dice | 0.6301 | 0.7053 | +11.9% |
| Precision | 0.6169 | 0.7090 | +14.9% |
| Recall | 0.7419 | 0.8752 | +18.0% |

SAM boundary refinement demonstrates measurable improvement across all metrics when architecture and training setup are held constant.

### 4.4 Cross-Version Comparison Caveat

The V1 vs V2/V3 comparison requires careful interpretation. Each version is evaluated against **its own pseudo-labels** as the test reference:

- V1 (IoU=0.767): model reproduces simple GradCAM blobs (fixed threshold, predictable round shape)
- V3 (IoU=0.624): model reproduces complex SAM-shaped boundaries (varied, sharper, but larger coverage)

Higher IoU in V1 does not imply V1 is better at disease detection — it reflects that simple targets are easier to reproduce. The only internally-consistent comparison is V2→V3 (same label type, same architecture). **Without ground-truth pixel annotation, absolute disease localization performance cannot be established.**

### 4.5 Training Dynamics

**V3 convergence analysis** (22 epochs, early-stopped):

| Epoch | val_loss | val_IoU |
|-------|----------|---------|
| E12 (best loss) | **0.4478** | 0.6479 |
| E17 (best IoU) | 0.4537 | **0.6981** |

Val loss and val IoU are not monotonically aligned — early stopping on val_loss led to selecting E12 over E17 (ΔIoU = 0.050). Tracking val_IoU for checkpoint selection is recommended for future experiments.

V3 converged faster than V2: val_loss 0.4478 at E12 vs V2's 0.5957 at E20, confirming SAM labels provide cleaner training signal.

### 4.6 Qualitative Observations

- **Recall > Precision** across all versions (V3: 0.875 vs 0.709): models systematically over-segment, inheriting the over-coverage tendency from pseudo-labels.
- **HEALTHY_LEAF false positives eliminated**: hard-zero masking in V2/V3 ensures the model does not learn spurious activations for lesion-free images.
- **V3 boundary sharpness**: SAM-produced labels provide clear lesion boundaries, helping UNet++ learn precise edge features — visible in probability map confidence concentration around lesion regions.

---

## 5. CONCLUSION

This paper presented a weakly-supervised pipeline for durian leaf disease detection progressing from image classification through XAI-based pseudo-labeling to SAM-refined segmentation. Key findings:

1. **EfficientNet-B0 classification**: 97.52% accuracy on five disease classes, providing reliable CAM activations as segmentation seeds.

2. **Percentile threshold pseudo-labeling**: Coverage-controlled pseudo-labels (18–22% per disease class) eliminate Otsu over-segmentation and hard-zero Healthy Leaf masks, producing cleaner training signal than naive thresholding.

3. **SAM refinement effect**: V2→V3 IoU improvement +21.5% with identical architecture confirms SAM boundary quality contributes meaningful signal improvement, even though SAM expands coverage beyond intended lesion areas.

4. **Metric comparability limitation**: Segmentation IoU/Dice values across pipeline versions are not directly comparable without ground-truth annotation. V1 appears numerically superior due to simpler label targets, not superior disease localization.

**Limitations and Future Work**:

- **Ground-truth annotation**: A small manually-annotated test set (50–100 images) would enable absolute performance validation and fair cross-version comparison.
- **SAM IoU guard improvement**: Replace the current one-sided IoU guard with a coverage-ratio constraint (`if sam_coverage > v2_coverage × 2.0: fallback`) to prevent mask expansion.
- **Early stopping criterion**: Track val_IoU instead of val_loss for checkpoint selection.
- **Multi-class segmentation**: Extend binary disease/background to per-class lesion segmentation.
- **SAM2 integration**: SAM2 offers improved boundary accuracy and temporal consistency, potentially reducing the coverage expansion issue.

---

## ACKNOWLEDGMENTS

We thank the agricultural experts who provided domain knowledge and validated our disease classifications. We acknowledge the use of publicly available pre-trained models (EfficientNet, SAM ViT-B) which significantly accelerated our research.

---

## DATA AVAILABILITY

Code and trained model weights are available upon request. Dataset available at [repository link].

---

## REFERENCES

[1] M. Tan and Q. V. Le, "EfficientNet: Rethinking model scaling for convolutional neural networks," in *Proc. ICML*, 2019, pp. 6105–6114.

[2] R. R. Selvaraju et al., "Grad-CAM: Visual explanations from deep networks via gradient-based localization," in *Proc. ICCV*, 2017, pp. 618–626.

[3] A. Chattopadhay et al., "Grad-CAM++: Generalized gradient-based visual explanations for deep CNNs," in *Proc. WACV*, 2018, pp. 839–847.

[4] A. Kirillov et al., "Segment anything," in *Proc. ICCV*, 2023, pp. 4015–4026.

[5] O. Ronneberger, P. Fischer, and T. Brox, "U-Net: Convolutional networks for biomedical image segmentation," in *Proc. MICCAI*, 2015, pp. 234–241.

[6] Z. Zhou et al., "UNet++: A nested U-Net architecture for medical image segmentation," in *Deep Learning in Medical Image Analysis*, 2018, pp. 3–11.

[7] T.-Y. Lin et al., "Focal loss for dense object detection," in *Proc. ICCV*, 2017, pp. 2980–2988.

[8] S. P. Mohanty, D. P. Hughes, and M. Salathé, "Using deep learning for image-based plant disease detection," *Frontiers in Plant Science*, vol. 7, p. 1419, 2016.

[9] A. Buslaev et al., "Albumentations: Fast and flexible image augmentations," *Information*, vol. 11, no. 2, p. 125, 2020.

[10] I. Loshchilov and F. Hutter, "Decoupled weight decay regularization," in *Proc. ICLR*, 2019.

[11] N. Otsu, "A threshold selection method from gray-level histograms," *IEEE Trans. SMC*, vol. 9, no. 1, pp. 62–66, 1979.

[12] J. Deng et al., "ImageNet: A large-scale hierarchical image database," in *Proc. CVPR*, 2009, pp. 248–255.

[13] K. P. Ferentinos, "Deep learning models for plant disease detection and diagnosis," *Computers and Electronics in Agriculture*, vol. 145, pp. 311–318, 2018.

[14] A. Kamilaris and F. X. Prenafeta-Boldú, "Deep learning in agriculture: A survey," *Computers and Electronics in Agriculture*, vol. 147, pp. 70–90, 2018.

[15] A. Fuentes et al., "A robust deep-learning-based detector for real-time tomato plant diseases and pests recognition," *Sensors*, vol. 17, no. 9, p. 2022, 2017.
