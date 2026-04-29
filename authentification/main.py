import uvicorn
from fastapi import FastAPI
from app.database import Base, engine
from app.api import router

# Créer les tables automatiquement
Base.metadata.create_all(bind=engine)

# Créer l'application
app = FastAPI(title="Auth Service")

# Inclure les routes
app.include_router(router, prefix="/auth")

# Route de test
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "auth-service"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8081, reload=True)