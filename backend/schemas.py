"""Request/response models for the API."""
from typing import Any, Optional

from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    password: str
    role: str = "patient"
    name: Optional[str] = None


class LoginBody(BaseModel):
    email: str
    password: str
    role: str = "patient"  # used when auto-registering new user


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthUser(BaseModel):
    id: str
    email: str
    role: str


class AuthResponse(BaseModel):
    token: Token
    user: AuthUser


class PatientOut(BaseModel):
    id: str
    name: str
    age: int
    condition: str
    created_at: str


class DeviceReadings(BaseModel):
    spo2: Optional[float] = None
    bp_systolic: Optional[float] = None
    bp_diastolic: Optional[float] = None
    weight_kg: Optional[float] = None
    glucose_mgdl: Optional[float] = None


class CheckInCreate(BaseModel):
    patient_id: str
    date: str
    fatigue: float = 0
    breathlessness: float = 0
    cough: float = 0
    pain: float = 0
    nausea: float = 0
    dizziness: float = 0
    swelling: float = 0
    anxiety: float = 0
    headache: float = 0
    chest_tightness: float = 0
    joint_stiffness: float = 0
    skin_issues: float = 0
    constipation: float = 0
    bloating: float = 0
    sleep_hours: float = 0
    meds_taken: bool = True
    appetite: str = "Normal"
    mobility: str = "Normal"
    devices: Optional[DeviceReadings] = None
    notes: Optional[str] = None


class CheckInWithScoresOut(BaseModel):
    id: str
    patient_id: str
    date: str
    fatigue: float
    breathlessness: float
    cough: float
    pain: float
    nausea: float
    dizziness: float
    swelling: float
    anxiety: float
    headache: float
    chest_tightness: float
    joint_stiffness: float
    skin_issues: float
    constipation: float
    bloating: float
    sleep_hours: float
    meds_taken: bool
    appetite: str
    mobility: str
    devices: Optional[Any] = None
    notes: Optional[str] = None
    symptom_score: float = 0
    risk_score: float = 0
    status: str = "Normal"
