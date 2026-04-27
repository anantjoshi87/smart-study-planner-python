import os
import json
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, DateTime
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

load_dotenv(Path(__file__).resolve().parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

# Railway provides `mysql://` URLs — SQLAlchemy needs `mysql+pymysql://`
# This line auto-fixes it so the app works regardless of which prefix is used.
if DATABASE_URL and DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

# MySQL-specific engine config
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,     # auto-reconnect on stale connections
    pool_recycle=280,       # recycle before MySQL's default wait_timeout (300s)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ── Table Model ───────────────────────────────────────────────────────────────
class StudyPlan(Base):
    __tablename__ = "study_plans"

    id            = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title         = Column(String(255), nullable=False)
    subjects      = Column(Text, nullable=False)     # JSON string
    hours_per_day = Column(String(50), nullable=False)
    days          = Column(Integer, nullable=False)
    original_plan = Column(Text, nullable=True)      # JSON string
    ai_plan       = Column(Text, nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow)

    def subjects_as_list(self):
        return json.loads(self.subjects) if self.subjects else []

    def original_plan_as_dict(self):
        return json.loads(self.original_plan) if self.original_plan else {}


# ── DB Initializer ────────────────────────────────────────────────────────────
def init_db():
    """Creates all tables in MySQL if they don't already exist."""
    Base.metadata.create_all(bind=engine)


# ── Session dependency for FastAPI routes ─────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
