from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import uvicorn
import json

from scheduler import generate_schedule, PlanRequest
from ai_service import enhance_schedule
from database import init_db, get_db, StudyPlan

# ── Create MySQL tables on startup (modern lifespan pattern) ─────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()   # runs on startup
    yield       # app is running
    # (add shutdown logic here if needed)

app = FastAPI(title="AI Smart Study Planner API", lifespan=lifespan)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ok", "message": "AI Smart Study Planner API is running."}


# ── Generate Plan ─────────────────────────────────────────────────────────────
@app.post("/generate-plan")
def create_plan(req: PlanRequest):
    try:
        original_plan = generate_schedule(req)
        ai_plan = enhance_schedule(original_plan)
        return {
            "original_plan": original_plan,
            "ai_plan": ai_plan
        }
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail="We couldn't create your study plan. Please check your inputs and try again."
        )


# ── Request schema for saving a plan ─────────────────────────────────────────
class SavePlanRequest(BaseModel):
    title: str
    subjects: list
    hours_per_day: float
    days: int
    original_plan: dict
    ai_plan: Optional[str] = None


# ── Save Plan to MySQL ────────────────────────────────────────────────────────
@app.post("/save-plan")
def save_plan(req: SavePlanRequest, db: Session = Depends(get_db)):
    try:
        plan = StudyPlan(
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
        return {"message": "Plan saved successfully!", "plan_id": plan.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save plan: {str(e)}")


# ── Get All Saved Plans ───────────────────────────────────────────────────────
@app.get("/plans")
def get_all_plans(db: Session = Depends(get_db)):
    plans = db.query(StudyPlan).order_by(StudyPlan.created_at.desc()).all()
    return [
        {
            "id": p.id,
            "title": p.title,
            "subjects": json.loads(p.subjects) if p.subjects else [],
            "hours_per_day": p.hours_per_day,
            "days": p.days,
            "original_plan": json.loads(p.original_plan) if p.original_plan else {},
            "ai_plan": p.ai_plan,
            "created_at": p.created_at.isoformat(),
        }
        for p in plans
    ]


# ── Get Single Plan by ID ─────────────────────────────────────────────────────
@app.get("/plans/{plan_id}")
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(StudyPlan).filter(StudyPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
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


# ── Delete a Plan ─────────────────────────────────────────────────────────────
@app.delete("/plans/{plan_id}")
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(StudyPlan).filter(StudyPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    db.delete(plan)
    db.commit()
    return {"message": "Plan deleted successfully"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
