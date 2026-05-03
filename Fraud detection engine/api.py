from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
from typing import List
from score import calculer_score
from rules import Transaction

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
def analyser_transaction(data: TransactionSchema) -> ResultatScoringSchema:
    tx = Transaction()
    tx.id = data.id
    tx.id_expediteur = data.id_expediteur
    tx.id_beneficiaire = data.id_beneficiaire
    tx.montant = data.montant
    tx.devise = data.devise
    tx.pays = data.pays
    tx.date_heure = data.date_heure
    tx.nb_transactions_heure = data.nb_transactions_heure
    tx.est_nouveau_beneficiaire = data.est_nouveau_beneficiaire
    tx.type = data.type
    tx.statut = data.statut
    resultat = calculer_score(tx)
    return ResultatScoringSchema(
        score_total=resultat.score_total,
        decision=resultat.decision,
        niveau_risque=resultat.niveau_risque,
        regles_declenchees=resultat.regles_declenchees
    )