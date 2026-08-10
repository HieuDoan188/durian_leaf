import os
import sys

import cv2
import numpy as np
import streamlit as st
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms
import albumentations as A
from albumentations.pytorch import ToTensorV2
import segmentation_models_pytorch as smp
import plotly.graph_objects as go

proj_root = os.path.dirname(os.path.abspath(__file__))
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
    "V2 — GradCAM++ pseudo-labels": os.path.join(proj_root, "notebooks", "models", "segmentation_v2", "checkpoints", "unetpp_best.pth"),
    "V3 — SAM-refined pseudo-labels": os.path.join(proj_root, "notebooks", "models", "segmentation_v3", "checkpoints", "unetpp_v3_best.pth"),
    "V1 — Baseline": os.path.join(proj_root, "notebooks", "models", "segmentation",    "checkpoints", "efficientnet_unet_best.pth"),
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
    with torch.no_grad():
        probs = torch.softmax(model(tensor), dim=1)[0].cpu().numpy()
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


def make_overlay(img_arr, heatmap, alpha=0.45):
    h_uint8   = (heatmap * 255).astype(np.uint8)
    h_colored = cv2.applyColorMap(h_uint8, cv2.COLORMAP_JET)
    h_rgb     = cv2.cvtColor(h_colored, cv2.COLOR_BGR2RGB)
    return cv2.addWeighted(img_arr, 1 - alpha, h_rgb, alpha, 0)


def make_seg_overlay(img_arr, mask):
    green = np.zeros_like(img_arr)
    green[:, :, 1] = mask * 255
    return cv2.addWeighted(img_arr, 0.65, green, 0.35, 0)


def make_combined(img_arr, heatmap, mask, alpha=0.35):
    base      = make_overlay(img_arr, heatmap, alpha)
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
    threshold = st.slider("Segmentation threshold", 0.1, 0.9, 0.5, 0.05)
    show_gradcam = st.checkbox("Show GradCAM", value=True)

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
        use_container_width=True,
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
    seg_mask = (prob_map > threshold).astype(np.uint8)
    coverage = seg_mask.mean() * 100

    gradcam_overlay = img_224.copy()
    heatmap         = None
    if show_gradcam:
        heatmap         = run_gradcam(cls_model, cls_tensor, pred_idx)
        gradcam_overlay = make_overlay(img_224, heatmap)

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
    st.image(img_224, use_container_width=True)

with c2:
    st.markdown("**Classification**")
    st.plotly_chart(prob_bar_chart(probs, pred_idx), use_container_width=True, config={"displayModeBar": False})

with c3:
    label = "**GradCAM Overlay**" if show_gradcam else "**GradCAM** *(disabled)*"
    st.markdown(label)
    st.image(gradcam_overlay, use_container_width=True)

with c4:
    st.markdown("**Segmentation Mask**")
    seg_ov = make_seg_overlay(img_224, seg_mask)
    st.image(seg_ov, use_container_width=True)
    st.caption(f"Coverage: {coverage:.1f}%")

with c5:
    st.markdown("**Combined**")
    if heatmap is not None:
        combined = make_combined(img_224, heatmap, seg_mask)
    else:
        combined = make_seg_overlay(img_224, seg_mask)
        contours, _ = cv2.findContours(seg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(combined, contours, -1, (255, 255, 0), 2)
    st.image(combined, use_container_width=True)

# ── Probability map expander ──────────────────────────────────────────────────
with st.expander("Raw probability map"):
    prob_vis = (prob_map * 255).astype(np.uint8)
    prob_colored = cv2.applyColorMap(prob_vis, cv2.COLORMAP_HOT)
    st.image(cv2.cvtColor(prob_colored, cv2.COLOR_BGR2RGB), use_container_width=True)

# ── Model info ────────────────────────────────────────────────────────────────
with st.expander("Model info"):
    st.write(f"**Classifier**: EfficientNet-B0, checkpoint `{os.path.basename(CKPT_CLS)}`")
    st.write(f"**Segmentor**: {seg_choice}, epoch {epoch}, val_loss={vloss:.4f}" if isinstance(vloss, float) else f"**Segmentor**: {seg_choice}, epoch {epoch}")
    st.write(f"**Device**: {device}")
    st.write(f"**Threshold**: {threshold}")
