from datetime import datetime
from typing import Optional

class Transaction:
    def __init__(self, id: str = None, id_expediteur: str = None, id_beneficiaire: str = None, 
                 montant: float = None, devise: str = None, pays: str = None, date_heure: datetime = None,
                 nb_transactions_heure: int = None, est_nouveau_beneficiaire: bool = None,
                 type: str = None, statut: str = None):
        self.id = id
        self.id_expediteur = id_expediteur
        self.id_beneficiaire = id_beneficiaire
        self.montant = montant
        self.devise = devise
        self.pays = pays
        self.date_heure = date_heure
        self.nb_transactions_heure = nb_transactions_heure
        self.est_nouveau_beneficiaire = est_nouveau_beneficiaire
        self.type = type
        self.statut = statut

class ResultatRegle:
    def __init__(self, regle: str, declenchee: bool, score: float, raison: Optional[str] = None):
        self.regle = regle
        self.declenchee = declenchee
        self.score = score
        self.raison = raison

PAYS_FAIBLE_RISQUE = [
    "MA", "FR", "BE", "ES", "IT", "DE",
    "NL", "PT", "GB", "SN", "CI", "CM",
    "GA", "TN", "DZ", "EG", "SA", "AE",
    "TR", "US", "CA"
]

PAYS_RISQUE_ELEVE = [
    "KP", "IR", "SY", "CU",
    "VE", "MM", "SD", "LY", "YE"
]

def regle_montant_eleve(tx: Transaction) -> ResultatRegle:
    if tx.montant > 20000:
        return ResultatRegle(
            regle="montant_tres_eleve",
            declenchee=True,
            score=100.0,
            raison=f"Le montant ({tx.montant}DH) dépasse le seuil critique de 20 000DH."
        )
    elif tx.montant >= 10000:
        return ResultatRegle(
            regle="montant_eleve",
            declenchee=True,
            score=75.0,
            raison=f"Le montant ({tx.montant}DH) dépasse le seuil de 10 000DH."
        )
    elif tx.montant > 3000:
        return ResultatRegle(
            regle="montant_a_surveiller",
            declenchee=True,
            score=50.0,
            raison=f"Montant significatif ({tx.montant}DH) au-dessus de la moyenne usuelle."
        )
    else:
        return ResultatRegle(
            regle="montant_standard",
            declenchee=False,
            score=0.0,
            raison=None
        )

def regle_heure_suspecte(tx: Transaction) -> ResultatRegle:
    heure = tx.date_heure.hour
    if heure >= 7 and heure <= 22:
        return ResultatRegle(
            regle="heure_standard",
            declenchee=False,
            score=0.0,
            raison=None
        )
    elif heure >= 22 or heure <= 1:
        return ResultatRegle(
            regle="heure_vigilance",
            declenchee=True,
            score=30.0,
            raison=f"Heure ({heure}h) en zone de vigilance."
        )
    else:
        return ResultatRegle(
            regle="heure_nuit_profonde",
            declenchee=True,
            score=60.0,
            raison=f"Heure ({heure}h) en nuit profonde."
        )

def regle_pays_inhabituel(tx: Transaction) -> ResultatRegle:
    if tx.pays in PAYS_RISQUE_ELEVE:
        return ResultatRegle(
            regle="pays_risque_eleve",
            declenchee=True,
            score=80.0,
            raison=f"Pays à risque élevé: {tx.pays}."
        )
    elif tx.pays not in PAYS_FAIBLE_RISQUE:
        return ResultatRegle(
            regle="pays_inhabituel",
            declenchee=True,
            score=40.0,
            raison=f"Pays inhabituel: {tx.pays}."
        )
    else:
        return ResultatRegle(
            regle="pays_standard",
            declenchee=False,
            score=0.0,
            raison=None
        )

def regle_trop_de_transactions(tx: Transaction) -> ResultatRegle:
    nb = tx.nb_transactions_heure
    if nb >= 1 and nb <= 3:
        return ResultatRegle(
            regle="transactions_normales",
            declenchee=False,
            score=0.0,
            raison=f"{nb} transactions/heure — activité normale."
        )
    elif nb >= 4 and nb <= 7:
        return ResultatRegle(
            regle="transactions_suspectes",
            declenchee=True,
            score=40.0,
            raison=f"{nb} transactions/heure — activité suspecte."
        )
    else:
        return ResultatRegle(
            regle="transactions_anormales",
            declenchee=True,
            score=80.0,
            raison=f"{nb} transactions/heure — activité anormale, possible fraude."
        )

def regle_nouveau_beneficiaire(tx: Transaction) -> ResultatRegle:
    if not tx.est_nouveau_beneficiaire:
        return ResultatRegle(
            regle="beneficiaire_connu",
            declenchee=False,
            score=0.0,
            raison=None
        )
    else:
        if tx.montant > 20000:
            return ResultatRegle(
                regle="nouveau_beneficiaire_montant_tres_eleve",
                declenchee=True,
                score=100.0,
                raison="Nouveau bénéficiaire avec montant très élevé."
            )
        elif tx.montant > 3000:
            return ResultatRegle(
                regle="nouveau_beneficiaire_montant_eleve",
                declenchee=True,
                score=75.0,
                raison="Nouveau bénéficiaire avec montant élevé."
            )
        else:
            return ResultatRegle(
                regle="nouveau_beneficiaire_petit_montant",
                declenchee=True,
                score=25.0,
                raison="Nouveau bénéficiaire avec petit montant, léger risque."
            )

def appliquer_toutes_les_regles(tx: Transaction) -> list:
    regles = [
        regle_montant_eleve,
        regle_heure_suspecte,
        regle_pays_inhabituel,
        regle_trop_de_transactions,
        regle_nouveau_beneficiaire,
    ]
    return [regle(tx) for regle in regles]


