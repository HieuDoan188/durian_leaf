import os
import sys
import json

import cv2
import numpy as np
import requests
import streamlit as st
import torch
from PIL import Image
from torchvision import transforms
import albumentations as A
from albumentations.pytorch import ToTensorV2
import segmentation_models_pytorch as smp
import plotly.graph_objects as go

app_dir = os.path.dirname(os.path.abspath(__file__))
proj_root = os.path.dirname(app_dir)
sys.path.insert(0, proj_root)

from utils.models import EfficientNetClassifier, EfficientNetUNet
from utils.gradcam import GradCAMGenerator, find_efficientnet_target_layer

# ── Constants ────────────────────────────────────────────────────────────────
CLASS_NAMES = [
    "ALGAL_LEAF_SPOT",
    "ALLOCARIDARA_ATTACK",
    "HEALTHY_LEAF",
    "LEAF_BLIGHT",
    "PHOMOPSIS_LEAF_SPOT",
]
CLASS_LABELS = [
    "Algal Leaf Spot",
    "Allocaridara Attack",
    "Healthy Leaf",
    "Leaf Blight",
    "Phomopsis Leaf Spot",
]
CLASS_COLORS = ["#E69F00", "#56B4E9", "#009E73", "#0072B2", "#D55E00"]

CKPT_CLS  = os.path.join(proj_root, "notebooks", "models", "classification",    "checkpoints", "best_model.pth")
CKPT_SEG  = {
    "V5 — Disease color prior": os.path.join(proj_root, "notebooks", "models", "segmentation_v5", "checkpoints", "unetpp_v5_best.pth"),
    "V3 — SAM diagnostic": os.path.join(proj_root, "notebooks", "models", "segmentation_v3", "checkpoints", "unetpp_v3_best.pth"),
    "V2 — GradCAM++ pseudo-labels": os.path.join(proj_root, "notebooks", "models", "segmentation_v2", "checkpoints", "unetpp_best.pth"),
    "V1 — Baseline": os.path.join(proj_root, "notebooks", "models", "segmentation",    "checkpoints", "efficientnet_unet_best.pth"),
}

SEG_INFO = {
    "V1 — Baseline": {
        "architecture": "EfficientNet-B0 encoder + custom U-Net decoder",
        "pseudo_label": "V1 Grad-CAM threshold masks",
        "model_dir": "segmentation",
    },
    "V2 — GradCAM++ pseudo-labels": {
        "architecture": "UNet++ with EfficientNet-B0 encoder",
        "pseudo_label": "V2 multi-scale GradCAM++ percentile masks",
        "model_dir": "segmentation_v2",
    },
    "V3 — SAM diagnostic": {
        "architecture": "UNet++ with EfficientNet-B0 encoder",
        "pseudo_label": "V3 SAM-refined V2 masks with coverage guard",
        "model_dir": "segmentation_v3",
    },
    "V5 — Disease color prior": {
        "architecture": "UNet++ with EfficientNet-B0 encoder",
        "pseudo_label": "V5 GradCAM++ intersected with disease color priors",
        "model_dir": "segmentation_v5",
    },
}

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

CLS_TRANSFORM = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])
SEG_TRANSFORM = A.Compose([
    A.Resize(224, 224),
    A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ToTensorV2(),
])


