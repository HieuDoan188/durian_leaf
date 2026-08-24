FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY utils ./utils
COPY notebooks/models/classification/checkpoints/best_model.pth ./notebooks/models/classification/checkpoints/best_model.pth
COPY notebooks/models/segmentation/checkpoints/efficientnet_unet_best.pth ./notebooks/models/segmentation/checkpoints/efficientnet_unet_best.pth
COPY notebooks/models/segmentation_v2/checkpoints/unetpp_best.pth ./notebooks/models/segmentation_v2/checkpoints/unetpp_best.pth
COPY notebooks/models/segmentation_v3/checkpoints/unetpp_v3_best.pth ./notebooks/models/segmentation_v3/checkpoints/unetpp_v3_best.pth
COPY notebooks/models/segmentation_v5/checkpoints/unetpp_v5_best.pth ./notebooks/models/segmentation_v5/checkpoints/unetpp_v5_best.pth
COPY notebooks/models/classification/metrics ./notebooks/models/classification/metrics
COPY notebooks/models/segmentation/metrics ./notebooks/models/segmentation/metrics
COPY notebooks/models/segmentation_v2/metrics ./notebooks/models/segmentation_v2/metrics
COPY notebooks/models/segmentation_v3/metrics ./notebooks/models/segmentation_v3/metrics
COPY notebooks/models/segmentation_v5/metrics ./notebooks/models/segmentation_v5/metrics

EXPOSE 8501

CMD ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
