import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib

# Create synthetic dataset
np.random.seed(42)

X = np.random.rand(5000, 3)  # 3 features
y = (X[:, 0] + X[:, 1] * 0.5 + X[:, 2] * 0.2 > 0.9).astype(int)

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Scale
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

# Train model
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train_scaled, y_train)

# Create folder if not exists
os.makedirs("model_artifacts", exist_ok=True)

# Save artifacts
joblib.dump(model, "model_artifacts/fraud_model.pkl")
joblib.dump(scaler, "model_artifacts/scaler.pkl")

print("Dummy fraud model trained and saved successfully.")
