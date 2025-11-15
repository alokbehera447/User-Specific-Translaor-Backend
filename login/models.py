from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True, nullable=True)  # Username for accent storage
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    # Relationship to saved accents
    saved_accents = relationship("SavedAccent", back_populates="user", cascade="all, delete-orphan")

class SavedAccent(Base):
    __tablename__ = "saved_accents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    accent_name = Column(String, nullable=False)  # User-provided name
    language_code = Column(String, nullable=False)  # e.g., "en", "hi", "fr"
    file_path = Column(String, nullable=False)  # Path to audio file
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to user
    user = relationship("User", back_populates="saved_accents")