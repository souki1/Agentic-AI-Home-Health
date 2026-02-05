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
from models import User, CheckIn, RAGChunk
from schemas import (
    RegisterBody,
    LoginBody,
    AuthUser,
    AuthToken,
    AuthResponse,
    Patient,
    CheckInCreate,
    CheckInWithScores,
    RAGQueryRequest,
    RAGQueryResponse,
    RAGSource,
    RAGDocumentIngest,
    RAGIngestResponse,
)
from auth import hash_password, verify_password, create_access_token, get_current_user
from scores import compute_symptom_score, compute_risk_score, compute_status

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _rag_configured() -> bool:
    return bool(
        getattr(settings, "google_cloud_project", None)
        and getattr(settings, "vector_search_index_endpoint_id", None)
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create DB tables on startup; optionally load RAG chunk store. Do not block listen."""
    # Defer DB init so we bind to PORT first; run in thread to avoid blocking startup
    import threading
    def _init_db():
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables ready.")
        except OperationalError as e:
            logger.warning(
                "Could not connect to PostgreSQL. The API will start but DB endpoints will fail. Error: %s",
                str(e),
            )
    t = threading.Thread(target=_init_db, daemon=True)
    t.start()
    # Load RAG chunk store from file if configured
    rag_path = getattr(settings, "rag_chunk_store_path", None)
    if rag_path:
        try:
            from rag.lookup import load_store_from_path
            load_store_from_path(rag_path)
        except Exception as e:
            logger.warning("RAG chunk store load skipped: %s", e)
    yield
    pass


app = FastAPI(title="Health Analytics API", lifespan=lifespan)

# CORS: with allow_credentials=True you must set explicit origins (not "*")
# Parse CORS origins from env (comma-separated, all from CORS_ORIGINS env var)
cors_origins_str = settings.cors_origins
cors_origins_list = [
    origin.strip()
    for origin in cors_origins_str.split(",")
    if origin.strip()
] if cors_origins_str else []

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins_list,
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
    # Fallback name so Patient Name always shows in UI (e.g. after register without name)
    name = (u.name or "").strip()
    if not name and u.email:
        name = u.email.split("@")[0] or "Patient"
    return Patient(
        id=u.id,
        name=name or "Patient",
        age=u.age if u.age is not None else 0,
        condition=(u.condition or "").strip() or "—",
        created_at=u.created_at.isoformat() if u.created_at else "",
    )


# ----- Auth -----
@app.post("/auth/register", status_code=status.HTTP_204_NO_CONTENT)
def register(body: RegisterBody, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == body.email.lower()).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    role = (body.role or "patient").lower().strip()
    if role not in ("patient", "admin"):
        role = "patient"
    name = (body.name or "").strip() or None
    if not name:
        name = body.email.split("@")[0] if body.email else "User"
    user = User(
        email=body.email.lower(),
        hashed_password=hash_password(body.password),
        role=role,
        name=name,
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
        user=AuthUser(id=user.id, email=user.email, role=(user.role or "patient").lower()),
    )


@app.get("/auth/me", response_model=AuthUser)
def auth_me(current_user: User = Depends(get_current_user)):
    return AuthUser(id=current_user.id, email=current_user.email, role=(current_user.role or "patient").lower())


# ----- Patients -----
@app.get("/patients", response_model=list[Patient])
def list_patients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if (current_user.role or "").lower() == "admin":
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
    if (current_user.role or "").lower() == "admin":
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
    if (current_user.role or "").lower() == "patient":
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
    if (current_user.role or "").lower() == "patient" and body.patient_id != current_user.id:
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


# ----- RAG (Vertex AI) -----
@app.get("/rag/status")
def rag_status(db: Session = Depends(get_db)):
    """Return whether RAG is configured and chunk store is loaded. No auth required for status."""
    configured = _rag_configured()
    chunk_count = 0
    try:
        chunk_count = db.query(RAGChunk).count()
    except Exception:
        try:
            from rag.lookup import get_store
            chunk_count = len(get_store())
        except Exception:
            pass
    if not configured:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "configured": False,
                "message": "Set GOOGLE_CLOUD_PROJECT and VECTOR_SEARCH_INDEX_ENDPOINT_ID in .env to enable RAG.",
                "chunk_count": 0,
            },
        )
    return {
        "configured": True,
        "chunk_store_loaded": chunk_count > 0,
        "chunk_count": chunk_count,
    }


@app.post("/rag/query", response_model=RAGQueryResponse)
def rag_query(
    body: RAGQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Run RAG: embed question, search vector index, build prompt, generate answer. Requires auth."""
    if not _rag_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG is not configured. Set GOOGLE_CLOUD_PROJECT and VECTOR_SEARCH_INDEX_ENDPOINT_ID.",
        )
    try:
        from rag.lookup import lookup
        from rag.rag_pipeline import retrieve, build_prompt, generate

        # Use DB-aware lookup
        def db_lookup(chunk_id: str) -> str | None:
            return lookup(chunk_id, db_session=db)

        chunks = retrieve(body.question, db_lookup, top_k=body.top_k)
        prompt = build_prompt(body.question, chunks)
        answer = generate(prompt)
        sources = [RAGSource(chunk_id=cid, text=text) for cid, text in chunks]
        return RAGQueryResponse(answer=answer, sources=sources)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception("RAG query failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"RAG pipeline error: {e}",
        )


@app.post("/rag/ingest", response_model=RAGIngestResponse)
def rag_ingest(
    body: RAGDocumentIngest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Ingest a document: chunk it, embed it, store chunks in DB.
    Note: To add to Vector Search index, you'll need to build/update the index separately
    (use the embeddings output or call /rag/build-index after ingesting documents).
    Requires admin auth.
    """
    if (current_user.role or "").lower() != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can ingest documents",
        )
    if not _rag_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG is not configured. Set GOOGLE_CLOUD_PROJECT and VECTOR_SEARCH_INDEX_ENDPOINT_ID.",
        )
    try:
        from rag.chunking import chunk_by_fixed_size
        from rag.config import CHUNK_SIZE, CHUNK_OVERLAP
        from rag.embeddings import chunks_to_embeddings

        # Chunk the document
        chunks = chunk_by_fixed_size(
            body.text,
            source_id=body.source,
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
        if not chunks:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Document produced no chunks")

        # Store chunks in DB
        chunk_ids = []
        for chunk in chunks:
            existing = db.query(RAGChunk).filter(RAGChunk.id == chunk.id).first()
            if existing:
                existing.text = chunk.text
                existing.source = body.source
                existing.chunk_metadata = chunk.metadata
            else:
                db_chunk = RAGChunk(
                    id=chunk.id,
                    text=chunk.text,
                    source=body.source,
                    chunk_metadata=chunk.metadata,
                )
                db.add(db_chunk)
            chunk_ids.append(chunk.id)
        db.commit()

        logger.info("Ingested document '%s': %d chunks", body.source, len(chunk_ids))
        return RAGIngestResponse(
            chunks_created=len(chunk_ids),
            chunk_ids=chunk_ids,
            message=f"Document '{body.source}' ingested. {len(chunk_ids)} chunks stored. Next: build/update Vector Search index with these chunks.",
        )
    except Exception as e:
        db.rollback()
        logger.exception("RAG ingest failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest document: {e}",
        )


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
