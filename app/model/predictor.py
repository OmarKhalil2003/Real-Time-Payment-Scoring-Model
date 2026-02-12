import numpy as np

class Predictor:

    def __init__(self, model, scaler):
        self.model = model
        self.scaler = scaler

    def predict(self, features: list):
        features_array = np.array(features).reshape(1, -1)
        scaled = self.scaler.transform(features_array)

        score = float(self.model.predict_proba(scaled)[0][1])
        prediction = int(score > 0.5)

        return score, prediction
