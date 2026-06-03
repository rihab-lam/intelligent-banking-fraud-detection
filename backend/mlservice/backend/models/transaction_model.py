from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, Text
from sqlalchemy.sql import func

from database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    transaction_ref = Column(String, nullable=True)
    id_expediteur = Column(String, nullable=True)
    id_beneficiaire = Column(String, nullable=True)

    montant = Column(Float, nullable=False)
    devise = Column(String, nullable=True)
    pays = Column(String, nullable=False)
    date_heure = Column(DateTime, nullable=False)

    nb_transactions_heure = Column(Integer, nullable=False)
    est_nouveau_beneficiaire = Column(Boolean, nullable=False)

    type = Column(String, nullable=True)
    statut = Column(String, nullable=True)

    score_total = Column(Float, nullable=True)
    decision = Column(String, nullable=True)
    niveau_risque = Column(String, nullable=True)
    regles_declenchees = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())