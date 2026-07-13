"""
Train XGBoost fraud detection model with versioning.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

ARTIFACTS_DIR = Path(os.getenv("MODEL_ARTIFACTS_DIR", "model_artifacts"))
MODEL_VERSION = os.getenv("MODEL_VERSION", "xgboost-v1.0")


def generate_training_data(n_samples: int = 50000) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(42)
    X = rng.random((n_samples, 3))
    y = ((X[:, 0] * 0.5 + X[:, 1] * 0.3 + X[:, 2] * 0.2) > 0.55).astype(int)
    # Inject fraud patterns
    fraud_idx = rng.choice(n_samples, size=int(n_samples * 0.04), replace=False)
    X[fraud_idx] = rng.uniform(0.7, 1.0, size=(len(fraud_idx), 3))
    y[fraud_idx] = 1
    return X, y


def train() -> dict:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    X, y = generate_training_data()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        eval_metric="logloss",
        random_state=42,
    )
    model.fit(X_train_scaled, y_train)

    y_proba = model.predict_proba(X_test_scaled)[:, 1]
    y_pred = model.predict(X_test_scaled)
    auc = roc_auc_score(y_test, y_proba)

    metrics = {
        "model_version": MODEL_VERSION,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "auc_roc": round(float(auc), 4),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "classification_report": classification_report(y_test, y_pred, output_dict=True),
    }

    joblib.dump(model, ARTIFACTS_DIR / "fraud_model.pkl")
    joblib.dump(scaler, ARTIFACTS_DIR / "scaler.pkl")
    with open(ARTIFACTS_DIR / "model_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    # Versioned snapshot
    version_dir = ARTIFACTS_DIR / "versions" / MODEL_VERSION
    version_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, version_dir / "fraud_model.pkl")
    joblib.dump(scaler, version_dir / "scaler.pkl")
    with open(version_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(json.dumps(metrics, indent=2))
    return metrics


if __name__ == "__main__":
    train()
