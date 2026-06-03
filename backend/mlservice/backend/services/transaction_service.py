from sqlalchemy.orm import Session

from models.transaction_model import Transaction
from schemas.transaction_schema import TransactionCreate
from services.fraud_engine_service import FraudEngineService


class TransactionService:

    @staticmethod
    def create_transaction(db: Session, transaction_data: TransactionCreate):
        scoring_result = FraudEngineService.analyze(transaction_data)

        transaction = Transaction(
            transaction_ref=transaction_data.transaction_ref,
            id_expediteur=transaction_data.id_expediteur,
            id_beneficiaire=transaction_data.id_beneficiaire,
            montant=transaction_data.montant,
            devise=transaction_data.devise,
            pays=transaction_data.pays,
            date_heure=transaction_data.date_heure,
            nb_transactions_heure=transaction_data.nb_transactions_heure,
            est_nouveau_beneficiaire=transaction_data.est_nouveau_beneficiaire,
            type=transaction_data.type,
            statut=transaction_data.statut,

            score_total=scoring_result.score_total,
            decision=scoring_result.decision,
            niveau_risque=scoring_result.niveau_risque,
            regles_declenchees=", ".join(scoring_result.regles_declenchees)
        )

        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        return transaction

    @staticmethod
    def get_transactions(db: Session):
        return db.query(Transaction).all()

    @staticmethod
    def get_transaction_by_id(db: Session, transaction_id: int):
        return db.query(Transaction).filter(
            Transaction.id == transaction_id
        ).first()