def read_json_safe(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_nested(data, *keys, default=None):
    cur = data or {}
    for key in keys:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def fmt_value(value, pct=False):
    if value is None:
        return "n/a"
    if isinstance(value, (int, np.integer)):
        return f"{value:,}"
    if isinstance(value, (float, np.floating)):
        return f"{value * 100:.2f}%" if pct else f"{value:.4f}"
    return str(value)


def count_parameters(model):
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return total, trainable


def file_size_mb(path):
    return os.path.getsize(path) / (1024 * 1024) if os.path.exists(path) else None


def segmentation_metrics_for(seg_name):
    model_dir = SEG_INFO.get(seg_name, {}).get("model_dir", "")
    metrics_dir = os.path.join(proj_root, "notebooks", "models", model_dir, "metrics")
    test_metrics = read_json_safe(os.path.join(metrics_dir, "test_metrics.json"))
    history = read_json_safe(os.path.join(metrics_dir, "training_history.json"))
    manual_gt = read_json_safe(os.path.join(metrics_dir, "manual_gt_metrics.json"))
    return test_metrics, history, manual_gt


def best_from_history(history, key, mode="max"):
    vals = history.get(key, []) if isinstance(history, dict) else []
    vals = [v for v in vals if isinstance(v, (int, float))]
    if not vals:
        return None
    return max(vals) if mode == "max" else min(vals)


# ── Advisory helpers ─────────────────────────────────────────────────────────
DISEASE_GUIDANCE = {
    "ALGAL_LEAF_SPOT": {
        "name_vi": "Đốm rong/tảo trên lá",
        "signals": "đốm cam, vàng gỉ hoặc nâu nhỏ, thường rải rác trên phiến lá",
        "actions": [
            "Tỉa bớt cành/lá quá rậm để tăng thông thoáng tán.",
            "Hạn chế tưới phun lên lá, nhất là chiều tối hoặc khi vườn ẩm kéo dài.",
            "Loại bỏ lá bị nặng để giảm nguồn lây trong vườn.",
            "Nếu lan rộng, hỏi cán bộ kỹ thuật về thuốc gốc đồng hoặc chế phẩm được phép dùng tại địa phương.",
        ],
    },
    "ALLOCARIDARA_ATTACK": {
        "name_vi": "Tổn thương do Allocaridara/côn trùng chích hút",
        "signals": "vết hại nâu vàng, thủng lá, vùng mô bị bạc màu hoặc loang quanh mép/vết thương",
        "actions": [
            "Kiểm tra mặt dưới lá, đọt non và các cây lân cận để tìm côn trùng hoặc trứng.",
            "Cắt bỏ lá bị hại nặng và vệ sinh tàn dư quanh gốc.",
            "Ưu tiên biện pháp cơ học/sinh học nếu mật số thấp; theo dõi lại sau 3-5 ngày.",
            "Nếu mật số cao, dùng thuốc trừ sâu đã đăng ký cho sầu riêng theo đúng nhãn và hướng dẫn địa phương.",
        ],
    },
    "HEALTHY_LEAF": {
        "name_vi": "Lá khỏe",
        "signals": "không có vùng tổn thương rõ theo mô hình",
        "actions": [
            "Tiếp tục theo dõi định kỳ, đặc biệt sau mưa hoặc giai đoạn vườn ẩm.",
            "Duy trì tán thông thoáng, dinh dưỡng cân đối và vệ sinh vườn.",
            "Nếu quan sát thực tế có đốm lạ nhưng mô hình dự đoán khỏe, nên chụp lại ảnh rõ hơn dưới ánh sáng đều.",
        ],
    },
    "LEAF_BLIGHT": {
        "name_vi": "Cháy lá",
        "signals": "vùng cháy nâu, vàng úa, mô hoại tử lớn hoặc lan từ mép lá",
        "actions": [
            "Cắt bỏ phần lá/cành bị cháy nặng và tiêu hủy xa khu trồng.",
            "Giảm ẩm độ tán: tỉa cành, tránh tưới phun lên lá, cải thiện thoát nước.",
            "Theo dõi tốc độ lan trong 3-7 ngày; ưu tiên xử lý sớm nếu vết cháy lan nhanh.",
            "Tham khảo cán bộ kỹ thuật về thuốc phòng trị nấm/khuẩn đã đăng ký, dùng đúng liều và thời gian cách ly.",
        ],
    },
    "PHOMOPSIS_LEAF_SPOT": {
        "name_vi": "Đốm lá Phomopsis",
        "signals": "đốm nâu/xám, tâm hoại tử hoặc viền tối, có thể nhỏ và rải rác",
        "actions": [
            "Thu gom lá bệnh, tỉa lá/cành che khuất để giảm ẩm và nguồn bào tử.",
            "Tránh làm xây xát lá non; hạn chế tưới phun khi chiều tối.",
            "Theo dõi các đốm nhỏ mới xuất hiện vì bệnh có thể bị nhầm với chói sáng hoặc vết cơ học.",
            "Nếu xuất hiện nhiều ổ bệnh, hỏi kỹ sư nông nghiệp về thuốc nấm phù hợp và luân phiên hoạt chất theo khuyến cáo.",
        ],
    },
}


def severity_from_coverage(class_name, coverage_pct, confidence):
    if class_name == "HEALTHY_LEAF" or coverage_pct <= 0.2:
        return "Không phát hiện rõ", "Chưa thấy vùng bệnh đáng kể trên ảnh."
    if coverage_pct < 3:
        level, note = "Nhẹ", "Vùng nghi bệnh nhỏ; nên theo dõi thêm và xử lý vệ sinh cơ bản."
    elif coverage_pct < 10:
        level, note = "Trung bình", "Vùng nghi bệnh đã rõ; nên kiểm tra nhiều lá/cây lân cận."
    elif coverage_pct < 20:
        level, note = "Khá nặng", "Tỷ lệ vùng nghi bệnh cao; cần can thiệp sớm và kiểm tra điều kiện vườn."
    else:
        level, note = "Nặng", "Vùng nghi bệnh rất rộng; nên xác minh thực địa và xử lý theo hướng dẫn chuyên môn."
    if confidence < 0.75:
        note += " Độ tin cậy phân loại chưa cao nên cần xem như cảnh báo sơ bộ."
    return level, note


def get_llm_api_key():
    if os.getenv("OPENAI_API_KEY"):
        return os.getenv("OPENAI_API_KEY")
    try:
        return st.secrets.get("OPENAI_API_KEY", "")
    except Exception:
        return ""


def build_advisory_context(pred_idx, probs, coverage, seg_choice, inference_mode, color_prior_strength, post_debug):
    class_name = CLASS_NAMES[pred_idx]
    top_probs = sorted(
        [{"class": CLASS_LABELS[i], "probability": float(probs[i])} for i in range(len(probs))],
        key=lambda x: x["probability"],
        reverse=True,
    )
    debug_summary = {}
    if post_debug:
        debug_summary = {
            "color_prior_used": True,
            "rescue_coverage_pct": float(post_debug.get("rescue", np.zeros((1, 1))).mean() * 100),
            "valid_tissue_coverage_pct": float(post_debug.get("leaf", np.zeros((1, 1))).mean() * 100),
        }
    return {
        "predicted_class": CLASS_LABELS[pred_idx],
        "predicted_class_key": class_name,
        "confidence_pct": float(probs[pred_idx] * 100),
        "lesion_coverage_pct": float(coverage),
        "severity": severity_from_coverage(class_name, coverage, float(probs[pred_idx]))[0],
        "segmentation_model": seg_choice,
        "inference_mode": inference_mode,
        "color_prior_strength": float(color_prior_strength),
        "top_probabilities": top_probs,
        "debug": debug_summary,
        "class_guidance": DISEASE_GUIDANCE[class_name],
    }


def rule_based_advisory(context):
    class_name = context["predicted_class_key"]
    guidance = context["class_guidance"]
    severity, severity_note = severity_from_coverage(
        class_name,
        context["lesion_coverage_pct"],
        context["confidence_pct"] / 100.0,
    )
    actions = "\n".join([f"{i + 1}. {action}" for i, action in enumerate(guidance["actions"])])
    uncertainty = []
    if context["confidence_pct"] < 80:
        uncertainty.append("độ tin cậy phân loại chưa cao")
    if context["lesion_coverage_pct"] < 1 and class_name != "HEALTHY_LEAF":
        uncertainty.append("mask rất nhỏ nên có thể bỏ sót vết bệnh mờ")
    if context["inference_mode"] != "Model only":
        uncertainty.append("kết quả có hậu xử lý màu nên phụ thuộc ánh sáng ảnh chụp")
    uncertainty_text = "; ".join(uncertainty) if uncertainty else "kết quả tương đối nhất quán giữa phân loại và mask"

    return f"""### Đánh giá mức độ
- **Loại dự đoán:** {context['predicted_class']} ({guidance['name_vi']})
- **Mức độ ước tính:** **{severity}**
- **Diện tích vùng nghi bệnh:** {context['lesion_coverage_pct']:.1f}% ảnh chuẩn hóa 224x224
- **Nhận định:** {severity_note}

### Dấu hiệu cần kiểm tra ngoài vườn
{guidance['signals']}.

### Gợi ý xử lý
{actions}

### Lưu ý độ tin cậy
Đây là tư vấn hỗ trợ dựa trên mô hình AI, không thay thế chẩn đoán của kỹ sư nông nghiệp. Điểm cần chú ý: {uncertainty_text}. Khi dùng thuốc BVTV, chỉ dùng sản phẩm được phép tại địa phương và làm đúng nhãn."""


@st.cache_data(ttl=3600, show_spinner=False)
def llm_advisory_cached(context_json, model_name, api_key):
    context = json.loads(context_json)
    prompt = f"""
Bạn là trợ lý kỹ thuật nông nghiệp cho demo luận văn về bệnh lá sầu riêng.
Hãy viết bằng tiếng Việt, ngắn gọn, thực tế, không khẳng định quá mức.

Dữ liệu mô hình:
{json.dumps(context, ensure_ascii=False, indent=2)}

Yêu cầu trả lời theo 4 mục Markdown:
1. Đánh giá mức độ bệnh
2. Vì sao mô hình đưa ra nhận định đó
3. Phương án xử lý cụ thể tại vườn
4. Lưu ý an toàn và giới hạn của AI

Không tự bịa lịch phun thuốc hoặc liều lượng hóa chất. Nếu cần thuốc, hãy nói
tham khảo kỹ sư nông nghiệp/cán bộ địa phương và tuân thủ nhãn sản phẩm.
"""
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model_name,
            "messages": [
                {
                    "role": "system",
                    "content": "Bạn là trợ lý nông nghiệp thận trọng, giải thích kết quả AI theo hướng hỗ trợ quyết định.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 900,
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()


def generate_advisory(context, use_llm, llm_model):
    if not use_llm:
        return rule_based_advisory(context), "Rule-based advisory"
    api_key = get_llm_api_key()
    if not api_key:
        fallback = rule_based_advisory(context)
        note = "\n\n> Chưa cấu hình `OPENAI_API_KEY`, nên app đang dùng tư vấn rule-based thay cho LLM."
        return fallback + note, "Rule-based fallback"
    try:
        context_json = json.dumps(context, ensure_ascii=False, sort_keys=True)
        return llm_advisory_cached(context_json, llm_model, api_key), f"LLM: {llm_model}"
    except Exception as exc:
        fallback = rule_based_advisory(context)
        note = f"\n\n> LLM gọi lỗi (`{type(exc).__name__}`), nên app dùng tư vấn rule-based fallback."
        return fallback + note, "Rule-based fallback"


# ── Model loaders (cached) ────────────────────────────────────────────────────
@st.cache_resource
def load_classifier():
    model = EfficientNetClassifier(num_classes=len(CLASS_NAMES), backbone="efficientnet_b0", pretrained=False)
    ckpt  = torch.load(CKPT_CLS, map_location=device, weights_only=False)
    model.load_state_dict(ckpt["model_state_dict"])
    model.to(device).eval()
    return model


@st.cache_resource
def load_segmentor(seg_name: str):
    ckpt_path = CKPT_SEG[seg_name]
    if seg_name.startswith("V1"):
        model = EfficientNetUNet(num_classes=1, pretrained=False).to(device)
    else:
        model = smp.UnetPlusPlus(
            encoder_name="efficientnet-b0",
            encoder_weights=None,
            in_channels=3, classes=1, activation=None,
        ).to(device)
    ckpt = torch.load(ckpt_path, map_location=device, weights_only=False)
    model.load_state_dict(ckpt["model_state_dict"])
    model.eval()
    epoch    = ckpt.get("epoch", "?")
    val_loss = ckpt.get("val_loss", float("nan"))
    return model, epoch, val_loss


# ── Inference helpers ─────────────────────────────────────────────────────────
def run_classification(model, pil_img):
    tensor = CLS_TRANSFORM(pil_img).unsqueeze(0).to(device)
    with torch.enable_grad():
        logits = model(tensor)
        probs = torch.softmax(logits, dim=1)[0].detach().cpu().numpy()
    pred_idx = int(np.argmax(probs))
    return probs, pred_idx, tensor


def run_gradcam(cls_model, tensor, pred_idx):
    target_layer = find_efficientnet_target_layer(cls_model)
    gen = GradCAMGenerator(cls_model, target_layer, device=device.type)
    heatmap, _, _ = gen.generate(tensor, pred_idx)
    return heatmap


def run_segmentation(seg_model, pil_img):
    img_np    = np.array(pil_img.resize((224, 224)))
    aug       = SEG_TRANSFORM(image=img_np)
    seg_input = aug["image"].unsqueeze(0).to(device)
    with torch.no_grad():
        prob = torch.sigmoid(seg_model(seg_input))[0, 0].cpu().numpy()
    mask = (prob > 0.5).astype(np.uint8)
    return prob, mask


def normalize01(arr):
    arr = np.asarray(arr, dtype=np.float32)
    arr = arr - np.nanmin(arr)
    max_val = np.nanmax(arr)
    if max_val > 0:
        arr = arr / max_val
    return np.nan_to_num(arr, nan=0.0, posinf=1.0, neginf=0.0)


def heatmap_to_2d(heatmap, target_shape=None):
    h = np.asarray(heatmap)
    h = np.squeeze(h)
    while h.ndim > 2:
        h = h.mean(axis=-1)
    h = h.astype(np.float32)
    if target_shape is not None and h.shape[:2] != target_shape:
        h = cv2.resize(h, (target_shape[1], target_shape[0]), interpolation=cv2.INTER_LINEAR)
    return normalize01(h)


def clean_binary(mask, close=5, open_=3, min_area=18, top_k=12):
    mask = np.squeeze(np.asarray(mask)).astype(np.uint8)
    if close > 0:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close, close))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k)
    if open_ > 0:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (open_, open_))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, k)

    num, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    comps = []
    for i in range(1, num):
        area = stats[i, cv2.CC_STAT_AREA]
        if area >= min_area:
            comps.append((area, i))
    comps = sorted(comps, reverse=True)[:top_k]
    out = np.zeros_like(mask, dtype=np.uint8)
    for _, i in comps:
        out[labels == i] = 1
    return out


