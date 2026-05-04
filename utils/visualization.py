"""
Visualization utilities for durian leaf classification and segmentation.

This module provides plotting and visualization functions for model analysis,
performance monitoring, and result presentation.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import torch
from typing import Dict, List, Any, Optional, Tuple
import cv2
from pathlib import Path
from datetime import datetime
import json


class DurianVisualizer:
    """Visualization utilities for durian leaf analysis."""

    def __init__(self, output_dir: str = "visualizations"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set up matplotlib style
        plt.style.use('default')
        sns.set_palette("husl")

    def plot_class_distribution(self, class_counts: Dict[int, int],
                              class_names: Optional[List[str]] = None,
                              title: str = "Class Distribution") -> str:
        """Plot class distribution as bar chart."""
        if class_names is None:
            class_names = [f"Class {i}" for i in class_counts.keys()]

        classes = list(class_counts.keys())
        counts = list(class_counts.values())

        plt.figure(figsize=(10, 6))
        bars = plt.bar(classes, counts, color=sns.color_palette("husl", len(classes)))

        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel('Class', fontsize=12)
        plt.ylabel('Number of Images', fontsize=12)
        plt.xticks(classes, class_names, rotation=45, ha='right')

        # Add value labels on bars
        for bar, count in zip(bars, counts):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                    f'{count}', ha='center', va='bottom', fontweight='bold')

        plt.tight_layout()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"class_distribution_{timestamp}.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        return str(output_path)

    def plot_dataset_split(self, split_counts: Dict[str, int],
                          title: str = "Dataset Split Distribution") -> str:
        """Plot dataset split distribution as pie chart."""
        splits = list(split_counts.keys())
        counts = list(split_counts.values())

        plt.figure(figsize=(8, 8))
        colors = sns.color_palette("pastel", len(splits))

        plt.pie(counts, labels=splits, colors=colors, autopct='%1.1f%%',
               startangle=90, wedgeprops={'edgecolor': 'black', 'linewidth': 1})

        plt.title(title, fontsize=14, fontweight='bold')
        plt.axis('equal')

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"dataset_split_{timestamp}.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        return str(output_path)

    def plot_training_curves(self, history: Dict[str, List[float]],
                           title: str = "Training History") -> str:
        """Plot training and validation curves."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

        epochs = range(1, len(history.get('train_loss', [])) + 1)

        # Loss curves
        if 'train_loss' in history:
            ax1.plot(epochs, history['train_loss'], 'b-', label='Training Loss', linewidth=2)
        if 'val_loss' in history:
            ax1.plot(epochs, history['val_loss'], 'r-', label='Validation Loss', linewidth=2)
        ax1.set_title('Loss Curves', fontweight='bold')
        ax1.set_xlabel('Epoch')
        ax1.set_ylabel('Loss')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Accuracy curves
        if 'train_accuracy' in history:
            ax2.plot(epochs, history['train_accuracy'], 'b-', label='Training Accuracy', linewidth=2)
        if 'val_accuracy' in history:
            ax2.plot(epochs, history['val_accuracy'], 'r-', label='Validation Accuracy', linewidth=2)
        ax2.set_title('Accuracy Curves', fontweight='bold')
        ax2.set_xlabel('Epoch')
        ax2.set_ylabel('Accuracy')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Learning rate
        if 'learning_rate' in history:
            ax3.plot(epochs, history['learning_rate'], 'g-', label='Learning Rate', linewidth=2)
            ax3.set_title('Learning Rate Schedule', fontweight='bold')
            ax3.set_xlabel('Epoch')
            ax3.set_ylabel('Learning Rate')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            ax3.set_yscale('log')

        # Additional metrics (if available)
        if 'train_f1' in history or 'val_f1' in history:
            if 'train_f1' in history:
                ax4.plot(epochs, history['train_f1'], 'b-', label='Training F1', linewidth=2)
            if 'val_f1' in history:
                ax4.plot(epochs, history['val_f1'], 'r-', label='Validation F1', linewidth=2)
            ax4.set_title('F1 Score Curves', fontweight='bold')
            ax4.set_xlabel('Epoch')
            ax4.set_ylabel('F1 Score')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
        else:
            ax4.text(0.5, 0.5, 'No additional\nmetrics available',
                    ha='center', va='center', transform=ax4.transAxes, fontsize=12)
            ax4.set_title('Additional Metrics', fontweight='bold')

        plt.suptitle(title, fontsize=16, fontweight='bold')
        plt.tight_layout()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"training_curves_{timestamp}.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        return str(output_path)

    def plot_confusion_matrix(self, cm: np.ndarray, class_names: Optional[List[str]] = None,
                            title: str = "Confusion Matrix", normalize: bool = False) -> str:
        """Plot confusion matrix as heatmap."""
        if class_names is None:
            class_names = [f"Class {i}" for i in range(cm.shape[0])]

        if normalize:
            cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
            fmt = '.2f'
            title += ' (Normalized)'
        else:
            fmt = 'd'

        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt=fmt, cmap='Blues',
                   xticklabels=class_names, yticklabels=class_names,
                   cbar_kws={'label': 'Count' if not normalize else 'Proportion'})

        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel('Predicted Label', fontsize=12)
        plt.ylabel('True Label', fontsize=12)
        plt.tight_layout()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"confusion_matrix_{timestamp}.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        return str(output_path)

    def plot_segmentation_metrics(self, metrics: Dict[str, float],
                                title: str = "Segmentation Performance") -> str:
        """Plot segmentation metrics as bar chart."""
        metric_names = list(metrics.keys())
        metric_values = list(metrics.values())

        plt.figure(figsize=(12, 6))
        bars = plt.bar(metric_names, metric_values, color=sns.color_palette("Set2", len(metric_names)))

        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel('Metric', fontsize=12)
        plt.ylabel('Value', fontsize=12)
        plt.ylim(0, 1.0)

        # Add value labels on bars
        for bar, value in zip(bars, metric_values):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                    f'{value:.3f}', ha='center', va='bottom', fontweight='bold')

        # Add target lines for constitution requirements
        if 'iou' in metrics:
            plt.axhline(y=0.7, color='red', linestyle='--', alpha=0.7, label='IoU Target (0.7)')
        if 'dice' in metrics:
            plt.axhline(y=0.82, color='orange', linestyle='--', alpha=0.7, label='Dice Target (0.82)')

        plt.legend()
        plt.grid(True, alpha=0.3, axis='y')
        plt.tight_layout()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"segmentation_metrics_{timestamp}.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        return str(output_path)

    def create_image_grid(self, images: List[np.ndarray], titles: Optional[List[str]] = None,
                         cols: int = 4, title: str = "Image Grid") -> str:
        """Create a grid of images."""
        n_images = len(images)
        rows = (n_images + cols - 1) // cols

        fig, axes = plt.subplots(rows, cols, figsize=(4*cols, 4*rows))
        if rows == 1:
            axes = axes.reshape(1, -1)

        for i in range(rows * cols):
            ax = axes[i // cols, i % cols]

            if i < n_images:
                ax.imshow(images[i])
                if titles and i < len(titles):
                    ax.set_title(titles[i], fontsize=10)
            else:
                ax.axis('off')

            ax.axis('off')

        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"image_grid_{timestamp}.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.show()
        plt.close()

        return str(output_path)

    def plot_gradcam_comparison(self, original_images: List[np.ndarray],
                              heatmaps: List[np.ndarray], overlays: List[np.ndarray],
                              titles: Optional[List[str]] = None,
                              title: str = "Grad-CAM Analysis") -> str:
        """Create comparison grid for Grad-CAM visualizations."""
        n_samples = len(original_images)
        fig, axes = plt.subplots(n_samples, 3, figsize=(12, 4*n_samples))

        if n_samples == 1:
            axes = axes.reshape(1, -1)

        for i in range(n_samples):
            # Original image
            axes[i, 0].imshow(original_images[i])
            axes[i, 0].set_title(f'Original\n{titles[i] if titles else ""}')
            axes[i, 0].axis('off')

            # Heatmap
            im = axes[i, 1].imshow(heatmaps[i], cmap='jet')
            axes[i, 1].set_title('Grad-CAM Heatmap')
            axes[i, 1].axis('off')

            # Overlay
            axes[i, 2].imshow(overlays[i])
            axes[i, 2].set_title('Overlay')
            axes[i, 2].axis('off')

        # Add colorbar for heatmaps
        plt.colorbar(im, ax=axes[:, 1], shrink=0.8, label='Attention Intensity')

        plt.suptitle(title, fontsize=14, fontweight='bold')
        plt.tight_layout()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = self.output_dir / f"gradcam_comparison_{timestamp}.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        return str(output_path)

    def save_metrics_summary(self, metrics: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """Save metrics summary as JSON file."""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"metrics_summary_{timestamp}.json"

        with open(output_path, 'w') as f:
            json.dump(metrics, f, indent=2, default=str)

        return str(output_path)


def create_comparison_report(classification_metrics: Dict, segmentation_metrics: Dict,
                           output_dir: str = "reports") -> str:
    """Create a comprehensive comparison report with visualizations."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    visualizer = DurianVisualizer(output_dir / "plots")

    report = {
        'timestamp': datetime.now().isoformat(),
        'classification': classification_metrics,
        'segmentation': segmentation_metrics,
        'plots': {}
    }

    # Create confusion matrix plot if available
    if 'confusion_matrix' in classification_metrics:
        cm = np.array(classification_metrics['confusion_matrix'])
        class_names = [f"Class {i}" for i in range(cm.shape[0])]
        report['plots']['confusion_matrix'] = visualizer.plot_confusion_matrix(
            cm, class_names, "Classification Confusion Matrix"
        )

    # Create segmentation metrics plot
    seg_metrics = {
        'IoU': segmentation_metrics.get('iou', 0),
        'Dice': segmentation_metrics.get('dice', 0),
        'Precision': segmentation_metrics.get('precision', 0),
        'Recall': segmentation_metrics.get('recall', 0),
        'F1': segmentation_metrics.get('f1_score', 0)
    }
    report['plots']['segmentation_metrics'] = visualizer.plot_segmentation_metrics(
        seg_metrics, "Segmentation Performance Metrics"
    )

    # Save report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = output_dir / f"comparison_report_{timestamp}.json"

    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    return str(report_path)


if __name__ == "__main__":
    # Example usage
    print("Visualization utilities loaded successfully")
    print("Use DurianVisualizer() to create plots and visualizations")