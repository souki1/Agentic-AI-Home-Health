"""DB engine, session, and models. PostgreSQL only (e.g. Cloud SQL or local)."""
from collections.abc import Generator
from datetime import datetime
from typing import Annotated

from fastapi import Depends
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from config import settings

url = settings.database_url
engine = create_engine(url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


DbSession = Annotated[Session, Depends(get_db)]


class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class Patient(Base):
    __tablename__ = "patients"
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    condition = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


class CheckIn(Base):
    __tablename__ = "check_ins"
    id = Column(String(36), primary_key=True)
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False)
    fatigue = Column(Float, default=0)
    breathlessness = Column(Float, default=0)
    cough = Column(Float, default=0)
    pain = Column(Float, default=0)
    nausea = Column(Float, default=0)
    dizziness = Column(Float, default=0)
    swelling = Column(Float, default=0)
    anxiety = Column(Float, default=0)
    headache = Column(Float, default=0)
    chest_tightness = Column(Float, default=0)
    joint_stiffness = Column(Float, default=0)
    skin_issues = Column(Float, default=0)
    constipation = Column(Float, default=0)
    bloating = Column(Float, default=0)
    sleep_hours = Column(Float, default=0)
    meds_taken = Column(Boolean, default=True)
    appetite = Column(String(20), default="Normal")
    mobility = Column(String(20), default="Normal")
    devices = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
