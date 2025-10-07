from sqlalchemy import Column, Integer, String
from app.db.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    wilaya = Column(String, nullable=False)
    commune = Column(String, nullable=False)
    phone = Column(String, unique=True, nullable=False)  
    password = Column(String, nullable=False)  
    doc = Column(String, nullable=True)  #pour le scan plus tard

    posts = relationship("Post", back_populates="user", cascade="all, delete")
    