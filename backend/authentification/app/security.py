import os
import hashlib
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from dotenv import load_dotenv

load_dotenv()

# Configuration from environment variables
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def hacher_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verifier_password(plain: str, hashed: str) -> bool:
    """Verify plain password against hashed password"""
    return hashlib.sha256(plain.encode()).hexdigest() == hashed


def creer_access_token(data: dict):
    a_encoder = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    a_encoder.update({"exp": expire})
    return jwt.encode(a_encoder, SECRET_KEY, algorithm=ALGORITHM)

def decoder_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  
    except JWTError:
        return None