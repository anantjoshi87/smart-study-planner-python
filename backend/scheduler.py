from pydantic import BaseModel, Field
from typing import List, Dict, Any

class Subject(BaseModel):
    name: str
    priority: int = Field(..., ge=1, le=5)

class PlanRequest(BaseModel):
    subjects: List[Subject]
    hours_per_day: float
    days: int

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

    for name in allocations:
        allocations[name] = round(allocations[name], 2)

    return {
        "metadata": {
            "total_daily_hours": daily_hours,
            "total_days": num_days,
            "subjects_count": len(subjects)
        },
        "daily_allocation": allocations,
        "total_course_allocation": {
            name: round(hours * num_days, 2) for name, hours in allocations.items()
        }
    }
