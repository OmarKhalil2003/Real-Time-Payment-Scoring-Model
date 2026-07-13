"""FastAPI prediction service for fraud scoring."""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field

from app.config.logging_config import setup_logging
from app.database.connection import SessionLocal
from app.database.models import ScoredTransaction
from app.model.loader import ModelLoader
from app.model.predictor import Predictor

setup_logging()
logger = logging.getLogger("fraud-api")

from app.api.logic import MODEL_VERSION, determine_status

_predictor: Optional[Predictor] = None

app = FastAPI(
    title="Fraud Detection API",
    description="Real-time payment fraud scoring with model versioning",
    version="1.0.0",
)


class PredictionRequest(BaseModel):
    transaction_id: str
    customer_id: str
    amount: float
    country: str = "Egypt"
    feature_1: float = Field(ge=0, le=1)
    feature_2: float = Field(ge=0, le=1)
    feature_3: float = Field(ge=0, le=1)


class PredictionResponse(BaseModel):
    transaction_id: str
    score: float
    prediction: int
    status: str
    confidence: float
    model_version: str
    latency_ms: float


def _get_predictor() -> Predictor:
    global _predictor
    if _predictor is None:
        model = ModelLoader.load_model()
        scaler = ModelLoader.load_scaler()
        _predictor = Predictor(model, scaler)
    return _predictor


@app.get("/health")
def health():
    return {"status": "healthy", "model_version": MODEL_VERSION}


@app.get("/metrics")
def metrics():
    """Prometheus-compatible basic metrics."""
    session = SessionLocal()
    try:
        total = session.query(ScoredTransaction).count()
        declined = session.query(ScoredTransaction).filter_by(status="DECLINED").count()
    finally:
        session.close()
    body = (
        f"# HELP fraud_transactions_total Total scored transactions\n"
        f"# TYPE fraud_transactions_total gauge\n"
        f"fraud_transactions_total {total}\n"
        f"# HELP fraud_declined_total Total declined transactions\n"
        f"# TYPE fraud_declined_total gauge\n"
        f"fraud_declined_total {declined}\n"
    )
    return Response(content=body, media_type="text/plain; version=0.0.4")


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    start = time.perf_counter()
    try:
        predictor = _get_predictor()
        score, prediction = predictor.predict([
            request.feature_1,
            request.feature_2,
            request.feature_3,
        ])
        status = determine_status(score)
        confidence = score if prediction == 1 else 1.0 - score
        latency_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "API predict tx=%s score=%.4f status=%s latency=%.2fms",
            request.transaction_id, score, status, latency_ms,
        )

        return PredictionResponse(
            transaction_id=request.transaction_id,
            score=round(score, 4),
            prediction=prediction,
            status=status,
            confidence=round(confidence, 4),
            model_version=MODEL_VERSION,
            latency_ms=round(latency_ms, 2),
        )
    except Exception as exc:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/predictions/{transaction_id}")
def get_prediction(transaction_id: str):
    session = SessionLocal()
    try:
        row = session.query(ScoredTransaction).filter_by(
            transaction_id=transaction_id
        ).first()
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return {
            "transaction_id": row.transaction_id,
            "score": row.score,
            "prediction": row.prediction,
            "status": row.status,
            "reason": row.reason,
            "model_version": MODEL_VERSION,
            "processed_at": row.processed_at.isoformat() if row.processed_at else None,
        }
    finally:
        session.close()