def clean_rescue_mask(mask, min_area=18, top_k=8, max_aspect=8.0, min_extent=0.12):
    mask = clean_binary(mask, close=5, open_=3, min_area=min_area, top_k=top_k * 3)
    num, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    comps = []
    for i in range(1, num):
        area = stats[i, cv2.CC_STAT_AREA]
        w = max(1, stats[i, cv2.CC_STAT_WIDTH])
        h = max(1, stats[i, cv2.CC_STAT_HEIGHT])
        aspect = max(w / h, h / w)
        extent = area / float(w * h)
        if area >= min_area and aspect <= max_aspect and extent >= min_extent:
            comps.append((area, i))
    comps = sorted(comps, reverse=True)[:top_k]
    out = np.zeros_like(mask, dtype=np.uint8)
    for _, i in comps:
        out[labels == i] = 1
    return out


def leaf_mask_rule(img_rgb):
    hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
    lab = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2LAB)
    H, S, V = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    A, B = lab[:, :, 1], lab[:, :, 2]
    green = ((H >= 25) & (H <= 95) & (S >= 25) & (V >= 35)).astype(np.uint8)
    yellow_green = ((H >= 18) & (H <= 105) & (S >= 18) & (V >= 45) & (A <= 142) & (B >= 118)).astype(np.uint8)
    leaf = np.logical_or(green, yellow_green).astype(np.uint8)
    return clean_binary(leaf, close=15, open_=5, min_area=450, top_k=3)


