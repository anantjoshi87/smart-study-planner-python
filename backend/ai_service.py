import os
import time
import random
from google import genai
from google.genai import errors
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def call_gemini_with_retry(prompt: str, retries: int = 3):
    delay = 1.0
    client = genai.Client()
    
    for attempt in range(retries + 1):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            return response.text
        except Exception as e:
            if "RESOURCE_EXHAUSTED" in str(e):
                return {
                    "status": "quota_exceeded",
                    "message": "Daily AI limit reached. Please try again tomorrow."
                }
                
            error_msg = str(e).lower()
            is_transient = any(keyword in error_msg for keyword in ["503", "unavailable", "high demand", "serviceunavailable"])
            
            if is_transient:
                if attempt < retries:
                    time.sleep(delay + random.uniform(0, 0.5))
                    delay *= 2
                    continue
                else:
                    return "AI Generation Failed: Our AI servers are currently experiencing extremely high demand. Please wait a moment and try again!"
            else:
                if "api key" in error_msg or "403" in error_msg or "401" in error_msg:
                    return "AI Generation Failed: We couldn't authenticate with the AI service. Please ensure your API key is correctly configured."
                return "AI Generation Failed: An unexpected error occurred while generating your plan. Please try again later."

def enhance_schedule(original_schedule: dict):
    """Calls the Gemini API to enhance the provided study schedule."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        # Fallback Demo Mode so the UI looks great even without an API key!
        subjects_list = list(original_schedule.get('daily_allocation', {}).keys())
        top_subject = subjects_list[0] if subjects_list else "your hardest subject"
        
        return f"""AI Study Recommendations (Demo Mode)
Note: You are currently seeing a mock response because GEMINI_API_KEY is not set.

- The 50/10 Rule for Focus: For {top_subject}, study for 50 minutes, then walk away for 10 minutes.
- Active Recall over Rereading: Spend 30% of your time self-testing instead of just reading.
- Burnout Prevention: You scheduled {original_schedule.get('metadata', {}).get('total_daily_hours', 1)} hours. Take a 45-minute lunch break and stop studying 1 hour before bed.

To activate real AI responses, add GEMINI_API_KEY to your .env file."""

    subjects = ", ".join(original_schedule.get('daily_allocation', {}).keys())
    hours = original_schedule.get('metadata', {}).get('total_daily_hours', 1)
    days = original_schedule.get('metadata', {}).get('total_days', 7)

    prompt = f"""
Create a short study plan.
Subjects: {subjects}
Exam Date: In {days} days
Study Hours: {hours} hours/day

Add breaks, prevent burnout, suggest study techniques.
Use dashes (-) for bullets. NO asterisks, NO bold text. Keep it extremely short.
"""

    return call_gemini_with_retry(prompt)
