import os
import subprocess
from app.config.settings import settings
import joblib


class ModelLoader:

    @staticmethod
    def load_model():
        if not os.path.exists(settings.MODEL_PATH):
            print("Model not found. Training automatically...")
            subprocess.run(["python", "scripts/train_dummy_model.py"], check=True)
        return joblib.load(settings.MODEL_PATH)

    @staticmethod
    def load_scaler():
        return joblib.load(settings.SCALER_PATH)
