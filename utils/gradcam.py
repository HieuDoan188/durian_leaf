"""
Grad-CAM utilities for explainable AI in durian leaf classification.

This module provides Grad-CAM visualization capabilities using torchcam library,
following the GradCAMGenerator contract specifications.
"""

import torch
import torch.nn as nn
import numpy as np
try:
    from torchcam.methods import GradCAM
    torchcam_available = True
except ImportError:
    GradCAM = None
    torchcam_available = False
import cv2
from PIL import Image
from typing import List, Dict, Any, Optional, Tuple
import matplotlib.pyplot as plt
import os
from pathlib import Path
import json
from datetime import datetime


class GradCAMGenerator:
    """Grad-CAM generator following contract specifications."""

    def __init__(self, model: nn.Module, target_layer: str, device: str = 'cuda'):

        self.device = torch.device(device if torch.cuda.is_available() and device == 'cuda' else 'cpu')
        self.model = model.to(self.device)
        self.model.eval()

        # Find target layer
        self.target_layer = self._find_target_layer(target_layer)

        # Initialize Grad-CAM
        if torchcam_available and GradCAM is not None:
            try:
                self.gradcam = GradCAM(self.model, self.target_layer)
                self.use_torchcam = True
            except Exception as e:
                raise ValueError(f"Could not initialize Grad-CAM for layer {target_layer}: {e}")
        else:
            self.gradcam = None
            self.use_torchcam = False
            self._register_manual_hooks()

    def _register_manual_hooks(self):

        self.feature_map = None
        self.gradients = None

        def forward_hook(module, input, output):
            self.feature_map = output

        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0]

        self.target_layer.register_forward_hook(forward_hook)

        # FIX: use new API
        self.target_layer.register_full_backward_hook(backward_hook)

    def _find_target_layer(self, target_layer_name: str) -> nn.Module:

        for name, layer in self.model.named_modules():
            if name == target_layer_name:
                return layer

        for name, layer in self.model.named_modules():
            if target_layer_name in name:
                print(f"Warning: Using partial match for target layer: {name}")
                return layer

        raise ValueError(
            f"Target layer '{target_layer_name}' not found in model."
        )

    def generate(self, input_tensor: torch.Tensor, target_class: int):

        if input_tensor.dim() != 4 or input_tensor.shape[0] != 1:
            raise ValueError("Input tensor must be (1, C, H, W)")

        input_tensor = input_tensor.to(self.device)

        # reset stored tensors
        self.feature_map = None
        self.gradients = None

        # Forward pass (WITH grad)
        self.model.zero_grad()

        output = self.model(input_tensor)

        predicted_class = output.argmax(dim=1).item()
        confidence = torch.softmax(output, dim=1)[0, target_class].item()

        # Generate Grad-CAM
        if self.use_torchcam and self.gradcam is not None:

            try:
                heatmap = self.gradcam(target_class, output)
                heatmap = heatmap[0].cpu().numpy()

            except Exception as e:
                raise RuntimeError(f"Failed to generate Grad-CAM: {e}")

        else:

            # Backward pass
            loss = output[:, target_class]
            loss.backward()

            if self.feature_map is None or self.gradients is None:
                raise RuntimeError("Manual GradCAM hooks not triggered.") # abc

            gradients = self.gradients.detach()[0].cpu().numpy()
            activations = self.feature_map.detach()[0].cpu().numpy()

            weights = np.mean(gradients, axis=(1, 2))

            cam = np.zeros(activations.shape[1:], dtype=np.float32)

            for i, w in enumerate(weights):
                cam += w * activations[i]

            cam = np.maximum(cam, 0)

            cam = cv2.resize(cam, (input_tensor.shape[3], input_tensor.shape[2]))

            if cam.max() > 0:
                cam = cam / cam.max()

            heatmap = cam

        if heatmap.max() > heatmap.min():
            heatmap = (heatmap - heatmap.min()) / (heatmap.max() - heatmap.min())

        return heatmap, confidence, predicted_class

    def generate_batch(self, input_batch: torch.Tensor, target_classes: List[int]):

        if input_batch.shape[0] != len(target_classes):
            raise ValueError("Number of inputs must match number of target classes")

        results = []

        for i in range(input_batch.shape[0]):

            single_input = input_batch[i:i+1]

            heatmap, confidence, predicted = self.generate(
                single_input,
                target_classes[i]
            )

            results.append((heatmap, confidence, predicted))

        return results

    def overlay_heatmap(self, original_image: np.ndarray, heatmap: np.ndarray,
                       alpha: float = 0.5):

        if original_image.shape[:2] != heatmap.shape:
            heatmap = cv2.resize(
                heatmap,
                (original_image.shape[1], original_image.shape[0])
            )

        heatmap_colored = cv2.applyColorMap(
            np.uint8(255 * heatmap),
            cv2.COLORMAP_JET
        )

        if original_image.dtype != np.uint8:
            original_image = (original_image * 255).astype(np.uint8)

        overlay = cv2.addWeighted(
            original_image,
            1 - alpha,
            heatmap_colored,
            alpha,
            0
        )

        return overlay


