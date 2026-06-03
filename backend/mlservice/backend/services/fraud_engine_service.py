import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
FRAUD_ENGINE_PATH = ROOT_DIR / "Fraud detection engine"

if str(FRAUD_ENGINE_PATH) not in sys.path:
    sys.path.insert(0, str(FRAUD_ENGINE_PATH))

from rules import Transaction as EngineTransaction
from score import calculer_score

class FraudEngineService:

    @staticmethod
    def analyze(transaction_data):
        tx = EngineTransaction(
            id=transaction_data.transaction_ref,
            id_expediteur=transaction_data.id_expediteur,
            id_beneficiaire=transaction_data.id_beneficiaire,
            montant=transaction_data.montant,
            devise=transaction_data.devise,
            pays=transaction_data.pays,
            date_heure=transaction_data.date_heure,
            nb_transactions_heure=transaction_data.nb_transactions_heure,
            est_nouveau_beneficiaire=transaction_data.est_nouveau_beneficiaire,
            type=transaction_data.type,
            statut=transaction_data.statut
        )

        result = calculer_score(tx)

        return result