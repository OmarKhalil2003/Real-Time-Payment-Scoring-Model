from fastapi import FastAPI
from app.api.routes import router
from app.database.models import Base
from app.database.session import engine

app = FastAPI(title="Real-Time Payment Scoring System")

Base.metadata.create_all(bind=engine)

app.include_router(router)
