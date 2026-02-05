"""FastAPI app. Run: uvicorn main:app --reload --port 8000"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import Base, engine
from routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Health Analytics API", lifespan=lifespan)
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
