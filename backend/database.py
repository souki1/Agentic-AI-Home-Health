# Ensure psycopg2 is available before SQLAlchemy tries to use it
# This helps with Windows multiprocessing issues in uvicorn --reload
try:
    import psycopg2
except ImportError:
    # On Windows, uvicorn --reload spawns processes that may not inherit the Python path
    # Try to add common Windows user site-packages locations
    import sys
    import site
    import os
    from pathlib import Path
    
    # Get user site-packages
    user_site = site.getusersitepackages()
    if user_site and Path(user_site).exists() and user_site not in sys.path:
        sys.path.insert(0, user_site)
    
    # Try to find Windows Store Python site-packages dynamically
    if os.name == 'nt':  # Windows
        packages_dir = Path.home() / "AppData" / "Local" / "Packages"
        if packages_dir.exists():
            # Find any PythonSoftwareFoundation.Python.* directory
            for python_dir in packages_dir.glob("PythonSoftwareFoundation.Python.*"):
                # Try both Python3X and Python313 format
                for py_ver_dir in [f"Python{sys.version_info.major}{sys.version_info.minor}", f"Python{sys.version_info.major}.{sys.version_info.minor}"]:
                    site_packages = python_dir / "LocalCache" / "local-packages" / py_ver_dir / "site-packages"
                    if site_packages.exists() and str(site_packages) not in sys.path:
                        sys.path.insert(0, str(site_packages))
                        break
    
    try:
        import psycopg2
    except ImportError:
        raise ImportError(
            "psycopg2-binary is not installed or not accessible. "
            "On Windows with uvicorn --reload, try using: python -m uvicorn main:app --reload --port 8000\n"
            "Or install/reinstall: pip install psycopg2-binary"
        )

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import logging

from config import settings

logger = logging.getLogger(__name__)

# Determine database connection URL from environment variables
# Priority: DATABASE_URL (TCP, works from Cloud Run or local) > INSTANCE_CONNECTION_NAME (Unix socket)
# Use DATABASE_URL when set (e.g. postgresql://user:pass@PUBLIC_IP:5432/health_analytics?sslmode=require)
database_url: str

if settings.database_url:
    # Direct connection (TCP) - use when socket is unavailable or for local dev
    database_url = settings.database_url
    logger.info("Using DATABASE_URL (direct TCP connection)")
elif settings.instance_connection_name:
    # Cloud SQL connection via Unix socket (recommended for Cloud Run)
    # All values MUST come from environment variables - no defaults
    db_user = settings.db_user
    db_pass = settings.db_pass
    db_name = settings.db_name
    instance_connection_name = settings.instance_connection_name
    db_port = settings.db_port
    sslmode = settings.db_sslmode
    
    # Validate required fields for Cloud SQL (all from env vars)
    if not db_user:
        raise ValueError(
            f"DB_USER is required when using INSTANCE_CONNECTION_NAME. "
            f"Set DB_USER in your environment variables (.env.local or Cloud Run env vars)."
        )
    if not db_name:
        raise ValueError(
            f"DB_NAME is required when using INSTANCE_CONNECTION_NAME. "
            f"Set DB_NAME in your environment variables (.env.local or Cloud Run env vars)."
        )
    # Format: postgresql+psycopg2://user:pass@/dbname?host=/cloudsql/instance&sslmode=require
    # Note: Password can be empty if using Cloud SQL IAM authentication
    query_parts = [f"host=/cloudsql/{instance_connection_name}"]
    if sslmode:
        query_parts.append(f"sslmode={sslmode}")
    if db_port is not None:
        query_parts.append(f"port={db_port}")
    query = "&".join(query_parts)
    if db_pass:
        database_url = f"postgresql+psycopg2://{db_user}:{db_pass}@/{db_name}?{query}"
    else:
        # No password (using IAM auth or password from Secret Manager)
        database_url = f"postgresql+psycopg2://{db_user}@/{db_name}?{query}"
    
    logger.info(f"Using Cloud SQL Unix socket: {instance_connection_name}")
else:
    # Neither is set - this should be caught by config validation, but handle gracefully
    raise ValueError(
        "Database connection not configured. "
        "Set either DATABASE_URL or INSTANCE_CONNECTION_NAME environment variable."
    )

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
