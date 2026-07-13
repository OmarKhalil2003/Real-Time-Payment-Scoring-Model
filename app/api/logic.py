"""Shared fraud API logic (testable without FastAPI)."""

MODEL_VERSION = "xgboost-v1.0"


def determine_status(score: float) -> str:
    if score >= 0.85:
        return "DECLINED"
    if score >= 0.65:
        return "REVIEW"
    return "APPROVED"
