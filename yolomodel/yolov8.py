from ultralytics import YOLO

model = YOLO("D:\webPrac\\fastapi\yolomodel\yolov8.pt")

def inference(frame):
    results = model.predict(source=frame)

    names = results[0].names
    fruit_name = names[results[0].probs.top1]
    probs = results[0].probs.top1conf.cpu()

    return fruit_name, probs

