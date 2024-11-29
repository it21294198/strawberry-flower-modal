from ultralytics import YOLO

model = YOLO("yolov8n.yaml")

results = model.train(
    data="dataset/data.yaml",
    epochs=100,
    patience=15,  # early stopping patience
)

metrics = model.val(conf=0.25)