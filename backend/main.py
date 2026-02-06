"""FastAPI app. Run: uvicorn main:app --reload --port 8000"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

from config import settings
from database import Base, get_engine
from routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    if (settings.database_url or "").strip():
        Base.metadata.create_all(bind=get_engine())
    yield


app = FastAPI(title="Health Analytics API", lifespan=lifespan)


@app.exception_handler(RuntimeError)
async def runtime_error_handler(request: Request, exc: RuntimeError):
    msg = str(exc)
    if "DATABASE_URL" in msg:
        return JSONResponse(
            status_code=503,
            content={"detail": "Database not configured. Set DATABASE_URL or Cloud Run secret DATABASE_URL_SECRET (Unix socket URL for Cloud SQL).", "error": msg},
        )
    return JSONResponse(status_code=500, content={"detail": msg})


@app.exception_handler(OperationalError)
async def db_connection_error_handler(request: Request, exc: OperationalError):
    return JSONResponse(
        status_code=503,
        content={"detail": "Database connection failed. Check DATABASE_URL and Cloud SQL connection.", "error": str(exc.orig) if getattr(exc, "orig", None) else str(exc)},
    )
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# All routes under /api (e.g. /api/health, /api/auth/login, /api/check-ins)
app.include_router(router, prefix="/api")


@app.get("/")
def root():
    return {"message": "Health Analytics API", "docs": "/docs", "health": "/api/health"}


@app.get("/health")
def health_root():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)
