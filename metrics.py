import io
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Indispensable pour éviter les bugs de thread avec FastAPI
import matplotlib.pyplot as plt
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from sklearn.metrics import roc_curve, auc

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

@router.get("/roc-curve")
def get_roc_curve():
    # Simulation de données (Remplace par tes vrais y_test et y_scores de ton modèle)
    y_true = np.array([0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0])
    y_scores = np.array([0.1, 0.2, 0.8, 0.3, 0.6, 0.9, 0.1, 0.85, 0.2, 0.3, 0.75, 0.4, 0.95, 0.7, 0.2])
    
    fpr, tpr, _ = roc_curve(y_true, y_scores)
    roc_auc = auc(fpr, tpr)
    
    # Création du graphique Matplotlib
    plt.figure(figsize=(6, 5))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'Courbe ROC (AUC = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('Taux de Faux Positifs (FPR)')
    plt.ylabel('Taux de Vrais Positifs (TPR)')
    plt.title('Courbe ROC - Détection de Fraude')
    plt.legend(loc="lower right")
    plt.grid(True, linestyle='--', alpha=0.6)
    
    # Sauvegarde de l'image dans un flux mémoire
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close()
    
    return StreamingResponse(buf, media_type="image/png")