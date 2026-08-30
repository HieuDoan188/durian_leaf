# Experiment Comparison

| experiment | task | test_accuracy | test_f1 | test_iou | test_dice | test_precision | test_recall | manual_gt_iou | manual_gt_dice | best_val_iou | best_val_loss | pseudo_mean_coverage |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| classification_efficientnet_b0 | classification | 0.9719 | 0.9719 |  |  | 0.9722 | 0.9719 |  |  |  |  |  |
| gradcam_unet | segmentation |  |  | 0.8126 | 0.8813 | 0.8851 | 0.9091 | 0.2169 | 0.3565 | 0.8150 | 0.2538 | 0.1698 |
| gradcampp_unetpp | segmentation |  |  | 0.5088 | 0.6181 | 0.6302 | 0.6952 |  |  | 0.4862 | 0.6180 | 0.0734 |
| sam_guard_unetpp | segmentation |  |  | 0.6781 | 0.7567 | 0.7723 | 0.8664 | 0.1351 | 0.2381 | 0.6838 | 0.4473 | 0.2543 |
| color_prior_unetpp | segmentation |  |  | 0.5084 | 0.6030 | 0.6665 | 0.6687 | 0.2183 | 0.3583 | 0.4947 | 0.6452 | 0.1319 |
