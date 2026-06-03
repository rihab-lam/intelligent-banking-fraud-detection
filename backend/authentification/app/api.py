from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database import get_db
from app.model import UserDB
from app.schema import UserCreate, UserLogin, UserOut, Token
from app.security import hacher_password, verifier_password, creer_access_token, SECRET_KEY, ALGORITHM

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ─── Endpoint 1 : Inscription ─────────────────────────────
@router.post("/register", response_model=UserOut, status_code=201)
async def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(UserDB).filter(
        (UserDB.email == user.email) | (UserDB.identifiant == user.identifiant)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email ou identifiant déjà utilisé")

    hashed = hacher_password(user.mot_de_passe)

    new_user = UserDB(
        identifiant        = user.identifiant,
        email              = user.email,
        mot_de_passe_hache = hashed,
        role               = user.role,
        is_active          = True,  # activé directement sans email
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# ─── Endpoint 2 : Connexion ───────────────────────────────
@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.identifiant == credentials.identifiant).first()
    if not user:
        raise HTTPException(status_code=401, detail="Identifiant introuvable")

    if not verifier_password(credentials.mot_de_passe, user.mot_de_passe_hache):
        raise HTTPException(status_code=401, detail="Mot de passe incorrect")

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Compte non activé."
        )

    token = creer_access_token({"sub": str(user.id), "role": user.role})
    return {"access_token": token, "token_type": "bearer"}


# ─── Endpoint 3 : Qui suis-je ? ──────────────────────────
def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
) -> UserDB:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=401, detail="Token invalide ou expiré")
        user_id = int(user_id_str)
    except (JWTError, ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")

    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return user


@router.get("/me", response_model=UserOut)
def get_me(current_user: UserDB = Depends(get_current_user)):
    return current_user