class GradCAMVisualizer:
    """Utilities for visualizing and analyzing Grad-CAM results."""

    def __init__(self, output_dir: str = "models/classification/gradcam"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_visualization(self, original_image: np.ndarray, heatmap: np.ndarray,
                          overlay: np.ndarray, image_id: str, target_class: int,
                          confidence: float, predicted_class: int):
        """Save Grad-CAM visualization components."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save original image
        original_path = self.output_dir / f"{image_id}_original_{timestamp}.png"
        Image.fromarray(original_image).save(original_path)

        # Save heatmap
        heatmap_path = self.output_dir / f"{image_id}_heatmap_{timestamp}.png"
        plt.figure(figsize=(6, 6))
        plt.imshow(heatmap, cmap='jet')
        plt.colorbar()
        plt.title(f'Grad-CAM Heatmap (Class {target_class})')
        plt.axis('off')
        plt.savefig(heatmap_path, bbox_inches='tight', dpi=150)
        plt.close()

        # Save overlay
        overlay_path = self.output_dir / f"{image_id}_overlay_{timestamp}.png"
        Image.fromarray(overlay).save(overlay_path)

        # Save metadata
        metadata = {
            'image_id': image_id,
            'target_class': target_class,
            'predicted_class': predicted_class,
            'confidence': confidence,
            'timestamp': timestamp,
            'original_image': str(original_path),
            'heatmap': str(heatmap_path),
            'overlay': str(overlay_path)
        }

        metadata_path = self.output_dir / f"{image_id}_metadata_{timestamp}.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        return metadata

    def create_comparison_grid(self, visualizations: List[Dict], output_path: str):
        """Create a grid comparison of multiple Grad-CAM visualizations."""
        n_images = len(visualizations)
        cols = min(3, n_images)
        rows = (n_images + cols - 1) // cols

        fig, axes = plt.subplots(rows, cols * 3, figsize=(6 * cols, 4 * rows))
        if rows == 1:
            axes = axes.reshape(1, -1)

        for i, viz in enumerate(visualizations):
            row = i // cols
            col_start = (i % cols) * 3

            # Original image
            axes[row, col_start].imshow(viz['original'])
            axes[row, col_start].set_title(f'Original\nClass: {viz["target_class"]}')
            axes[row, col_start].axis('off')

            # Heatmap
            im = axes[row, col_start + 1].imshow(viz['heatmap'], cmap='jet')
            axes[row, col_start + 1].set_title(f'Heatmap\nConf: {viz["confidence"]:.3f}')
            axes[row, col_start + 1].axis('off')

            # Overlay
            axes[row, col_start + 2].imshow(viz['overlay'])
            axes[row, col_start + 2].set_title(f'Overlay\nPred: {viz["predicted_class"]}')
            axes[row, col_start + 2].axis('off')

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

    def analyze_attention_patterns(self, visualizations: List[Dict]) -> Dict[str, Any]:
        """Analyze attention patterns across multiple visualizations."""
        confidences = [v['confidence'] for v in visualizations]
        correct_predictions = [v['target_class'] == v['predicted_class'] for v in visualizations]

        analysis = {
            'total_samples': len(visualizations),
            'correct_predictions': sum(correct_predictions),
            'accuracy': sum(correct_predictions) / len(visualizations),
            'mean_confidence': np.mean(confidences),
            'std_confidence': np.std(confidences),
            'min_confidence': np.min(confidences),
            'max_confidence': np.max(confidences),
            'confidence_correct': np.mean([c for c, correct in zip(confidences, correct_predictions) if correct]),
            'confidence_incorrect': np.mean([c for c, correct in zip(confidences, correct_predictions) if not correct])
        }

        return analysis


def find_efficientnet_target_layer(model: nn.Module) -> str:
    """Find appropriate target layer for EfficientNet Grad-CAM."""
    # For EfficientNet, good target layers are typically the last convolutional blocks
    target_candidates = []

    for name, module in model.named_modules():
        if 'features' in name and isinstance(module, nn.Conv2d):
            target_candidates.append(name)

    if target_candidates:
        # Use the last convolutional layer in features
        return target_candidates[-1]

    # Fallback: look for any Conv2d layer
    for name, module in model.named_modules():
        if isinstance(module, nn.Conv2d):
            return name

    raise ValueError("No suitable convolutional layer found for Grad-CAM")


def create_gradcam_pipeline(model_path: str, model_class: nn.Module,
                           target_layer: Optional[str] = None,
                           device: str = 'cuda') -> GradCAMGenerator:
    """
    Create a complete Grad-CAM pipeline from model checkpoint.

    Args:
        model_path: Path to saved model checkpoint
        model_class: Model class for instantiation
        target_layer: Target layer name (auto-detected if None)
        device: Compute device

    Returns:
        Configured GradCAMGenerator
    """
    # Load model
    device = torch.device(device if torch.cuda.is_available() and device == 'cuda' else 'cpu')

    try:
        checkpoint = torch.load(model_path, map_location=device)
        model = model_class()
        model.load_state_dict(checkpoint['model_state_dict'])
        model.to(device)
        model.eval()
    except Exception as e:
        raise RuntimeError(f"Failed to load model from {model_path}: {e}")

    # Find target layer if not specified
    if target_layer is None:
        target_layer = find_efficientnet_target_layer(model)
        print(f"Auto-detected target layer: {target_layer}")

    # Create Grad-CAM generator
    gradcam_gen = GradCAMGenerator(model, target_layer, device)

    return gradcam_gen


if __name__ == "__main__":
    # Example usage
    print("Grad-CAM utilities loaded successfully")
    print("Use create_gradcam_pipeline() to initialize Grad-CAM for your model")