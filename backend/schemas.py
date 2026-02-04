from pydantic import BaseModel
from typing import Optional


# ----- Auth -----
class RegisterBody(BaseModel):
    email: str
    password: str
    role: str  # 'patient' | 'admin'
    name: Optional[str] = None


class LoginBody(BaseModel):
    email: str
    password: str


class AuthUser(BaseModel):
    id: str
    email: str
    role: str

    class Config:
        from_attributes = True


class AuthToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthResponse(BaseModel):
    token: AuthToken
    user: AuthUser


# ----- Patient (same as User with role=patient for list/detail) -----
class Patient(BaseModel):
    id: str
    name: str
    age: int
    condition: str
    created_at: str

    class Config:
        from_attributes = True


# ----- Check-in -----
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
    sleep_hours: float = 7
    meds_taken: bool = True
    appetite: str = "Normal"
    mobility: str = "Normal"
    devices: Optional[dict] = None
    notes: Optional[str] = None


# ----- RAG -----
class RAGQueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = None


class RAGSource(BaseModel):
    chunk_id: str
    text: str


class RAGQueryResponse(BaseModel):
    answer: str
    sources: list[RAGSource] = []


class RAGDocumentIngest(BaseModel):
    text: str
    source: str  # e.g. "health_guidelines", "patient_record_123", etc.
    title: Optional[str] = None


class RAGIngestResponse(BaseModel):
    chunks_created: int
    chunk_ids: list[str]
    message: str


# ----- Check-in -----
class CheckInWithScores(BaseModel):
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
    devices: Optional[dict] = None
    notes: Optional[str] = None
    symptom_score: float = 0
    risk_score: float = 0
    status: str = "Normal"

    class Config:
        from_attributes = True
