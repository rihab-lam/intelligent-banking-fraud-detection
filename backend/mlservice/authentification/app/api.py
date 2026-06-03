from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Header
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.database import get_db
from src.model import UserDB
from app.schema import UserCreate, UserLogin, UserOut, Token
from src.security import hacher_password, verifier_password, creer_access_token, SECRET_KEY, ALGORITHM

router = APIRouter()

# ─── Endpoint 1 : Inscription ─────────────────────────────
@router.post("/register", response_model=UserOut, status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    
    # Vérifier si email existe déjà
    existing = db.query(UserDB).filter(UserDB.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    # Hacher le mot de passe
    hashed = hacher_password(user.mot_de_passe)
    
    # Créer l'objet UserDB
    new_user = UserDB(
        identifiant        = user.identifiant,
        email              = user.email,
        mot_de_passe_hache = hashed,
        role               = user.role
    )
    
    # Sauvegarder dans la base
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

# ─── Endpoint 2 : Connexion ───────────────────────────────
@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    
    # Chercher l'utilisateur par email
    user = db.query(UserDB).filter(UserDB.email == credentials.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Email introuvable")
    
    # Vérifier le mot de passe
    if not verifier_password(credentials.mot_de_passe, user.mot_de_passe_hache):
        raise HTTPException(status_code=401, detail="Mot de passe incorrect")
    
    # Créer le token JWT
    token = creer_access_token({"sub": str(user.id), "role": user.role})
    
    return {"access_token": token, "token_type": "bearer"}

# ─── Endpoint 3 : Qui suis-je ? ───────────────────────────
@router.get("/me", response_model=UserOut, responses={
    401: {"description": "Token invalide ou expiré"},
    404: {"description": "Utilisateur introuvable"}
})
def get_me(
    token: Annotated[str, Header()],
    db: Annotated[Session, Depends(get_db)]
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=401, detail="Token invalide ou expiré")
        user_id = int(user_id_str)
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")
    
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    
    return user