# Experiment Comparison

| experiment | task | test_accuracy | test_f1 | test_iou | test_dice | test_precision | test_recall | manual_gt_iou | manual_gt_dice | best_val_iou | best_val_loss | pseudo_mean_coverage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| classification_efficientnet_b0 | classification | 0.9730 | 0.9731 |  |  | 0.9734 | 0.9730 |  |  |  |  |  |
| gradcam_unet | segmentation |  |  | 0.7671 | 0.8623 | 0.8562 | 0.8877 |  |  | 0.7715 | 0.2959 | 0.1660 |
| gradcampp_unetpp | segmentation |  |  | 0.5135 | 0.6301 | 0.6169 | 0.7419 |  |  | 0.5438 | 0.5957 | 0.1504 |
| sam_guard_unetpp | segmentation |  |  | 0.6239 | 0.7053 | 0.7090 | 0.8752 |  |  | 0.6981 | 0.4478 | 0.2543 |
| color_prior_unetpp | segmentation |  |  | 0.3723 | 0.4703 | 0.5216 | 0.6136 | 0.2040 | 0.3389 | 0.3601 | 0.6953 | 0.1396 |