def plant_tissue_mask_rule(img_rgb):
    hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
    lab = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2LAB)
    H, S, V = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    A, B = lab[:, :, 1], lab[:, :, 2]
    green_leaf = ((H >= 25) & (H <= 95) & (S >= 20) & (V >= 35)).astype(np.uint8)
    damaged_tissue = (
        ((H <= 35) & (S >= 30) & (V >= 45) & (V <= 220))
        | ((S <= 85) & (V >= 55) & (V <= 190) & (A >= 118) & (B >= 116))
    ).astype(np.uint8)
    not_sky_or_white = ~((S < 22) & (V > 170))
    tissue = ((green_leaf | damaged_tissue) & not_sky_or_white).astype(np.uint8)
    return clean_binary(tissue, close=7, open_=3, min_area=160, top_k=8)


def select_leaf_by_heat(leaf, heat, max_components=2):
    leaf = np.squeeze(np.asarray(leaf)).astype(np.uint8)
    heat = heatmap_to_2d(heat, target_shape=leaf.shape[:2])
    num, labels, stats, _ = cv2.connectedComponentsWithStats(leaf, 8)
    comps = []
    for i in range(1, num):
        comp = labels == i
        area = stats[i, cv2.CC_STAT_AREA]
        if area < 450:
            continue
        overlap = float(heat[comp].mean()) if comp.any() else 0.0
        score = overlap * np.sqrt(area)
        comps.append((score, area, i))
    comps = sorted(comps, reverse=True)[:max_components]
    out = np.zeros_like(leaf, dtype=np.uint8)
    for _, _, i in comps:
        out[labels == i] = 1
    return out if out.any() else leaf


