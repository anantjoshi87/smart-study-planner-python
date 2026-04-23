from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from scheduler import generate_schedule, PlanRequest
from ai_service import enhance_schedule

app = FastAPI(title="AI Smart Study Planner API")

# Setup CORS to allow requests from the React frontend running on localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
