"""Train model if missing — uses XGBoost trainer."""
import subprocess
import sys

if __name__ == "__main__":
    subprocess.run([sys.executable, "ml/train_model.py"], check=True)