def disease_color_prior(img_rgb, class_name):
    hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
    lab = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2LAB)
    H, S, V = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
    L, A, B = lab[:, :, 0], lab[:, :, 1], lab[:, :, 2]

    rust_orange = ((H <= 28) & (S >= 45) & (V >= 55)).astype(np.float32)
    brown_necrosis = (((H <= 24) | (H >= 165)) & (S >= 35) & (V >= 35) & (V <= 205)).astype(np.float32)
    yellow_chlorosis = ((H >= 18) & (H <= 45) & (S >= 30) & (V >= 95)).astype(np.float32)
    pale_scar = ((S >= 12) & (S <= 85) & (V >= 115) & (A >= 116) & (B >= 126)).astype(np.float32)
    gray_brown = ((S <= 95) & (V >= 45) & (V <= 185) & (A >= 118) & (B >= 116)).astype(np.float32)

    if class_name == "ALGAL_LEAF_SPOT":
        prior = 0.75 * rust_orange + 0.45 * yellow_chlorosis + 0.35 * brown_necrosis
    elif class_name == "ALLOCARIDARA_ATTACK":
        prior = 0.65 * brown_necrosis + 0.55 * yellow_chlorosis + 0.45 * pale_scar + 0.25 * rust_orange
    elif class_name == "LEAF_BLIGHT":
        prior = 0.75 * brown_necrosis + 0.65 * yellow_chlorosis + 0.45 * pale_scar
    elif class_name == "PHOMOPSIS_LEAF_SPOT":
        highlight_reject = ((V < 220) & (L < 210) & ~((S < 38) & (V > 170))).astype(np.float32)
        prior = (0.65 * gray_brown + 0.50 * brown_necrosis + 0.35 * rust_orange) * highlight_reject
    else:
        prior = np.zeros(H.shape, dtype=np.float32)

    return normalize01(prior)


def color_prior_postprocess(img_rgb, class_name, heatmap, model_mask, mode, strength=0.35):
    if class_name == "HEALTHY_LEAF":
        return np.zeros_like(model_mask, dtype=np.uint8), {}

    heat = heatmap_to_2d(heatmap, target_shape=model_mask.shape[:2])
    green_leaf = select_leaf_by_heat(leaf_mask_rule(img_rgb), heat, max_components=1)
    tissue = plant_tissue_mask_rule(img_rgb)
    target_tissue = select_leaf_by_heat(tissue, heat, max_components=1)
    prior = disease_color_prior(img_rgb, class_name)
    strength = float(np.clip(strength, 0.0, 1.0))

    base_heat_thr = {
        "ALGAL_LEAF_SPOT": 0.38,
        "ALLOCARIDARA_ATTACK": 0.34,
        "LEAF_BLIGHT": 0.36,
        "PHOMOPSIS_LEAF_SPOT": 0.40,
    }.get(class_name, 0.30)
    base_color_thr = {
        "ALGAL_LEAF_SPOT": 0.42,
        "ALLOCARIDARA_ATTACK": 0.34,
        "LEAF_BLIGHT": 0.38,
        "PHOMOPSIS_LEAF_SPOT": 0.44,
    }.get(class_name, 0.30)
    heat_thr = max(0.18, base_heat_thr - 0.12 * strength)
    color_thr = max(0.18, base_color_thr - 0.10 * strength)

    heat_support = (heat >= heat_thr).astype(np.uint8)
    heat_support = cv2.dilate(
        heat_support,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)),
        iterations=1,
    )
    if class_name in {"LEAF_BLIGHT", "ALLOCARIDARA_ATTACK"}:
        valid_area = np.logical_or(
            target_tissue > 0,
            (green_leaf > 0) & (heat >= max(0.18, heat_thr - 0.08)),
        ).astype(np.uint8)
    else:
        valid_area = green_leaf

    color_seed = ((prior >= color_thr) & (valid_area > 0)).astype(np.uint8)
    strong_color_seed = (
        (prior >= max(0.55, color_thr + 0.14))
        & (valid_area > 0)
        & (heat >= max(0.16, heat_thr - 0.10))
    ).astype(np.uint8)

    if class_name in {"LEAF_BLIGHT", "ALLOCARIDARA_ATTACK"}:
        color_seed = cv2.dilate(
            color_seed,
            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)),
            iterations=1,
        )
        min_area, top_k = 40, 5
    else:
        min_area, top_k = 10, 16

    rescue = (color_seed & heat_support & valid_area).astype(np.uint8)
    if class_name == "LEAF_BLIGHT":
        rescue = np.logical_or(rescue, strong_color_seed).astype(np.uint8)
    rescue = clean_rescue_mask(
        rescue,
        min_area=min_area,
        top_k=top_k,
        max_aspect=5.5 if class_name in {"LEAF_BLIGHT", "ALLOCARIDARA_ATTACK"} else 4.5,
        min_extent=0.16 if class_name in {"LEAF_BLIGHT", "ALLOCARIDARA_ATTACK"} else 0.18,
    )

    if mode == "GradCAM ∩ color prior preview":
        final = rescue
    else:
        final = np.logical_or(model_mask > 0, rescue > 0).astype(np.uint8)

    base_max_cov = {
        "ALGAL_LEAF_SPOT": 0.08,
        "ALLOCARIDARA_ATTACK": 0.14,
        "LEAF_BLIGHT": 0.16,
        "PHOMOPSIS_LEAF_SPOT": 0.08,
    }.get(class_name, 0.20)
    max_cov = base_max_cov + 0.08 * strength
    if final.mean() > max_cov:
        score = normalize01(0.65 * prior + 0.35 * heat)
        inside = np.where((final > 0) & (valid_area > 0), score, -1)
        vals = inside[inside >= 0]
        if len(vals) > 0:
            keep_thr = np.quantile(vals, max(0.0, 1.0 - max_cov / max(final.mean(), 1e-6)))
            final = ((inside >= keep_thr) & (valid_area > 0)).astype(np.uint8)
            final = clean_binary(final, close=5, open_=3, min_area=min_area, top_k=top_k)

    debug = {"leaf": valid_area, "prior": prior, "heat_support": heat_support, "rescue": rescue}
    return final, debug


