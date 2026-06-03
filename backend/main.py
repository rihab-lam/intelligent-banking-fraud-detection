from fastapi import FastAPI
import uvicorn
import sys
from pathlib import Path

from database import Base, engine
from routes.transaction_routes import router as transaction_router

# Add authentification module to path
AUTH_PATH = Path(__file__).parent / "authentification"
if str(AUTH_PATH) not in sys.path:
    sys.path.insert(0, str(AUTH_PATH))

from authentification.app.database import Base as AuthBase, engine as auth_engine
from authentification.app.api import router as auth_router

# Create tables for both main and auth databases
Base.metadata.create_all(bind=engine)
AuthBase.metadata.create_all(bind=auth_engine)

app = FastAPI(
    title="Fraud Detection API",
    version="1.0.0"
)

# Include routers
app.include_router(transaction_router)
app.include_router(auth_router, prefix="/auth")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "fraud-detection-api"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8081)