from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    KAFKA_TOPIC: str = "payments"
    KAFKA_GROUP_ID: str = "payment-scoring-group"

    # Preferred: set DATABASE_URL directly (works for Postgres/MySQL/etc).
    # Example (Postgres): postgresql+psycopg2://postgres:password@postgres:5432/payment_scoring
    DATABASE_URL: str | None = None

    # Backward-compatible MySQL env vars (used only if DATABASE_URL is not set).
    MYSQL_HOST: str = "mysql"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "password"
    MYSQL_DATABASE: str = "payment_scoring"

    # Postgres env vars (used only if DATABASE_URL is not set).
    POSTGRES_HOST: str | None = None
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "payment_scoring"

    MODEL_PATH: str = "model_artifacts/fraud_model.pkl"
    SCALER_PATH: str = "model_artifacts/scaler.pkl"

    MCP_ENABLED: bool = True


settings = Settings()