def make_overlay(img_arr, heatmap, alpha=0.45):
    h = heatmap_to_2d(heatmap, target_shape=img_arr.shape[:2])
    h_uint8 = np.clip(h * 255, 0, 255).astype(np.uint8)
    h_colored = cv2.applyColorMap(h_uint8, cv2.COLORMAP_JET)
    h_rgb     = cv2.cvtColor(h_colored, cv2.COLOR_BGR2RGB)
    return cv2.addWeighted(img_arr, 1 - alpha, h_rgb, alpha, 0)


def make_seg_overlay(img_arr, mask):
    green = np.zeros_like(img_arr)
    green[:, :, 1] = mask * 255
    return cv2.addWeighted(img_arr, 0.65, green, 0.35, 0)


def make_combined(img_arr, heatmap, mask, alpha=0.35):
    base      = make_overlay(img_arr, heatmap, alpha)
    mask = np.squeeze(np.asarray(mask)).astype(np.uint8)
    if mask.shape[:2] != img_arr.shape[:2]:
        mask = cv2.resize(mask, (img_arr.shape[1], img_arr.shape[0]), interpolation=cv2.INTER_NEAREST)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(base, contours, -1, (255, 255, 0), 2)
    return base


def prob_bar_chart(probs, pred_idx):
    colors = [CLASS_COLORS[pred_idx] if i == pred_idx else "#AAAAAA" for i in range(len(CLASS_NAMES))]
    fig = go.Figure(go.Bar(
        x=probs,
        y=CLASS_LABELS,
        orientation="h",
        marker_color=colors,
        text=[f"{p*100:.1f}%" for p in probs],
        textposition="outside",
    ))
    fig.update_layout(
        margin=dict(l=10, r=50, t=10, b=10),
        xaxis=dict(range=[0, 1.15], showticklabels=False),
        yaxis=dict(autorange="reversed"),
        height=220,
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Durian Leaf Disease Detection",
    page_icon="🌿",
    layout="wide",
)

