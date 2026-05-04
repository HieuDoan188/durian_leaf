"""
Model definitions for durian leaf classification and segmentation.

Contains EfficientNet-based classification model and hybrid EfficientNet+UNet segmentation model.
"""

import torch
import torch.nn as nn
import torchvision
import torch.nn.functional as F


class EfficientNetClassifier(nn.Module):
    def __init__(self, num_classes: int = 8, backbone='efficientnet_b0', pretrained=True):
        super().__init__()
        if backbone == 'efficientnet_b0':
            self.base = torchvision.models.efficientnet_b0(weights=torchvision.models.EfficientNet_B0_Weights.IMAGENET1K_V1 if pretrained else None)
            in_features = self.base.classifier[1].in_features
            self.base.classifier = nn.Sequential(nn.Dropout(p=0.2, inplace=True), nn.Linear(in_features, num_classes))
        elif backbone == 'efficientnet_b4':
            self.base = torchvision.models.efficientnet_b4(weights=torchvision.models.EfficientNet_B4_Weights.IMAGENET1K_V1 if pretrained else None)
            in_features = self.base.classifier[1].in_features
            self.base.classifier = nn.Sequential(nn.Dropout(p=0.4, inplace=True), nn.Linear(in_features, num_classes))
        else:
            raise ValueError(f"Unsupported backbone: {backbone}")

    def forward(self, x):
        return self.base(x)

class DoubleConv(nn.Module):
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.double_conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )

    def forward(self, x):
        return self.double_conv(x)


class UNetDecoder(nn.Module):
    def __init__(self, feature_channels, decoder_channels):
        """
        feature_channels: [1280, 80, 40, 24]  (deep → shallow)
        decoder_channels: [256, 128, 64, 32]
        """
        super().__init__()
        self.up_blocks = nn.ModuleList()

        for i in range(len(feature_channels) - 1):
            in_ch   = feature_channels[i] if i == 0 else decoder_channels[i - 1]
            out_ch  = decoder_channels[i]
            skip_ch = feature_channels[i + 1]

            self.up_blocks.append(nn.ModuleDict({
                'up'  : nn.ConvTranspose2d(in_ch, out_ch, kernel_size=2, stride=2),
                'conv': DoubleConv(out_ch + skip_ch, out_ch)
            }))

    def forward(self, features):
        x = features[0]  # bottleneck: [B, 1280, 7, 7]

        for i, blocks in enumerate(self.up_blocks):
            x    = blocks['up'](x)
            skip = features[i + 1]

            if x.shape[2:] != skip.shape[2:]:
                x = F.interpolate(x, size=skip.shape[2:], mode='bilinear', align_corners=False)

            x = torch.cat([x, skip], dim=1)
            x = blocks['conv'](x)

        return x


class EfficientNetUNet(nn.Module):
    def __init__(self, num_classes: int = 1, pretrained: bool = True):
        super().__init__()

        weights = torchvision.models.EfficientNet_B0_Weights.IMAGENET1K_V1 if pretrained else None
        eff = torchvision.models.efficientnet_b0(weights=weights)
        self.encoder = nn.Sequential(*list(eff.features.children()))
        self.enc_indices = [2, 3, 4, 8]

        self.decoder = UNetDecoder(
            feature_channels=[1280, 80, 40, 24],
            decoder_channels=[256, 128, 64]  # ✅ 3 blocks = 3 values
        )

        self.final_conv = nn.Conv2d(64, num_classes, kernel_size=1)  # ✅ 64 thay vì 32

    def forward(self, x):
        input_size = x.shape[2:]
        features = []

        for i, layer in enumerate(self.encoder):
            x = layer(x)
            if i in self.enc_indices:
                features.append(x)

        features = features[::-1]  # [1280, 80, 40, 24]

        x = self.decoder(features)
        x = self.final_conv(x)
        x = F.interpolate(x, size=input_size, mode='bilinear', align_corners=False)
        return x