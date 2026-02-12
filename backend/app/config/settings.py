from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    MYSQL_HOST: str = "mysql"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = "password"
    MYSQL_DB: str = "payments"

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    KAFKA_TOPIC: str = "transactions"
    KAFKA_GROUP_ID: str = "scoring-group"

    # Model
    MODEL_PATH: str = "model_artifacts/fraud_model.pkl"

    class Config:
        env_file = ".env"


settings = Settings()
