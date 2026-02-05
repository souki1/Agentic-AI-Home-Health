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

from config import settings

# For Cloud SQL, use Unix socket if INSTANCE_CONNECTION_NAME is set (from env)
database_url = settings.database_url
if settings.instance_connection_name:
    # Cloud SQL connection via Unix socket (all values from settings/env)
    db_user = settings.db_user
    db_pass = settings.db_pass
    db_name = settings.db_name
    instance_connection_name = settings.instance_connection_name
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
