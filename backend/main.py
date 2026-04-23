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

def ensure_schema(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            hours_per_day FLOAT NOT NULL,
            total_days INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS session_subjects (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id INT NOT NULL,
            subject_name VARCHAR(255) NOT NULL,
            priority_level INT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES study_sessions(id) ON DELETE CASCADE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS generated_plans (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id INT NOT NULL,
            raw_ai_json LONGTEXT NOT NULL,
            formatted_text_summary LONGTEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES study_sessions(id) ON DELETE CASCADE
        )
    """)

def normalize_ai_plan(ai_plan):
    if isinstance(ai_plan, dict):
        summary = ai_plan.get("summary", "Study plan generated successfully.")
        return ai_plan, summary

    if isinstance(ai_plan, str):
        return ai_plan, ai_plan

    fallback = str(ai_plan)
    return fallback, fallback

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
    session_id = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        ensure_schema(cursor)

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
        normalized_ai_plan, summary = normalize_ai_plan(ai_plan)
        cursor.execute(plan_query, (session_id, json.dumps(normalized_ai_plan), summary))

        conn.commit()

    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
        session_id = None
    except Exception as e:
        print(f"Logic Error: {e}")
        session_id = None
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

    return {
        "session_id": session_id,
        "original_plan": original_plan,
        "ai_plan": ai_plan
    }

@app.get("/history/{user_id}")
def get_history(user_id: int):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        ensure_schema(cursor)

        cursor.execute(
            """
            SELECT s.id, s.user_id, s.hours_per_day, s.total_days, s.created_at,
                   p.formatted_text_summary
            FROM study_sessions s
            LEFT JOIN generated_plans p ON p.session_id = s.id
            WHERE s.user_id = %s
            ORDER BY s.created_at DESC, s.id DESC
            """,
            (user_id,)
        )
        sessions = cursor.fetchall()

        for session in sessions:
            cursor.execute(
                """
                SELECT subject_name, priority_level
                FROM session_subjects
                WHERE session_id = %s
                ORDER BY id ASC
                """,
                (session["id"],)
            )
            session["subjects"] = cursor.fetchall()

        return sessions
    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")
        return []
    except Exception as e:
        print(f"History Error: {e}")
        return []
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
