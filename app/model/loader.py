import joblib
from app.config.settings import settings

class ModelLoader:

    @staticmethod
    def load_model():
        return joblib.load(settings.MODEL_PATH)

    @staticmethod
    def load_scaler():
        return joblib.load(settings.SCALER_PATH)
