from rules import appliquer_toutes_les_regles, Transaction

class ResultatScoring:
    def __init__(self, score_total: float, decision: str, niveau_risque: str, regles_declenchees: list):
        self.score_total = score_total
        self.decision = decision
        self.niveau_risque = niveau_risque
        self.regles_declenchees = regles_declenchees

def calculer_score(tx: Transaction) -> ResultatScoring:
    resultats = appliquer_toutes_les_regles(tx)
    total = sum(r.score for r in resultats if r.declenchee == True)
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
    regles_declenchees = [r.regle for r in resultats if r.declenchee == True]
    
    return ResultatScoring(
        score_total=score_final,
        decision=decision,
        niveau_risque=niveau_risque,
        regles_declenchees=regles_declenchees
    )