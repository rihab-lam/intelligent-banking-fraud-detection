from typing import List
from dataclasses import dataclass
from rules import appliquer_toutes_les_regles, Transaction

@dataclass
class ResultatScoring:
    score_total: float
    decision: str
    niveau_risque: str
    regles_declenchees: List[str]

def calculer_score(tx: Transaction) -> ResultatScoring:
    resultats = appliquer_toutes_les_regles(tx)
    total = sum(r.score for r in resultats if r.declenchee)
    score_final = min(total, 100)
    
    if score_final < 50:
        decision = "normale"
        niveau_risque = "faible"
    elif score_final <= 70:
        decision = "suspecte"
        niveau_risque = "moyen"
    else:
        decision = "fraude"
        niveau_risque = "élevé"
    
    regles_declenchees = [r.regle for r in resultats if r.declenchee]
    
    return ResultatScoring(
        score_total=score_final,
        decision=decision,
        niveau_risque=niveau_risque,
        regles_declenchees=regles_declenchees
    )