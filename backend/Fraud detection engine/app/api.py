from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import List
from src.score import calculer_score
from src.rules import Transaction
app = FastAPI()

class TransactionSchema(BaseModel):
    id: str
    id_expediteur: str
    id_beneficiaire: str
    montant: float
    devise: str
    pays: str
    date_heure: datetime
    nb_transactions_heure: int
    est_nouveau_beneficiaire: bool
    type: str
    statut: str

class ResultatScoringSchema(BaseModel):
    score_total: float
    decision: str
    niveau_risque: str
    regles_declenchees: List[str]

@app.post("/analyser-transaction")
def analyser_transaction(
    data: TransactionSchema, 
    # token: str = Depends(verify_token) # Optionnel: Ajouter une vérification ici
) -> ResultatScoringSchema:
    # Conversion directe du schéma Pydantic vers la dataclass Transaction
    tx = Transaction(**data.model_dump())
    resultat = calculer_score(tx)
    return ResultatScoringSchema(
        score_total=resultat.score_total,
        decision=resultat.decision,
        niveau_risque=resultat.niveau_risque,
        regles_declenchees=resultat.regles_declenchees
    )