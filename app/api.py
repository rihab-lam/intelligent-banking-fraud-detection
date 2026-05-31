from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List
from src.scorer import score_transaction  # Logique de scoring ML isolée dans src/
from src.train import train as run_training

app = FastAPI(title="ML Fraud Detection Service", version="1.0.0")

class TransactionMLSchema(BaseModel):
    # Liste des caractéristiques numériques attendues par le modèle
    features: List[float] = Field(..., example=[100.5, 1.0, 0.0, 22.0])

@app.get("/")
def health_check():
    return {"status": "ok", "service": "ml-detection-service"}

@app.post("/predict")
def predict(transaction: TransactionMLSchema):
    """
    Endpoint pour obtenir une prédiction de fraude via le modèle Machine Learning.
    """
    try:
        result = score_transaction(transaction.features)
        return {"decision": result, "status": "processed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur de prédiction : {str(e)}")

@app.post("/train")
async def trigger_training(background_tasks: BackgroundTasks):
    """
    Endpoint pour déclencher le réentraînement du modèle en arrière-plan.
    """
    background_tasks.add_task(run_training)
    return {"message": "Le réentraînement du modèle a été lancé en arrière-plan."}