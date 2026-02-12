import numpy as np
from app.model.predictor import Predictor

class DummyModel:
    def predict_proba(self, X):
        return np.array([[0.2, 0.8]])

class DummyScaler:
    def transform(self, X):
        return X

def test_predict():
    predictor = Predictor(DummyModel(), DummyScaler())
    score, prediction = predictor.predict([0.1, 0.2, 0.3])

    assert isinstance(score, float)
    assert prediction in [0, 1]
