from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

from config import settings

# For Cloud SQL, use Unix socket if INSTANCE_CONNECTION_NAME is set
database_url = settings.database_url
if os.getenv("INSTANCE_CONNECTION_NAME"):
    # Cloud SQL connection via Unix socket
    db_user = os.getenv("DB_USER", "postgres")
    db_pass = os.getenv("DB_PASS", "root")
    db_name = os.getenv("DB_NAME", "healtappdb")
    instance_connection_name = os.getenv("INSTANCE_CONNECTION_NAME")
    # Format: postgresql+psycopg2://user:pass@/dbname?host=/cloudsql/instance
    database_url = f"postgresql+psycopg2://{db_user}:{db_pass}@/{db_name}?host=/cloudsql/{instance_connection_name}"

# Connection pool settings for Cloud Run
engine = create_engine(
    database_url,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
