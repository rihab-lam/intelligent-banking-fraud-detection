# Scoring
from .predictor import predict_fraude, predict_proba_fraude


def score_transaction(transaction):
    score = predict_proba_fraude(transaction)[0][1]
    if score<=0.5:
        return "Approuvé"
    return "Bloqué"