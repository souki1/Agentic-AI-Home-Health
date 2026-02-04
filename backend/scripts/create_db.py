"""
Create the health_analytics database if it doesn't exist.
Run from backend folder: python scripts/create_db.py

Uses DATABASE_URL from .env but connects to the default 'postgres' database first,
then creates health_analytics.
"""
import sys
from urllib.parse import urlparse, urlunparse

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Load .env from backend folder
import os
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

url = os.environ.get("DATABASE_URL", "postgresql://postgres:root@localhost:5432/health_analytics")
parsed = urlparse(url)
# Connect to default 'postgres' database to create our DB
conn_url = urlunparse(parsed._replace(path="/postgres"))
conn = psycopg2.connect(conn_url)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()
cur.execute("SELECT 1 FROM pg_database WHERE datname = 'health_analytics'")
if cur.fetchone():
    print("Database 'health_analytics' already exists.")
else:
    cur.execute('CREATE DATABASE health_analytics')
    print("Database 'health_analytics' created.")
cur.close()
conn.close()
