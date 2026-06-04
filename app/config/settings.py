import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    KAFKA_TOPIC: str = "payments"
    KAFKA_GROUP_ID: str = "payment-scoring-group"

    MYSQL_HOST: str = "mysql"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "password"
    MYSQL_DATABASE: str = "payment_scoring"

    MODEL_PATH: str = "model_artifacts/fraud_model.pkl"
    SCALER_PATH: str = "model_artifacts/scaler.pkl"

    MCP_ENABLED: bool = True


settings = Settings()

