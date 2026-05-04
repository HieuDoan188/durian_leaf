"""
Preprocessing utilities for durian leaf classification and segmentation.

This module provides data loading, preprocessing, and augmentation functionality
for the durian leaf ML pipeline. Follows the DataLoader contract specifications.
"""

import os
import random
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
import cv2
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime


class DurianLeafImage:
    """Represents a single durian leaf image with metadata."""

    def __init__(self, image_path: str, class_label: int, split: str = None):
        self.image_path = image_path
        self.filename = os.path.basename(image_path)
        self.class_label = class_label
        self.split = split
        self.image_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{self.filename}"

        # Load and store original image properties
        with Image.open(image_path) as img:
            self.original_shape = img.size + (len(img.getbands()),)

        # Will be set during preprocessing
        self.resized_array = None

    def load_and_preprocess(self, target_size: Tuple[int, int] = (224, 224)) -> np.ndarray:
        """Load and preprocess image to standard format."""
        # Load image
        image = cv2.imread(self.image_path)
        if image is None:
            raise ValueError(f"Could not load image: {self.image_path}")

        # Convert BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Resize to target size
        image = cv2.resize(image, target_size, interpolation=cv2.INTER_LINEAR)

        # Normalize to [0, 1]
        image = image.astype(np.float32) / 255.0

        # Store processed array
        self.resized_array = image

        return image

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'image_path': self.image_path,
            'filename': self.filename,
            'class_label': self.class_label,
            'split': self.split,
            'image_id': self.image_id,
            'original_shape': self.original_shape
        }


class DurianLeafDataset(Dataset):
    """PyTorch Dataset for durian leaf images."""

    def __init__(self, images: List[DurianLeafImage], transform=None, is_training=False):
        self.images = images
        self.transform = transform
        self.is_training = is_training

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        image_obj = self.images[idx]

        # Load and preprocess image
        image_array = image_obj.load_and_preprocess()

        # Convert to PIL Image for torchvision transforms
        image = Image.fromarray((image_array * 255).astype(np.uint8))

        if self.transform:
            image = self.transform(image)

        return {
            'image': image,
            'label': image_obj.class_label,
            'image_id': image_obj.image_id,
            'filename': image_obj.filename
        }


