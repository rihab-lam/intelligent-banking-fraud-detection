from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    identifiant: str
    email: EmailStr
    mot_de_passe: str
    role: str = "analyste"
    
class UserLogin(BaseModel):
    email: EmailStr
    mot_de_passe: str
    
class UserOut(BaseModel):
    id: int
    identifiant: str
    email: str
    role: str
    is_active: bool
    
    class Config:
        from_attributes = True
        
class Token(BaseModel):
    access_token: str
    token_type: str