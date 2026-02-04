import uuid
from sqlalchemy import Column, String, Integer, Boolean, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # 'patient' | 'admin'
    name = Column(String(255), nullable=True)
    age = Column(Integer, nullable=True)
    condition = Column("condition", String(255), nullable=True, quote=True)  # quote: reserved in PostgreSQL
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    check_ins = relationship("CheckIn", back_populates="patient", foreign_keys="CheckIn.patient_id")


class CheckIn(Base):
    __tablename__ = "check_ins"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    patient_id = Column(UUID(as_uuid=False), ForeignKey("users.id"), nullable=False)
    date = Column(String(10), nullable=False)
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
    sleep_hours = Column(Float, default=7)
    meds_taken = Column(Boolean, default=True)
    appetite = Column(String(20), default="Normal")
    mobility = Column(String(20), default="Normal")
    devices = Column(JSONB, nullable=True)
    notes = Column(Text, nullable=True)

    patient = relationship("User", back_populates="check_ins", foreign_keys=[patient_id])
