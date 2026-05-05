from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional
import base64
import hashlib
import hmac
import json
import os
import secrets

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import uvicorn

from scheduler import PlanRequest, generate_schedule
from ai_service import enhance_schedule
from database import StudyPlan, User, get_db, init_db


AUTH_SECRET_KEY = os.getenv("AUTH_SECRET_KEY") or "change-this-dev-secret"
TOKEN_EXPIRE_HOURS = int(os.getenv("TOKEN_EXPIRE_HOURS", "24"))
security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="AI Smart Study Planner API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AuthRequest(BaseModel):
    email: str
    password: str = Field(..., min_length=6)


class RegisterRequest(AuthRequest):
    name: str = Field(..., min_length=2, max_length=120)


class SavePlanRequest(BaseModel):
    title: str
    subjects: list
    hours_per_day: float
    days: int
    original_plan: dict
    ai_plan: Optional[str] = None


def encode_token_payload(payload: dict) -> str:
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def decode_token_payload(payload: str) -> dict:
    padded = payload + "=" * (-len(payload) % 4)
    return json.loads(base64.urlsafe_b64decode(padded.encode()).decode())


def sign_token(payload: str) -> str:
    signature = hmac.new(AUTH_SECRET_KEY.encode(), payload.encode(), hashlib.sha256).digest()
    return base64.urlsafe_b64encode(signature).decode().rstrip("=")


def create_access_token(user: User) -> str:
    expires_at = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)
    payload = encode_token_payload({"sub": user.id, "exp": int(expires_at.timestamp())})
    return f"{payload}.{sign_token(payload)}"


def get_password_hash(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120000)
    return f"{salt}${base64.b64encode(digest).decode()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        salt, expected_hash = password_hash.split("$", 1)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 120000)
        return hmac.compare_digest(base64.b64encode(digest).decode(), expected_hash)
    except ValueError:
        return False


def normalize_email(email: str) -> str:
    normalized = email.lower().strip()
    if "@" not in normalized or "." not in normalized.rsplit("@", 1)[-1]:
        raise HTTPException(status_code=422, detail="Please enter a valid email address.")
    return normalized


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


def serialize_plan(plan: StudyPlan) -> dict:
    return {
        "id": plan.id,
        "title": plan.title,
        "subjects": json.loads(plan.subjects) if plan.subjects else [],
        "hours_per_day": plan.hours_per_day,
        "days": plan.days,
        "original_plan": json.loads(plan.original_plan) if plan.original_plan else {},
        "ai_plan": plan.ai_plan,
        "created_at": plan.created_at.isoformat(),
    }


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Please log in to continue.",
    )

    try:
        payload_part, signature = credentials.credentials.split(".", 1)
        if not hmac.compare_digest(sign_token(payload_part), signature):
            raise credentials_exception
        payload = decode_token_payload(payload_part)
        if datetime.utcnow().timestamp() > payload["exp"]:
            raise credentials_exception
        user_id = int(payload["sub"])
    except Exception as exc:
        raise credentials_exception from exc

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise credentials_exception
    return user


@app.get("/")
def root():
    return {"status": "ok", "message": "AI Smart Study Planner API is running."}


@app.post("/auth/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    email = normalize_email(req.email)
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="An account with this email already exists.")

    user = User(name=req.name.strip(), email=email, password_hash=get_password_hash(req.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"user": serialize_user(user), "access_token": create_access_token(user)}


@app.post("/auth/login")
def login(req: AuthRequest, db: Session = Depends(get_db)):
    email = normalize_email(req.email)
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    return {"user": serialize_user(user), "access_token": create_access_token(user)}


@app.get("/auth/me")
def me(current_user: User = Depends(get_current_user)):
    return serialize_user(current_user)


@app.post("/generate-plan")
def create_plan(req: PlanRequest, current_user: User = Depends(get_current_user)):
    try:
        original_plan = generate_schedule(req)
        ai_plan = enhance_schedule(original_plan)
        return {"original_plan": original_plan, "ai_plan": ai_plan}
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="We couldn't create your study plan. Please check your inputs and try again.",
        ) from exc


@app.post("/save-plan")
def save_plan(
    req: SavePlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        plan = StudyPlan(
            user_id=current_user.id,
            title=req.title,
            subjects=json.dumps(req.subjects),
            hours_per_day=str(req.hours_per_day),
            days=req.days,
            original_plan=json.dumps(req.original_plan),
            ai_plan=req.ai_plan,
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return {"message": "Plan saved successfully!", "plan_id": plan.id, "plan": serialize_plan(plan)}
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save plan: {str(exc)}") from exc


@app.get("/plans")
def get_all_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plans = (
        db.query(StudyPlan)
        .filter(StudyPlan.user_id == current_user.id)
        .order_by(StudyPlan.created_at.desc())
        .all()
    )
    return [serialize_plan(plan) for plan in plans]


@app.get("/plans/{plan_id}")
def get_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = (
        db.query(StudyPlan)
        .filter(StudyPlan.id == plan_id, StudyPlan.user_id == current_user.id)
        .first()
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return serialize_plan(plan)


@app.delete("/plans/{plan_id}")
def delete_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    plan = (
        db.query(StudyPlan)
        .filter(StudyPlan.id == plan_id, StudyPlan.user_id == current_user.id)
        .first()
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    db.delete(plan)
    db.commit()
    return {"message": "Plan deleted successfully"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
