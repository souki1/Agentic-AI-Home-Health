"""All API routes. Auth required except /health and /seed."""
import json
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status

from auth import create_access_token, get_current_user, pwd_ctx
from database import CheckIn, Patient, User, DbSession
from rag import get_rag_chat
from schemas import AuthResponse, AuthUser, ChatRequest, ChatResponse, CheckInCreate, CheckInWithScoresOut, LoginBody, PatientOut, Token, UserCreate
from scores import check_in_to_response

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


# ---- Auth ----
@router.post("/auth/register", status_code=status.HTTP_204_NO_CONTENT)
def register(body: UserCreate, db: DbSession):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    role = "patient" if body.role != "admin" else "admin"
    uid = str(uuid.uuid4())
    db.add(User(id=uid, email=body.email, hashed_password=pwd_ctx.hash(body.password), role=role))
    if role == "patient":
        name = (body.name or body.email or "Patient").strip() or "Patient"
        db.add(Patient(id=uid, name=name, age=0, condition=""))
    return Response(status_code=204)


@router.post("/auth/login", response_model=AuthResponse)
def login(body: LoginBody, db: DbSession):
    user = db.query(User).filter(User.email == body.email).first()
    if user:
        if not pwd_ctx.verify(body.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
    else:
        # Auto-register: create user (and patient if patient) so login always works
        uid = str(uuid.uuid4())
        role = "admin" if body.role == "admin" else "patient"
        db.add(User(id=uid, email=body.email, hashed_password=pwd_ctx.hash(body.password), role=role))
        if role == "patient":
            name = (body.email or "Patient").strip() or "Patient"
            db.add(Patient(id=uid, name=name, age=0, condition=""))
        db.flush()
        user = db.query(User).filter(User.id == uid).first()
    return AuthResponse(
        token=Token(access_token=create_access_token(user.id), token_type="bearer"),
        user=AuthUser(id=user.id, email=user.email, role=user.role),
    )


@router.get("/auth/me", response_model=AuthUser)
def me(current: AuthUser = Depends(get_current_user)):
    return current


# ---- Patients ----
@router.get("/patients", response_model=List[PatientOut])
def list_patients(db: DbSession, current: AuthUser = Depends(get_current_user)):
    rows = db.query(Patient).order_by(Patient.created_at.desc()).all()
    return [PatientOut(id=r.id, name=r.name, age=r.age, condition=r.condition, created_at=(r.created_at.isoformat() if r.created_at else "")) for r in rows]


@router.get("/patients/{patient_id}", response_model=PatientOut)
def get_patient(patient_id: str, db: DbSession, current: AuthUser = Depends(get_current_user)):
    r = db.query(Patient).filter(Patient.id == patient_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Patient not found")
    return PatientOut(id=r.id, name=r.name, age=r.age, condition=r.condition, created_at=(r.created_at.isoformat() if r.created_at else ""))


# ---- Check-ins ----
@router.get("/check-ins", response_model=List[CheckInWithScoresOut])
def list_check_ins(db: DbSession, patient_id: Optional[str] = None, current: AuthUser = Depends(get_current_user)):
    q = db.query(CheckIn)
    if patient_id:
        q = q.filter(CheckIn.patient_id == patient_id)
    return [CheckInWithScoresOut(**check_in_to_response(r)) for r in q.order_by(CheckIn.date.desc()).all()]


@router.post("/check-ins", response_model=CheckInWithScoresOut)
def create_check_in(body: CheckInCreate, db: DbSession, current: AuthUser = Depends(get_current_user)):
    if not db.query(Patient).filter(Patient.id == body.patient_id).first():
        raise HTTPException(status_code=404, detail="Patient not found")
    try:
        dt = datetime.fromisoformat(body.date.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        dt = datetime.utcnow()
    cid = str(uuid.uuid4())
    dev = json.dumps(body.devices.model_dump(exclude_none=True)) if body.devices else None
    row = CheckIn(
        id=cid, patient_id=body.patient_id, date=dt,
        fatigue=body.fatigue, breathlessness=body.breathlessness, cough=body.cough, pain=body.pain,
        nausea=body.nausea, dizziness=body.dizziness, swelling=body.swelling, anxiety=body.anxiety,
        headache=body.headache, chest_tightness=body.chest_tightness, joint_stiffness=body.joint_stiffness,
        skin_issues=body.skin_issues, constipation=body.constipation, bloating=body.bloating,
        sleep_hours=body.sleep_hours, meds_taken=body.meds_taken, appetite=body.appetite, mobility=body.mobility,
        devices=dev, notes=body.notes,
    )
    db.add(row)
    db.flush()
    return CheckInWithScoresOut(**check_in_to_response(row))


@router.post("/check-ins/sync-analytics", status_code=status.HTTP_204_NO_CONTENT)
def sync_analytics(current: AuthUser = Depends(get_current_user)):
    return Response(status_code=204)


# ---- Chat / RAG ----
@router.post("/chat", response_model=ChatResponse)
def chat(body: ChatRequest, db: DbSession, current: AuthUser = Depends(get_current_user)):
    """RAG chat endpoint. Uses Ollama locally or Vertex AI in cloud."""
    try:
        rag = get_rag_chat()
        history = None
        if body.conversation_history:
            history = [{"role": msg.role, "content": msg.content} for msg in body.conversation_history]
        response_text = rag.chat(body.message, current.id, db, history)
        return ChatResponse(response=response_text, provider=rag.provider)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


# ---- Seed ----
@router.post("/seed")
def seed(db: DbSession):
    if db.query(Patient).first():
        return {"message": "Already seeded"}
    db.add(Patient(id=str(uuid.uuid4()), name="Demo Patient", age=65, condition="CHF"))
    db.add(Patient(id=str(uuid.uuid4()), name="Jane Doe", age=58, condition="COPD"))
    return {"message": "Seeded demo patients"}
