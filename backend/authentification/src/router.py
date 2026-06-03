# src/router.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# Importations depuis ton propre projet
from app.database import get_db  # Vérifie que le chemin d'importation de get_db correspond bien à ton architecture
from src.model import UserDB
from src.schemas import UserLogin, UserRegister, UserResponse
from src.security import hacher_password, verifier_password, creer_access_token

# Initialisation du routeur (sans préfixe ici car il est géré globalement dans main.py avec /auth)
router = APIRouter()

# =======================================================
# 1. ENDPOINT : INSCRIPTION (ID + EMAIL + MDP)
# =======================================================
@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Reçoit un identifiant, un e-mail et un mot de passe en clair.
    Vérifie l'unicité, hache le mot de passe et enregistre l'utilisateur.
    """
    # Vérifier si l'identifiant est déjà pris
    db_user_by_id = db.query(UserDB).filter(UserDB.identifiant == user_data.identifiant).first()
    if db_user_by_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet identifiant est déjà utilisé."
        )
    
    # Vérifier si l'adresse e-mail est déjà prise
    db_user_by_email = db.query(UserDB).filter(UserDB.email == user_data.email).first()
    if db_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cette adresse e-mail est déjà enregistrée."
        )
    
    # Créer l'instance du modèle de base de données avec le mot de passe haché
    new_user = UserDB(
        identifiant=user_data.identifiant,
        email=user_data.email,
        mot_de_passe_hache=hacher_password(user_data.password)
        # Le rôle ('analyste'), l'état actif (True) et la date sont gérés par les valeurs par défaut du modèle
    )
    
    # Sauvegarde dans la base de données
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


# =======================================================
# 2. ENDPOINT : CONNEXION (IDENTIFIANT + MDP UNIQUEMENT)
# =======================================================
@router.post("/login", status_code=status.HTTP_200_OK)
def login_user(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Vérifie l'identifiant et le mot de passe.
    Génère et retourne un Token JWT d'accès en cas de succès.
    """
    # 1. Chercher l'utilisateur par son identifiant unique
    db_user = db.query(UserDB).filter(UserDB.identifiant == credentials.identifiant).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiant ou mot de passe incorrect."
        )
    
    # 2. Vérifier si le mot de passe correspond au mot de passe haché en BDD
    if not verifier_password(credentials.password, db_user.mot_de_passe_hache):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiant ou mot de passe incorrect."
        )
    
    # 3. Vérifier si le compte est actif
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ce compte utilisateur a été désactivé."
        )
    
    # 4. Préparer les données utiles (payload) à intégrer dans le token JWT
    token_data = {
        "sub": db_user.identifiant,
        "role": db_user.role,
        "id": db_user.id
    }
    
    # 5. Générer le jeton d'accès sécurisé
    access_token = creer_access_token(data=token_data)
    
    # 6. Réponse renvoyée au frontend Streamlit
    return {
        "status": "success",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "identifiant": db_user.identifiant,
            "role": db_user.role
        }
    }