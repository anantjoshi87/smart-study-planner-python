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
    'password': '@PANKAJkarpe1', # ENTER YOUR REAL PASSWORD HERE
    'database': 'project'
}

@app.post("/generate-plan")
def create_plan(req: PlanRequest):
    # 1. Generate Plans
    try:
        original_plan = generate_schedule(req)
        ai_plan = enhance_schedule(original_plan)
    except Exception as e:
        print(f"Generation Error: {e}")
        raise HTTPException(status_code=400, detail="Failed to generate plan.")

    # 2. Database Integration
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Save Session (Uses 'days' from your scheduler.py)
        session_query = "INSERT INTO study_sessions (user_id, hours_per_day, total_days) VALUES (%s, %s, %s)"
        cursor.execute(session_query, (req.user_id, req.hours_per_day, req.days))
        session_id = cursor.lastrowid

        # Save Subjects
        subject_query = "INSERT INTO session_subjects (session_id, subject_name, priority_level) VALUES (%s, %s, %s)"
        for sub in req.subjects:
            cursor.execute(subject_query, (session_id, sub.name, sub.priority))

        # Save AI Plan Output
        plan_query = "INSERT INTO generated_plans (session_id, raw_ai_json, formatted_text_summary) VALUES (%s, %s, %s)"
        # Note: We use ai_plan.get() to safely grab the summary if it exists
        summary = ai_plan.get("summary", "Study plan generated successfully.")
        cursor.execute(plan_query, (session_id, json.dumps(ai_plan), summary))

        conn.commit()
        
        return {
            "session_id": session_id,
            "original_plan": original_plan,
            "ai_plan": ai_plan
        }

    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
        raise HTTPException(status_code=500, detail="Database connection failed.")
    except Exception as e:
        print(f"Logic Error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
