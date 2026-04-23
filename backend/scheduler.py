from pydantic import BaseModel, Field
from typing import List, Dict, Any

class Subject(BaseModel):
    name: str
    priority: int = Field(..., ge=1, le=5)

class PlanRequest(BaseModel):
    user_id: int  # <--- ADD THIS LINE
    subjects: List[Subject]
    hours_per_day: float
    days: int

def format_time(hours_float: float) -> str:
    h = int(hours_float)
    m = int(round((hours_float - h) * 60))
    m = int(round(m / 10.0) * 10)
    if m == 60:
        h += 1
        m = 0
    if h == 0 and m == 0:
        return "0 min"
    if h == 0:
        return f"{m} min"
    if m == 0:
        return f"{h} hr"
    return f"{h} hr {m} min"

def generate_schedule(schedule_req: PlanRequest) -> Dict[str, Any]:
    """
    Generates a structured study schedule using a GREEDY algorithm.
    """
    subjects = schedule_req.subjects
    daily_hours = schedule_req.hours_per_day
    num_days = schedule_req.days

    if not subjects:
        return {}

    min_time_per_subject = 0.5
    total_min_required = len(subjects) * min_time_per_subject

    if daily_hours <= total_min_required:
        min_time_per_subject = daily_hours / len(subjects)

    allocations = {sub.name: min_time_per_subject for sub in subjects}
    remaining_time = daily_hours - (min_time_per_subject * len(subjects))

    # GREEDY ALLOCATION based on priority weight
    if remaining_time > 0:
        total_priority = sum(sub.priority for sub in subjects)
        if total_priority > 0:
            for sub in subjects:
                proportion = sub.priority / total_priority
                extra_time = proportion * remaining_time
                allocations[sub.name] += extra_time

    formatted_allocations = {}
    for name, hours in allocations.items():
        formatted_allocations[name] = format_time(hours)

    return {
        "metadata": {
            "total_daily_hours": daily_hours,
            "total_days": num_days,
            "subjects_count": len(subjects)
        },
        "daily_allocation": formatted_allocations,
        "total_course_allocation": {
            name: format_time(hours * num_days) for name, hours in allocations.items()
        }
    }
