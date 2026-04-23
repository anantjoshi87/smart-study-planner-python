from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import mysql.connector
import json
from scheduler import generate_schedule, PlanRequest
from ai_service import enhance_schedule

app = FastAPI(title="AI Smart Study Planner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password', # UPDATE THIS
    'database': 'project'
}

@app.post("/generate-plan")
def create_plan(req: PlanRequest):
    # 1. Generate the logic and AI plan first
    try:
        original_plan = generate_schedule(req)
        ai_plan = enhance_schedule(original_plan)
    except Exception:
        raise HTTPException(status_code=400, detail="AI generation failed.")

    # 2. Database Connection and Saving
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        # Save to study_sessions
        # Note: req.user_id must exist in your PlanRequest model
        session_query = "INSERT INTO study_sessions (user_id, hours_per_day, total_days) VALUES (%s, %s, %s)"
        cursor.execute(session_query, (req.user_id, req.hours_per_day, req.total_days))
        session_id = cursor.lastrowid

        # Save to session_subjects
        subject_query = "INSERT INTO session_subjects (session_id, subject_name, priority_level) VALUES (%s, %s, %s)"
        for sub in req.subjects:
            cursor.execute(subject_query, (session_id, sub.name, sub.priority))

        # Save to generated_plans
        plan_query = "INSERT INTO generated_plans (session_id, raw_ai_json, formatted_text_summary) VALUES (%s, %s, %s)"
        # Saving the AI plan as a JSON string
        cursor.execute(plan_query, (session_id, json.dumps(ai_plan), ai_plan.get("summary", "")))

        conn.commit()

        return {
            "session_id": session_id,
            "original_plan": original_plan,
            "ai_plan": ai_plan
        }

    except Exception as e:
        conn.rollback()
        print(f"Database Error: {e}")
        raise HTTPException(status_code=500, detail="Plan generated but failed to save to history.")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
