from fastapi import FastAPI

from database import Base, engine
from routes.transaction_routes import router as transaction_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Fraud Detection API"
)

app.include_router(transaction_router)