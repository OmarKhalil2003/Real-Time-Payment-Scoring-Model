from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings

def _build_database_url() -> str:
    if settings.DATABASE_URL:
        return settings.DATABASE_URL

    # Prefer Postgres if configured (and running in docker-compose prod-grade stack)
    if settings.POSTGRES_HOST:
        return (
            f"postgresql+psycopg2://{settings.POSTGRES_USER}:"
            f"{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:"
            f"{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        )

    # Fallback to MySQL (legacy stack)
    return (
        f"mysql+pymysql://{settings.MYSQL_USER}:"
        f"{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:"
        f"{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
    )


DATABASE_URL = _build_database_url()

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
