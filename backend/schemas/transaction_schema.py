from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TransactionCreate(BaseModel):
    transaction_ref: Optional[str] = None
    id_expediteur: Optional[str] = None
    id_beneficiaire: Optional[str] = None

    montant: float
    devise: Optional[str] = "MAD"
    pays: str
    date_heure: datetime

    nb_transactions_heure: int
    est_nouveau_beneficiaire: bool

    type: Optional[str] = None
    statut: Optional[str] = None


class TransactionResponse(TransactionCreate):
    id: int
    score_total: Optional[float] = None
    decision: Optional[str] = None
    niveau_risque: Optional[str] = None
    regles_declenchees: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True