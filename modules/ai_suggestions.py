# modules/ai_suggestions.py

import os
from groq import Groq
from dotenv import load_dotenv

# load env variables
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_suggestions(cv_text, missing_skills):
    """
    Generate AI suggestions to improve resume
    """

    prompt = f"""
You are a professional resume reviewer.

Analyze the resume text and missing skills.

Resume Text:
{cv_text[:2000]}

Missing Skills:
{missing_skills}

Give short practical suggestions to improve this resume.
Focus on skills, projects, and improvements.
"""

    # Use environment variable to select the model; pick a supported default.
    preferred_model = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")

    # Try the preferred model first, then a few common fallbacks.
    candidate_models = [
        preferred_model,
        "mixtral-8x7b-32768",
        "llama2-70b-4096",
        "gemma-7b-it"
    ]

    last_error = None
    for model_name in candidate_models:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are an expert resume reviewer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200
            )

            return response.choices[0].message.content

        except Exception as e:
            last_error = e
            err_str = str(e).lower()
            if "model" not in err_str or ("not found" not in err_str and "decommissioned" not in err_str):
                break

    # Fallback: If all models fail, provide template-based suggestions
    return generate_fallback_suggestions(missing_skills)


def generate_fallback_suggestions(missing_skills):
    """
    Provide template-based suggestions when Groq API is unavailable.
    """
    suggestions = []
    
    if not missing_skills:
        suggestions.append("✓ Excellent! You have all the required skills for this role.")
        suggestions.append("• Consider adding certifications or advanced skills to stand out.")
    else:
        suggestions.append(f"• You are missing {len(missing_skills)} required skill(s):")
        for skill in missing_skills[:3]:
            suggestions.append(f"  - {skill}")
        suggestions.append("\n• Consider:")
        suggestions.append("  - Taking online courses in missing skills")
        suggestions.append("  - Adding more projects that demonstrate these skills")
        suggestions.append("  - Getting certifications in key areas")
    
    suggestions.append("\n• General tips:")
    suggestions.append("  - Use quantifiable achievements (e.g., '30% improvement', 'handled 50K+ items')")
    suggestions.append("  - Include relevant projects with GitHub links if available")
    suggestions.append("  - Add keywords from the job description naturally")
    
    return "\n".join(suggestions)
