from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime,Time
from sqlalchemy.orm import relationship
from datetime import datetime,timezone
from app.db.database import Base

#eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4IiwiZXhwIjoxNzU5OTIxMDc5fQ._c5pzbt8NwBnZoVIN2mquhWqYYRxopABJD55Jg_eTC0

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    departure = Column(Text, nullable=False)
    destination = Column(Text, nullable=False)
    departure_time = Column(Time, nullable=False)
    details = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Permet d'accéder facilement à l'utilisateur depuis la publication sans passer par getbyId
    user = relationship("User", back_populates="posts")
