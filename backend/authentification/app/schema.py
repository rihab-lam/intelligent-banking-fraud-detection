from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

class UserLogin(BaseModel):
    identifiant: str
    mot_de_passe: str

class UserCreate(BaseModel):
    identifiant: str
    email: EmailStr
    mot_de_passe: str
    role: str = "analyste"

class UserOut(BaseModel):
    id: int
    identifiant: str
    email: EmailStr
    role: str
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class EmailSchema(BaseModel):
    email: EmailStr          

class ResetPasswordSchema(BaseModel):
    nouveau_mot_de_passe: str