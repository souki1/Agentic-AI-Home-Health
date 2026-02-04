from contextlib import asynccontextmanager
from typing import Optional
import logging

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from sqlalchemy import text

from config import settings
from database import engine, get_db, Base
from models import User, CheckIn
from schemas import (
    RegisterBody,
    LoginBody,
    AuthUser,
    AuthToken,
    AuthResponse,
    Patient,
    CheckInCreate,
    CheckInWithScores,
)
from auth import hash_password, verify_password, create_access_token, get_current_user
from scores import compute_symptom_score, compute_risk_score, compute_status

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create DB tables on startup. If PostgreSQL is not reachable, log and continue so the server still runs."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables ready.")
    except OperationalError as e:
        logger.warning(
            "Could not connect to PostgreSQL. The API will start but DB endpoints will fail. "
            "Check: 1) PostgreSQL is running  2) Database 'health_analytics' exists (createdb health_analytics)  "
            "3) backend/.env has the correct DATABASE_URL (user and password). Error: %s",
            str(e),
        )
    yield
    # shutdown if needed
    pass


app = FastAPI(title="Health Analytics API", lifespan=lifespan)

# CORS: with allow_credentials=True you must set explicit origins (not "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.exception_handler(Exception)
def global_exception_handler(request, exc):
    """Return JSON 500 so frontend gets a proper response (and CORS headers are applied)."""
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc) if str(exc) else "Internal server error"},
    )


def checkin_to_with_scores(c: CheckIn) -> CheckInWithScores:
    d = {
        "id": c.id,
        "patient_id": c.patient_id,
        "date": c.date,
        "fatigue": c.fatigue,
        "breathlessness": c.breathlessness,
        "cough": c.cough,
        "pain": c.pain,
        "nausea": c.nausea,
        "dizziness": c.dizziness,
        "swelling": c.swelling,
        "anxiety": c.anxiety,
        "headache": c.headache,
        "chest_tightness": c.chest_tightness,
        "joint_stiffness": c.joint_stiffness,
        "skin_issues": c.skin_issues,
        "constipation": c.constipation,
        "bloating": c.bloating,
        "sleep_hours": c.sleep_hours,
        "meds_taken": c.meds_taken,
        "appetite": c.appetite or "Normal",
        "mobility": c.mobility or "Normal",
        "devices": c.devices,
        "notes": c.notes,
    }
    symptom = compute_symptom_score(d)
    risk = compute_risk_score(d)
    status_val = compute_status(risk)
    return CheckInWithScores(**d, symptom_score=symptom, risk_score=risk, status=status_val)


def user_to_patient(u: User) -> Patient:
    return Patient(
        id=u.id,
        name=u.name or "",
        age=u.age if u.age is not None else 0,
        condition=u.condition or "",
        created_at=u.created_at.isoformat() if u.created_at else "",
    )


# ----- Auth -----
@app.post("/auth/register", status_code=status.HTTP_204_NO_CONTENT)
def register(body: RegisterBody, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == body.email.lower()).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = User(
        email=body.email.lower(),
        hashed_password=hash_password(body.password),
        role=body.role,
        name=body.name or None,
        age=None,
        condition=None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/auth/login", response_model=AuthResponse)
def login(body: LoginBody, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email.lower()).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_access_token(data={"sub": user.id})
    return AuthResponse(
        token=AuthToken(access_token=token, token_type="bearer"),
        user=AuthUser(id=user.id, email=user.email, role=user.role),
    )


@app.get("/auth/me", response_model=AuthUser)
def auth_me(current_user: User = Depends(get_current_user)):
    return AuthUser(id=current_user.id, email=current_user.email, role=current_user.role)


# ----- Patients -----
@app.get("/patients", response_model=list[Patient])
def list_patients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "admin":
        users = db.query(User).filter(User.role == "patient").order_by(User.created_at.desc()).all()
        return [user_to_patient(u) for u in users]
    # patient sees only themselves
    return [user_to_patient(current_user)]


@app.get("/patients/{patient_id}", response_model=Patient)
def get_patient(
    patient_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "admin":
        user = db.query(User).filter(User.id == patient_id, User.role == "patient").first()
    else:
        if patient_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
        user = current_user
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")
    return user_to_patient(user)


# ----- Check-ins -----
@app.get("/check-ins", response_model=list[CheckInWithScores])
def list_check_ins(
    patient_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(CheckIn)
    if current_user.role == "patient":
        q = q.filter(CheckIn.patient_id == current_user.id)
    elif patient_id:
        q = q.filter(CheckIn.patient_id == patient_id)
    rows = q.order_by(CheckIn.date.desc()).all()
    return [checkin_to_with_scores(c) for c in rows]


@app.post("/check-ins", response_model=CheckInWithScores)
def create_check_in(
    body: CheckInCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "patient" and body.patient_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can only create check-in for yourself")
    # ensure patient exists
    patient = db.query(User).filter(User.id == body.patient_id).first()
    if not patient:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Patient not found")
    c = CheckIn(
        patient_id=body.patient_id,
        date=body.date,
        fatigue=body.fatigue,
        breathlessness=body.breathlessness,
        cough=body.cough,
        pain=body.pain,
        nausea=body.nausea,
        dizziness=body.dizziness,
        swelling=body.swelling,
        anxiety=body.anxiety,
        headache=body.headache,
        chest_tightness=body.chest_tightness,
        joint_stiffness=body.joint_stiffness,
        skin_issues=body.skin_issues,
        constipation=body.constipation,
        bloating=body.bloating,
        sleep_hours=body.sleep_hours,
        meds_taken=body.meds_taken,
        appetite=body.appetite,
        mobility=body.mobility,
        devices=body.devices,
        notes=body.notes,
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return checkin_to_with_scores(c)


@app.post("/check-ins/sync-analytics", status_code=status.HTTP_204_NO_CONTENT)
def sync_analytics(
    current_user: User = Depends(get_current_user),
):
    # No-op for now; can run aggregations later
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/")
def root():
    return {"message": "Health Analytics API", "docs": "/docs"}


@app.get("/health")
def health():
    """Check if the API and database are reachable. Use this to verify DATABASE_URL."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "database": "unreachable",
                "hint": "Ensure PostgreSQL is running, database 'health_analytics' exists, and backend/.env DATABASE_URL is correct.",
                "error": str(e),
            },
        )
    return {"status": "ok", "database": "connected"}
