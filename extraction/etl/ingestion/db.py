"""
Database connection for the extraction (ingestion) module.

Points at Supabase Postgres via SUPABASE_DB_URL (or the generic
DATABASE_URL) -- no code changes needed between local Postgres, a
teammate's Postgres, and the real Supabase project. Get the connection
string from: Supabase Dashboard -> Project Settings -> Database ->
Connection string (URI) -- use the "Session pooler" or direct connection
string, and swap postgres:// for postgresql+psycopg2:// as shown below.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

# Accepts either SUPABASE_DB_URL or DATABASE_URL -- whichever is set.
# Example Supabase URL shape:
#   postgresql+psycopg2://postgres:<password>@db.<project-ref>.supabase.co:5432/postgres
DATABASE_URL = os.getenv("SUPABASE_DB_URL") or os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "No database URL configured. Set SUPABASE_DB_URL (or DATABASE_URL) "
        "in your .env file -- see .env.example."
    )

engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_session():
    return SessionLocal()