class DataLoader:
    """Data loading and preprocessing pipeline following contract specifications."""

    def __init__(self, data_dir: str, batch_size: int = 32, image_size: Tuple[int, int] = (224, 224),
                 random_seed: int = 42):
        self.data_dir = Path(data_dir)
        self.batch_size = batch_size
        self.image_size = image_size
        self.random_seed = random_seed

        # Set random seeds for reproducibility
        random.seed(random_seed)
        np.random.seed(random_seed)
        torch.manual_seed(random_seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed(random_seed)
            torch.cuda.manual_seed_all(random_seed)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False

        # Validate data directory. Allow both data/raw and direct data class folder layout.
        if not self.data_dir.exists():
            # Fallback to direct data folder structure if available
            candidate = self.data_dir.parent if self.data_dir.name.lower() == 'raw' else None
            if candidate and candidate.exists():
                self.data_dir = candidate
            else:
                raise FileNotFoundError(f"Data directory not found: {self.data_dir}")

    def load_dataset(self) -> Dict[str, List[DurianLeafImage]]:
        """Load and split dataset into train/val/test sets.

        If data is already organized into train/val/test folders, use those splits directly.
        Otherwise perform an internal randomized split (80/10/10).
        """
        split_dirs = {
            'train': self.data_dir / 'train',
            'val': self.data_dir / 'val',
            'test': self.data_dir / 'test'
        }

        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']

        # If split directories exist, load from them directly
        if all(d.exists() and d.is_dir() for d in split_dirs.values()):
            class_dirs = [d for d in split_dirs['train'].iterdir() if d.is_dir()]
            if len(class_dirs) == 0:
                raise ValueError(f"No class directories found in {split_dirs['train']}")

            class_dirs.sort()
            class_to_label = {class_dir.name: i for i, class_dir in enumerate(class_dirs)}

            datasets = {}
            for split, split_dir in split_dirs.items():
                split_images = []
                for class_name, label in class_to_label.items():
                    class_dir = split_dir / class_name
                    if not class_dir.exists() or not class_dir.is_dir():
                        continue

                    class_images = []
                    for ext in image_extensions:
                        class_images.extend(list(class_dir.glob(ext)))

                    for img_path in class_images:
                        image_obj = DurianLeafImage(str(img_path), label, split=split)
                        split_images.append(image_obj)

                datasets[split] = split_images

            # Validate that each split contains images
            if not any(len(v) for v in datasets.values()):
                raise ValueError(f"Split directories are present but no images were found under {self.data_dir}")

            return datasets

        # Default behavior: consolidated class folders at root and random split
        class_dirs = [d for d in self.data_dir.iterdir() if d.is_dir()]
        if len(class_dirs) == 0:
            raise ValueError(f"No class directories found in {self.data_dir}")

        class_dirs.sort()
        class_to_label = {class_dir.name: i for i, class_dir in enumerate(class_dirs)}

        if len(class_to_label) < 2:
            raise ValueError(f"At least 2 classes are required; found {len(class_to_label)}")

        all_images = []
        for class_name, label in class_to_label.items():
            class_dir = self.data_dir / class_name

            class_images = []
            for ext in image_extensions:
                class_images.extend(list(class_dir.glob(ext)))

            if len(class_images) == 0:
                raise ValueError(f"No images found in class directory: {class_dir}")

            for img_path in class_images:
                image_obj = DurianLeafImage(str(img_path), label)
                all_images.append(image_obj)

        random.shuffle(all_images)

        n_total = len(all_images)
        n_train = int(0.8 * n_total)
        n_val = int(0.1 * n_total)

        train_images = all_images[:n_train]
        val_images = all_images[n_train:n_train + n_val]
        test_images = all_images[n_train + n_val:]

        for img in train_images:
            img.split = 'train'
        for img in val_images:
            img.split = 'val'
        for img in test_images:
            img.split = 'test'

        return {
            'train': train_images,
            'val': val_images,
            'test': test_images
        }

    def get_data_loader(self, split: str, is_training: bool = False) -> torch.utils.data.DataLoader:
        """Get PyTorch DataLoader for specified split."""
        if not hasattr(self, '_datasets'):
            self._datasets = self.load_dataset()

        if split not in self._datasets:
            raise ValueError(f"Invalid split: {split}. Must be one of: {list(self._datasets.keys())}")

        images = self._datasets[split]

        # Define transforms
        if is_training:
            transform = transforms.Compose([
                transforms.RandomHorizontalFlip(p=0.5),
                transforms.RandomVerticalFlip(p=0.5),
                transforms.RandomRotation(degrees=30),
                transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
        else:
            transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])

        dataset = DurianLeafDataset(images, transform=transform, is_training=is_training)

        # Use multiple workers if available (Windows multiprocessing uses spawn requirements)
        if os.name == 'nt':
            num_workers = 0
        else:
            num_workers = min(4, os.cpu_count() or 1)

        return torch.utils.data.DataLoader(
            dataset,
            batch_size=self.batch_size,
            shuffle=is_training,
            num_workers=num_workers,
            pin_memory=torch.cuda.is_available()
        )

    def get_class_distribution(self) -> Dict[int, int]:
        """Get class distribution across all splits."""
        if not hasattr(self, '_datasets'):
            self._datasets = self.load_dataset()

        distribution = {}
        for split, images in self._datasets.items():
            for img in images:
                label = img.class_label
                distribution[label] = distribution.get(label, 0) + 1

        return distribution

    def save_split_info(self, output_path: str):
        """Save dataset split information to JSON file."""
        if not hasattr(self, '_datasets'):
            self._datasets = self.load_dataset()

        split_info = {}
        for split, images in self._datasets.items():
            split_info[split] = [img.to_dict() for img in images]

        with open(output_path, 'w') as f:
            json.dump(split_info, f, indent=2, default=str)


def create_augmentation_pipeline():
    """Create data augmentation pipeline for training."""
    return transforms.Compose([
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.5),
        transforms.RandomRotation(degrees=30),
        transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
        transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])


def create_validation_transform():
    """Create transform pipeline for validation/test."""
    return transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])


if __name__ == "__main__":
    # Example usage
    data_loader = DataLoader("data/raw", batch_size=16)

    try:
        datasets = data_loader.load_dataset()
        print(f"Dataset loaded successfully:")
        print(f"Train: {len(datasets['train'])} images")
        print(f"Val: {len(datasets['val'])} images")
        print(f"Test: {len(datasets['test'])} images")

        distribution = data_loader.get_class_distribution()
        print(f"Class distribution: {distribution}")

        # Save split information
        data_loader.save_split_info("data/processed/dataset_split.json")

    except Exception as e:
        print(f"Error loading dataset: {e}")