st.title("🌿 Durian Leaf Disease Detection")
st.caption("EfficientNet-B0 Classification · GradCAM++ Explainability · UNet++ Segmentation")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Settings")
    seg_choice = st.selectbox(
        "Segmentation model",
        list(CKPT_SEG.keys()),
        index=0,
    )
    inference_mode = st.selectbox(
        "Inference mode",
        [
            "Model only",
            "Model + color prior postprocess",
            "GradCAM ∩ color prior preview",
        ],
        index=0,
    )
    color_prior_strength = st.slider("Color prior strength", 0.0, 1.0, 0.35, 0.05)
    threshold = st.slider("Segmentation threshold", 0.1, 0.9, 0.5, 0.05)
    show_gradcam = st.checkbox("Show GradCAM", value=True)

    st.divider()
    st.subheader("AI Advisory")
    advisory_engine = st.selectbox(
        "Disease assessment engine",
        ["Rule-based", "LLM via OpenAI API"],
        index=0,
    )
    llm_model = st.text_input("LLM model", value=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    use_llm_advisory = advisory_engine == "LLM via OpenAI API"
    if use_llm_advisory and not get_llm_api_key():
        st.caption("Set `OPENAI_API_KEY` to enable LLM advisory. Rule-based fallback will be used.")

    st.divider()
    st.subheader("Upload Image")
    uploaded = st.file_uploader("Choose a leaf image", type=["jpg", "jpeg", "png"])

    st.divider()
    st.caption(f"Device: **{str(device).upper()}**")
    seg_ckpt_exists = os.path.exists(CKPT_SEG[seg_choice])
    cls_ckpt_exists = os.path.exists(CKPT_CLS)
    st.caption(f"Classifier: {'✅' if cls_ckpt_exists else '❌'}")
    st.caption(f"Segmentor ({seg_choice[:2]}): {'✅' if seg_ckpt_exists else '❌'}")

# ── Main area ─────────────────────────────────────────────────────────────────
if uploaded is None:
    st.info("Upload a durian leaf image in the sidebar to get started.")
    st.image(
        os.path.join(proj_root, "notebooks", "visualizations", "eda", "sample_images_per_class.png"),
        caption="Example images from each disease class",
        width="stretch",
    )
    st.stop()

# Load image
pil_img  = Image.open(uploaded).convert("RGB")
img_224  = np.array(pil_img.resize((224, 224)))

# Load models
if not cls_ckpt_exists:
    st.error(f"Classification checkpoint not found: {CKPT_CLS}")
    st.stop()
if not seg_ckpt_exists:
    st.error(f"Segmentation checkpoint not found: {CKPT_SEG[seg_choice]}")
    st.stop()

with st.spinner("Loading models..."):
    cls_model              = load_classifier()
    seg_model, epoch, vloss = load_segmentor(seg_choice)

# Run inference
with st.spinner("Running inference..."):
    probs, pred_idx, cls_tensor = run_classification(cls_model, pil_img)
    prob_map, seg_mask          = run_segmentation(seg_model, pil_img)
    raw_seg_mask = (prob_map > threshold).astype(np.uint8)

    gradcam_overlay = img_224.copy()
    heatmap         = None
    needs_gradcam = show_gradcam or inference_mode != "Model only"
    if needs_gradcam:
        heatmap = run_gradcam(cls_model, cls_tensor, pred_idx)
        if show_gradcam:
            gradcam_overlay = make_overlay(img_224, heatmap)

    post_debug = {}
    if inference_mode == "Model only" or heatmap is None:
        seg_mask = raw_seg_mask
    else:
        seg_mask, post_debug = color_prior_postprocess(
            img_224,
            CLASS_NAMES[pred_idx],
            heatmap,
            raw_seg_mask,
            inference_mode,
            color_prior_strength,
        )
    coverage = seg_mask.mean() * 100

# ── Results header ────────────────────────────────────────────────────────────
pred_label = CLASS_LABELS[pred_idx]
conf_pct   = probs[pred_idx] * 100

col_a, col_b, col_c = st.columns(3)
col_a.metric("Predicted class", pred_label)
col_b.metric("Confidence", f"{conf_pct:.1f}%")
col_c.metric("Lesion coverage", f"{coverage:.1f}%")

st.divider()

# ── Visualization columns ─────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    st.markdown("**Input Image**")
    st.image(img_224, width="stretch")

with c2:
    st.markdown("**Classification**")
    st.plotly_chart(prob_bar_chart(probs, pred_idx), width="stretch", config={"displayModeBar": False})

with c3:
    label = "**GradCAM Overlay**" if show_gradcam else "**GradCAM** *(disabled)*"
    st.markdown(label)
    st.image(gradcam_overlay, width="stretch")

with c4:
    st.markdown("**Segmentation Mask**")
    seg_ov = make_seg_overlay(img_224, seg_mask)
    st.image(seg_ov, width="stretch")
    st.caption(f"Coverage: {coverage:.1f}%")

with c5:
    st.markdown("**Combined**")
    if heatmap is not None:
        combined = make_combined(img_224, heatmap, seg_mask)
    else:
        combined = make_seg_overlay(img_224, seg_mask)
        contours, _ = cv2.findContours(seg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(combined, contours, -1, (255, 255, 0), 2)
    st.image(combined, width="stretch")

# ── AI advisory ──────────────────────────────────────────────────────────────
st.divider()
st.subheader("AI disease severity assessment and treatment suggestion")
advisory_context = build_advisory_context(
    pred_idx,
    probs,
    coverage,
    seg_choice,
    inference_mode,
    color_prior_strength,
    post_debug,
)
with st.spinner("Generating advisory..."):
    advisory_text, advisory_source = generate_advisory(advisory_context, use_llm_advisory, llm_model)

adv_a, adv_b, adv_c = st.columns(3)
adv_a.metric("Estimated severity", advisory_context["severity"])
adv_b.metric("Advisory source", advisory_source)
adv_c.metric("Coverage used", f"{coverage:.1f}%")
st.markdown(advisory_text)

with st.expander("Advisory input sent to LLM / rule engine"):
    st.json(advisory_context)

# ── Probability map expander ──────────────────────────────────────────────────
with st.expander("Raw probability map"):
    prob_vis = (prob_map * 255).astype(np.uint8)
    prob_colored = cv2.applyColorMap(prob_vis, cv2.COLORMAP_HOT)
    st.image(cv2.cvtColor(prob_colored, cv2.COLOR_BGR2RGB), width="stretch")

if post_debug:
    with st.expander("Color prior postprocess debug"):
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            st.markdown("**Raw model mask**")
            st.image(make_seg_overlay(img_224, raw_seg_mask), width="stretch")
            st.caption(f"Coverage: {raw_seg_mask.mean() * 100:.1f}%")
        with d2:
            st.markdown("**Disease color prior**")
            prior_vis = np.clip(post_debug["prior"] * 255, 0, 255).astype(np.uint8)
            prior_colored = cv2.applyColorMap(prior_vis, cv2.COLORMAP_MAGMA)
            st.image(cv2.cvtColor(prior_colored, cv2.COLOR_BGR2RGB), width="stretch")
        with d3:
            st.markdown("**GradCAM support**")
            st.image(post_debug["heat_support"] * 255, width="stretch")
        with d4:
            st.markdown("**Rescue mask**")
            st.image(make_seg_overlay(img_224, post_debug["rescue"]), width="stretch")
            st.caption(f"Added/rescue: {post_debug['rescue'].mean() * 100:.1f}%")

# ── Model info ────────────────────────────────────────────────────────────────
with st.expander("Model info"):
    cls_total, cls_trainable = count_parameters(cls_model)
    seg_total, seg_trainable = count_parameters(seg_model)
    cls_metrics = read_json_safe(os.path.join(proj_root, "notebooks", "models", "classification", "metrics", "test_metrics.json"))
    seg_test, seg_history, seg_manual = segmentation_metrics_for(seg_choice)
    seg_meta = SEG_INFO.get(seg_choice, {})

    st.markdown("**Runtime**")
    st.table([
        {"Item": "Device", "Value": str(device)},
        {"Item": "Input size", "Value": "224 x 224"},
        {"Item": "Segmentation threshold", "Value": f"{threshold:.2f}"},
        {"Item": "Inference mode", "Value": inference_mode},
        {"Item": "Color prior strength", "Value": f"{color_prior_strength:.2f}"},
        {"Item": "Advisory engine", "Value": advisory_source},
    ])

    st.markdown("**Classifier**")
    st.table([
        {"Item": "Architecture", "Value": "EfficientNet-B0"},
        {"Item": "Classes", "Value": str(len(CLASS_NAMES))},
        {"Item": "Checkpoint", "Value": CKPT_CLS},
        {"Item": "Checkpoint size", "Value": fmt_value(file_size_mb(CKPT_CLS)) + " MB"},
        {"Item": "Parameters", "Value": f"{cls_total:,} total / {cls_trainable:,} trainable"},
        {"Item": "Test accuracy", "Value": fmt_value(get_nested(cls_metrics, "accuracy"), pct=True)},
        {"Item": "Test macro/weighted F1", "Value": fmt_value(get_nested(cls_metrics, "f1_score", default=get_nested(cls_metrics, "f1")), pct=True)},
    ])

    st.markdown("**Segmentor**")
    st.table([
        {"Item": "Selected version", "Value": seg_choice},
        {"Item": "Architecture", "Value": seg_meta.get("architecture", "n/a")},
        {"Item": "Pseudo-label source", "Value": seg_meta.get("pseudo_label", "n/a")},
        {"Item": "Checkpoint", "Value": CKPT_SEG[seg_choice]},
        {"Item": "Checkpoint size", "Value": fmt_value(file_size_mb(CKPT_SEG[seg_choice])) + " MB"},
        {"Item": "Epoch in checkpoint", "Value": fmt_value(epoch)},
        {"Item": "Checkpoint val_loss", "Value": fmt_value(vloss)},
        {"Item": "Best val IoU from history", "Value": fmt_value(get_nested(seg_history, "best_val_iou", default=best_from_history(seg_history, "val_iou", "max")))},
        {"Item": "Best val loss from history", "Value": fmt_value(get_nested(seg_history, "best_val_loss", default=best_from_history(seg_history, "val_loss", "min")))},
        {"Item": "Parameters", "Value": f"{seg_total:,} total / {seg_trainable:,} trainable"},
    ])

    st.markdown("**Segmentation Metrics**")
    st.table([
        {"Split": "Pseudo-label test", "IoU": fmt_value(get_nested(seg_test, "iou", default=get_nested(seg_test, "test_iou"))), "Dice": fmt_value(get_nested(seg_test, "dice", default=get_nested(seg_test, "test_dice"))), "Precision": fmt_value(get_nested(seg_test, "precision")), "Recall": fmt_value(get_nested(seg_test, "recall"))},
        {"Split": "Manual GT", "IoU": fmt_value(get_nested(seg_manual, "overall", "iou", default=get_nested(seg_manual, "iou"))), "Dice": fmt_value(get_nested(seg_manual, "overall", "dice", default=get_nested(seg_manual, "dice"))), "Precision": fmt_value(get_nested(seg_manual, "overall", "precision")), "Recall": fmt_value(get_nested(seg_manual, "overall", "recall"))},
    ])

    if seg_manual.get("per_class"):
        st.markdown("**Manual GT Per-Class Metrics**")
        rows = []
        for cls_name, m in seg_manual["per_class"].items():
            rows.append({
                "Class": cls_name,
                "IoU": fmt_value(m.get("iou")),
                "Dice": fmt_value(m.get("dice")),
                "Precision": fmt_value(m.get("precision")),
                "Recall": fmt_value(m.get("recall")),
            })
        st.table(rows)
