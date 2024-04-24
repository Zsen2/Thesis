from ultralytics import YOLO
import numpy as np

class FruitClassifier:
    def __init__(self, model_path):
        self.model = YOLO(model_path)

    def inference(self, frame):
        results = self.model(frame)
        names_dict = results[0].names
        probs = results[0].probs.data.tolist()
        max_prob_index = np.argmax(probs)
        predicted_class = names_dict[max_prob_index]

        return predicted_class, probs[max_prob_index]