from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
from app.database import Base

class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    identifiant = Column(String, unique=True, index=True)
    email = Column(String, unique=True, nullable=False)
    role = Column(String, default='analyste')
    mot_de_passe_hache = Column(String)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())