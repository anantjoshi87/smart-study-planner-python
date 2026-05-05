import os
import json
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, Column, Integer, String, Text, DateTime, ForeignKey, inspect, text
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


class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name          = Column("username", String(120), nullable=False)
    email         = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column("hashed_password", String(255), nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow)


# ── Table Model ───────────────────────────────────────────────────────────────
class StudyPlan(Base):
    __tablename__ = "study_plans"

    id            = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id       = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
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
    ensure_study_plan_user_id_column()


def ensure_study_plan_user_id_column():
    """Adds user ownership to older study_plans tables created before auth existed."""
    inspector = inspect(engine)
    if "study_plans" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("study_plans")}
    if "user_id" in columns:
        return

    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE study_plans ADD COLUMN user_id INT NULL"))


# ── Session dependency for FastAPI routes ─────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
