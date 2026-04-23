import os
import json
from google import genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def enhance_schedule(original_schedule: dict) -> str:
    """Calls the Gemini API to enhance the provided study schedule."""
    original_str = json.dumps(original_schedule, indent=2)
    prompt = f"""
Here is a study schedule:
{original_str}

Improve this schedule by adding breaks, preventing burnout, and suggesting study techniques, while keeping total time the same.
CRITICAL: Keep your response extremely short and to the point. Structure your response using simple dashes (-) for bullet points to make it easy to read. DO NOT use any markdown asterisks (* or **) and DO NOT use bold text.
"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        # Fallback Demo Mode so the UI looks great even without an API key!
        subjects = list(original_schedule.get('daily_allocation', {}).keys())
        top_subject = subjects[0] if subjects else "your hardest subject"
        
        return f"""AI Study Recommendations (Demo Mode)
Note: You are currently seeing a mock response because GEMINI_API_KEY is not set.

- The 50/10 Rule for Focus: For {top_subject}, study for 50 minutes, then walk away for 10 minutes.
- Active Recall over Rereading: Spend 30% of your time self-testing instead of just reading.
- Burnout Prevention: You scheduled {original_schedule.get('metadata', {}).get('total_daily_hours', 1)} hours. Take a 45-minute lunch break and stop studying 1 hour before bed.

To activate real AI responses, add GEMINI_API_KEY to your .env file."""
    
    try:
        # Using the recommended new SDK format (Client automatically detects GEMINI_API_KEY)
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"AI API call failed: {str(e)}\n\nPlease double check your API key or network connection."
