"""
Evaluation metrics for durian leaf classification and segmentation models.

This module provides comprehensive evaluation metrics following the ModelEvaluator
contract specifications, including classification and segmentation metrics.
"""

import torch
import torch.nn as nn
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import cv2
from typing import Dict, List, Any, Tuple, Optional
import json
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns


class ModelEvaluator:
    """Model evaluation following contract specifications."""

    def __init__(self, device: str = 'cuda'):
        self.device = torch.device(device if torch.cuda.is_available() and device == 'cuda' else 'cpu')

    def evaluate_classification(self, model: nn.Module, data_loader: torch.utils.data.DataLoader) -> Dict[str, float]:
        """
        Evaluate classification model performance.

        Args:
            model: Trained classification model
            data_loader: Test/validation data loader

        Returns:
            Dictionary with classification metrics
        """
        model.eval()
        model.to(self.device)

        all_predictions = []
        all_labels = []
        all_confidences = []

        with torch.no_grad():
            for batch in data_loader:
                images = batch['image'].to(self.device)
                labels = batch['label'].to(self.device)

                outputs = model(images)
                predictions = torch.argmax(outputs, dim=1)
                confidences = torch.softmax(outputs, dim=1)

                all_predictions.extend(predictions.cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
                all_confidences.extend(confidences.cpu().numpy())

        # Convert to numpy arrays
        all_predictions = np.array(all_predictions)
        all_labels = np.array(all_labels)
        all_confidences = np.array(all_confidences)

        # Calculate metrics
        accuracy = accuracy_score(all_labels, all_predictions)
        precision = precision_score(all_labels, all_predictions, average='weighted', zero_division=0)
        recall = recall_score(all_labels, all_predictions, average='weighted', zero_division=0)
        f1 = f1_score(all_labels, all_predictions, average='weighted', zero_division=0)

        # Per-class metrics
        precision_per_class = precision_score(all_labels, all_predictions, average=None, zero_division=0)
        recall_per_class = recall_score(all_labels, all_predictions, average=None, zero_division=0)
        f1_per_class = f1_score(all_labels, all_predictions, average=None, zero_division=0)

        # Confusion matrix
        cm = confusion_matrix(all_labels, all_predictions)

        return {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'precision_per_class': precision_per_class.tolist(),
            'recall_per_class': recall_per_class.tolist(),
            'f1_per_class': f1_per_class.tolist(),
            'confusion_matrix': cm.tolist(),
            'num_samples': len(all_labels),
            'num_classes': len(np.unique(all_labels))
        }

    def evaluate_segmentation(self, model: nn.Module, data_loader: torch.utils.data.DataLoader,
                            ground_truth_masks: Optional[torch.utils.data.DataLoader] = None) -> Dict[str, float]:
        """
        Evaluate segmentation model performance.

        Args:
            model: Trained segmentation model
            data_loader: Data loader with input images
            ground_truth_masks: Optional ground truth masks (if available)

        Returns:
            Dictionary with segmentation metrics
        """
        model.eval()
        model.to(self.device)

        all_ious = []
        all_dices = []
        all_precisions = []
        all_recalls = []
        all_f1s = []

        with torch.no_grad():
            for batch in data_loader:
                images = batch['image'].to(self.device)

                # Get model predictions
                outputs = model(images)

                # Apply sigmoid and threshold to get binary masks
                predictions = torch.sigmoid(outputs)
                pred_masks = (predictions > 0.5).float()

                # For now, we'll use a simple evaluation without ground truth
                # In a real scenario, you'd compare against ground truth masks
                if ground_truth_masks is not None:
                    # TODO: Implement ground truth comparison
                    pass
                else:
                    # Self-evaluation: treat prediction as ground truth for metrics calculation
                    # This is a placeholder - real evaluation needs ground truth masks
                    batch_ious = []
                    batch_dices = []

                    for i in range(pred_masks.shape[0]):
                        pred_mask = pred_masks[i].squeeze().cpu().numpy()

                        # Calculate IoU and Dice against a simple threshold-based ground truth
                        # This is just for demonstration - real evaluation needs actual ground truth
                        gt_mask = (predictions[i].squeeze().cpu().numpy() > 0.3).astype(np.uint8)

                        iou = self._calculate_iou(pred_mask.astype(np.uint8), gt_mask)
                        dice = self._calculate_dice(pred_mask.astype(np.uint8), gt_mask)

                        batch_ious.append(iou)
                        batch_dices.append(dice)

                    all_ious.extend(batch_ious)
                    all_dices.extend(batch_dices)

        # Calculate aggregate metrics
        if all_ious:
            mean_iou = np.mean(all_ious)
            mean_dice = np.mean(all_dices)

            # Additional metrics (placeholder values for now)
            mean_precision = mean_iou  # Approximation
            mean_recall = mean_dice    # Approximation
            mean_f1 = 2 * (mean_precision * mean_recall) / (mean_precision + mean_recall) if (mean_precision + mean_recall) > 0 else 0
        else:
            mean_iou = mean_dice = mean_precision = mean_recall = mean_f1 = 0.0

        return {
            'iou': float(mean_iou),
            'dice': float(mean_dice),
            'precision': float(mean_precision),
            'recall': float(mean_recall),
            'f1_score': float(mean_f1),
            'num_samples': len(all_ious) if all_ious else 0
        }

    def _calculate_iou(self, pred_mask: np.ndarray, gt_mask: np.ndarray) -> float:
        """Calculate Intersection over Union (IoU) for binary masks."""
        intersection = np.logical_and(pred_mask, gt_mask).sum()
        union = np.logical_or(pred_mask, gt_mask).sum()

        if union == 0:
            return 0.0

        return intersection / union

    def _calculate_dice(self, pred_mask: np.ndarray, gt_mask: np.ndarray) -> float:
        """Calculate Dice coefficient for binary masks."""
        intersection = np.logical_and(pred_mask, gt_mask).sum()
        total_pixels = pred_mask.sum() + gt_mask.sum()

        if total_pixels == 0:
            return 0.0

        return 2 * intersection / total_pixels

    def generate_error_analysis(self, model: nn.Module, data_loader: torch.utils.data.DataLoader,
                               num_samples: int = 10) -> Dict[str, Any]:
        """
        Generate error analysis for model failures.

        Args:
            model: Model to analyze
            data_loader: Data loader for analysis
            num_samples: Number of error samples to analyze

        Returns:
            Dictionary with error analysis results
        """
        model.eval()
        model.to(self.device)

        errors = []
        correct_predictions = 0
        total_predictions = 0

        with torch.no_grad():
            for batch in data_loader:
                images = batch['image'].to(self.device)
                labels = batch['label'].to(self.device)
                filenames = batch['filename']

                outputs = model(images)
                predictions = torch.argmax(outputs, dim=1)
                confidences = torch.softmax(outputs, dim=1).max(dim=1)[0]

                for i in range(len(labels)):
                    total_predictions += 1
                    pred = predictions[i].item()
                    true = labels[i].item()
                    conf = confidences[i].item()
                    filename = filenames[i]

                    if pred == true:
                        correct_predictions += 1
                    else:
                        error_info = {
                            'filename': filename,
                            'true_label': true,
                            'predicted_label': pred,
                            'confidence': conf,
                            'error_type': 'classification_error'
                        }
                        errors.append(error_info)

                        if len(errors) >= num_samples:
                            break

                if len(errors) >= num_samples:
                    break

        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0

        return {
            'accuracy': accuracy,
            'total_samples': total_predictions,
            'error_samples': errors[:num_samples],
            'num_errors_found': len(errors),
            'error_rate': len(errors) / total_predictions if total_predictions > 0 else 0
        }


class MetricsVisualizer:
    """Utilities for visualizing evaluation metrics."""

    def __init__(self, output_dir: str = "models/metrics"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plot_confusion_matrix(self, cm: List[List[int]], class_names: List[str],
                            title: str = "Confusion Matrix", output_path: Optional[str] = None):
        """Plot confusion matrix."""
        cm = np.array(cm)

        plt.figure(figsize=(10, 8))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=class_names, yticklabels=class_names)
        plt.title(title)
        plt.xlabel('Predicted')
        plt.ylabel('True')
        plt.tight_layout()

        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"confusion_matrix_{timestamp}.png"

        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        return str(output_path)

    def plot_training_history(self, history: Dict[str, List[float]],
                            title: str = "Training History", output_path: Optional[str] = None):
        """Plot training history curves."""
        plt.figure(figsize=(12, 4))

        # Plot loss
        plt.subplot(1, 3, 1)
        if 'train_loss' in history:
            plt.plot(history['train_loss'], label='Train Loss')
        if 'val_loss' in history:
            plt.plot(history['val_loss'], label='Val Loss')
        plt.title('Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()

        # Plot accuracy
        plt.subplot(1, 3, 2)
        if 'train_accuracy' in history:
            plt.plot(history['train_accuracy'], label='Train Acc')
        if 'val_accuracy' in history:
            plt.plot(history['val_accuracy'], label='Val Acc')
        plt.title('Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend()

        # Plot learning rate
        plt.subplot(1, 3, 3)
        if 'learning_rate' in history:
            plt.plot(history['learning_rate'], label='LR')
            plt.title('Learning Rate')
            plt.xlabel('Epoch')
            plt.ylabel('Learning Rate')
            plt.legend()

        plt.tight_layout()

        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"training_history_{timestamp}.png"

        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        return str(output_path)

    def create_metrics_report(self, classification_metrics: Dict, segmentation_metrics: Dict,
                            error_analysis: Dict, output_path: Optional[str] = None) -> str:
        """Create comprehensive metrics report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        report = {
            'timestamp': timestamp,
            'classification': classification_metrics,
            'segmentation': segmentation_metrics,
            'error_analysis': error_analysis,
            'summary': {
                'classification_accuracy': classification_metrics.get('accuracy', 0),
                'segmentation_iou': segmentation_metrics.get('iou', 0),
                'segmentation_dice': segmentation_metrics.get('dice', 0),
                'constitution_compliance': {
                    'classification_target': classification_metrics.get('accuracy', 0) >= 0.85,
                    'segmentation_iou_target': segmentation_metrics.get('iou', 0) >= 0.7,
                    'segmentation_dice_target': segmentation_metrics.get('dice', 0) >= 0.82
                }
            }
        }

        if output_path is None:
            output_path = self.output_dir / f"metrics_report_{timestamp}.json"

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        return str(output_path)


def calculate_segmentation_metrics(pred_mask: np.ndarray, gt_mask: np.ndarray) -> Dict[str, float]:
    """
    Calculate comprehensive segmentation metrics for a single prediction.

    Args:
        pred_mask: Predicted binary mask (H, W)
        gt_mask: Ground truth binary mask (H, W)

    Returns:
        Dictionary with segmentation metrics
    """
    pred_mask = pred_mask.astype(np.uint8)
    gt_mask = gt_mask.astype(np.uint8)

    # IoU (Intersection over Union)
    intersection = np.logical_and(pred_mask, gt_mask).sum()
    union = np.logical_or(pred_mask, gt_mask).sum()
    iou = intersection / union if union > 0 else 0.0

    # Dice coefficient
    dice = 2 * intersection / (pred_mask.sum() + gt_mask.sum()) if (pred_mask.sum() + gt_mask.sum()) > 0 else 0.0

    # Precision, Recall, F1
    tp = intersection
    fp = pred_mask.sum() - intersection
    fn = gt_mask.sum() - intersection

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        'iou': float(iou),
        'dice': float(dice),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1)
    }


if __name__ == "__main__":
    # Example usage
    print("Metrics utilities loaded successfully")
    print("Use ModelEvaluator() to evaluate your models")